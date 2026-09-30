import streamlit as st
import os
import time
import subprocess

st.set_page_config(page_title="Potong Video", page_icon="🎬")
st.title("🎬 Aplikasi Potong Video Mandiri")
st.write("Upload video Anda, tentukan detik pemotongan, dan download hasilnya.")

# 1. Fitur Upload Video
uploaded_file = st.file_uploader("📂 Pilih file video (MP4, MOV):", type=['mp4', 'mov'])

if uploaded_file is not None:
    st.success("✅ Video berhasil dimuat!")
    
    st.write("📺 **Tinjau Video Anda:**")
    st.video(uploaded_file)
    
    st.divider()
    
    st.write("### ⏱️ Tentukan Waktu Potong")
    col1, col2 = st.columns(2)
    with col1:
        waktu_mulai = st.number_input("Mulai di detik ke:", min_value=0, value=0)
    with col2:
        waktu_selesai = st.number_input("Selesai di detik ke:", min_value=1, value=10)
        
    if st.button("✂️ Potong Video Sekarang!"):
        if waktu_mulai >= waktu_selesai:
            st.error("❌ Waktu 'Selesai' harus lebih besar dari waktu 'Mulai'!")
        else:
            with st.spinner("Sedang memotong video dengan kecepatan tinggi..."):
                id_unik = str(int(time.time()))
                file_input = f"input_{id_unik}.mp4"
                file_output = f"output_{id_unik}.mp4"
                
                try:
                    # Simpan file upload ke server
                    with open(file_input, "wb") as f:
                        f.write(uploaded_file.read())
                        
                    # Perintah langsung ke mesin FFmpeg
                    cmd = [
                        "ffmpeg", "-y", 
                        "-i", file_input, 
                        "-ss", str(waktu_mulai), 
                        "-to", str(waktu_selesai), 
                        "-c:v", "copy", 
                        "-c:a", "copy", 
                        file_output
                    ]
                    
                    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    
                    st.success(f"🎉 Berhasil! Video dipotong dari detik {waktu_mulai} ke {waktu_selesai}.")
                    
                    st.write("📺 **Hasil Potongan:**")
                    st.video(file_output)
                    
                    # Tombol Download
                    with open(file_output, "rb") as f:
                        st.download_button(
                            label="⬇️ Download Hasil Klip",
                            data=f.read(),
                            file_name=f"klip_saya_{id_unik}.mp4",
                            mime="video/mp4"
                        )
                        
                except subprocess.CalledProcessError as e:
                    st.error(f"❌ Terjadi kesalahan mesin: {e.stderr.decode()}")
                except Exception as e:
                    st.error(f"❌ Terjadi kesalahan: {e}")
                finally:
                    # Bersihkan file sampah
                    if os.path.exists(file_input): 
                        try: 
                            os.remove(file_input) 
                        except: 
                            pass
                    if os.path.exists(file_output): 
                        try: 
                            os.remove(file_output) 
                        except: 
                            pass
