#!/usr/bin/env python3
"""
ginfo - Linux Sistem Bilgi Aracı
Ahmet Yasin BEREKET tarafından geliştirildi
"""

import os
import platform
import psutil
import socket
import subprocess

def sistem_bilgisi():
    print("===== Sistem Bilgisi =====")
    print(f"Kullanıcı: {os.getlogin()}")
    print(f"Hostname: {platform.node()}")
    print(f"İşletim Sistemi: {platform.system()} {platform.release()}")
    print(f"Kernel: {platform.version()}")
    print(f"CPU: {platform.processor()} ({psutil.cpu_count()} çekirdek)")
    print(f"RAM: {round(psutil.virtual_memory().total / (1024**3), 2)} GB")
    print(f"IP Adresi: {socket.gethostbyname(socket.gethostname())}")
    print()

def disk_kullanimi():
    print("===== Disk Kullanımı =====")
    for part in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(part.mountpoint)
            print(f"{part.device} -> {round(usage.used / (1024**3),2)}GB / {round(usage.total / (1024**3),2)}GB ({usage.percent}%)")
        except PermissionError:
            continue
    print()

def ag_bilgisi():
    print("===== Ağ Bilgisi =====")
    interfaces = psutil.net_if_addrs()
    for intf_name, addresses in interfaces.items():
        for addr in addresses:
            if addr.family == socket.AF_INET:
                print(f"{intf_name}: {addr.address}")
    print()

def prosesler():
    print("===== Çalışan Süreçler =====")
    for proc in psutil.process_iter(['pid', 'name', 'username']):
        print(f"PID: {proc.info['pid']}, İsim: {proc.info['name']}, Kullanıcı: {proc.info['username']}")
    print()

def paket_kontrol(paket):
    print(f"===== {paket} Paketi Kontrolü =====")
    result = subprocess.run(['dpkg', '-s', paket], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if "installed" in result.stdout:
        print(f"{paket} yüklü.")
    else:
        print(f"{paket} yüklü değil.")
    print()

def menu():
    while True:
        print("""

 _____ _____ _   _ ______ _____  
|  __ \_   _| \ | ||  ___|  _  | 
| |  \/ | | |  \| || |_  | | | | 
| | __  | | | . ` ||  _| | | | | 
| |_\ \_| |_| |\  || |   \ \_/ / 
 \____/\___/\_| \_/\_|    \___/   
==================== ginfo ====================
1. Sistem Bilgisi
2. Disk Kullanımı
3. Ağ Bilgisi
4. Çalışan Süreçler
5. Paket Kontrolü
6. Çıkış
===============================================
        """)
        secim = input("Seçiminiz: ")
        if secim == "1":
            sistem_bilgisi()
        elif secim == "2":
            disk_kullanimi()
        elif secim == "3":
            ag_bilgisi()
        elif secim == "4":
            prosesler()
        elif secim == "5":
            paket = input("Kontrol etmek istediğiniz paketin adını yazın: ")
            paket_kontrol(paket)
        elif secim == "6":
            print("Çıkış yapılıyor...")
            break
        else:
            print("Geçersiz seçim!")

if __name__ == "__main__":
    menu()
