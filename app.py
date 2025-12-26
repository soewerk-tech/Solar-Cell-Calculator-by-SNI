import streamlit as st
import math

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Kalkulator Solar Cell Pro",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- JUDUL APLIKASI (UMUM) ---
st.title("☀️ Kalkulator Estimasi Proyek PLTS")
st.markdown("Simulasi biaya investasi (CAPEX), operasional (OPEX), dan titik impas (BEP) untuk berbagai skema panel surya.")

# --- SIDEBAR INPUT ---
with st.sidebar:
    st.header("⚙️ Parameter Proyek")
    
    with st.expander("1. Beban & Lokasi", expanded=True):
        daya_jam = st.number_input("Rata-rata Beban (kW)", value=1.5, step=0.1, help="Total daya alat yang menyala dalam satu waktu")
        jam_ops = st.number_input("Jam Operasional/Hari", value=24, step=1)
        tarif_pln = st.number_input("Tarif Listrik (Rp/kWh)", value=1444, step=100)
        psh = st.number_input("Sun Hours (PSH)", value=3.8, step=0.1, help="Rata-rata jam matahari efektif di lokasi")

    with st.expander("2. Spesifikasi Teknis"):
        wp_panel = st.number_input("Kapasitas Panel (Wp)", value=550, step=50)
        loss_factor = st.number_input("Faktor Loss Sistem (%)", value=20, step=5)
        p_len = st.number_input("Panjang Panel (m)", value=2.3, step=0.1)
        p_wid = st.number_input("Lebar Panel (m)", value=1.1, step=0.1)
        st.markdown("---")
        batt_v = st.number_input("Voltase Baterai (V)", value=48, step=12)
        batt_ah = st.number_input("Ampere Baterai (Ah)", value=100, step=50)

    with st.expander("3. Asumsi Harga"):
        price_panel = st.number_input("Biaya Instalasi/kWp (Rp)", value=14000000, step=500000)
        price_batt = st.number_input("Harga Baterai/Unit (Rp)", value=16000000, step=500000)
        opex_discount = st.number_input("Diskon Skema Sewa (%)", value=10, step=1, help="Jika menggunakan skema rental/PPA")

# --- LOGIKA PERHITUNGAN ---
def calculate():
    # 1. Energi
    real_loss = loss_factor / 100
    daya_harian = daya_jam * jam_ops
    daya_bulanan = daya_harian * 30
    biaya_pln_bulanan = daya_bulanan * tarif_pln
    
    target_prod_harian = daya_harian / (1 - real_loss)
    kwp_needed = target_prod_harian / psh
    
    # 2. Fisik
    panel_capacity_kw = wp_panel / 1000
    jumlah_panel = math.ceil(kwp_needed / panel_capacity_kw)
    total_luas = jumlah_panel * (p_len * p_wid)
    
    batt_kwh = (batt_v * batt_ah) / 1000
    dod = 0.8
    qty_batt_off = math.ceil(daya_harian / (batt_kwh * dod))
    qty_batt_hyb = math.ceil((daya_harian * 0.5) / (batt_kwh * dod))
    
    # 3. CAPEX
    base_capex = kwp_needed * price_panel
    capex_on = base_capex + 10000000
    capex_off = base_capex + (qty_batt_off * price_batt) + 25000000
    capex_hyb = base_capex + (qty_batt_hyb * price_batt) + 30000000
    
    # 4. BEP
    # On Grid (Hemat 40%)
    hemat_on_bln = biaya_pln_bulanan * 0.4
    bep_on = capex_on / (hemat_on_bln * 12) if hemat_on_bln > 0 else 0
    
    # Off Grid (Hemat 100%)
    hemat_off_bln = biaya_pln_bulanan
    bep_off = capex_off / (hemat_off_bln * 12) if hemat_off_bln > 0 else 0
    
    # Hybrid (Hemat 90%)
    hemat_hyb_bln = biaya_pln_bulanan * 0.9
    bep_hyb = capex_hyb / (hemat_hyb_bln * 12) if hemat_hyb_bln > 0 else 0
    
    # 5. OPEX
    tarif_sewa = tarif_pln * (1 - (opex_discount/100))
    
    # Opex On Grid
    bayar_vendor_on = (daya_bulanan * 0.4) * tarif_sewa
    sisa_pln_on = (daya_bulanan * 0.6) * tarif_pln
    total_opex_on = bayar_vendor_on + sisa_pln_on
    hemat_opex_on = biaya_pln_bulanan - total_opex_on
    
    # Opex Off Grid
    bayar_vendor_off = daya_bulanan * tarif_sewa
    total_opex_off = bayar_vendor_off
    hemat_opex_off = biaya_pln_bulanan - total_opex_off
    
    # Opex Hybrid
    bayar_vendor_hyb = (daya_bulanan * 0.9) * tarif_sewa
    sisa_pln_hyb = (daya_bulanan * 0.1) * tarif_pln
    total_opex_hyb = bayar_vendor_hyb + sisa_pln_hyb
    hemat_opex_hyb = biaya_pln_bulanan - total_opex_hyb
    
    return {
        "pln_bln": biaya_pln_bulanan,
        "daya_harian": daya_harian,
        "panel_qty": jumlah_panel, "area": total_luas,
        "batt_off": qty_batt_off, "batt_hyb": qty_batt_hyb,
        "capex_on": capex_on, "capex_off": capex_off, "capex_hyb": capex_hyb,
        "bep_on": bep_on, "bep_off": bep_off, "bep_hyb": bep_hyb,
        "vendor_on": bayar_vendor_on, "sisa_on": sisa_pln_on, "tot_on": total_opex_on, "sav_on": hemat_opex_on,
        "vendor_off": bayar_vendor_off, "sisa_off": 0, "tot_off": total_opex_off, "sav_off": hemat_opex_off,
        "vendor_hyb": bayar_vendor_hyb, "sisa_hyb": sisa_pln_hyb, "tot_hyb": total_opex_hyb, "sav_hyb": hemat_opex_hyb
    }

res = calculate()

# --- CSS STYLING (AGAR JELAS DI MODE GELAP) ---
st.markdown(f"""
<style>
    .banner {{
        background-color: #e8f5e9; 
        padding: 20px; 
        border-radius: 10px; 
        border: 1px solid #c8e6c9;
        text-align: center;
        margin-bottom: 25px;
    }}
    .banner h4 {{
        color: #2e7d32 !important; 
        margin-bottom: 5px;
        font-weight: 600;
    }}
    .banner h2 {{
        color: #1b5e20 !important;
        margin: 0;
        font-weight: 800;
        font-size: 2em;
    }}
    .banner p {{
        color: #388e3c !important;
        font-weight: bold;
        margin-top: 5px;
        font-size: 1.1em;
    }}
    
    .highlight {{ font-weight: bold; font-size: 1.1rem; }}
    .green {{ color: #2e7d32; }}
    .blue {{ color: #1565c0; }}
</style>

<div class="banner">
    <h4>Tagihan Listrik Saat Ini (Baseline)</h4>
    <h2>Rp {res['pln_bln']:,.0f} / Bulan</h2>
    <p>⚡ Beban Energi: {res['daya_harian']:.1f} kWh / Hari</p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

# --- KOLOM 1: ON GRID ---
with col1:
    st.markdown("### 🏙️ ON-GRID")
    st.info("Koneksi Jaringan (Tanpa Baterai)")
    
    st.markdown(f"""
    **1. KEBUTUHAN FISIK**
    * Panel: {res['panel_qty']} Unit ({wp_panel}Wp)
    * Luas Atap: {res['area']:.1f} m²
    * Baterai: Tidak Ada
    
    ---
    **2. BELI ALAT (CAPEX)**
    * Investasi: **Rp {res['capex_on']:,.0f}**
    * Balik Modal: <span class='blue highlight'>{res['bep_on']:.1f} Tahun</span>
    
    ---
    **3. SEWA ALAT (OPEX)**
    * Bayar Vendor: Rp {res['vendor_on']:,.0f}
    * Sisa PLN: Rp {res['sisa_on']:,.0f}
    * **Total Keluar: Rp {res['tot_on']:,.0f}**
    * Hemat: <span class='green highlight'>Rp {res['sav_on']:,.0f}</span>
    """, unsafe_allow_html=True)

# --- KOLOM 2: OFF GRID ---
with col2:
    st.markdown("### 🔋 OFF-GRID")
    st.error("Sistem Mandiri (Lepas Jaringan)")
    
    st.markdown(f"""
    **1. KEBUTUHAN FISIK**
    * Panel: {res['panel_qty']} Unit
    * Luas Atap: {res['area']:.1f} m²
    * Baterai: {res['batt_off']} Unit
    
    ---
    **2. BELI ALAT (CAPEX)**
    * Investasi: **Rp {res['capex_off']:,.0f}**
    * Balik Modal: <span class='blue highlight'>{res['bep_off']:.1f} Tahun</span>
    
    ---
    **3. SEWA ALAT (OPEX)**
    * Bayar Vendor: Rp {res['vendor_off']:,.0f}
    * Sisa PLN: Rp 0
    * **Total Keluar: Rp {res['tot_off']:,.0f}**
    * Hemat: <span class='green highlight'>Rp {res['sav_off']:,.0f}</span>
    """, unsafe_allow_html=True)

# --- KOLOM 3: HYBRID ---
with col3:
    st.markdown("### ⚡ HYBRID")
    st.success("Kombinasi (Aman & Stabil)")
    
    st.markdown(f"""
    **1. KEBUTUHAN FISIK**
    * Panel: {res['panel_qty']} Unit
    * Luas Atap: {res['area']:.1f} m²
    * Baterai: {res['batt_hyb']} Unit (Backup)
    
    ---
    **2. BELI ALAT (CAPEX)**
    * Investasi: **Rp {res['capex_hyb']:,.0f}**
    * Balik Modal: <span class='blue highlight'>{res['bep_hyb']:.1f} Tahun</span>
    
    ---
    **3. SEWA ALAT (OPEX)**
    * Bayar Vendor: Rp {res['vendor_hyb']:,.0f}
    * Sisa PLN: Rp {res['sisa_hyb']:,.0f}
    * **Total Keluar: Rp {res['tot_hyb']:,.0f}**
    * Hemat: <span class='green highlight'>Rp {res['sav_hyb']:,.0f}</span>
    """, unsafe_allow_html=True)
