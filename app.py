import streamlit as st
import math
import os

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Feasibility Study PLTS",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. HEADER & LOGO AUTO-DETECT ---
def render_header():
    col_logo, col_text = st.columns([1, 4])
    
    # Logika pencari logo
    logo_file = None
    if os.path.exists("logo.png"): 
        logo_file = "logo.png"
    elif os.path.exists("LOGO HORIZONTAL.png"): 
        logo_file = "LOGO HORIZONTAL.png"
    else:
        # Cari file gambar apapun di folder
        files = [f for f in os.listdir('.') if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if files: logo_file = files[0]
    
    with col_logo:
        if logo_file:
            st.image(logo_file, width=220)
        else:
            st.error("⚠️ Logo tidak ditemukan.")

    with col_text:
        st.title("☀️ Kalkulator Studi Kelayakan PLTS")
        st.markdown("""
        <div style="color: #555; font-size: 16px;">
            Dashboard Analisis Finansial Proyek PLTS (Lifecycle 25 Tahun) & Profitabilitas Bisnis EPC.
        </div>
        """, unsafe_allow_html=True)

render_header()
st.markdown("---")

# --- 3. SIDEBAR INPUT (LENGKAP) ---
with st.sidebar:
    st.header("⚙️ Parameter Proyek")
    
    with st.expander("A. Profil Beban & Lokasi", expanded=True):
        daya_jam = st.number_input("Rata-rata Beban (kW)", value=1.5, step=0.1)
        jam_ops = st.number_input("Jam Operasional/Hari", value=24, step=1)
        tarif_pln = st.number_input("Tarif Listrik (Rp/kWh)", value=1444, step=100)
        # FITUR PSH 5 JAM
        psh = st.number_input("Sun Hours (PSH)", value=5.0, step=0.1)

    with st.expander("B. Spesifikasi Komponen"):
        wp_panel = st.number_input("Kapasitas Panel (Wp)", value=550, step=50)
        loss_factor = st.number_input("System Loss (%)", value=20, step=5)
        p_len = st.number_input("Panjang Panel (m)", value=2.3, step=0.1)
        p_wid = st.number_input("Lebar Panel (m)", value=1.1, step=0.1)
        st.markdown("---")
        st.markdown("### 🔋 Spesifikasi Baterai")
        batt_v = st.number_input("Voltase Baterai (V)", value=48, step=12)
        batt_ah = st.number_input("Ampere Baterai (Ah)", value=100, step=50)
        # FITUR DoD
        batt_dod = st.number_input("Efisiensi Pemakaian (DoD) %", value=80, step=5, help="Lithium saran 80-90%, Aki 50%")

    with st.expander("C. Asumsi Harga Jual (Client)", expanded=True):
        st.caption("Harga Penawaran ke User (Per kWp)")
        price_kwp_on = st.number_input("Harga On-Grid / kWp", value=12000000, step=500000)
        price_kwp_off = st.number_input("Harga Off-Grid / kWp", value=16000000, step=500000)
        price_kwp_hyb = st.number_input("Harga Hybrid / kWp", value=14000000, step=500000)
        st.markdown("---")
        price_batt = st.number_input("Harga Baterai / Unit", value=16000000, step=500000)
        st.markdown("---")
        opex_discount = st.number_input("Diskon Tarif PPA/Sewa (%)", value=10, step=1)

    with st.expander("D. Analisis Profit (Internal)", expanded=True):
        st.warning("⚠️ Area Khusus Penyedia Jasa")
        target_margin = st.slider("Target Profit Margin (%)", 10, 50, 25)
        tax_rate = st.number_input("Pajak Final (PPh) %", value=0.5, step=0.1)

# --- 4. CSS STYLE (Layout Kartu) ---
st.markdown("""
<style>
    .banner-box { background-color: #f1f8e9; border: 2px solid #c5e1a5; border-radius: 12px; padding: 20px; text-align: center; margin-bottom: 30px; color: #33691e; }
    
    .card-top { border-top-left-radius: 10px; border-top-right-radius: 10px; padding: 15px; border: 1px solid #ddd; border-bottom: none; background: white; margin-bottom: 0px; }
    .card-mid { padding: 10px 15px; background: white; border-left: 1px solid #ddd; border-right: 1px solid #ddd; }
    .card-bot { border-bottom-left-radius: 10px; border-bottom-right-radius: 10px; padding: 15px; border: 1px solid #ddd; border-top: none; background: white; margin-top: 0px; margin-bottom: 20px;}
    
    .blue-top { border-top: 5px solid #1976d2; }
    .red-top { border-top: 5px solid #d32f2f; }
    .green-top { border-top: 5px solid #388e3c; }
    .gold-top { border-top: 5px solid #fbc02d; background: #fffde7; }
    
    .card-title { font-size: 18px; font-weight: 800; text-transform: uppercase; display: block; }
    .card-sub { font-size: 12px; color: #555; display: block; font-style: italic; margin-bottom: 10px;}
    
    .divider { border-bottom: 1px solid #eee; margin: 12px 0; }
    .row-item { display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 13px; align-items: center; }
    .val-bold { font-weight: 700; color: #222; }
    .val-blue { font-weight: 700; color: #1565c0; font-size: 14px; }
    .val-green { font-weight: 700; color: #2e7d32; font-size: 14px; }
    .sec-head { font-size: 11px; font-weight: 700; color: #777; text-transform: uppercase; margin-top: 15px; margin-bottom: 10px; letter-spacing: 0.5px; }
</style>
""", unsafe_allow_html=True)

# --- 5. BANNER & SLIDER ---
baseline_energi = daya_jam * jam_ops
baseline_biaya = baseline_energi * 30 * tarif_pln

st.markdown(f"""
<div class="banner-box">
<h4 style="margin:0; opacity:0.8; font-size: 14px; text-transform: uppercase;">Baseline Tagihan Listrik (Eksisting)</h4>
<h1 style="margin:5px 0; font-size: 32px; font-weight: 900;">Rp {baseline_biaya:,.0f} / Bulan</h1>
<span style="font-weight: bold; background: #dcedc8; padding: 5px 12px; border-radius: 15px; font-size: 13px;">
⚡ Konsumsi Energi: {baseline_energi:.1f} kWh / Hari
</span>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

# SLIDER INPUTS
with col1:
    st.markdown("""
    <div class="card-top blue-top">
        <span class="card-title" style="color: #1976d2;">🏙️ ON-GRID SYSTEM</span>
        <span class="card-sub">Grid-Tied (Tanpa Baterai)</span>
    </div>
    <div class="card-mid">
    """, unsafe_allow_html=True)
    target_on = st.slider("Target Penghematan (%)", 0, 40, 40, key="slider_on")
    st.caption("Maksimal 40% (Permen ESDM No. 2/2024)")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="card-top red-top">
        <span class="card-title" style="color: #d32f2f;">🔋 OFF-GRID SYSTEM</span>
        <span class="card-sub">Stand-Alone (Mandiri Total)</span>
    </div>
    <div class="card-mid">
    """, unsafe_allow_html=True)
    st.markdown("**Target Penghematan: 100%**")
    st.progress(100)
    st.caption("Sistem mandiri lepas total dari PLN")
    target_off = 100
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="card-top green-top">
        <span class="card-title" style="color: #2e7d32;">⚡ HYBRID SYSTEM</span>
        <span class="card-sub">Smart Grid (PLN + Storage)</span>
    </div>
    <div class="card-mid">
    """, unsafe_allow_html=True)
    target_hyb = st.slider("Target Penghematan (%)", 0, 100, 90, key="slider_hyb")
    st.caption("Atur proporsi penggunaan PLTS vs PLN")
    st.markdown('</div>', unsafe_allow_html=True)


# --- 6. LOGIKA HITUNGAN UTAMA ---
def calculate_final(eff_on, eff_off, eff_hyb):
    # Basic Params
    real_loss = loss_factor / 100
    daya_harian = daya_jam * jam_ops
    biaya_pln_tahunan = daya_harian * 30 * 12 * tarif_pln
    
    # Hitungan kWp (PSH 5)
    target_prod_harian = daya_harian / (1 - real_loss)
    kwp_needed = target_prod_harian / psh
    
    panel_kw = wp_panel / 1000
    jml_panel = math.ceil(kwp_needed / panel_kw)
    total_kwp = jml_panel * panel_kw
    area = jml_panel * (p_len * p_wid)
    
    # Baterai (Dengan DoD)
    batt_kwh = (batt_v * batt_ah) / 1000
    real_dod = batt_dod / 100
    
    qty_batt_on = 0
    qty_batt_off = math.ceil(daya_harian / (batt_kwh * real_dod))
    qty_batt_hyb = math.ceil((daya_harian * (eff_hyb/100)) / (batt_kwh * real_dod)) if eff_hyb > 0 else 0

    # --- INVESTASI AWAL (INITIAL CAPEX) ---
    base_install_on = (total_kwp * price_kwp_on) + 10000000
    base_install_off = (total_kwp * price_kwp_off) + 25000000
    base_install_hyb = (total_kwp * price_kwp_hyb) + 30000000
    
    init_batt_off = qty_batt_off * price_batt
    init_batt_hyb = qty_batt_hyb * price_batt
    
    total_init_on = base_install_on
    total_init_off = base_install_off + init_batt_off
    total_init_hyb = base_install_hyb + init_batt_hyb

    # --- HARDWARE REPLACEMENT (25 TAHUN) ---
    # On-Grid: Ganti Inverter 1x (Asumsi 15% dari Initial)
    repl_on = total_init_on * 0.15
    
    # Off-Grid & Hybrid: Ganti Baterai 1x (Full Harga Baterai) + Inverter 1x (10% Initial System)
    repl_off = init_batt_off + (base_install_off * 0.10)
    repl_hyb = init_batt_hyb + (base_install_hyb * 0.10)

    # --- TOTAL CAPEX (PROJECT VALUE) ---
    capex_on = total_init_on + repl_on
    capex_off = total_init_off + repl_off
    capex_hyb = total_init_hyb + repl_hyb
    
    # Unit Cost
    unit_on = capex_on / total_kwp
    unit_off = capex_off / total_kwp
    unit_hyb = capex_hyb / total_kwp

    # --- BUSINESS LOGIC (PROFIT) ---
    # Profit dihitung dari Total Project Value
    profit_on = capex_on * (target_margin / 100)
    profit_off = capex_off * (target_margin / 100)
    profit_hyb = capex_hyb * (target_margin / 100)
    
    # Net Profit (Potong Pajak)
    net_on = profit_on - (capex_on * (tax_rate/100))
    net_off = profit_off - (capex_off * (tax_rate/100))
    net_hyb = profit_hyb - (capex_hyb * (tax_rate/100))

    # Penghematan (Yearly)
    hemat_on = biaya_pln_tahunan * (eff_on / 100)
    hemat_off = biaya_pln_tahunan * (eff_off / 100)
    hemat_hyb = biaya_pln_tahunan * (eff_hyb / 100)

    # BEP (Total Capex / Penghematan Tahunan)
    bep_on = capex_on / hemat_on if hemat_on > 0 else 0
    bep_off = capex_off / hemat_off if hemat_off > 0 else 0
    bep_hyb = capex_hyb / hemat_hyb if hemat_hyb > 0 else 0
    
    # OPEX Monthly (User View)
    tarif_sewa = tarif_pln * (1 - (opex_discount/100))
    daya_bln = daya_harian * 30
    
    return {
        "p_qty": jml_panel, "kwp": total_kwp, "area": area,
        "b_off": qty_batt_off, "b_hyb": qty_batt_hyb,
        "init_on": total_init_on, "init_off": total_init_off, "init_hyb": total_init_hyb,
        "repl_on": repl_on, "repl_off": repl_off, "repl_hyb": repl_hyb,
        "capex_on": capex_on, "capex_off": capex_off, "capex_hyb": capex_hyb,
        "unit_on": unit_on, "unit_off": unit_off, "unit_hyb": unit_hyb,
        "bep_on": bep_on, "bep_off": bep_off, "bep_hyb": bep_hyb,
        "prof_on": profit_on, "prof_off": profit_off, "prof_hyb": profit_hyb,
        "net_on": net_on, "net_off": net_off, "net_hyb": net_hyb,
        "v_on": (daya_bln * (eff_on/100)) * tarif_sewa, 
        "s_on": (daya_bln * (1 - (eff_on/100))) * tarif_pln,
        "v_off": daya_bln * tarif_sewa,
        "v_hyb": (daya_bln * (eff_hyb/100)) * tarif_sewa,
        "s_hyb": (daya_bln * (1 - (eff_hyb/100))) * tarif_pln
    }

res = calculate_final(target_on, target_off, target_hyb)

# --- 7. TAMPILAN KARTU (CUSTOMER VIEW) ---

with col1:
    st.markdown(f"""
    <div class="card-bot">
        <div class="sec-head">1. Kebutuhan Perangkat</div>
        <div class="row-item"><span>Panel Surya:</span><span class="val-bold">{res['p_qty']} Unit</span></div>
        <div class="row-item"><span>Total Kapasitas:</span><span class="val-bold">{res['kwp']:.2f} kWp</span></div>
        <div class="row-item"><span>Kebutuhan Area:</span><span class="val-bold">{res['area']:.1f} m²</span></div>
        <div class="divider"></div>
        <div class="sec-head">2. Investasi (25 Tahun)</div>
        <div class="row-item"><span>Investasi Awal:</span><span class="val-bold">Rp {res['init_on']:,.0f}</span></div>
        <div class="row-item" title="Cadangan ganti Inverter"><span>Biaya Replacement:</span><span class="val-bold">Rp {res['repl_on']:,.0f}</span></div>
        <div class="row-item" style="background:#e3f2fd; padding:5px; border-radius:5px;"><span><b>TOTAL CAPEX:</b></span><span class="val-bold">Rp {res['capex_on']:,.0f}</span></div>
        <div class="row-item"><span>ROI (Balik Modal):</span><span class="val-blue">{res['bep_on']:.1f} Tahun</span></div>
        <div class="divider"></div>
        <div class="sec-head">3. Estimasi Tagihan (OPEX)</div>
        <div class="row-item"><span>Bayar Sewa Alat:</span><span>Rp {res['v_on']:,.0f}</span></div>
        <div class="row-item"><span>Sisa Tagihan PLN:</span><span>Rp {res['s_on']:,.0f}</span></div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="card-bot">
        <div class="sec-head">1. Kebutuhan Perangkat</div>
        <div class="row-item"><span>Panel Surya:</span><span class="val-bold">{res['p_qty']} Unit</span></div>
        <div class="row-item"><span>Total Kapasitas:</span><span class="val-bold">{res['kwp']:.2f} kWp</span></div>
        <div class="row-item"><span>Kebutuhan Area:</span><span class="val-bold">{res['area']:.1f} m²</span></div>
        <div class="row-item"><span>Bank Baterai:</span><span class="val-bold">{res['b_off']} Unit</span></div>
        <div class="divider"></div>
        <div class="sec-head">2. Investasi (25 Tahun)</div>
        <div class="row-item"><span>Investasi Awal:</span><span class="val-bold">Rp {res['init_off']:,.0f}</span></div>
        <div class="row-item" title="Cadangan ganti Baterai + Inverter"><span>Biaya Replacement:</span><span class="val-bold">Rp {res['repl_off']:,.0f}</span></div>
        <div class="row-item" style="background:#e3f2fd; padding:5px; border-radius:5px;"><span><b>TOTAL CAPEX:</b></span><span class="val-bold">Rp {res['capex_off']:,.0f}</span></div>
        <div class="row-item"><span>ROI (Balik Modal):</span><span class="val-blue">{res['bep_off']:.1f} Tahun</span></div>
        <div class="divider"></div>
        <div class="sec-head">3. Estimasi Tagihan (OPEX)</div>
        <div class="row-item"><span>Bayar Sewa Alat:</span><span>Rp {res['v_off']:,.0f}</span></div>
        <div class="row-item"><span>Sisa Tagihan PLN:</span><span>Rp 0</span></div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="card-bot">
        <div class="sec-head">1. Kebutuhan Perangkat</div>
        <div class="row-item"><span>Panel Surya:</span><span class="val-bold">{res['p_qty']} Unit</span></div>
        <div class="row-item"><span>Total Kapasitas:</span><span class="val-bold">{res['kwp']:.2f} kWp</span></div>
        <div class="row-item"><span>Kebutuhan Area:</span><span class="val-bold">{res['area']:.1f} m²</span></div>
        <div class="row-item"><span>Bank Baterai:</span><span class="val-bold">{res['b_hyb']} Unit</span></div>
        <div class="divider"></div>
        <div class="sec-head">2. Investasi (25 Tahun)</div>
        <div class="row-item"><span>Investasi Awal:</span><span class="val-bold">Rp {res['init_hyb']:,.0f}</span></div>
        <div class="row-item" title="Cadangan ganti Baterai + Inverter"><span>Biaya Replacement:</span><span class="val-bold">Rp {res['repl_hyb']:,.0f}</span></div>
        <div class="row-item" style="background:#e3f2fd; padding:5px; border-radius:5px;"><span><b>TOTAL CAPEX:</b></span><span class="val-bold">Rp {res['capex_hyb']:,.0f}</span></div>
        <div class="row-item"><span>ROI (Balik Modal):</span><span class="val-blue">{res['bep_hyb']:.1f} Tahun</span></div>
        <div class="divider"></div>
        <div class="sec-head">3. Estimasi Tagihan (OPEX)</div>
        <div class="row-item"><span>Bayar Sewa Alat:</span><span>Rp {res['v_hyb']:,.0f}</span></div>
        <div class="row-item"><span>Sisa Tagihan PLN:</span><span>Rp {res['s_hyb']:,.0f}</span></div>
    </div>
    """, unsafe_allow_html=True)

# --- 8. BUSINESS DASHBOARD (GOLD CARDS) ---
st.markdown("---")
st.markdown("### 💼 Analisis Profitabilitas (Internal EPC)")
st.info(f"Target Margin: **{target_margin}%** | Pajak Final: **{tax_rate}%** | *Margin dihitung dari Total Nilai Proyek (Termasuk Replacement)*")

col_biz1, col_biz2, col_biz3 = st.columns(3)

with col_biz1:
    st.markdown(f"""
    <div class="card-top gold-top"><span class="card-title" style="color: #f57f17;">💰 ON-GRID PROFIT</span></div>
    <div class="card-bot" style="background: #fffde7; border-top:none;">
        <div class="row-item"><span>Total Project Value:</span><span class="val-bold">Rp {res['capex_on']:,.0f}</span></div>
        <div class="row-item"><span>Gross Profit:</span><span class="val-bold" style="color:#2e7d32;">Rp {res['prof_on']:,.0f}</span></div>
        <div class="divider"></div>
        <div class="row-item" style="background: #fbc02d; padding: 5px; border-radius: 5px;">
            <span style="color:white; font-weight:bold;">NET PROFIT:</span>
            <span style="color:white; font-weight:900; float:right;">Rp {res['net_on']:,.0f}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_biz2:
    st.markdown(f"""
    <div class="card-top gold-top"><span class="card-title" style="color: #f57f17;">💰 OFF-GRID PROFIT</span></div>
    <div class="card-bot" style="background: #fffde7; border-top:none;">
        <div class="row-item"><span>Total Project Value:</span><span class="val-bold">Rp {res['capex_off']:,.0f}</span></div>
        <div class="row-item"><span>Gross Profit:</span><span class="val-bold" style="color:#2e7d32;">Rp {res['prof_off']:,.0f}</span></div>
        <div class="divider"></div>
        <div class="row-item" style="background: #fbc02d; padding: 5px; border-radius: 5px;">
            <span style="color:white; font-weight:bold;">NET PROFIT:</span>
            <span style="color:white; font-weight:900; float:right;">Rp {res['net_off']:,.0f}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_biz3:
    st.markdown(f"""
    <div class="card-top gold-top"><span class="card-title" style="color: #f57f17;">💰 HYBRID PROFIT</span></div>
    <div class="card-bot" style="background: #fffde7; border-top:none;">
        <div class="row-item"><span>Total Project Value:</span><span class="val-bold">Rp {res['capex_hyb']:,.0f}</span></div>
        <div class="row-item"><span>Gross Profit:</span><span class="val-bold" style="color:#2e7d32;">Rp {res['prof_hyb']:,.0f}</span></div>
        <div class="divider"></div>
        <div class="row-item" style="background: #fbc02d; padding: 5px; border-radius: 5px;">
            <span style="color:white; font-weight:bold;">NET PROFIT:</span>
            <span style="color:white; font-weight:900; float:right;">Rp {res['net_hyb']:,.0f}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
