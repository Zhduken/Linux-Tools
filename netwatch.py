#!/usr/bin/env python3
"""
netwatch.py - Basit, paket gerektirmeyen ev ağı tarayıcı / izleyici
- Hiçbir harici Python paketi gerekmez.
- Linux üzerinde test edildi (uses /proc/net/arp).
Kullanım:
    python3 netwatch.py          # etkileşimli menü
    python3 netwatch.py --scan   # tek seferlik tarama
    python3 netwatch.py --watch 5  # her 5 saniyede tarama
"""

import os
import sys
import socket
import platform
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import csv

# ------------------ DÜZELTİLMİŞ ASCII BAŞLIK ------------------
ASCII = r"""
 _   _      _   _       _       _       _     __        __      _ _
| \ | | ___| |_| | ___ | | __ _| |_ ___| |__  \ \      / /__ _ (_) |
|  \| |/ _ \ __| |/ _ \| |/ _` | __/ __| '_ \  \ \ /\ / / _ \ | | |
| |\  |  __/ |_| | (_) | | (_| | || (__| | | |  \ V  V /  __/ | | |
|_| \_|\___|\__|_|\___/|_|\__,_|\__\___|_| |_|   \_/\_/ \___|_|_|_|

                             Net Watch !
          (ev ağı tarayıcı — standart kütüphaneler, Linux için)
"""
# ---------------------------------------------------------------

# --------- CONFIG ----------
DEFAULT_WORKERS = 60
PING_TIMEOUT = 1  # saniye
# --------------------------

COMMON_NETS = [
    "192.168.1.",
    "192.168.0.",
    "10.0.0.",
    "172.16.0."
]

def guess_local_subnet():
    # Deneyerek lokal IP al
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        my_ip = s.getsockname()[0]
        s.close()
        parts = my_ip.split('.')
        return f"{parts[0]}.{parts[1]}.{parts[2]}."
    except Exception:
        # fallback
        for p in COMMON_NETS:
            return p
    return "192.168.1."

def ping(ip):
    # ping tek paket, timeout 1s
    args = ["ping", "-c", "1", "-W", str(PING_TIMEOUT), ip]
    try:
        with open(os.devnull, 'wb') as DEVNULL:
            r = subprocess.run(args, stdout=DEVNULL, stderr=DEVNULL)
            return r.returncode == 0
    except Exception:
        return False

def read_arp_table():
    arp = {}
    try:
        with open("/proc/net/arp") as f:
            lines = f.readlines()[1:]
        for line in lines:
            parts = line.split()
            if len(parts) >= 4:
                ip = parts[0]
                mac = parts[3]
                arp[ip] = mac
    except Exception:
        pass
    return arp

def scan(subnet_prefix, start=1, end=254, workers=DEFAULT_WORKERS):
    live = []
    ips = [f"{subnet_prefix}{i}" for i in range(start, end+1)]
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(ping, ip): ip for ip in ips}
        for fut in as_completed(futures):
            ip = futures[fut]
            try:
                ok = fut.result()
                if ok:
                    live.append(ip)
            except Exception:
                pass
    return live

def reverse_dns(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except Exception:
        return "-"

def save_csv(entries, filename=None):
    if not filename:
        filename = f"netwatch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    try:
        with open(filename, "w", newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["IP", "MAC", "Hostname"])
            for e in entries:
                writer.writerow([e.get("ip",""), e.get("mac",""), e.get("host","")])
        print(f"CSV'ye kaydedildi: {filename}")
    except Exception as e:
        print("CSV kaydedilemedi:", e)

def single_scan_flow(subnet):
    print(f"\n[TARANIYOR] subnet: {subnet}0/24  (ping timeout {PING_TIMEOUT}s)\n")
    live = scan(subnet, 1, 254)
    arp = read_arp_table()
    results = []
    for ip in sorted(live, key=lambda x: tuple(map(int, x.split('.')))):
        mac = arp.get(ip, "—")
        host = reverse_dns(ip)
        results.append({"ip": ip, "mac": mac, "host": host})
    return results

def pretty_print(results):
    print(f"\nCanlı cihaz sayısı: {len(results)}\n")
    print(f"{'IP':16} {'MAC':20} {'Host/Not'}")
    print("-"*60)
    for r in results:
        print(f"{r['ip']:16} {r['mac']:20} {r['host']}")
    print()

def watch_mode(subnet, interval):
    try:
        while True:
            os.system("clear")
            print(ASCII)
            print(f"Watch modu — subnet: {subnet}0/24 — interval: {interval}s  (Ctrl+C ile çık)\n")
            results = single_scan_flow(subnet)
            pretty_print(results)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nWatch modu sonlandırıldı.")

def interactive_menu():
    os.system("clear")
    print(ASCII)
    print(f"Sistem: {platform.system()} {platform.release()}    Hostname: {platform.node()}\n")
    subnet = guess_local_subnet()
    while True:
        print("Seçenekler:")
        print(" 1) Hızlı tarama (tek seferlik)")
        print(" 2) İzle (watch) modu")
        print(" 3) Tarama sonucu CSV'ye kaydet")
        print(" 4) Alt ağ değiştir (şu an):", subnet + "0/24")
        print(" 0) Çıkış")
        choice = input("\nSeçiminiz: ").strip()
        if choice == "1":
            results = single_scan_flow(subnet)
            pretty_print(results)
            input("Devam için Enter'a basın...")
            os.system("clear")
            print(ASCII)
        elif choice == "2":
            try:
                sec = int(input("Interval (saniye, örn 5): ").strip())
            except:
                sec = 5
            watch_mode(subnet, sec)
            os.system("clear")
            print(ASCII)
        elif choice == "3":
            results = single_scan_flow(subnet)
            pretty_print(results)
            fn = input("CSV dosya adı (boş bırak default): ").strip() or None
            save_csv(results, fn)
            input("Devam için Enter'a basın...")
            os.system("clear")
            print(ASCII)
        elif choice == "4":
            new = input("Yeni subnet prefix (örn 192.168.1.): ").strip()
            if new.endswith("."):
                subnet = new
            else:
                print("prefix sonuna '.' eklemeyi unutma (örn 192.168.1.)")
            os.system("clear")
            print(ASCII)
        elif choice == "0":
            print("Çıkılıyor...")
            break
        else:
            print("Geçersiz seçim!")
            time.sleep(1)
            os.system("clear")
            print(ASCII)

def cli_main():
    # Basit CLI işleme: --scan, --watch N
    args = sys.argv[1:]
    subnet = guess_local_subnet()
    if "--help" in args or "-h" in args:
        print(__doc__)
        return
    if "--scan" in args:
        results = single_scan_flow(subnet)
        pretty_print(results)
        return
    if "--watch" in args:
        try:
            idx = args.index("--watch")
            interval = int(args[idx+1]) if idx+1 < len(args) else 5
        except Exception:
            interval = 5
        watch_mode(subnet, interval)
        return
    # GUI (etkileşimli)
    interactive_menu()

if __name__ == "__main__":
    try:
        cli_main()
    except KeyboardInterrupt:
        print("\nİptal edildi.")
