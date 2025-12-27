import streamlit as st
import math
import os

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Feasibility Study PLTS",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. HEADER & LOGO ---
def render_header():
    col_logo, col_text = st.columns([1, 4])
    
    # Auto-Detect Logo
    logo_file = None
    if os.path.exists("logo.png"): logo_file = "logo.png"
    elif os.path.exists("LOGO HORIZONTAL.png"): logo_file = "LOGO HORIZONTAL.png"
    
    with col_logo:
        if logo_file:
            st.image(logo_file, width=220)
        else:
            files = [f for f in os.listdir('.') if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            if files:
                st.image(files[0], width=220)
            else:
                st.error("Logo tidak ditemukan.")

    with col_text:
        st.title("☀️ Kalkulator Studi Kelayakan PLTS")
        st.markdown("""
        <div style="color: #555; font-size: 16px;">
            Dashboard analisis finansial proyek PLTS (Customer View) & Analisis Profitabilitas (Business View).
        </div>
        """, unsafe_allow_html=True)

render_header()
st.markdown("---")

# --- 3. SIDEBAR INPUT ---
with st.sidebar:
    st.header("⚙️ Parameter Proyek")
    
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
        st.markdown("### 🔋 Spesifikasi Baterai")
        batt_v = st.number_input("Voltase Baterai (V)", value=48, step=12)
        batt_ah = st.number_input("Ampere Baterai (Ah)", value=100, step=50)
        batt_dod = st.number_input("Efisiensi Pemakaian (DoD) %", value=80, step=5, help="Lead Acid ~50%, Lithium ~80-90%")

    with st.expander("C. Asumsi Harga Jual (CAPEX Client)", expanded=True):
        st.info("Harga ini adalah harga penawaran ke Klien.")
        st.markdown("### 💰 Instalasi per kWp")
        price_kwp_on = st.number_input("Harga Jual On-Grid / kWp", value=12000000, step=500000)
        price_kwp_off = st.number_input("Harga Jual Off-Grid / kWp", value=16000000, step=500000)
        price_kwp_hyb = st.number_input("Harga Jual Hybrid / kWp", value=14000000, step=500000)
        
        st.markdown("---")
        st.markdown("### 🔋 Harga Jual Baterai")
        price_batt = st.number_input("Harga Baterai / Unit", value=16000000, step=500000)
        
        st.markdown("---")
        opex_discount = st.number_input("Diskon Tarif PPA (%)", value=10, step=1)

    # --- BARU: SECTION BISNIS ---
    with st.expander("D. Analisis Profit (Internal)", expanded=True):
        st.warning("⚠️ Area Khusus Penyedia Jasa")
        target_margin = st.slider("Target Profit Margin (%)", 10, 50, 25, help="Berapa % keuntungan kotor yang diinginkan dari Total Proyek")
        tax_rate = st.number_input("Pajak Final (PPh) %", value=0.5, step=0.1, help="PPh Final UMKM (0.5%) atau Jasa Konstruksi")

# --- 4. STYLE & BANNER ---
st.markdown("""
<style>
    .banner-box { background-color: #f1f8e9; border: 2px solid #c5e1a5; border-radius: 12px; padding: 20px; text-align: center; margin-bottom: 30px; color: #33691e; }
    
    /* Card Styles */
    .card-top { border-top-left-radius: 10px; border-top-right-radius: 10px; padding: 15px; margin-bottom: 0px; color: #333; border: 1px solid #ddd; border-bottom: none; background: white; }
    .card-mid { padding: 10px 15px; background: white; border-left: 1px solid #ddd; border-right: 1px solid #ddd; }
    .card-bot { border-bottom-left-radius: 10px; border-bottom-right-radius: 10px; padding: 15px; margin-top: 0px; color: #333; border: 1px solid #ddd; border-top: none; background: white; }
    
    .blue-top { border-top: 5px solid #1976d2; }
    .red-top { border-top: 5px solid #d32f2f; }
    .green-top { border-top: 5px solid #388e3c; }
    .gold-top { border-top: 5px solid #fbc02d; background: #fffde7; } /* Style Baru untuk Business Card */

    .card-title { font-size: 18px; font-weight: 800; text-transform: uppercase; display: block; }
    .card-sub { font-size: 12px; color: #555; display: block; font-style: italic; margin-bottom: 10px;}
    
    .divider { border-bottom: 1px solid #eee; margin: 12px 0; }
    .row-item { display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 13px; align-items: center; }
    .val-bold { font-weight: 700; color: #222; }
    .val-blue { font-weight: 700; color: #1565c0; font-size: 14px; }
    .val-green { font-weight: 700; color: #2e7d32; font-size: 14px; }
    .val-gold { font-weight: 800; color: #f57f17; font-size: 15px; } /* Warna Angka Profit */
    
    .sec-head { font-size: 11px; font-weight: 700; color: #777; text-transform: uppercase; margin-top: 15px; margin-bottom: 10px; letter-spacing: 0.5px; }
</style>
""", unsafe_allow_html=True)

# Hitung Baseline
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

# --- 5. INTERFACE INPUT (SLIDER) ---
col1, col2, col3 = st.columns(3)

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


# --- 6. LOGIKA HITUNGAN (CLIENT + BUSINESS) ---
def calculate_final(eff_on, eff_off, eff_hyb):
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
    real_dod = batt_dod / 100 
    
    # Baterai
    qty_batt_on = 0
    qty_batt_off = math.ceil(daya_harian / (batt_kwh * real_dod))
    
    if eff_hyb > 0:
        kebutuhan_backup = daya_harian * (eff_hyb / 100)
        qty_batt_hyb = math.ceil(kebutuhan_backup / (batt_kwh * real_dod))
    else:
        qty_batt_hyb = 0

    # === CAPEX CALCULATION (HARGA JUAL KE CLIENT) ===
    
    # 1. Total Harga Jual
    capex_on = (kwp_needed * price_kwp_on) + 10000000 
    capex_off = (kwp_needed * price_kwp_off) + (qty_batt_off * price_batt) + 25000000
    capex_hyb = (kwp_needed * price_kwp_hyb) + (qty_batt_hyb * price_batt) + 30000000
    
    # Unit Cost
    unit_cost_on = capex_on / total_kapasitas_kwp
    unit_cost_off = capex_off / total_kapasitas_kwp
    unit_cost_hyb = capex_hyb / total_kapasitas_kwp

    # === BUSINESS LOGIC (HITUNGAN PROFIT PENYEDIA JASA) ===
    # Margin dihitung dari Total Omzet
    
    # 1. Profit Kotor (Gross Profit)
    profit_on = capex_on * (target_margin / 100)
    profit_off = capex_off * (target_margin / 100)
    profit_hyb = capex_hyb * (target_margin / 100)
    
    # 2. HPP (Harga Pokok Penjualan) / Modal Maksimal
    # Ini adalah budget maksimal belanja alat & tukang agar margin tercapai
    hpp_on = capex_on - profit_on
    hpp_off = capex_off - profit_off
    hpp_hyb = capex_hyb - profit_hyb
    
    # 3. Pajak Final
    tax_on = capex_on * (tax_rate / 100)
    tax_off = capex_off * (tax_rate / 100)
    tax_hyb = capex_hyb * (tax_rate / 100)
    
    # 4. Profit Bersih (Net Profit)
    net_on = profit_on - tax_on
    net_off = profit_off - tax_off
    net_hyb = profit_hyb - tax_hyb

    # Penghematan Client
    hemat_thn_on = biaya_pln_tahunan * (eff_on / 100)
    hemat_thn_off = biaya_pln_tahunan * (eff_off / 100)
    hemat_thn_hyb = biaya_pln_tahunan * (eff_hyb / 100)

    # BEP Client
    bep_on = capex_on / hemat_thn_on if hemat_thn_on > 0 else 0
    bep_off = capex_off / hemat_thn_off if hemat_thn_off > 0 else 0
    bep_hyb = capex_hyb / hemat_thn_hyb if hemat_thn_hyb > 0 else 0
    
    # OPEX Client
    tarif_sewa = tarif_pln * (1 - (opex_discount/100))
    
    return {
        "panel_qty": jumlah_panel, "kwp_total": total_kapasitas_kwp, "area": total_luas,
        "batt_off": qty_batt_off, "batt_hyb": qty_batt_hyb,
        "capex_on": capex_on, "capex_off": capex_off, "capex_hyb": capex_hyb,
        "unit_on": unit_cost_on, "unit_off": unit_cost_off, "unit_hyb": unit_cost_hyb,
        "bep_on": bep_on, "bep_off": bep_off, "bep_hyb": bep_hyb,
        "vendor_on": (daya_bulanan * (eff_on/100)) * tarif_sewa, 
        "sisa_on": (daya_bulanan * (1 - (eff_on/100))) * tarif_pln,
        "vendor_off": daya_bulanan * tarif_sewa,
        "vendor_hyb": (daya_bulanan * (eff_hyb/100)) * tarif_sewa,
        "sisa_hyb": (daya_bulanan * (1 - (eff_hyb/100))) * tarif_pln,
        # DATA BISNIS
        "profit_on": profit_on, "hpp_on": hpp_on, "net_on": net_on,
        "profit_off": profit_off, "hpp_off": hpp_off, "net_off": net_off,
        "profit_hyb": profit_hyb, "hpp_hyb": hpp_hyb, "net_hyb": net_hyb
    }

res = calculate_final(target_on, target_off, target_hyb)

# --- 7. MENAMPILKAN HASIL (CUSTOMER VIEW) ---

with col1:
    st.markdown(f"""
    <div class="card-bot">
        <div class="sec-head">1. Kebutuhan Perangkat</div>
        <div class="row-item"><span>Panel Surya:</span><span class="val-bold">{res['panel_qty']} Unit</span></div>
        <div class="row-item"><span>Total Kapasitas:</span><span class="val-bold">{res['kwp_total']:.2f} kWp</span></div>
        <div class="row-item"><span>Kebutuhan Area:</span><span class="val-bold">{res['area']:.1f} m²</span></div>
        <div class="divider"></div>
        <div class="sec-head">2. Penawaran Harga (CAPEX)</div>
        <div class="row-item"><span>Total Investasi:</span><span class="val-bold">Rp {res['capex_on']:,.0f}</span></div>
        <div class="row-item"><span>Harga per kWp:</span><span class="val-blue">Rp {res['unit_on']/1000000:.1f} Juta</span></div>
        <div class="row-item"><span>ROI (Balik Modal):</span><span class="val-blue">{res['bep_on']:.1f} Tahun</span></div>
        <div class="divider"></div>
        <div class="sec-head">3. Estimasi Tagihan (OPEX)</div>
        <div class="row-item"><span>Bayar Sewa Alat:</span><span>Rp {res['vendor_on']:,.0f}</span></div>
        <div class="row-item"><span>Sisa Tagihan PLN:</span><span>Rp {res['sisa_on']:,.0f}</span></div>
        <div class="row-item" style="margin-top:5px; background:#f5f5f5; padding:5px; border-radius:5px;">
        <span>Total Pengeluaran:</span><span class="val-blue">Rp {(res['vendor_on']+res['sisa_on']):,.0f}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="card-bot">
        <div class="sec-head">1. Kebutuhan Perangkat</div>
        <div class="row-item"><span>Panel Surya:</span><span class="val-bold">{res['panel_qty']} Unit</span></div>
        <div class="row-item"><span>Total Kapasitas:</span><span class="val-bold">{res['kwp_total']:.2f} kWp</span></div>
        <div class="row-item"><span>Kebutuhan Area:</span><span class="val-bold">{res['area']:.1f} m²</span></div>
        <div class="row-item"><span>Bank Baterai:</span><span class="val-bold">{res['batt_off']} Unit</span></div>
        <div class="divider"></div>
        <div class="sec-head">2. Penawaran Harga (CAPEX)</div>
        <div class="row-item"><span>Total Investasi:</span><span class="val-bold">Rp {res['capex_off']:,.0f}</span></div>
        <div class="row-item"><span>Harga per kWp:</span><span class="val-blue">Rp {res['unit_off']/1000000:.1f} Juta</span></div>
        <div class="row-item"><span>ROI (Balik Modal):</span><span class="val-blue">{res['bep_off']:.1f} Tahun</span></div>
        <div class="divider"></div>
        <div class="sec-head">3. Estimasi Tagihan (OPEX)</div>
        <div class="row-item"><span>Bayar Sewa Alat:</span><span>Rp {res['vendor_off']:,.0f}</span></div>
        <div class="row-item"><span>Sisa Tagihan PLN:</span><span>Rp 0</span></div>
        <div class="row-item" style="margin-top:5px; background:#f5f5f5; padding:5px; border-radius:5px;">
        <span>Total Pengeluaran:</span><span class="val-blue">Rp {res['vendor_off']:,.0f}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="card-bot">
        <div class="sec-head">1. Kebutuhan Perangkat</div>
        <div class="row-item"><span>Panel Surya:</span><span class="val-bold">{res['panel_qty']} Unit</span></div>
        <div class="row-item"><span>Total Kapasitas:</span><span class="val-bold">{res['kwp_total']:.2f} kWp</span></div>
        <div class="row-item"><span>Kebutuhan Area:</span><span class="val-bold">{res['area']:.1f} m²</span></div>
        <div class="row-item"><span>Bank Baterai:</span><span class="val-bold">{res['batt_hyb']} Unit</span></div>
        <div class="divider"></div>
        <div class="sec-head">2. Penawaran Harga (CAPEX)</div>
        <div class="row-item"><span>Total Investasi:</span><span class="val-bold">Rp {res['capex_hyb']:,.0f}</span></div>
        <div class="row-item"><span>Harga per kWp:</span><span class="val-blue">Rp {res['unit_hyb']/1000000:.1f} Juta</span></div>
        <div class="row-item"><span>ROI (Balik Modal):</span><span class="val-blue">{res['bep_hyb']:.1f} Tahun</span></div>
        <div class="divider"></div>
        <div class="sec-head">3. Estimasi Tagihan (OPEX)</div>
        <div class="row-item"><span>Bayar Sewa Alat:</span><span>Rp {res['vendor_hyb']:,.0f}</span></div>
        <div class="row-item"><span>Sisa Tagihan PLN:</span><span>Rp {res['sisa_hyb']:,.0f}</span></div>
        <div class="row-item" style="margin-top:5px; background:#f5f5f5; padding:5px; border-radius:5px;">
        <span>Total Pengeluaran:</span><span class="val-green">Rp {(res['vendor_hyb']+res['sisa_hyb']):,.0f}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 8. BAGIAN BARU: BUSINESS DASHBOARD (PoV Penyedia Jasa) ---
st.markdown("---")
st.markdown("### 💼 Analisis Profitabilitas Proyek (Internal Only)")
st.info(f"Target Margin: **{target_margin}%** | Pajak Final: **{tax_rate}%**")

col_biz1, col_biz2, col_biz3 = st.columns(3)

# Hitungan On-Grid Business
with col_biz1:
    st.markdown(f"""
    <div class="card-top gold-top">
        <span class="card-title" style="color: #f57f17;">💰 ON-GRID PROFIT</span>
        <span class="card-sub">Analisis Cuan Proyek</span>
    </div>
    <div class="card-bot" style="background: #fffde7; border-top:none;">
        <div class="row-item"><span>Total Omzet (Penjualan):</span><span class="val-bold">Rp {res['capex_on']:,.0f}</span></div>
        <div class="row-item" title="Batas maksimal belanja material & upah"><span>Batas HPP/Modal:</span><span style="color:#d32f2f;">Rp {res['hpp_on']:,.0f}</span></div>
        <div class="divider"></div>
        <div class="row-item"><span>Gross Profit:</span><span class="val-bold">Rp {res['profit_on']:,.0f}</span></div>
        <div class="row-item"><span>Pajak ({tax_rate}%):</span><span>- Rp {(res['profit_on'] - res['net_on']):,.0f}</span></div>
        <div class="row-item" style="background: #fbc02d; padding: 5px; border-radius: 5px; margin-top: 5px;">
            <span style="color:white; font-weight:bold;">NET PROFIT:</span>
            <span style="color:white; font-weight:900; float:right;">Rp {res['net_on']:,.0f}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Hitungan Off-Grid Business
with col_biz2:
    st.markdown(f"""
    <div class="card-top gold-top">
        <span class="card-title" style="color: #f57f17;">💰 OFF-GRID PROFIT</span>
        <span class="card-sub">Analisis Cuan Proyek</span>
    </div>
    <div class="card-bot" style="background: #fffde7; border-top:none;">
        <div class="row-item"><span>Total Omzet (Penjualan):</span><span class="val-bold">Rp {res['capex_off']:,.0f}</span></div>
        <div class="row-item" title="Batas maksimal belanja material & upah"><span>Batas HPP/Modal:</span><span style="color:#d32f2f;">Rp {res['hpp_off']:,.0f}</span></div>
        <div class="divider"></div>
        <div class="row-item"><span>Gross Profit:</span><span class="val-bold">Rp {res['profit_off']:,.0f}</span></div>
        <div class="row-item"><span>Pajak ({tax_rate}%):</span><span>- Rp {(res['profit_off'] - res['net_off']):,.0f}</span></div>
        <div class="row-item" style="background: #fbc02d; padding: 5px; border-radius: 5px; margin-top: 5px;">
            <span style="color:white; font-weight:bold;">NET PROFIT:</span>
            <span style="color:white; font-weight:900; float:right;">Rp {res['net_off']:,.0f}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Hitungan Hybrid Business
with col_biz3:
    st.markdown(f"""
    <div class="card-top gold-top">
        <span class="card-title" style="color: #f57f17;">💰 HYBRID PROFIT</span>
        <span class="card-sub">Analisis Cuan Proyek</span>
    </div>
    <div class="card-bot" style="background: #fffde7; border-top:none;">
        <div class="row-item"><span>Total Omzet (Penjualan):</span><span class="val-bold">Rp {res['capex_hyb']:,.0f}</span></div>
        <div class="row-item" title="Batas maksimal belanja material & upah"><span>Batas HPP/Modal:</span><span style="color:#d32f2f;">Rp {res['hpp_hyb']:,.0f}</span></div>
        <div class="divider"></div>
        <div class="row-item"><span>Gross Profit:</span><span class="val-bold">Rp {res['profit_hyb']:,.0f}</span></div>
        <div class="row-item"><span>Pajak ({tax_rate}%):</span><span>- Rp {(res['profit_hyb'] - res['net_hyb']):,.0f}</span></div>
        <div class="row-item" style="background: #fbc02d; padding: 5px; border-radius: 5px; margin-top: 5px;">
            <span style="color:white; font-weight:bold;">NET PROFIT:</span>
            <span style="color:white; font-weight:900; float:right;">Rp {res['net_hyb']:,.0f}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
