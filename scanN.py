#!/usr/bin/env python3
"""
syssec_no_install.py
Saf-Python yerel güvenlik kontrol aracı — ekstra paket indirtmez.
Kullanım: python3 syssec_no_install.py
Not: root ile çalıştırmak daha fazla bilgi verir.
"""

import os
import socket
import time
from datetime import datetime

# ---------- Ayarlar ----------
PORT_SCAN_TIMEOUT = 0.35  # saniye
DEFAULT_SCAN_RANGE = (1, 1024)
WORLD_WRITABLE_PATHS = ["/tmp"]
SUID_SEARCH_PATHS = ["/usr/bin", "/usr/sbin", "/bin", "/sbin"]

# ---------- Yardımcı fonksiyonlar ----------
def read_proc_net(path):
    try:
        with open(path, "r") as f:
            lines = f.read().splitlines()
        return lines
    except Exception:
        return []

def hex_to_ip_port(h):
    """local_address field '0100007F:1F90' -> ('127.0.0.1', 8080)"""
    try:
        ip_hex, port_hex = h.split(":")
        port = int(port_hex, 16)
        if len(ip_hex) == 8:  # IPv4
            ip = ".".join(str(int(ip_hex[i:i+2], 16)) for i in (6,4,2,0))
            return ip, port
        else:
            # IPv6 (not prettified)
            return ip_hex, port
    except Exception:
        return h, None

# ---------- Dinlenen portları oku (proc) ----------
def list_listening_proc():
    print("\n== /proc/net - Dinlenen bağlantılar (temel, paket gerektirmez) ==")
    files = ["/proc/net/tcp", "/proc/net/tcp6", "/proc/net/udp", "/proc/net/udp6"]
    found = False
    for p in files:
        lines = read_proc_net(p)
        if not lines or len(lines) < 2:
            continue
        print(f"\n-- {p} --")
        for L in lines[1:]:
            parts = L.split()
            if len(parts) < 2:
                continue
            local = parts[1]
            state = parts[3] if len(parts) > 3 else "??"
            ip, port = hex_to_ip_port(local)
            # state '0A' usually LISTEN for tcp
            print(f"{ip}:{port}  state={state}")
            found = True
    if not found:
        print("(proc/net içinde dinlenen port bulunamadı veya okuma yetkisi kısıtlı)")

# ---------- Lokal port tarayıcı (safe, pure Python) ----------
def scan_ports(host="127.0.0.1", port_range=(1,1024), timeout=PORT_SCAN_TIMEOUT):
    start, end = port_range
    print(f"\n== Lokal port taraması: {host} {start}-{end} (timeout={timeout}s) ==")
    open_ports = []
    for port in range(start, end+1):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        try:
            s.connect((host, port))
            open_ports.append(port)
        except Exception:
            pass
        finally:
            try:
                s.close()
            except:
                pass
    if open_ports:
        print("Açık portlar:", ", ".join(str(p) for p in open_ports))
    else:
        print("Açık port bulunamadı (tarama kısa, local).")

# ---------- SSH config kontrolü ----------
def check_ssh_config():
    print("\n== SSH (/etc/ssh/sshd_config) kontrolü ==")
    path = "/etc/ssh/sshd_config"
    if not os.path.exists(path):
        print("sshd_config bulunamadı.")
        return
    try:
        with open(path, "r", errors="ignore") as f:
            lines = f.read().splitlines()
        def find_opt(opt):
            for ln in lines:
                s = ln.strip()
                if not s or s.startswith("#"):
                    continue
                if s.lower().startswith(opt.lower()):
                    return s
            return None
        print("Örnek ayarlar (varsa):")
        for opt in ("PermitRootLogin", "PasswordAuthentication", "Port", "PermitEmptyPasswords", "ChallengeResponseAuthentication"):
            val = find_opt(opt)
            print(f" {opt}: {val if val else '(yok veya yorumlanmış)'}")
    except Exception as e:
        print("Okuma hatası:", e)

# ---------- World-writable kontrolü ----------
def check_world_writable(paths=WORLD_WRITABLE_PATHS, depth_limit=2):
    print("\n== World-writable dizin / örnek dosyalar (ilk derinlikler) ==")
    for root in paths:
        if not os.path.isdir(root):
            print(f" {root} yok.")
            continue
        print(f" Aranıyor: {root} (derinlik <= {depth_limit})")
        for cur_root, dirs, files in os.walk(root):
            level = cur_root[len(root):].count(os.sep)
            if level > depth_limit:
                dirs[:] = []  # derinliği sınırlamak için
                continue
            try:
                mode = os.stat(cur_root).st_mode
                if mode & 0o002:
                    print(f"  World-writable dir: {cur_root}")
            except Exception:
                pass

# ---------- SUID bitli dosyaları bul (sınırlı yollar) ----------
def check_suid(paths=SUID_SEARCH_PATHS, max_results=80):
    print("\n== SUID bitli dosyalar (sınırlı tarama) ==")
    results = []
    for p in paths:
        if not os.path.isdir(p):
            continue
        for root, dirs, files in os.walk(p):
            for fn in files:
                fp = os.path.join(root, fn)
                try:
                    st = os.stat(fp)
                    if st.st_mode & 0o4000:
                        results.append(fp)
                        if len(results) >= max_results:
                            break
                except Exception:
                    pass
            if len(results) >= max_results:
                break
        if len(results) >= max_results:
            break
    if results:
        for r in results[:max_results]:
            print(" ", r)
        if len(results) > max_results:
            print(f" ... ve daha fazla ({len(results)-max_results} adet) ...")
    else:
        print(" Önemli SUID dosyası bulunamadı (veya izin yok).")

# ---------- Basit öneriler ----------
def suggestions():
    print("\n== Hızlı öneriler ==")
    print("- Gereksiz servisleri kapatın (telnet, ftp vb.).")
    print("- SSH: PermitRootLogin no; mümkünse PasswordAuthentication no; SSH key kullanın.")
    print("- /tmp gibi dizinlerde world-writable içerikleri düzenli kontrol edin.")
    print("- SUID dosyalarını inceleyin; gereksizse izinleri kısıtlayın.")
    print("- Sistem güncellemelerini düzenli uygulayın.")

# ---------- Ana akış ----------
def main():
    print("=== SYSSEC (no-install) QUICK CHECK ===")
    if os.geteuid() == 0:
        print("Not: root olarak çalıştırılıyor — daha fazla bilgi alınabilir.")
    else:
        print("Not: root değilsiniz. Bazı kontroller eksik olabilir (daha ayrıntılı için sudo kullanın).")

    t0 = time.time()
    list_listening_proc()
    do_scan = input("\nLocal port taraması yap? (1-1024) [E/h]: ").strip().lower() or "e"
    if do_scan in ("e","evet","y","yes","1"):
        rng = input(f"Tarama aralığı gir (ör. 1-1024) veya Enter: ").strip()
        if rng:
            try:
                a,b = rng.split("-",1)
                a,b = int(a), int(b)
            except:
                print("Aralık parse edilemedi, varsayılan kullanılacak.")
                a,b = DEFAULT_SCAN_RANGE
            scan_ports("127.0.0.1", (a,b))
        else:
            scan_ports("127.0.0.1", DEFAULT_SCAN_RANGE)
    check_ssh_config()
    check_world_writable()
    check_suid()
    suggestions()
    print(f"\nTamam. Çalışma süresi: {time.time()-t0:.1f}s")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nİptal edildi.")
