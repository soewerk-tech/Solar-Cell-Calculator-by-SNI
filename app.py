import streamlit as st
import math

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Kalkulator Solar Pro",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. JUDUL APLIKASI ---
st.title("☀️ Kalkulator Estimasi Proyek PLTS")
st.markdown("""
<style>
    .big-font { font-size:18px !important; }
</style>
<div class="big-font">
    Simulasi perbandingan biaya investasi (CAPEX), operasional (OPEX), dan titik impas (BEP) 
    untuk berbagai skema panel surya.
</div>
""", unsafe_allow_html=True)

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

# --- 5. TAMPILAN CARD UI (RENDER) ---
res = calculate()

# CSS STYLE (Layout Kartu & Warna)
st.markdown("""
<style>
    .banner-box {
        background-color: #f1f8e9;
        border: 2px solid #c5e1a5;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin-bottom: 30px;
        color: #33691e;
    }
    .card {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        color: #333;
    }
    .card-blue { border-top: 8px solid #1976d2; }
    .card-red { border-top: 8px solid #d32f2f; }
    .card-green { border-top: 8px solid #388e3c; }
    .card-title {
        font-size: 20px;
        font-weight: 900;
        text-transform: uppercase;
        margin-bottom: 5px;
        display: block;
    }
    .card-sub { font-size: 12px; color: #666; margin-bottom: 15px; display: block; }
    .divider { border-bottom: 1px solid #eee; margin: 10px 0; }
    .row-item {
        display: flex;
        justify-content: space-between;
        margin-bottom: 8px;
        font-size: 14px;
    }
    .val-bold { font-weight: 800; color: #000; }
    .val-blue { font-weight: 800; color: #1565c0; font-size: 15px; }
    .val-green { font-weight: 800; color: #2e7d32; font-size: 16px; }
    .sec-head {
        font-size: 11px;
        font-weight: bold;
        color: #888;
        text-transform: uppercase;
        margin-top: 15px;
        margin-bottom: 8px;
        letter-spacing: 1px;
    }
</style>
""", unsafe_allow_html=True)

# BANNER HEADLINE
st.markdown(f"""
<div class="banner-box">
<h4 style="margin:0; opacity:0.8;">Tagihan Listrik Saat Ini (Baseline)</h4>
<h1 style="margin:5px 0; font-size: 36px; font-weight: 900;">Rp {res['pln_bln']:,.0f} / Bulan</h1>
<span style="font-weight: bold; background: #dcedc8; padding: 5px 10px; border-radius: 15px;">
⚡ Beban Energi: {res['daya_harian']:.1f} kWh / Hari
</span>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

# KOLOM 1: ON GRID
with col1:
    st.markdown(f"""
<div class="card card-blue">
<span class="card-title" style="color: #1976d2;">🏙️ ON-GRID</span>
<span class="card-sub">Hemat Siang Saja (Tanpa Baterai)</span>
<div class="sec-head">1. Kebutuhan Fisik</div>
<div class="row-item"><span>Panel Surya:</span><span class="val-bold">{res['panel_qty']} Unit</span></div>
<div class="row-item"><span>Luas Atap:</span><span class="val-bold">{res['area']:.1f} m²</span></div>
<div class="row-item"><span>Baterai:</span><span>-</span></div>
<div class="divider"></div>
<div class="sec-head">2. Beli Sendiri (CAPEX)</div>
<div class="row-item"><span>Modal Awal:</span><span class="val-bold">Rp {res['capex_on']:,.0f}</span></div>
<div class="row-item"><span>Balik Modal:</span><span class="val-blue">{res['bep_on']:.1f} Tahun</span></div>
<div class="divider"></div>
<div class="sec-head">3. Sewa Alat (OPEX)</div>
<div class="row-item"><span>Bayar Langganan PLTS:</span><span>Rp {res['vendor_on']:,.0f}</span></div>
<div class="row-item"><span>Sisa PLN:</span><span>Rp {res['sisa_on']:,.0f}</span></div>
<div class="row-item" style="margin-top:5px; background:#e3f2fd; padding:5px; border-radius:5px;">
<span>Total:</span><span class="val-blue">Rp {(res['vendor_on']+res['sisa_on']):,.0f}</span>
</div>
</div>
""", unsafe_allow_html=True)

# KOLOM 2: OFF GRID
with col2:
    st.markdown(f"""
<div class="card card-red">
<span class="card-title" style="color: #d32f2f;">🔋 OFF-GRID</span>
<span class="card-sub">Mandiri Total (Lepas PLN)</span>
<div class="sec-head">1. Kebutuhan Fisik</div>
<div class="row-item"><span>Panel Surya:</span><span class="val-bold">{res['panel_qty']} Unit</span></div>
<div class="row-item"><span>Luas Atap:</span><span class="val-bold">{res['area']:.1f} m²</span></div>
<div class="row-item"><span>Baterai:</span><span class="val-bold">{res['batt_off']} Unit</span></div>
<div class="divider"></div>
<div class="sec-head">2. Beli Sendiri (CAPEX)</div>
<div class="row-item"><span>Modal Awal:</span><span class="val-bold">Rp {res['capex_off']:,.0f}</span></div>
<div class="row-item"><span>Balik Modal:</span><span class="val-blue">{res['bep_off']:.1f} Tahun</span></div>
<div class="divider"></div>
<div class="sec-head">3. Sewa Alat (OPEX)</div>
<div class="row-item"><span>Bayar Langganan PLTS:</span><span>Rp {res['vendor_off']:,.0f}</span></div>
<div class="row-item"><span>Sisa PLN:</span><span>Rp 0</span></div>
<div class="row-item" style="margin-top:5px; background:#ffebee; padding:5px; border-radius:5px;">
<span>Total:</span><span class="val-blue">Rp {res['vendor_off']:,.0f}</span>
</div>
</div>
""", unsafe_allow_html=True)

# KOLOM 3: HYBRID
with col3:
    st.markdown(f"""
<div class="card card-green">
<span class="card-title" style="color: #2e7d32;">⚡ HYBRID</span>
<span class="card-sub">Stabil & Aman (PLN + Baterai)</span>
<div class="sec-head">1. Kebutuhan Fisik</div>
<div class="row-item"><span>Panel Surya:</span><span class="val-bold">{res['panel_qty']} Unit</span></div>
<div class="row-item"><span>Luas Atap:</span><span class="val-bold">{res['area']:.1f} m²</span></div>
<div class="row-item"><span>Baterai:</span><span class="val-bold">{res['batt_hyb']} Unit</span></div>
<div class="divider"></div>
<div class="sec-head">2. Beli Sendiri (CAPEX)</div>
<div class="row-item"><span>Modal Awal:</span><span class="val-bold">Rp {res['capex_hyb']:,.0f}</span></div>
<div class="row-item"><span>Balik Modal:</span><span class="val-blue">{res['bep_hyb']:.1f} Tahun</span></div>
<div class="divider"></div>
<div class="sec-head">3. Sewa Alat (OPEX)</div>
<div class="row-item"><span>Bayar Langganan PLTS:</span><span>Rp {res['vendor_hyb']:,.0f}</span></div>
<div class="row-item"><span>Sisa PLN:</span><span>Rp {res['sisa_hyb']:,.0f}</span></div>
<div class="row-item" style="margin-top:5px; background:#e8f5e9; padding:5px; border-radius:5px;">
<span>Total:</span><span class="val-green">Rp {(res['vendor_hyb']+res['sisa_hyb']):,.0f}</span>
</div>
</div>
""", unsafe_allow_html=True)
