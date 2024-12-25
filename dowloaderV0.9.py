import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
import yt_dlp
import threading
import configparser
from PIL import Image, ImageTk

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
    global default_download_path
    config["Settings"]["download_path"] = path
    with open(config_file, "w") as file:
        config.write(file)
    default_download_path = path
    default_path_label.configure(text=f"Varsayılan İndirme Klasörü: {default_download_path}")

def set_download_path():
    """Kullanıcının yeni bir indirme yolu seçmesine izin verir."""
    new_path = filedialog.askdirectory()
    if new_path:
        save_download_path(new_path)
        messagebox.showinfo("Başarılı", f"Yeni indirme klasörü: {new_path}")

def get_video_info(url):
    """Video bilgilerini alır (başlık ve altyazı seçenekleri)."""
    with yt_dlp.YoutubeDL() as ydl:
        result = ydl.extract_info(url, download=False)
        video_title = result.get('title', 'Video Adı Bulunamadı')
        subtitles = result.get('subtitles', {})
        available_subtitles = list(subtitles.keys())

        return video_title, available_subtitles
from PIL import Image, ImageTk
import requests
from io import BytesIO

def show_thumbnail(url):
    try:
        with yt_dlp.YoutubeDL({}) as ydl:
            info = ydl.extract_info(url, download=False)
            thumbnail_url = info.get('thumbnail', None)

            if thumbnail_url:
                # Thumbnail URL'sini indir
                response = requests.get(thumbnail_url)
                response.raise_for_status()  # İstek başarılı mı kontrol et
                img_data = BytesIO(response.content)

                # Görseli Pillow ile aç ve boyutlandır
                img = Image.open(img_data)
                img = img.resize((200, 200))  # Resmi yeniden boyutlandır
                photo = ImageTk.PhotoImage(img)

                # Thumbnail'i label üzerinde göster
                thumbnail_label.configure(image=photo, text="")
                thumbnail_label.image = photo
            else:
                thumbnail_label.configure(text="Önizleme resmi bulunamadı.", image=None)
    except Exception as e:
        thumbnail_label.configure(text=f"Hata: {e}", image=None)

def update_subtitle_dropdown():
    """Altyazı seçeneklerini günceller."""
    url = url_entry.get()
    if url:
        try:
            _, available_subtitles = get_video_info(url)
            if available_subtitles:
                subtitle_dropdown.configure(values=available_subtitles)
                subtitle_dropdown.set(available_subtitles[0])
            else:
                subtitle_dropdown.configure(values=["Altyazı yok"])
                subtitle_dropdown.set("Altyazı yok")
        except Exception as e:
            messagebox.showerror("Hata", f"Altyazılar alınamadı: {str(e)}")

def download_video():
    try:
        url = url_entry.get()
        if not url:
            messagebox.showerror("Hata", "Lütfen bir YouTube URL'si girin!")
            return

        video_title, available_subtitles = get_video_info(url)
        status_label.configure(text=f"Video Başlığı: {video_title}")


        resolution = resolution_var.get()
        ydl_opts = {
            'format': f'bestvideo[height<={resolution}]+bestaudio/best',
            'outtmpl': os.path.join(default_download_path, '%(title)s.%(ext)s'),
            'progress_hooks': [on_progress],
        }
        selected_option = option_var.get()
        if selected_option == "Video (Seçilen Çözünürlük)":
            resolution = resolution_var.get()
            ydl_opts['format'] = f'bestvideo[height<={resolution}]+bestaudio/best'
        elif selected_option == "Ses (MP3)":
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]

        # Altyazı indirme seçeneğini ekle
        if subtitle_option_var.get() and available_subtitles:
            selected_subtitle = subtitle_lang_var.get()
            if selected_subtitle != "Altyazı Seçiniz" and selected_subtitle in available_subtitles:
                ydl_opts['writesubtitles'] = True
                ydl_opts['subtitleslangs'] = [selected_subtitle]

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            status_label.configure(text="İndiriliyor, lütfen bekleyin...")
            progress_bar.set(0)
            ydl.download([url])

            status_label.configure(text="İndirme tamamlandı!")
            messagebox.showinfo("Başarılı", f"İndirme tamamlandı: {video_title}\nKaydedilen yer: {default_download_path}")

    except Exception as e:
        status_label.configure(text="Hata oluştu!")
        messagebox.showerror("Hata", f"Bir hata oluştu: {str(e)}")

def start_download():
    thread = threading.Thread(target=download_video)
    thread.start()

def on_progress(d):
    if d['status'] == 'downloading':
        total_size = d.get('total_bytes', 0)
        downloaded = d.get('downloaded_bytes', 0)
        percentage = (downloaded / total_size) * 100 if total_size else 0
        progress_bar.set(percentage / 100)

def toggle_theme():
    """Karanlık ve aydınlık modlar arasında geçiş yapar."""
    current_mode = ctk.get_appearance_mode()
    new_mode = "Light" if current_mode == "Dark" else "Dark"
    ctk.set_appearance_mode(new_mode)
    theme_button.configure(text="☀" if new_mode == "Light" else "🌙")

def on_url_entry_focus_out(event):
    url = url_entry.get()
    if url.strip():  # URL boş değilse thumbnail yükle
        show_thumbnail(url)


# Uygulama arayüzünü oluşturma
ctk.set_appearance_mode("System")  # Varsayılan olarak sistem temasını kullan
ctk.set_default_color_theme("dark-blue")

root = ctk.CTk()
root.title("YouTube İndirici")
root.geometry("500x550")

thumbnail_label = ctk.CTkLabel(root, text="Thumbnail Yüklenecek", width=200, height=200, anchor="center")
thumbnail_label.pack(pady=20)

# Başlık
title_label = ctk.CTkLabel(root, text="YouTube Video/Ses İndirici", font=ctk.CTkFont(size=20, weight="bold"))
title_label.pack(pady=10)

# URL Girişi
url_label = ctk.CTkLabel(root, text="YouTube URL:")
url_label.pack()
url_entry = ctk.CTkEntry(root, width=400)
url_entry.pack(pady=5)
url_entry.bind("<Return>", on_url_entry_focus_out)  # Odak dışına çıkıldığında çalıştır


# İndirme Seçenekleri
option_var = ctk.StringVar(value="Video (Seçilen Çözünürlük)")
video_option = ctk.CTkRadioButton(root, text="Video (Seçilen Çözünürlük)", variable=option_var, value="Video (Seçilen Çözünürlük)")
audio_option = ctk.CTkRadioButton(root, text="Ses (MP3)", variable=option_var, value="Ses (MP3)")
video_option.pack()
audio_option.pack()

# Çözünürlük Seçimi
resolution_var = ctk.StringVar(value="720")
resolution_label = ctk.CTkLabel(root, text="Çözünürlük Seç:")
resolution_label.pack()
resolution_dropdown = ctk.CTkComboBox(root, variable=resolution_var, values=["1080", "720", "480", "360", "240", "144"])
resolution_dropdown.pack(pady=5)

# Altyazı Seçimi
subtitle_option_var = ctk.BooleanVar(value=False)
subtitle_option = ctk.CTkCheckBox(root, text="Altyazı İndir", variable=subtitle_option_var,command=update_subtitle_dropdown)
subtitle_option.pack()

subtitle_lang_var = ctk.StringVar()
subtitle_dropdown = ctk.CTkComboBox(root, variable=subtitle_lang_var, values=["Altyazı Seçiniz"])
subtitle_dropdown.pack(pady=5)
subtitle_dropdown.set("Altyazı Seçiniz")

# İndirme Klasörü Ayarları
path_button = ctk.CTkButton(root, text="İndirme Klasörünü Ayarla", command=set_download_path)
path_button.pack(pady=10)

# Tema Değiştirme Tuşu
theme_button = ctk.CTkButton(root, text="☀", command=toggle_theme, width=50, height=50, corner_radius=25)
theme_button.pack(pady=10)

# İndirme Butonu
download_button = ctk.CTkButton(root, text="İndir", command=start_download)
download_button.pack(pady=10)

# Durum Bilgisi
status_label = ctk.CTkLabel(root, text="", font=ctk.CTkFont(size=12))
status_label.pack(pady=10)

# İlerleme Çubuğu
progress_bar = ctk.CTkProgressBar(root, orientation="horizontal", width=400)
progress_bar.pack(pady=10)
progress_bar.set(0)

# Varsayılan İndirme Yolunu Göster
default_path_label = ctk.CTkLabel(root, text=f"Varsayılan İndirme Klasörü: {default_download_path}", font=ctk.CTkFont(size=10))
default_path_label.pack(pady=5)

root.mainloop()
