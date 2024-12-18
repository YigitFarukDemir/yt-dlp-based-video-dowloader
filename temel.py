from pytube import YouTube
import os

def download_video(video_url):
    try:
        # Kullanıcı adıyla masaüstü yolu
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        save_path = os.path.join(desktop_path, "My_Videos")  # Masaüstünde "My_Videos" klasörü
        
        # Eğer "My_Videos" klasörü yoksa oluştur
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        
        # YouTube nesnesini oluştur
        yt = YouTube(video_url)

        # En yüksek çözünürlüklü video akışını seç
        video_stream = yt.streams.get_highest_resolution()

        # Videoyu indir
        video_stream.download(output_path=save_path)
        
        print(f"Video başarıyla indirildi: {yt.title}")
    except Exception as e:
        print(f"Hata oluştu: {e}")

# İndirmek istediğiniz YouTube videosunun URL'sini buraya ekleyin
video_url = "https://www.youtube.com/watch?v=4gzLVyNIXCs"

download_video(video_url)
