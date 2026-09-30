import streamlit as st
import os
import time
import subprocess

st.set_page_config(page_title="Video Trimmer Manual", page_icon="✂️")
st.title("✂️ Aplikasi Potong Video Manual")
st.write("Upload video Anda, tentukan durasi potong, dan download hasilnya dengan cepat tanpa perlu API Key.")

# 1. Fitur Upload Video
uploaded_file = st.file_uploader("📂 Pilih file video (MP4, MOV):", type=['mp4', 'mov'])

if uploaded_file is not None:
    st.success("✅ Video berhasil dimuat!")
    st.video(uploaded_file)
    
    st.divider()
    st.subheader("⚙️ Pengaturan Potong Video")
    
    # Pengaturan durasi potong manual
    col1, col2 = st.columns(2)
    with col1:
        start_time = st.number_input("Mulai dari detik ke-:", min_value=0, value=0, step=1)
    with col2:
        duration = st.number_input("Durasi video hasil potongan (detik):", min_value=1, value=30, step=1)
        
    if st.button("🚀 Potong Video Sekarang!"):
        with st.spinner("Sedang memotong video... Mohon tunggu sebentar!"):
            id_unik = str(int(time.time()))
            file_input = f"input_{id_unik}.mp4"
            file_output = f"output_{id_unik}.mp4"
            
            try:
                # Simpan file upload ke server sementara
                with open(file_input, "wb") as f:
                    f.write(uploaded_file.read())
                    
                # Jalankan perintah FFmpeg untuk memotong video tanpa re-encode (super cepat)
                cmd = [
                    "ffmpeg", "-y", 
                    "-ss", str(start_time),
                    "-i", file_input, 
                    "-t", str(duration), 
                    "-c:v", "copy", "-c:a", "copy", 
                    file_output
                ]
                
                subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                st.success("🎉 Berhasil! Video Anda sudah dipotong.")
                st.video(file_output)
                
                # Tombol Download
                with open(file_output, "rb") as f:
                    st.download_button(
                        label="⬇️ Download Video Hasil Potongan",
                        data=f.read(),
                        file_name=f"potongan_{id_unik}.mp4",
                        mime="video/mp4"
                    )
                    
            except Exception as e:
                st.error(f"❌ Terjadi kesalahan saat memproses video: {e}")
                
            finally:
                # Bersihkan file sampah di server
                if os.path.exists(file_input): 
                    try: os.remove(file_input) 
                    except: pass
                if os.path.exists(file_output): 
                    try: os.remove(file_output) 
                    except: pass
