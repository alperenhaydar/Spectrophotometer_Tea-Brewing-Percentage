import tkinter as tk
from tkinter import ttk
import serial
import threading
import queue
import time
import re

PORT = "COM3"
BAUDRATE = 9600

q = queue.Queue()

def dem_durumu_hesapla(sayi):
    sayi = int(sayi)

    if sayi < 300:
        return "Az"
    elif sayi < 500:
        return "Az Az"
    elif sayi < 700:
        return "Orta"
    elif sayi < 1200:
        return "Orta Orta"
    elif sayi < 1500:
        return "Orta Çok"
    else:
        return "Çok Çok"

def seri_oku():
    try:
        ser = serial.Serial(PORT, BAUDRATE, timeout=1)
        time.sleep(2)
        ser.reset_input_buffer()

        while True:
            satir = ser.readline().decode("utf-8", errors="ignore").strip()
            if satir:
                print("GELEN SATIR =", repr(satir))
                q.put(satir)

    except Exception as e:
        q.put(f"HATA:{e}")

def arayuz_guncelle():
    try:
        while not q.empty():
            satir = q.get()

            if satir.startswith("HATA:"):
                hata_var.set(satir)
                continue

            eslesme = re.search(r"\d+", satir)

            if eslesme:
                sayi = eslesme.group()

                # ADC'yi her sayı geldiğinde güncelle
                adc_var.set(f"ADC Değeri: {sayi}")
                dem_var.set(f"Çayın Demlenme Durumu: {dem_durumu_hesapla(sayi)}")
                progress["value"] = min(int(sayi), 52000)

                # Kayıt mesajı geldiyse ayrıca kayıt kısmını güncelle
                if "KAYDEDILDI" in satir:
                    kayit_durum_var.set("Kaydedildi mi: Evet")
                    kayit_deger_var.set(f"Kaydedilen Değer: {sayi}")

                # Kalibrasyon mesajı ileride gelirse
                if "KALIBRASYON" in satir:
                    kal_durum_var.set("Kalibrasyon Yapıldı mı: Evet")
                    kal_deger_var.set(f"Kalibrasyon Değeri: {sayi}")

                hata_var.set("Veri alınıyor")

            else:
                hata_var.set(f"Sayı bulunamadı: {satir}")

    except Exception as e:
        hata_var.set(f"Arayüz hatası: {e}")

    pencere.after(100, arayuz_guncelle)

pencere = tk.Tk()
pencere.title("Çay Dem Yoğunluğu")
pencere.geometry("560x420")
pencere.resizable(False, False)

adc_var = tk.StringVar(value="ADC Değeri: -")
dem_var = tk.StringVar(value="Çayın Demlenme Durumu: -")
kayit_durum_var = tk.StringVar(value="Kaydedildi mi: Hayır")
kayit_deger_var = tk.StringVar(value="Kaydedilen Değer: -")
kal_durum_var = tk.StringVar(value="Kalibrasyon Yapıldı mı: Hayır")
kal_deger_var = tk.StringVar(value="Kalibrasyon Değeri: -")
hata_var = tk.StringVar(value="Bekleniyor")

tk.Label(
    pencere,
    text="Çay Dem Yoğunluğu",
    font=("Arial", 18, "bold")
).pack(pady=12)

tk.Label(
    pencere,
    textvariable=adc_var,
    font=("Arial", 14)
).pack(pady=5)

tk.Label(
    pencere,
    textvariable=dem_var,
    font=("Arial", 14)
).pack(pady=5)

progress = ttk.Progressbar(
    pencere,
    orient="horizontal",
    length=500,
    mode="determinate",
    maximum=2000
)
progress.pack(pady=12)

frame_kayit = tk.LabelFrame(pencere, text="Kayıt Bilgisi", padx=10, pady=10)
frame_kayit.pack(fill="x", padx=20, pady=10)

tk.Label(frame_kayit, textvariable=kayit_durum_var, font=("Arial", 12)).pack(pady=3)
tk.Label(frame_kayit, textvariable=kayit_deger_var, font=("Arial", 12)).pack(pady=3)

frame_kal = tk.LabelFrame(pencere, text="Kalibrasyon Bilgisi", padx=10, pady=10)
frame_kal.pack(fill="x", padx=20, pady=10)

tk.Label(frame_kal, textvariable=kal_durum_var, font=("Arial", 12)).pack(pady=3)
tk.Label(frame_kal, textvariable=kal_deger_var, font=("Arial", 12)).pack(pady=3)

tk.Label(
    pencere,
    textvariable=hata_var,
    fg="blue",
    font=("Arial", 10)
).pack(pady=8)

threading.Thread(target=seri_oku, daemon=True).start()
arayuz_guncelle()

pencere.mainloop()