import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import yt_dlp
import threading
import configparser

# Ayarları kaydetmek için bir configparser kullanımı
config = configparser.ConfigParser()
config_file = "settings.ini"

# Ayarları yükle veya varsayılanları oluştur
if os.path.exists(config_file):
    config.read(config_file)
    default_download_path = config["Settings"]["download_path"]
else:
    default_download_path = os.path.expanduser("~/Downloads")  # Varsayılan indirme yeri
    config["Settings"] = {"download_path": default_download_path}
    with open(config_file, "w") as file:
        config.write(file)

def save_download_path(path):
    """Yeni indirme yolunu ayarlar dosyasına kaydeder."""
    config["Settings"]["download_path"] = path
    with open(config_file, "w") as file:
        config.write(file)

def set_download_path():
    """Kullanıcının yeni bir indirme yolu seçmesine izin verir."""
    global default_download_path
    new_path = filedialog.askdirectory()
    if new_path:
        default_download_path = new_path
        save_download_path(new_path)
        messagebox.showinfo("Başarılı", f"Yeni indirme klasörü: {new_path}")

def get_video_info(url):
    """Video bilgilerini alır (başlık ve altyazı seçenekleri)."""
    with yt_dlp.YoutubeDL() as ydl:
        result = ydl.extract_info(url, download=False)
        video_title = result.get('title', 'Video Adı Bulunamadı')
        subtitles = result.get('subtitles', {})
        available_subtitles = []

        # Altyazı seçeneklerini al
        for lang in subtitles:
            available_subtitles.append(lang)

        return video_title, available_subtitles

def download_video():
    try:
        url = url_entry.get()
        if not url:
            messagebox.showerror("Hata", "Lütfen bir YouTube URL'si girin!")
            return

        video_title, available_subtitles = get_video_info(url)
        status_label.config(text=f"Video Başlığı: {video_title}")

        ydl_opts = {
            'format': 'best',
            'outtmpl': os.path.join(default_download_path, '%(title)s.%(ext)s'),
            'progress_hooks': [on_progress],
            'writeinfojson': False,  # Bilgi dosyasını yaz
        }

        # Altyazı indirme seçeneğini ekle
        if subtitle_option_var.get() and available_subtitles:
            selected_subtitle = subtitle_lang_var.get()
            if selected_subtitle != "Altyazı Seçiniz" and selected_subtitle in available_subtitles:
                ydl_opts['writesubtitles'] = True
                ydl_opts['subtitleslangs'] = [selected_subtitle]  # Kullanıcının seçtiği dil

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            status_label.config(text="İndiriliyor, lütfen bekleyin...")
            progress_bar['value'] = 0
            ydl.download([url])

            status_label.config(text="İndirme tamamlandı!")
            messagebox.showinfo("Başarılı", f"İndirme tamamlandı: {video_title}\nKaydedilen yer: {default_download_path}")

    except Exception as e:
        status_label.config(text="Hata oluştu!")
        messagebox.showerror("Hata", f"Bir hata oluştu: {str(e)}")

def start_download():
    thread = threading.Thread(target=download_video)
    thread.start()

def on_progress(d):
    if d['status'] == 'downloading':
        total_size = d.get('total_bytes', 0)
        downloaded = d.get('downloaded_bytes', 0)
        percentage = (downloaded / total_size) * 100 if total_size else 0
        progress_bar['value'] = percentage
        root.update_idletasks()

def toggle_subtitle_dropdown():
    """Altyazı indirme seçeneği aktifse, altyazı dillerini kullanıcıya göster."""
    url = url_entry.get()
    if subtitle_option_var.get() and url:
        video_title, available_subtitles = get_video_info(url)
        if available_subtitles:
            subtitle_dropdown['values'] = available_subtitles
            subtitle_dropdown.set(available_subtitles[0])  # İlk seçeneği varsayılan olarak seç
        else:
            subtitle_dropdown['values'] = ["Altyazı yok"]
            subtitle_dropdown.set("Altyazı yok")
    else:
        subtitle_dropdown['values'] = []
        subtitle_dropdown.set("Altyazı Seçiniz")

# GUI oluşturma
root = tk.Tk()
root.title("YouTube İndirici")
root.geometry("500x450")

# Başlık
title_label = tk.Label(root, text="YouTube Video/Ses İndirici", font=("Arial", 16))
title_label.pack(pady=10)

# URL Girişi
url_label = tk.Label(root, text="YouTube URL:")
url_label.pack()
url_entry = tk.Entry(root, width=50)
url_entry.pack(pady=5)

# İndirme Seçenekleri
option_var = tk.StringVar(value="Video (Seçilen Çözünürlük)")
video_option = tk.Radiobutton(root, text="Video (Seçilen Çözünürlük)", variable=option_var, value="Video (Seçilen Çözünürlük)")
audio_option = tk.Radiobutton(root, text="Ses (MP3)", variable=option_var, value="Ses (MP3)")
video_option.pack()
audio_option.pack()

# Çözünürlük Seçimi
resolution_var = tk.StringVar(value="720p")
resolution_label = tk.Label(root, text="Çözünürlük Seç:")
resolution_label.pack()
resolution_dropdown = ttk.Combobox(root, textvariable=resolution_var, values=["1080p", "720p", "480p", "360p", "240p", "144p"])
resolution_dropdown.pack()

# Altyazı Seçimi
subtitle_option_var = tk.BooleanVar(value=False)
subtitle_option = tk.Checkbutton(root, text="Altyazı İndir", variable=subtitle_option_var, command=lambda: toggle_subtitle_dropdown())
subtitle_option.pack()

subtitle_lang_var = tk.StringVar()
subtitle_dropdown = ttk.Combobox(root, textvariable=subtitle_lang_var)
subtitle_dropdown.pack(pady=5)
subtitle_dropdown.set("Altyazı Seçiniz")

# İndirme Klasörü Ayarları
path_button = tk.Button(root, text="İndirme Klasörünü Ayarla", command=set_download_path)
path_button.pack(pady=10)

# İndirme Butonu
download_button = tk.Button(root, text="İndir", command=start_download)
download_button.pack(pady=10)

# Durum Bilgisi
status_label = tk.Label(root, text="", font=("Arial", 12), fg="green")
status_label.pack(pady=10)

# İlerleme Çubuğu
progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(pady=10)

# Varsayılan İndirme Yolunu Göster
default_path_label = tk.Label(root, text=f"Varsayılan İndirme Klasörü: {default_download_path}", font=("Arial", 10), fg="blue")
default_path_label.pack(pady=5)

# Ana döngü
root.mainloop()
