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
        df = pd.read_excel(nama_file_excel, sheet_name="Formula")
        df.columns = ['BARCODE', 'FULL_DESC', 'PRICE_1', 'PRICE_2', 'ARTIKEL', 'EMPTY', 'DESC']
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

st.subheader("1. Input Barang")
metode_input = st.radio("Pilih Metode Input Barcode:", ["⌨️ Ketik Manual", "📷 Scan Pakai Kamera (Otomatis)"])

# Tempat menampung barcode akhir
barcode_final = ""

if metode_input == "⌨️ Ketik Manual":
    barcode_final = st.text_input("Ketik Manual Barcode / Artikel di sini:", key="barcode_manual").strip()
else:
    st.info("Arahkan barcode fisik ke kamera. Sistem akan otomatis membaca angkanya.")
    
    # Komponen Scanner Kamera Otomatis berbasis JavaScript (Html5-Qrcode)
    # Ini akan memicu kamera HP/Laptop mendeteksi barcode secara real-time
    scanner_html = """
    <div id="reader" style="width:100%; max-width:500px; margin:auto; border: 2px dashed #ccc; border-radius: 8px;"></div>
    <script src="https://unpkg.com/html5-qrcode"></script>
    <script>
        function onScanSuccess(decodedText, decodedResult) {
            // Mengirim hasil scan barcode kembali ke Streamlit secara otomatis
            window.parent.postMessage({type: 'streamlit:set_widget_value', key: 'barcode_terdeteksi', value: decodedText}, '*');
            // Stop scanner setelah sukses biar batre awet
            html5QrcodeScanner.clear();
        }
        let html5QrcodeScanner = new Html5QrcodeScanner("reader", { fps: 10, qrbox: {width: 250, height: 150} });
        html5QrcodeScanner.render(onScanSuccess);
    </script>
    """
    # Memasang scanner ke halaman web
    components.html(scanner_html, height=350)
    
    # Menangkap hasil barcode otomatis dari JavaScript di atas
    if 'barcode_terdeteksi' in st.session_state:
        barcode_final = st.session_state['barcode_terdeteksi']
        st.success(f"🎉 Barcode Terdeteksi Otomatis: {barcode_final}")

# --- 4. PENGATURAN PROMO MANUAL ---
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
    if barcode_final and not df_master.empty:
        hasil_cari = df_master[df_master['BARCODE'] == barcode_final]
        
        if not hasil_cari.empty:
            row = hasil_cari.iloc[0]
            artikel = row['ARTIKEL'] if pd.notna(row['ARTIKEL']) else "TIDAK ADA"
            desc = row['DESC'] if pd.notna(row['DESC']) else "TIDAK ADA DESKRIPSI"
            harga_asli = int(row['PRICE_1']) if pd.notna(row['PRICE_1']) else 0
            
            if tipe_promo == "BOGOF (FREE)":
                harga_akhir = 0
                keterangan = "FREE (BOGOF)"
            elif tipe_promo in ["CASHBACK", "BMSM"]:
                harga_akhir = max(0, harga_asli - potongan_manual)
                keterangan = f"PROMO {tipe_promo} (-Rp {potongan_manual:,})"
            else:
                harga_akhir = harga_asli
                keterangan = "NORMAL"
                
            st.session_state.keranjang.append({
                "QTY": qty,
                "ARTIKEL": artikel,
                "DESCRIPTION": desc,
                "PRICE": harga_asli,
                "PROMO": keterangan,
                "AMOUNT": harga_akhir * qty
            })
            st.success(f"Berhasil menambahkan: {desc}")
            # Reset barcode terdeteksi biar bisa scan barang berikutnya
            if 'barcode_terdeteksi' in st.session_state:
                del st.session_state['barcode_terdeteksi']
        else:
            st.error(f"Barcode '{barcode_final}' tidak ditemukan di database Excel!")
    else:
        st.error("Silakan masukkan atau scan barcode barang terlebih dahulu!")

st.divider()

# --- 5. TAMPILAN RINGKASAN NOTA KASIR ---
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
            if 'barcode_terdeteksi' in st.session_state:
                del st.session_state['barcode_terdeteksi']
            st.rerun()
else:
    st.info("Belum ada barang di dalam nota. Silakan input/scan barcode barang.")
    
