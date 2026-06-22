import streamlit as st
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components

# Set tampilan halaman agar pas di layar HP/Tab/Laptop
st.set_page_config(page_title="Generator Kasir New Era", layout="centered")

# --- 1. MEMBACA DATABASE DARI EXCEL ASLI KAMU (SHEET FORMULA) ---
@st.cache_data
def load_database():
    try:
        nama_file_excel = "GEN RSD8 NEW ERA PRINT GEN ART (1)_065607.xlsx"
        # Membaca sheet 'Formula' karena datanya paling siap pakai
        df = pd.read_excel(nama_file_excel, sheet_name="Formula")
        
        # Sesuai dengan isi Excel asli yang memiliki tepat 7 kolom data utama (+1 kolom kosong jika ada)
        # Kita set kolomnya secara dinamis agar tidak memicu error 'Length mismatch' lagi
        jumlah_kolom = len(df.columns)
        nama_kolom_baru = ['BARCODE', 'FULL_DESC', 'PRICE_1', 'PRICE_2', 'ARTIKEL', 'EMPTY', 'DESC']
        
        # Jika kolom di excel melebihi atau kurang, kita sesuaikan otomatis aman tanpa error
        if jumlah_kolom > len(nama_kolom_baru):
            for i in range(len(nama_kolom_baru), jumlah_kolom):
                nama_kolom_baru.append(f"CADANGAN_{i}")
        elif jumlah_kolom < len(nama_kolom_baru):
            nama_kolom_baru = nama_kolom_baru[:jumlah_kolom]
            
        df.columns = nama_kolom_baru
        
        # Bersihkan barcode agar menjadi teks angka murni
        
