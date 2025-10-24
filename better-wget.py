#!/usr/bin/env python3
import os
import sys

HISTORY_FILE = os.path.expanduser("~/.better_wget_history")

def set_lang():
    lang = input("Dil seçin / Choose language: 1-Türkçe 2-English: ")
    return "TR" if lang=="1" else "EN"

def print_title(lang):
    title = "=== BETTER-WGET ===" if lang=="EN" else "=== BETTER-WGET ==="
    print("\033[95m" + title + "\033[0m")

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r") as f:
        return [line.strip() for line in f.readlines()]

def save_history(url):
    history = load_history()
    if url not in history:
        history.append(url)
        with open(HISTORY_FILE, "w") as f:
            f.write("\n".join(history)+"\n")

def choose_history(lang):
    history = load_history()
    if not history:
        return None
    if lang=="TR":
        print("Önceki URL’ler:")
    else:
        print("Previous URLs:")
    for i, url in enumerate(history, start=1):
        print(f"{i}. {url}")
    choice = input("Seçim (boş bırak geç / Enter to skip): ")
    if choice.strip().isdigit():
        idx = int(choice)-1
        if 0 <= idx < len(history):
            return history[idx]
    return None

def wget_menu(lang):
    while True:
        print_title(lang)
        if lang=="TR":
            print("1. Tek dosya indir")
            print("2. Tüm site indir (mirror)")
            print("3. History’den URL seç")
            print("q. Çık")
            choice = input("> ")
        else:
            print("1. Download single file")
            print("2. Download entire site (mirror)")
            print("3. Choose URL from history")
            print("q. Quit")
            choice = input("> ")

        if choice.lower() == "q":
            break
        elif choice in ["1","2","3"]:
            if choice=="1":
                url = input("URL: ")
                save_history(url)
                fname = input("Dosya adı (boş bırak default) / File name: ").strip()
                speed = input("Hız limiti kb/s (boş = yok) / Speed limit kb/s: ").strip()
                fname_part = f"-O {fname}" if fname else ""
                speed_part = f"--limit-rate={speed}k" if speed else ""
                cmd = f"wget -c {fname_part} {speed_part} {url}"
                print(f"Çalıştırılıyor / Running: {cmd}")
                os.system(cmd)
            elif choice=="2":
                url = input("Site URL: ")
                save_history(url)
                folder = input("Kaydedilecek klasör / Folder: ").strip() or "./mirror"
                speed = input("Hız limiti kb/s (boş = yok) / Speed limit kb/s: ").strip()
                speed_part = f"--limit-rate={speed}k" if speed else ""
                cmd = f"wget --mirror -p --convert-links -P {folder} {speed_part} {url}"
                print(f"Çalıştırılıyor / Running: {cmd}")
                os.system(cmd)
            elif choice=="3":
                url = choose_history(lang)
                if url:
                    print(f"Seçilen URL: {url}")
                    fname = input("Dosya adı (boş bırak default) / File name: ").strip()
                    fname_part = f"-O {fname}" if fname else ""
                    cmd = f"wget -c {fname_part} {url}"
                    print(f"Çalıştırılıyor / Running: {cmd}")
                    os.system(cmd)
        else:
            print("Geçersiz seçim!" if lang=="TR" else "Invalid choice!")

if __name__=="__main__":
    try:
        lang = set_lang()
        wget_menu(lang)
    except KeyboardInterrupt:
        print("\nÇıkış / Exit")
        sys.exit(0)
