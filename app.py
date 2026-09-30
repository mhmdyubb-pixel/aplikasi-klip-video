import streamlit as st
import yt_dlp
import os
import time
import glob
import re
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

def clean_youtube_url(url: str) -> str:
    """Membersihkan URL dari spasi, tanda kutip, dan mengambil format standar YouTube."""
    if not url:
        return ""
    # Hapus spasi dan tanda kutip
    cleaned = url.strip().strip("'\"").strip()
    
    # Ekstrak Video ID menggunakan Regex agar kebal dari error link aneh
    youtube_regex = r"(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})"
    match = re.search(youtube_regex, cleaned)
    
    if match:
        video_id = match.group(4)
        return f"https://www.youtube.com/watch?v={video_id}"
    return cleaned

# --- TAMPILAN WEBSITE ---
st.set_page_config(page_title="Klip YouTube", page_icon="✂️")
st.title("✂️ Aplikasi Klip YouTube Otomatis")
st.write("Sistem otomatis memotong 30 detik bagian tengah video.")

url_input = st.text_input("🔗 Paste Link YouTube di sini:")

if st.button("Buat Klip Sekarang!"):
    # 1. Bersihkan URL sebelum diproses
    cleaned_url = clean_youtube_url(url_input)
    
    if not cleaned_url:
        st.warning("Harap masukkan link YouTube yang valid terlebih dahulu!")
    else:
        with st.spinner("Sedang mengunduh dan memotong video... Mohon tunggu!"):
            id_unik = str(int(time.time()))
            file_asli_tanpa_ext = f"video_asli_{id_unik}"
            file_hasil = f"hasil_{id_unik}.mp4"
            
            # Pengaturan yt-dlp
            ydl_opts = {
                'format': 'best',
                'outtmpl': f"{file_asli_tanpa_ext}.%(ext)s", 
                'quiet': True,
                'noplaylist': True,
                'nocheckcertificate': True
            }
            
            try:
                # 2. Proses Download Video
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(cleaned_url, download=True)
                    durasi_total = info.get('duration', 0)
                    ext = info.get('ext', 'mp4')
                
                file_asli = f"{file_asli_tanpa_ext}.{ext}"
                
                # 3. Pengecekan file
                if not os.path.exists(file_asli) or os.path.getsize(file_asli) == 0:
                    st.error("❌ Gagal: File dari YouTube kosong atau diblokir.")
                elif durasi_total == 0:
                    st.error("❌ Gagal membaca durasi. (Pastikan ini bukan video Live Stream).")
                else:
                    # 4. Hitung Waktu dan Potong Video
                    waktu_mulai = max(0, (durasi_total // 2) - 15)
                    waktu_selesai = min(durasi_total, waktu_mulai + 30)
                    
                    ffmpeg_extract_subclip(file_asli, waktu_mulai, waktu_selesai, targetname=file_hasil)
                    
                    st.success("✅ Video berhasil dipotong!")
                    
                    # 5. Tombol Download
                    with open(file_hasil, "rb") as file:
                        st.download_button(
                            label="⬇️ Download Video Hasil Klip", 
                            data=file.read(), 
                            file_name=f"klip_youtube_{id_unik}.mp4", 
                            mime="video/mp4"
                        )
            except Exception as e:
                st.error(f"❌ Gagal memproses: {e}")
            finally:
                # 6. Bersihkan file sampah
                if os.path.exists(file_hasil): 
                    try: os.remove(file_hasil)
                    except: pass
                for f in glob.glob(f"{file_asli_tanpa_ext}.*"):
                    try: os.remove(f)
                    except: pass
