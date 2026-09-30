import re
import streamlit as st
import yt_dlp


def clean_youtube_url(url: str) -> str:
    """Membersihkan URL dari spasi, tanda kutip, dan mengambil format standar YouTube."""
    if not url:
        return ""

    # 1. Hapus spasi dan tanda kutip pembungkus
    cleaned = url.strip().strip("'\"").strip()

    # 2. Ekstrak Video ID 11 karakter menggunakan Regex
    youtube_regex = (
        r"(https?://)?(www\.)?"
        r"(youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)"
        r"([a-zA-Z0-9_-]{11})"
    )

    match = re.search(youtube_regex, cleaned)
    if match:
        video_id = match.group(4)
        return f"https://www.youtube.com/watch?v={video_id}"

    return cleaned


# --- UI Streamlit ---
url_input = st.text_input("Masukkan Link YouTube:")

if st.button("Proses Video"):
    # Pakai fungsi pembersih sebelum diproses yt-dlp
    cleaned_url = clean_youtube_url(url_input)

    if not cleaned_url:
        st.error("Silakan masukkan URL YouTube yang valid.")
    else:
        ydl_opts = {
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "quiet": True,
            "no_warnings": True,
        }

        try:
            with st.spinner("Memproses info video..."):
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(cleaned_url, download=False)
                    st.success(f"Berhasil memuat: **{info.get('title')}**")

        except Exception as e:
            st.error(f"Gagal memproses: {e}")import re
import streamlit as st
import yt_dlp


def clean_youtube_url(url: str) -> str:
    """Membersihkan URL dari spasi, tanda kutip, dan mengambil format standar YouTube."""
    if not url:
        return ""

    # 1. Hapus spasi dan tanda kutip pembungkus
    cleaned = url.strip().strip("'\"").strip()

    # 2. Ekstrak Video ID 11 karakter menggunakan Regex
    youtube_regex = (
        r"(https?://)?(www\.)?"
        r"(youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)"
        r"([a-zA-Z0-9_-]{11})"
    )

    match = re.search(youtube_regex, cleaned)
    if match:
        video_id = match.group(4)
        return f"https://www.youtube.com/watch?v={video_id}"

    return cleaned


# --- UI Streamlit ---
url_input = st.text_input("Masukkan Link YouTube:")

if st.button("Proses Video"):
    # Pakai fungsi pembersih sebelum diproses yt-dlp
    cleaned_url = clean_youtube_url(url_input)

    if not cleaned_url:
        st.error("Silakan masukkan URL YouTube yang valid.")
    else:
        ydl_opts = {
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "quiet": True,
            "no_warnings": True,
        }

        try:
            with st.spinner("Memproses info video..."):
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(cleaned_url, download=False)
                    st.success(f"Berhasil memuat: **{info.get('title')}**")

        except Exception as e:
            st.error(f"Gagal memproses: {e}")import streamlit as st
import yt_dlp
import os
import time
import glob
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

st.set_page_config(page_title="Klip YouTube", page_icon="✂️")
st.title("✂️ Aplikasi Klip YouTube Otomatis")
st.write("Sistem otomatis memotong 30 detik bagian tengah video.")

url = st.text_input("🔗 Paste Link YouTube di sini:")

if st.button("Buat Klip Sekarang!"):
    if url:
        url = url.strip()
        with st.spinner("Sedang mengunduh dan memotong video... Mohon tunggu!"):
            id_unik = str(int(time.time()))
            file_asli_tanpa_ext = f"video_asli_{id_unik}"
            file_hasil = f"hasil_{id_unik}.mp4"
            
            # Taktik baru: Ambil format yang sudah utuh dari YouTube, jangan digabung manual
            ydl_opts = {
                'format': 'best',
                'outtmpl': f"{file_asli_tanpa_ext}.%(ext)s", 
                'quiet': True,
                'noplaylist': True,
                'nocheckcertificate': True
            }
            
            try:
                # 1. Proses Download
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    durasi_total = info.get('duration', 0)
                    ext = info.get('ext', 'mp4') # Deteksi format asli (mp4/webm)
                
                file_asli = f"{file_asli_tanpa_ext}.{ext}"
                
                # 2. Cek apakah file berhasil diunduh dan tidak kosong
                if not os.path.exists(file_asli) or os.path.getsize(file_asli) == 0:
                    st.error("❌ Gagal: File dari YouTube kosong atau diblokir.")
                elif durasi_total == 0:
                    st.error("❌ Gagal membaca durasi. (Pastikan ini bukan video Live Stream).")
                else:
                    # 3. Hitung Waktu dan Potong
                    waktu_mulai = max(0, (durasi_total // 2) - 15)
                    waktu_selesai = min(durasi_total, waktu_mulai + 30)
                    
                    ffmpeg_extract_subclip(file_asli, waktu_mulai, waktu_selesai, targetname=file_hasil)
                    
                    st.success("✅ Video berhasil dipotong!")
                    
                    # 4. Tombol Download
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
                # 5. Bersihkan semua file sampah agar server tidak penuh
                if os.path.exists(file_hasil): 
                    os.remove(file_hasil)
                for f in glob.glob(f"{file_asli_tanpa_ext}.*"):
                    os.remove(f)
    else:
        st.warning("Harap masukkan link terlebih dahulu!")
