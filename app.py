import streamlit as st
import yt_dlp
import os
import time
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

st.set_page_config(page_title="Klip YouTube", page_icon="✂️")
st.title("✂️ Aplikasi Klip YouTube Otomatis")
st.write("Sistem otomatis memotong 30 detik bagian tengah video.")

url = st.text_input("🔗 Paste Link YouTube di sini:")

if st.button("Buat Klip Sekarang!"):
    if url:
        # 1. Bersihkan link dari spasi kosong (sering terjadi saat copy-paste)
        url = url.strip()
        
        with st.spinner("Sedang mengunduh dan memotong video... Mohon tunggu!"):
            # 2. Gunakan nama file unik agar tidak bentrok jika diproses berulang-ulang
            id_unik = str(int(time.time()))
            file_asli = f"video_asli_{id_unik}.mp4"
            file_hasil = f"hasil_{id_unik}.mp4"
            
            # 3. Format 'best' lebih stabil dan anti-playlist
            ydl_opts = {
                'format': 'best', 
                'outtmpl': file_asli, 
                'quiet': True,
                'noplaylist': True 
            }
            
            try:
                # Proses Download
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    durasi_total = info.get('duration', 0)
                
                # Cek jika video tidak memiliki durasi (misalnya Live Stream)
                if durasi_total == 0:
                    st.error("❌ Gagal membaca durasi. (Pastikan ini bukan video Live Stream).")
                else:
                    # Hitung waktu pemotongan
                    waktu_mulai = max(0, (durasi_total // 2) - 15)
                    waktu_selesai = min(durasi_total, waktu_mulai + 30)
                    
                    # Potong Video
                    ffmpeg_extract_subclip(file_asli, waktu_mulai, waktu_selesai, targetname=file_hasil)
                    
                    st.success("✅ Video berhasil dipotong!")
                    
                    # 4. Baca video ke memori agar file fisiknya bisa aman dihapus
                    with open(file_hasil, "rb") as file:
                        video_bytes = file.read()
                        
                    st.download_button(
                        label="⬇️ Download Video Hasil Klip", 
                        data=video_bytes, 
                        file_name=f"klip_youtube_{id_unik}.mp4", 
                        mime="video/mp4"
                    )
                    
            except Exception as e:
                # 5. Menampilkan error asli agar pengguna tahu penyebab pastinya (misal: video diprivate)
                st.error(f"❌ Gagal memproses: {e}")
                
            finally:
                # 6. Pastikan file sampah SELALU dihapus, baik saat berhasil maupun saat error
                if os.path.exists(file_asli): 
                    os.remove(file_asli)
                if os.path.exists(file_hasil): 
                    os.remove(file_hasil)
    else:
        st.warning("Harap masukkan link terlebih dahulu!")
