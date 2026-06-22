import streamlit as st
import pandas as pd
from datetime import datetime

# Set tampilan halaman agar pas di layar HP/Tab/Laptop
st.set_page_config(page_title="Generator Kasir New Era", layout="centered")

# --- 1. MEMBACA DATABASE DARI EXCEL ASLI KAMU (SHEET FORMULA) ---
@st.cache_data
def load_database():
    try:
        nama_file_excel = "GEN RSD8 NEW ERA PRINT GEN ART (1)_065607.xlsx"
        # Membaca sheet 'Formula' karena datanya paling siap pakai
        df = pd.read_excel(nama_file_excel, sheet_name="Formula")
        
        # Menamai ulang kolom agar mudah dibaca oleh program
        df.columns = ['BARCODE', 'FULL_DESC', 'PRICE_1', 'PRICE_2', 'ARTIKEL', 'EMPTY', 'DESC']
        
        # Bersihkan barcode agar menjadi teks angka murni
        df['BARCODE'] = df['BARCODE'].astype(str).str.split('.').str[0].str.strip()
        return df
    except Exception as e:
        st.error(f"Gagal membaca file Excel: {e}")
        return pd.DataFrame()

df_master = load_database()

# --- 2. PENYIMPANAN KERANJANG KASIR ---
if "keranjang" not in st.session_state:
    st.session_state.keranjang = []

# --- 3. TAMPILAN WEB UTAMA ---
st.title("🏪 Kasir Generator - New Era")
st.write(f"Tanggal: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.divider()

# INPUT BARCODE (BISA KETIK MANUAL ATAU FOTO KAMERA)
st.subheader("1. Input Barang")

# Tombol pilihan metode input
metode_input = st.radio("Pilih Metode Input Barcode:", ["⌨️ Ketik Manual", "📷 Ambil Foto Barcode"])

barcode_input = ""

if metode_input == "⌨️ Ketik Manual":
    barcode_input = st.text_input("Ketik Manual Barcode / Artikel di sini:", key="barcode_manual").strip()
else:
    # Mengaktifkan kamera bawaan HP / Laptop langsung di web
    foto_barcode = st.camera_input("Arahkan barcode barang tepat ke tengah kamera")
    if foto_barcode:
        st.info("Foto berhasil diambil!")
        # Catatan: Karena pembacaan barcode otomatis lewat gambar di server gratisan membutuhkan library khusus (seperti pyzbar),
        # di versi web ini kamu bisa melihat fotonya terlebih dahulu, lalu sementara ketik angkanya di bawah ini:
        barcode_input = st.text_input("Masukkan angka barcode dari foto di atas:", key="barcode_kamera").strip()

# PENGATURAN PROMO MANUAL
st.subheader("2. Pengaturan Promo Manual")
col1, col2 = st.columns(2)

with col1:
    tipe_promo = st.selectbox("Pilih Jenis Transaksi/Promo:", ["NORMAL", "BOGOF (FREE)", "CASHBACK", "BMSM"])

with col2:
    potongan_manual = 0
    if tipe_promo in ["CASHBACK", "BMSM"]:
        potongan_manual = st.number_input("Nominal Potongan (Rp):", min_value=0, step=1000, value=0)

qty = st.number_input("Jumlah (QTY):", min_value=1, value=1, step=1)

# TOMBOL TAMBAH BARANG KE KERANJANG
if st.button("➕ Tambahkan ke Nota", use_container_width=True):
    if barcode_input and not df_master.empty:
        # Mencari data barang berdasarkan barcode
        hasil_cari = df_master[df_master['BARCODE'] == barcode_input]
        
        if not hasil_cari.empty:
            row = hasil_cari.iloc[0]
            
            artikel = row['ARTIKEL'] if pd.notna(row['ARTIKEL']) else "TIDAK ADA"
            desc = row['DESC'] if pd.notna(row['DESC']) else "TIDAK ADA DESKRIPSI"
            harga_asli = int(row['PRICE_1']) if pd.notna(row['PRICE_1']) else 0
            
            # Hitung harga setelah diskon/promo manual
            if tipe_promo == "BOGOF (FREE)":
                harga_akhir = 0
                keterangan = "FREE (BOGOF)"
            elif tipe_promo in ["CASHBACK", "BMSM"]:
                harga_akhir = max(0, harga_asli - potongan_manual)
                keterangan = f"PROMO {tipe_promo} (-Rp {potongan_manual:,})"
            else:
                harga_akhir = harga_asli
                keterangan = "NORMAL"
                
            # Masukkan ke keranjang
            st.session_state.keranjang.append({
                "QTY": qty,
                "ARTIKEL": artikel,
                "DESCRIPTION": desc,
                "PRICE": harga_asli,
                "PROMO": keterangan,
                "AMOUNT": harga_akhir * qty
            })
            st.success(f"Berhasil menambahkan: {desc}")
        else:
            st.error(f"Barcode '{barcode_input}' tidak ditemukan di database Excel!")
    else:
        st.error("Silakan isi atau masukkan barcode terlebih dahulu!")

st.divider()

# --- 4. TAMPILAN RINGKASAN NOTA KASIR ---
st.subheader("📋 Ringkasan Nota")

if st.session_state.keranjang:
    df_nota = pd.DataFrame(st.session_state.keranjang)
    st.table(df_nota)
    
    total_item = df_nota["QTY"].sum()
    total_bayar = df_nota["AMOUNT"].sum()
    
    st.metric(label="TOTAL ITEMS", value=f"{total_item} Pcs")
    st.metric(label="TOTAL AMOUNT", value=f"Rp {total_bayar:,}")
    
    col_cetak, col_reset = st.columns(2)
    with col_cetak:
        if st.button("🖨️ Cetak Nota", type="primary", use_container_width=True):
            st.balloons()
            st.success("Nota berhasil diproses!")
            
    with col_reset:
        if st.button("🔄 Reset Transaksi Baru", use_container_width=True):
            st.session_state.keranjang = []
            st.rerun()
else:
    st.info("Belum ada barang di dalam nota. Silakan input barcode barang.")
        
