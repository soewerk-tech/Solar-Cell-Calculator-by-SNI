import streamlit as st
import math
import os

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Feasibility Study PLTS",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. JUDUL & LOGO AUTO-HUNTER ---
# Fungsi ini mencari file gambar apa saja yang ada di folder
def get_logo_file():
    files = os.listdir('.')
    # Cari file berakhiran png, jpg, atau jpeg (tidak peduli huruf besar/kecil)
    for f in files:
        if f.lower().endswith(('.png', '.jpg', '.jpeg')):
            return f
    return None

logo_found = get_logo_file()

col_logo, col_title = st.columns([1, 4])

with col_logo:
    if logo_found:
        st.image(logo_found, width=220)
        st.caption(f"Logo terdeteksi: {logo_found}") # Debugging info
    else:
        st.error("❌ Tidak ada file gambar ditemukan.")
        st.code(os.listdir('.')) # Tampilkan isi folder untuk debug

with col_title:
    st.title("☀️ Kalkulator Studi Kelayakan PLTS")
    st.markdown("""
    <div style="color: #555; font-size: 16px;">
        Analisis komprehensif kelayakan finansial proyek Pembangkit Listrik Tenaga Surya (PLTS) 
        mencakup perbandingan skema <b>Capital Expenditure (CAPEX)</b> dan <b>Operational Expenditure (OPEX)</b>.
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- 3. SIDEBAR INPUT ---
with st.sidebar:
    st.header("⚙️ Parameter Proyek")
    
    # --- SLIDER HYBRID (DIPAKSA MULAI DARI 0) ---
    st.markdown("### 🎚️ Target Hybrid")
    st.info("Persentase beban yang dicover sistem Hybrid:")
    
    # PERHATIKAN: angka 0 pertama adalah min_value
    target_eff_hyb = st.slider("Target Efisiensi (%)", 0, 100, 90, 5)
    
    st.markdown("---")

    with st.expander("A. Profil Beban & Lokasi", expanded=True):
        daya_jam = st.number_input("Rata-rata Beban (kW)", value=1.5, step=0.1)
        jam_ops = st.number_input("Jam Operasional/Hari", value=24, step=1)
        tarif_pln = st.number_input("Tarif Listrik (Rp/kWh)", value=1444, step=100)
        psh = st.number_input("Sun Hours (PSH)", value=3.8, step=0.1)

    with st.expander("B. Spesifikasi Komponen"):
        wp_panel = st.number_input("Kapasitas Panel (Wp)", value=550, step=50)
        loss_factor = st.number_input("System Loss (%)", value=20, step=5)
        p_len = st.number_input("Panjang Panel (m)", value=2.3, step=0.1)
        p_wid = st.number_input("Lebar Panel (m)", value=1.1, step=0.1)
        st.markdown("---")
        batt_v = st.number_input("Voltase Baterai (V)", value=48, step=12)
        batt_ah = st.number_input("Ampere Baterai (Ah)", value=100, step=50)

    with st.expander("C. Asumsi Finansial"):
        price_panel = st.number_input("Biaya EPC/kWp (Rp)", value=14000000, step=500000)
        price_batt = st.number_input("Harga Baterai/Unit (Rp)", value=16000000, step=500000)
        price_aftersales = st.number_input("Biaya Pemeliharaan (O&M)/Thn", value=2500000, step=100000)
        opex_discount = st.number_input("Diskon Tarif PPA/Sewa (%)", value=10, step=1)

# --- 4. LOGIKA HITUNGAN ---
def calculate():
    real_loss = loss_factor / 100
    daya_harian = daya_jam * jam_ops
    daya_bulanan = daya_harian * 30
    biaya_pln_bulanan = daya_bulanan * tarif_pln
    biaya_pln_tahunan = biaya_pln_bulanan * 12
    
    target_prod_harian = daya_harian / (1 - real_loss)
    kwp_needed = target_prod_harian / psh
    
    # Fisik
    panel_capacity_kw = wp_panel / 1000
    jumlah_panel = math.ceil(kwp_needed / panel_capacity_kw)
    total_kapasitas_kwp = jumlah_panel * panel_capacity_kw
    total_luas = jumlah_panel * (p_len * p_wid)
    
    batt_kwh = (batt_v * batt_ah) / 1000
    dod = 0.8
    qty_batt_off = math.ceil(daya_harian / (batt_kwh * dod))
    
    # Logic Hybrid Dinamis (0 - 100%)
    if target_eff_hyb > 0:
        kebutuhan_backup_kwh = daya_harian * (target_eff_hyb / 100)
        qty_batt_hyb = math.ceil(kebutuhan_backup_kwh / (batt_kwh * dod))
    else:
        qty_batt_hyb = 0
    
    # CAPEX
    base_capex = kwp_needed * price_panel
    capex_on = base_capex + 10000000
    capex_off = base_capex + (qty_batt_off * price_batt) + 25000000
    capex_hyb = base_capex + (qty_batt_hyb * price_batt) + 30000000
    
    # Unit Cost
    unit_cost_on = capex_on / total_kapasitas_kwp
    unit_cost_off = capex_off / total_kapasitas_kwp
    unit_cost_hyb = capex_hyb / total_kapasitas_kwp

    # Efisiensi & Hemat
    eff_on = 40  
    eff_off = 100 
    eff_hyb = target_eff_hyb 
    
    hemat_gross_on = biaya_pln_tahunan * (eff_on / 100)
    hemat_gross_off = biaya_pln_tahunan * (eff_off / 100)
    hemat_gross_hyb = biaya_pln_tahunan * (eff_hyb / 100)

    # Net Savings
    net_save_on = hemat_gross_on - price_aftersales
    net_save_off = hemat_gross_off - price_aftersales
    net_save_hyb = hemat_gross_hyb - price_aftersales

    # BEP
    bep_on = capex_on / net_save_on if net_save_on > 0 else 0
    bep_off = capex_off / net_save_off if net_save_off > 0 else 0
    bep_hyb = capex_hyb / net_save_hyb if net_save_hyb > 0 else 0
    
    # OPEX
    tarif_sewa = tarif_pln * (1 - (opex_discount/100))
    
    return {
        "pln_bln": biaya_pln_bulanan, "daya_harian": daya_harian,
        "panel_qty": jumlah_panel, "kwp_total": total_kapasitas_kwp, "area": total_luas,
        "batt_off": qty_batt_off, "batt_hyb": qty_batt_hyb,
        "capex_on": capex_on, "capex_off": capex_off, "capex_hyb": capex_hyb,
        "unit_on": unit_cost_on, "unit_off": unit_cost_off, "unit_hyb": unit_cost_hyb,
        "bep_on": bep_on, "bep_off": bep_off, "bep_hyb": bep_hyb,
        "eff_on": eff_on, "eff_off": eff_off, "eff_hyb": eff_hyb, 
        "aftersales": price_aftersales,
        "vendor_on": (daya_bulanan * (eff_on/100)) * tarif_sewa, 
        "sisa_on": (daya_bulanan * (1 - (eff_on/100))) * tarif_pln,
        "vendor_off": daya_bulanan * tarif_sewa,
        "vendor_hyb": (daya_bulanan * (eff_hyb/100)) * tarif_sewa,
        "sisa_hyb": (daya_bulanan * (1 - (eff_hyb/100))) * tarif_pln
    }

res = calculate()

# --- CSS STYLE ---
st.markdown("""
<style>
    .banner-box { background-color: #f1f8e9; border: 2px solid #c5e1a5; border-radius: 12px; padding: 20px; text-align: center; margin-bottom: 30px; color: #33691e; }
    .card { background-color: white; border-radius: 10px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); color: #333; }
    .card-blue { border-top: 8px solid #1976d2; }
    .card-red { border-top: 8px solid #d32f2f; }
    .card-green { border-top: 8px solid #388e3c; }
    .card-title { font-size: 18px; font-weight: 800; text-transform: uppercase; margin-bottom: 5px; display: block; }
    .card-sub { font-size: 12px; color: #555; margin-bottom: 15px; display: block; font-style: italic; }
    .divider { border-bottom: 1px solid #eee; margin: 12px 0; }
    .row-item { display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 13px; align-items: center; }
    .val-bold { font-weight: 700; color: #222; }
    .val-blue { font-weight: 700; color: #1565c0; font-size: 14px; }
    .val-green { font-weight: 700; color: #2e7d32; font-size: 14px; }
    .sec-head { font-size: 11px; font-weight: 700; color: #777; text-transform: uppercase; margin-top: 15px; margin-bottom: 10px; letter-spacing: 0.5px; }
</style>
""", unsafe_allow_html=True)

# BANNER HEADLINE
st.markdown(f"""
<div class="banner-box">
<h4 style="margin:0; opacity:0.8; font-size: 14px; text-transform: uppercase;">Baseline Tagihan Listrik (Eksisting)</h4>
<h1 style="margin:5px 0; font-size: 32px; font-weight: 900;">Rp {res['pln_bln']:,.0f} / Bulan</h1>
<span style="font-weight: bold; background: #dcedc8; padding: 5px 12px; border-radius: 15px; font-size: 13px;">
⚡ Konsumsi Energi: {res['daya_harian']:.1f} kWh / Hari
</span>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

# KOLOM 1: ON GRID
with col1:
    st.markdown(f"""
<div class="card card-blue">
<div style="display:flex; justify-content:space-between; align-items:start;">
<div>
<span class="card-title" style="color: #1976d2;">🏙️ ON-GRID SYSTEM</span>
<span class="card-sub">Grid-Tied (Tanpa Baterai)</span>
</div>
</div>
<div style="background:#e3f2fd; padding:8px; border-radius:6px; font-size:11px; margin-bottom:10px; color:#0d47a1;">
<b>⚠️ Limitasi Regulasi:</b><br>
Mengacu Permen ESDM No. 2/2024 (Ekspor Listrik ditiadakan).
</div>
<div class="sec-head">1. Kebutuhan Perangkat</div>
<div class="row-item"><span>Panel Surya:</span><span class="val-bold">{res['panel_qty']} Unit</span></div>
<div class="row-item"><span>Total Kapasitas:</span><span class="val-bold">{res['kwp_total']:.2f} kWp</span></div>
<div class="row-item"><span>Kebutuhan Area:</span><span class="val-bold">{res['area']:.1f} m²</span></div>
<div class="divider"></div>
<div class="sec-head">2. Analisis Investasi (CAPEX)</div>
<div class="row-item"><span>Total Investasi:</span><span class="val-bold">Rp {res['capex_on']:,.0f}</span></div>
<div class="row-item" title="Biaya Pembangunan per Kapasitas">
<span>Biaya per kWp:</span>
<span class="val-blue">Rp {res['unit_on']/1000000:.1f} Juta /kWp</span>
</div>
<div class="row-item" style="color:#d32f2f;">
<span>Biaya Pemeliharaan (O&M):</span>
<span>Rp {res['aftersales']/1000000:.1f} Juta /Thn</span>
</div>
<div class="row-item"><span>ROI (Balik Modal):</span><span class="val-blue">{res['bep_on']:.1f} Tahun</span></div>
<div class="divider"></div>
<div class="sec-head">3. Analisis Layanan (OPEX)</div>
<div class="row-item"><span>Efisiensi Penghematan:</span><span class="val-bold">{res['eff_on']}%</span></div>
<div class="row-item"><span>Biaya Langganan PLTS:</span><span>Rp {res['vendor_on']:,.0f}</span></div>
<div class="row-item"><span>Sisa Tagihan PLN:</span><span>Rp {res['sisa_on']:,.0f}</span></div>
<div class="row-item" style="margin-top:5px; background:#f5f5f5; padding:5px; border-radius:5px;">
<span>Total Pengeluaran:</span><span class="val-blue">Rp {(res['vendor_on']+res['sisa_on']):,.0f}</span>
</div>
</div>
""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""
<div class="card card-red">
<span class="card-title" style="color: #d32f2f;">🔋 OFF-GRID SYSTEM</span>
<span class="card-sub">Stand-Alone (Mandiri Total)</span>
<div class="sec-head">1. Kebutuhan Perangkat</div>
<div class="row-item"><span>Panel Surya:</span><span class="val-bold">{res['panel_qty']} Unit</span></div>
<div class="row-item"><span>Total Kapasitas:</span><span class="val-bold">{res['kwp_total']:.2f} kWp</span></div>
<div class="row-item"><span>Bank Baterai:</span><span class="val-bold">{res['batt_off']} Unit</span></div>
<div class="divider"></div>
<div class="sec-head">2. Analisis Investasi (CAPEX)</div>
<div class="row-item"><span>Total Investasi:</span><span class="val-bold">Rp {res['capex_off']:,.0f}</span></div>
<div class="row-item" title="Biaya Pembangunan per Kapasitas">
<span>Biaya per kWp:</span>
<span class="val-blue">Rp {res['unit_off']/1000000:.1f} Juta /kWp</span>
</div>
<div class="row-item" style="color:#d32f2f;">
<span>Biaya Pemeliharaan (O&M):</span>
<span>Rp {res['aftersales']/1000000:.1f} Juta /Thn</span>
</div>
<div class="row-item"><span>ROI (Balik Modal):</span><span class="val-blue">{res['bep_off']:.1f} Tahun</span></div>
<div class="divider"></div>
<div class="sec-head">3. Analisis Layanan (OPEX)</div>
<div class="row-item"><span>Efisiensi Penghematan:</span><span class="val-bold">{res['eff_off']}% (Full)</span></div>
<div class="row-item"><span>Biaya Langganan PLTS:</span><span>Rp {res['vendor_off']:,.0f}</span></div>
<div class="row-item"><span>Sisa Tagihan PLN:</span><span>Rp 0</span></div>
<div class="row-item" style="margin-top:5px; background:#f5f5f5; padding:5px; border-radius:5px;">
<span>Total Pengeluaran:</span><span class="val-blue">Rp {res['vendor_off']:,.0f}</span>
</div>
</div>
""", unsafe_allow_html=True)

with col3:
    st.markdown(f"""
<div class="card card-green">
<span class="card-title" style="color: #2e7d32;">⚡ HYBRID SYSTEM</span>
<span class="card-sub">Smart Grid (PLN + Storage)</span>
<div class="sec-head">1. Kebutuhan Perangkat</div>
<div class="row-item"><span>Panel Surya:</span><span class="val-bold">{res['panel_qty']} Unit</span></div>
<div class="row-item"><span>Total Kapasitas:</span><span class="val-bold">{res['kwp_total']:.2f} kWp</span></div>
<div class="row-item"><span>Bank Baterai:</span><span class="val-bold">{res['batt_hyb']} Unit</span></div>
<div class="divider"></div>
<div class="sec-head">2. Analisis Investasi (CAPEX)</div>
<div class="row-item"><span>Total Investasi:</span><span class="val-bold">Rp {res['capex_hyb']:,.0f}</span></div>
<div class="row-item" title="Biaya Pembangunan per Kapasitas">
<span>Biaya per kWp:</span>
<span class="val-blue">Rp {res['unit_hyb']/1000000:.1f} Juta /kWp</span>
</div>
<div class="row-item" style="color:#d32f2f;">
<span>Biaya Pemeliharaan (O&M):</span>
<span>Rp {res['aftersales']/1000000:.1f} Juta /Thn</span>
</div>
<div class="row-item"><span>ROI (Balik Modal):</span><span class="val-blue">{res['bep_hyb']:.1f} Tahun</span></div>
<div class="divider"></div>
<div class="sec-head">3. Analisis Layanan (OPEX)</div>
<div class="row-item"><span>Target Efisiensi:</span><span class="val-bold">{res['eff_hyb']}%</span></div>
<div class="row-item"><span>Biaya Langganan PLTS:</span><span>Rp {res['vendor_hyb']:,.0f}</span></div>
<div class="row-item"><span>Sisa Tagihan PLN:</span><span>Rp {res['sisa_hyb']:,.0f}</span></div>
<div class="row-item" style="margin-top:5px; background:#f5f5f5; padding:5px; border-radius:5px;">
<span>Total Pengeluaran:</span><span class="val-green">Rp {(res['vendor_hyb']+res['sisa_hyb']):,.0f}</span>
</div>
</div>
""", unsafe_allow_html=True)
