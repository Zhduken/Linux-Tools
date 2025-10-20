#!/usr/bin/env python3
"""
syspulse - Terminal tabanlı Linux Sistem İzleme Aracı
Ahmet Yasin BEREKET tarafından geliştirildi
"""

import os
import platform
import shutil
import socket
import time

# ---------------- ASCII Art ----------------
ascii_art = r"""
   _____       __             ____  _
  / ___/____  / /___  ____ _ / __ \(_)___  ____ _
  \__ \/ __ \/ / __ \/ __ `/ / / / / / __ \/ __ `/
 ___/ / /_/ / / /_/ / /_/ / / /_/ / / / / / /_/ /
/____/\____/_/\____/\__,_/ /_____/_/_/ /_/\__, /
                                        /____/
    SYSPULSE - Linux Sistem İzleme Aracı
    Ahmet Yasin BEREKET tarafından oluşturuldu
"""

# ---------------- Sistem Bilgisi ----------------
def sistem_bilgisi():
    print("\n[ Sistem Bilgisi ]")
    print(f"Hostname: {platform.node()}")
    print(f"OS: {platform.system()} {platform.release()}")
    try:
        with open("/etc/os-release") as f:
            lines = f.readlines()
        for line in lines:
            if line.startswith("PRETTY_NAME"):
                print(f"Dağıtım: {line.strip().split('=')[1].replace('\"','')}")
                break
    except:
        print("Dağıtım bilgisi bulunamadı")
    uptime = round(float(open('/proc/uptime').read().split()[0])/3600,2)
    print(f"Sistem Açık Kalma Süresi: {uptime} saat")
    print()

def cpu_ve_ram():
    print("\n[ CPU & RAM ]")
    print(f"CPU Çekirdek Sayısı: {os.cpu_count()}")
    with open("/proc/meminfo") as f:
        meminfo = f.read()
    total_ram = int([x for x in meminfo.split("\n") if "MemTotal" in x][0].split()[1])/1024
    free_ram = int([x for x in meminfo.split("\n") if "MemAvailable" in x][0].split()[1])/1024
    print(f"RAM Kullanımı: {round((total_ram-free_ram)/total_ram*100,2)}% ({round(total_ram-free_ram,2)} MB / {round(total_ram,2)} MB)")
    print()

def disk_bilgisi():
    print("\n[ Disk Kullanımı ]")
    total, used, free = shutil.disk_usage("/")
    print(f"Disk Kullanımı: {round(used/1024**3,2)} GB / {round(total/1024**3,2)} GB ({round(used/total*100,2)}%)")
    print()

def ag_bilgisi():
    print("\n[ Ağ Bilgisi ]")
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        print(f"IP Adresi: {ip}")
    except:
        print("IP bilgisi alınamadı")
    print()

# ---------------- Menü ----------------
def menu():
    while True:
        os.system("clear")
        print(ascii_art)
        print("\nLütfen görmek istediğiniz bilgiyi seçin:")
        print("1 - Sistem Bilgisi")
        print("2 - CPU & RAM")
        print("3 - Disk Kullanımı")
        print("4 - Ağ Bilgisi")
        print("5 - Tüm Bilgileri Göster")
        print("0 - Çıkış")
        secim = input("\nSeçiminiz: ")

        if secim == "1":
            sistem_bilgisi()
        elif secim == "2":
            cpu_ve_ram()
        elif secim == "3":
            disk_bilgisi()
        elif secim == "4":
            ag_bilgisi()
        elif secim == "5":
            sistem_bilgisi()
            cpu_ve_ram()
            disk_bilgisi()
            ag_bilgisi()
        elif secim == "0":
            print("Çıkılıyor...")
            break
        else:
            print("Geçersiz seçenek!")
        input("\nDevam etmek için Enter'a basın...")

if __name__ == "__main__":
    menu()
