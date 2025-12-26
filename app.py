import streamlit as st
import math

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Kalkulator Solar Cell Pro",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. JUDUL APLIKASI ---
st.title("☀️ Kalkulator Estimasi Proyek PLTS")
st.markdown("Simulasi biaya investasi (CAPEX), operasional (OPEX), dan titik impas (BEP).")

# --- 3. SIDEBAR INPUT (Parameter) ---
with st.sidebar:
    st.header("⚙️ Parameter Proyek")
    
    with st.expander("A. Beban & Lokasi", expanded=True):
        daya_jam = st.number_input("Rata-rata Beban (kW)", value=1.5, step=0.1)
        jam_ops = st.number_input("Jam Operasional/Hari", value=24, step=1)
        tarif_pln = st.number_input("Tarif Listrik (Rp/kWh)", value=1444, step=100)
        psh = st.number_input("Sun Hours (PSH)", value=3.8, step=0.1)

    with st.expander("B. Spesifikasi Teknis"):
        wp_panel = st.number_input("Kapasitas Panel (Wp)", value=550, step=50)
        loss_factor = st.number_input("Loss Sistem (%)", value=20, step=5)
        p_len = st.number_input("Panjang Panel (m)", value=2.3, step=0.1)
        p_wid = st.number_input("Lebar Panel (m)", value=1.1, step=0.1)
        st.markdown("---")
        batt_v = st.number_input("Voltase Baterai (V)", value=48, step=12)
        batt_ah = st.number_input("Ampere Baterai (Ah)", value=100, step=50)

    with st.expander("C. Asumsi Harga"):
        price_panel = st.number_input("Biaya Instalasi/kWp (Rp)", value=14000000, step=500000)
        price_batt = st.number_input("Harga Baterai/Unit (Rp)", value=16000000, step=500000)
        opex_discount = st.number_input("Diskon Sewa (%)", value=10, step=1)

# --- 4. LOGIKA HITUNGAN (FUNGSI) ---
def calculate():
    # Energi
    real_loss = loss_factor / 100
    daya_harian = daya_jam * jam_ops
    daya_bulanan = daya_harian * 30
    biaya_pln_bulanan = daya_bulanan * tarif_pln
    
    target_prod_harian = daya_harian / (1 - real_loss)
    kwp_needed = target_prod_harian / psh
    
    # Fisik
    panel_capacity_kw = wp_panel / 1000
    jumlah_panel = math.ceil(kwp_needed / panel_capacity_kw)
    total_luas = jumlah_panel * (p_len * p_wid)
    
    batt_kwh = (batt_v * batt_ah) / 1000
    dod = 0.8
    qty_batt_off = math.ceil(daya_harian / (batt_kwh * dod))
    qty_batt_hyb = math.ceil((daya_harian * 0.5) / (batt_kwh * dod))
    
    # CAPEX
    base_capex = kwp_needed * price_panel
    capex_on = base_capex + 10000000
    capex_off = base_capex + (qty_batt_off * price_batt) + 25000000
    capex_hyb = base_capex + (qty_batt_hyb * price_batt) + 30000000
    
    # BEP & OPEX
    hemat_on_bln = biaya_pln_bulanan * 0.4
    bep_on = capex_on / (hemat_on_bln * 12) if hemat_on_bln > 0 else 0
    
    hemat_off_bln = biaya_pln_bulanan
    bep_off = capex_off / (hemat_off_bln * 12) if hemat_off_bln > 0 else 0
    
    hemat_hyb_bln = biaya_pln_bulanan * 0.9
    bep_hyb = capex_hyb / (hemat_hyb_bln * 12) if hemat_hyb_bln > 0 else 0
    
    tarif_sewa = tarif_pln * (1 - (opex_discount/100))
    
    # Return Data
    return {
        "pln_bln": biaya_pln_bulanan, "daya_harian": daya_harian,
        "panel_qty": jumlah_panel, "area": total_luas,
        "batt_off": qty_batt_off, "batt_hyb": qty_batt_hyb,
        "capex_on": capex_on, "capex_off": capex_off, "capex_hyb": capex_hyb,
        "bep_on": bep_on, "bep_off": bep_off, "bep_hyb": bep_hyb,
        "vendor_on": (daya_bulanan * 0.4) * tarif_sewa, 
        "sisa_on": (daya_bulanan * 0.6) * tarif_pln,
        "vendor_off": daya_bulanan * tarif_sewa,
        "vendor_hyb": (daya_bulanan * 0.9) * tarif_sewa,
        "sisa_hyb": (daya_bulanan * 0.1) * tarif_pln
    }

# --- 5. EKSEKUSI DAN TAMPILAN (RENDER) ---
# Bagian ini yang sebelumnya mungkin tidak tercopy
res = calculate()

# CSS untuk Mode Gelap
st.markdown(f"""
<style>
    .banner {{
        background-color: #2e7d32; 
        color: white;
        padding: 20px; 
        border-radius: 10px; 
        text-align: center;
        margin-bottom: 25px;
    }}
    .highlight {{ font-weight: bold; font-size: 1.1rem; }}
    .blue {{ color: #42a5f5; }}
    .green {{ color: #66bb6a; }}
</style>

<div class="banner">
    <h4 style="margin:0;">Tagihan Listrik Baseline</h4>
    <h2 style="margin:0;">Rp {res['pln_bln']:,.0f} / Bulan</h2>
    <p style="margin:5px 0;">⚡ Beban: {res['daya_harian']:.1f} kWh / Hari</p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🏙️ ON-GRID")
    st.info("Koneksi Jaringan (Tanpa Baterai)")
    st.markdown(f"""
    **FISIK:** {res['panel_qty']} Panel | Area {res['area']:.1f} m²
    
    **1. BELI SENDIRI (CAPEX)**
    * Modal: **Rp {res['capex_on']:,.0f}**
    * BEP: <span class='blue highlight'>{res['bep_on']:.1f} Tahun</span>
    
    **2. SEWA (OPEX)**
    * Bayar Vendor: Rp {res['vendor_on']:,.0f}
    * Sisa PLN: Rp {res['sisa_on']:,.0f}
    * **Total: Rp {(res['vendor_on']+res['sisa_on']):,.0f}**
    """, unsafe_allow_html=True)

with col2:
    st.markdown("### 🔋 OFF-GRID")
    st.error("Mandiri (Lepas Jaringan)")
    st.markdown(f"""
    **FISIK:** {res['panel_qty']} Panel | {res['batt_off']} Baterai
    
    **1. BELI SENDIRI (CAPEX)**
    * Modal: **Rp {res['capex_off']:,.0f}**
    * BEP: <span class='blue highlight'>{res['bep_off']:.1f} Tahun</span>
    
    **2. SEWA (OPEX)**
    * Bayar Vendor: Rp {res['vendor_off']:,.0f}
    * Sisa PLN: Rp 0
    * **Total: Rp {res['vendor_off']:,.0f}**
    """, unsafe_allow_html=True)

with col3:
    st.markdown("### ⚡ HYBRID")
    st.success("Kombinasi (Aman & Stabil)")
    st.markdown(f"""
    **FISIK:** {res['panel_qty']} Panel | {res['batt_hyb']} Baterai
    
    **1. BELI SENDIRI (CAPEX)**
    * Modal: **Rp {res['capex_hyb']:,.0f}**
    * BEP: <span class='blue highlight'>{res['bep_hyb']:.1f} Tahun</span>
    
    **2. SEWA (OPEX)**
    * Bayar Vendor: Rp {res['vendor_hyb']:,.0f}
    * Sisa PLN: Rp {res['sisa_hyb']:,.0f}
    * **Total: Rp {(res['vendor_hyb']+res['sisa_hyb']):,.0f}**
    """, unsafe_allow_html=True)
