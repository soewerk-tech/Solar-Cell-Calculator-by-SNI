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
    hemat_opex_
