import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import yt_dlp
import threading

def download_video():
    try:
        url = url_entry.get()
        if not url:
            messagebox.showerror("Hata", "Lütfen bir YouTube URL'si girin!")
            return

        save_path = filedialog.askdirectory()
        if not save_path:
            messagebox.showerror("Hata", "Lütfen bir indirme klasörü seçin!")
            return

        # İndirme seçeneklerine göre ayarlar
        ydl_opts = {
            'outtmpl': f'{save_path}/%(title)s.%(ext)s',
            'progress_hooks': [on_progress],
            'merge_output_format': 'mp4',  # Videoyu ve sesi birleştirmek için
        }

        selected_option = option_var.get()
        if selected_option == "Video (Seçilen Çözünürlük)":
            resolution = resolution_var.get()
            ydl_opts['format'] = f'bestvideo[height<={resolution}]+bestaudio/best'
        elif selected_option == "Ses (MP3)":
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegAudioConvertor',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        else:
            messagebox.showerror("Hata", "Lütfen geçerli bir indirme seçeneği seçin!")
            return

        # İndirme işlemini başlat
        status_label.config(text="İndiriliyor, lütfen bekleyin...")
        progress_bar['value'] = 0

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        status_label.config(text="İndirme tamamlandı!")
        messagebox.showinfo("Başarılı", "İndirme tamamlandı!")

    except Exception as e:
        status_label.config(text="Hata oluştu!")
        messagebox.showerror("Hata", f"Bir hata oluştu: {str(e)}")

def start_download():
    thread = threading.Thread(target=download_video)
    thread.start()

def on_progress(d):
    if d['status'] == 'downloading':
        percentage = d['downloaded_bytes'] / d['total_bytes'] * 100
        progress_bar['value'] = percentage
        root.update_idletasks()

# GUI oluşturma
root = tk.Tk()
root.title("YouTube İndirici")
root.geometry("500x400")

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
resolution_var = tk.StringVar(value="720")
resolution_label = tk.Label(root, text="Çözünürlük Seç:")
resolution_label.pack()
resolution_dropdown = ttk.Combobox(root, textvariable=resolution_var, values=["1080", "720", "480", "360", "240", "144"])
resolution_dropdown.pack()

# İndirme Butonu
download_button = tk.Button(root, text="İndir", command=start_download)
download_button.pack(pady=10)

# Durum Bilgisi
status_label = tk.Label(root, text="", font=("Arial", 12), fg="green")
status_label.pack(pady=10)

# İlerleme Çubuğu
progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(pady=10)

# Ana döngü
root.mainloop()
