import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
from gspread_dataframe import set_with_dataframe
from datetime import datetime, date, timedelta
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
import plotly.express as px
warnings.filterwarnings('ignore')

# ========== KONFIGURASI WARNA & TEMA SEDERHANA ==========
# Tema sederhana: Biru Astra dominan, Putih, Merah minimal
ASTRA_BLUE = "#0055A4"      # Biru Astra utama
DARK_BLUE = "#003366"        # Biru tua untuk header
LIGHT_BLUE = "#E8F0F8"       # Biru sangat muda untuk background
WHITE = "#FFFFFF"            # Putih untuk konten
LIGHT_GRAY = "#F5F5F5"       # Abu-abu sangat terang
ACCENT_RED = "#CC0000"       # Merah untuk aksen minimal
TEXT_DARK = "#1E2A3A"        # Teks gelap
TEXT_MEDIUM = "#4A5568"      # Teks medium

# Warna status minimal
ROW_PENDING = "#FFE5E5"      # Merah sangat muda
ROW_COMPLETE = "#E5F5E5"     # Hijau sangat muda

# Konfigurasi Halaman
st.set_page_config(
    page_title="Astra Isuzu Tracking System", 
    page_icon="🚛",
    layout="wide"
)

# ========== CUSTOM CSS MODERN & INTERAKTIF ==========
st.markdown(f"""
<style>
    /* FONT IMPORT - GOOGLE FONTS */
    @import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    /* GLOBAL STYLES - ENHANCED */
    .stApp {{
        background: linear-gradient(135deg, {LIGHT_GRAY} 0%, #F0F4F8 100%);
        font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}
    
    /* HEADER MODERN */
    .main-header {{
        background: linear-gradient(135deg, {ASTRA_BLUE} 0%, {DARK_BLUE} 100%);
        padding: 1.25rem 2rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 20px rgba(0,85,164,0.15);
        border-bottom: none;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }}
    
    .main-header::before {{
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 70%);
        pointer-events: none;
    }}
    
    .main-header h1 {{
        color: {WHITE};
        font-size: 1.8rem !important;
        font-weight: 800 !important;
        margin-bottom: 0.25rem !important;
        letter-spacing: -0.02em;
        font-family: 'Plus Jakarta Sans', 'Segoe UI', sans-serif;
    }}
    
    .main-header p {{
        color: rgba(255, 255, 255, 0.9);
        font-size: 0.9rem;
        margin-bottom: 0 !important;
        font-weight: 400;
    }}
    
    /* SIDEBAR MODERN */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {WHITE} 0%, {LIGHT_GRAY} 100%);
        border-right: none;
        box-shadow: 4px 0 20px rgba(0,0,0,0.05);
    }}
    
    [data-testid="stSidebar"] * {{
        color: {TEXT_DARK};
        font-family: 'Inter', sans-serif;
    }}
    
    [data-testid="stSidebar"] .stMarkdown {{
        font-weight: 500;
    }}
    
    /* KPI METRIC CARDS - ENHANCED */
    .metric-card {{
        background: {WHITE};
        padding: 1.25rem;
        border-radius: 14px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.03);
        border-left: 4px solid {ASTRA_BLUE};
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }}
    
    .metric-card::after {{
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, {ASTRA_BLUE}, transparent);
        transform: scaleX(0);
        transition: transform 0.3s ease;
    }}
    
    .metric-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.1);
    }}
    
    .metric-card:hover::after {{
        transform: scaleX(1);
    }}
    
    /* BUTTON STYLING - ENHANCED */
    .stButton > button {{
        background: linear-gradient(135deg, {ASTRA_BLUE} 0%, {DARK_BLUE} 100%);
        color: {WHITE};
        border: none;
        padding: 0.6rem 1.25rem;
        border-radius: 10px;
        font-weight: 600;
        font-size: 0.875rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,85,164,0.2);
        font-family: 'Inter', sans-serif;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,85,164,0.3);
        background: linear-gradient(135deg, {DARK_BLUE} 0%, {ASTRA_BLUE} 100%);
    }}
    
    .stButton > button:active {{
        transform: translateY(0px);
    }}
    
    /* TABEL STYLING - ENHANCED */
    .dataframe {{
        background: {WHITE};
        border-radius: 12px !important;
        border: 1px solid #E8E8E8;
        overflow: hidden;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }}
    
    .dataframe thead {{
        background: linear-graditent(135deg, {ASTRA_BLUE} 0%, {DARK_BLUE} 100%);
    }}
    
    .dataframe th {{
        color: {WHITE} !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        padding: 12px 10px !important;
        font-family: 'Inter', sans-serif;
        letter-spacing: 0.3px;
    }}
    
    .dataframe td {{
        color: {TEXT_DARK} !important;
        font-size: 12.5px !important;
        padding: 10px 8px !important;
        font-family: 'Inter', sans-serif;
    }}
    
    .dataframe tr:hover td {{
        background-color: {LIGHT_BLUE} !important;
        transition: background-color 0.2s ease;
    }}
    
    /* SECTION HEADERS - ENHANCED */
    .section-header {{
        color: {DARK_BLUE} !important;
        font-weight: 700 !important;
        font-size: 1.15rem !important;
        margin: 1.25rem 0 0.85rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid {ASTRA_BLUE};
        display: flex;
        align-items: center;
        gap: 8px;
        letter-spacing: -0.01em;
        font-family: 'Plus Jakarta Sans', 'Segoe UI', sans-serif;
        width: 100%;
    }}
    
    .section-header::before {{
        content: '▌';
        color: {ASTRA_BLUE};
        font-weight: bold;
        font-size: 0.95rem;
    }}
    
    /* FOOTER - ENHANCED */
    .footer {{
        background: linear-gradient(135deg, {DARK_BLUE} 0%, {ASTRA_BLUE} 100%);
        color: {WHITE};
        padding: 1.25rem;
        border-radius: 16px;
        margin-top: 2rem;
        text-align: center;
        font-family: 'Inter', sans-serif;
    }}
    
    /* STATUS BADGES */
    .status-badge {{
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
    }}
    
    .status-pending {{
        background-color: {ROW_PENDING};
        color: {ACCENT_RED};
    }}
    
    .status-complete {{
        background-color: {ROW_COMPLETE};
        color: #2E7D32;
    }}
    
    /* ALERT BOXES - ENHANCED */
    .alert-info {{
        background: linear-gradient(135deg, {LIGHT_BLUE} 0%, #E3F0FA 100%);
        padding: 0.875rem 1rem;
        border-radius: 12px;
        border-left: 4px solid {ASTRA_BLUE};
        margin-bottom: 0.75rem;
        font-family: 'Inter', sans-serif;
        transition: all 0.2s ease;
    }}
    
    .alert-info:hover {{
        transform: translateX(4px);
    }}
    
    .alert-warning {{
        background: linear-gradient(135deg, #FFF5E5 0%, #FEF3C7 100%);
        padding: 0.875rem 1rem;
        border-radius: 12px;
        border-left: 4px solid {ACCENT_RED};
        margin-bottom: 0.75rem;
        font-family: 'Inter', sans-serif;
    }}
    
    .alert-success {{
        background: linear-gradient(135deg, #E8F5E9 0%, #D1FAE5 100%);
        padding: 0.875rem 1rem;
        border-radius: 12px;
        border-left: 4px solid #2E7D32;
        margin-bottom: 0.75rem;
        font-family: 'Inter', sans-serif;
    }}
    
    /* TIMELINE STYLING */
    .timeline-container {{
        position: relative;
        padding-left: 25px;
        margin: 15px 0;
    }}
    
    .timeline-item {{
        position: relative;
        margin-bottom: 15px;
        padding: 12px 16px;
        background: {WHITE};
        border-radius: 10px;
        border: 1px solid #E8E8E8;
        border-left: 3px solid {ASTRA_BLUE};
        transition: all 0.2s ease;
        font-family: 'Inter', sans-serif;
    }}
    
    .timeline-item:hover {{
        transform: translateX(4px);
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }}
    
    /* HEADER CONTROL PANEL */
    .header-control-panel {{
        background: linear-gradient(135deg, {LIGHT_BLUE} 0%, #E3F0FA 100%);
        padding: 0.875rem 1rem;
        border-radius: 12px;
        margin-bottom: 1.25rem;
        border: 1px solid rgba(0,85,164,0.2);
    }}
    
    /* CHASIS SEARCH HIGHLIGHT */
    .chasis-highlight {{
        background: linear-gradient(135deg, {LIGHT_BLUE} 0%, #E3F0FA 100%);
        padding: 0.875rem 1rem;
        border-radius: 12px;
        border-left: 4px solid {ASTRA_BLUE};
        margin-bottom: 1rem;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
    }}
    
    /* DATE RANGE PICKER */
    .date-range-container {{
        background-color: {LIGHT_BLUE};
        padding: 0.875rem;
        border-radius: 12px;
        border: 1px solid rgba(0,85,164,0.2);
        margin-bottom: 1rem;
    }}
    
    /* DROPDOWN STYLING */
    .stSelectbox label {{
        font-weight: 600 !important;
        color: {TEXT_DARK} !important;
        font-size: 0.85rem !important;
        font-family: 'Inter', sans-serif;
    }}
    
    .stSelectbox div[data-baseweb="select"] {{
        border-radius: 10px !important;
    }}
    
    /* PERIODE SELECTOR */
    .periode-selector {{
        background-color: {LIGHT_BLUE};
        padding: 0.875rem;
        border-radius: 12px;
        border-left: 4px solid {ASTRA_BLUE};
        margin-bottom: 1rem;
    }}
    
    /* METRIC VALUE */
    .metric-value {{
        font-size: 2rem;
        font-weight: 800;
        color: {ASTRA_BLUE};
        font-family: 'Plus Jakarta Sans', sans-serif;
        line-height: 1.2;
    }}
    
    /* SERVICE ADVISOR ALERT */
    .service-alert {{
        background: linear-gradient(135deg, #FFF5E5 0%, #FEF3C7 100%);
        padding: 0.875rem;
        border-radius: 10px;
        border-left: 4px solid #FFA000;
        margin-bottom: 0.5rem;
        font-family: 'Inter', sans-serif;
    }}
    
    .service-alert-warning {{
        background: linear-gradient(135deg, #FFF5E5 0%, #FEF3C7 100%);
        border-left: 4px solid {ACCENT_RED};
    }}
    
    .service-alert-success {{
        background: linear-gradient(135deg, #E8F5E9 0%, #D1FAE5 100%);
        border-left: 4px solid #2E7D32;
    }}
    
    /* READ-ONLY MODE INDICATOR */
    .readonly-indicator {{
        background-color: #F8F9FA;
        padding: 0.875rem;
        border-radius: 10px;
        border-left: 4px solid #6c757d;
        margin-bottom: 1rem;
        color: #495057;
        font-weight: 500;
        font-family: 'Inter', sans-serif;
    }}
    
    /* TABS STYLING - ENHANCED */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background-color: {WHITE};
        padding: 6px;
        border-radius: 14px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }}
    
    .stTabs [data-baseweb="tab"] {{
        border-radius: 10px;
        padding: 8px 20px;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        transition: all 0.2s ease;
    }}
    
    .stTabs [data-baseweb="tab"]:hover {{
        background-color: {LIGHT_BLUE};
    }}
    
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, {ASTRA_BLUE}, {DARK_BLUE});
        color: {WHITE};
    }}
    
    /* EXPANDER STYLING */
    .streamlit-expanderHeader strong{{
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        background-color: transparent !important;
        border-radius: 10px !important;
    }}
    /*STYLING BACKGROUND EXPANDER*/
    .streamlit-expanderContent strong {{
        background : transparent !important;
        background-color: transparent !important;
        color: #1E2A3A !important;
    }}
    
    /* DIVIDER */
    hr {{
        margin: 1.5rem 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, {ASTRA_BLUE}, {ASTRA_BLUE} 80%, transparent);
        width: 100%;
    }}
    
    /* TEXT INPUT */
    .stTextInput input {{
        border-radius: 10px !important;
        font-family: 'Inter', sans-serif !important;
    }}
    
    .stTextInput input:focus {{
        border-color: {ASTRA_BLUE} !important;
        box-shadow: 0 0 0 2px rgba(0,85,164,0.1) !important;
    }}
    
    /* NUMBER INPUT */
    .stNumberInput input {{
        border-radius: 10px !important;
    }}
    
    /* MULTISELECT */
    .stMultiSelect [data-baseweb="select"] {{
        border-radius: 10px !important;
    }}
    
    /* DATE INPUT */
    .stDateInput input {{
        border-radius: 10px !important;
        font-family: 'Inter', sans-serif !important;
    }}
    
    /* METRIC CARD ADDITIONAL */
    .stat-card {{
        background: {WHITE};
        border-radius: 14px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        border: 1px solid rgba(0,85,164,0.08);
        transition: all 0.2s ease;
    }}
    
    .stat-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }}
    
    .stat-number {{
        font-size: 1.75rem;
        font-weight: 800;
        color: {ASTRA_BLUE};
        font-family: 'Plus Jakarta Sans', sans-serif;
    }}
    
    .stat-label {{
        font-size: 0.7rem;
        font-weight: 600;
        color: {TEXT_MEDIUM};
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-family: 'Inter', sans-serif;
    }}
    
    .nav-hint:hover {{
        transform: scale(1.05);
        box-shadow: 0 6px 20px rgba(0,85,164,0.4);
    }}
    
    @keyframes fadeOut {{
        0% {{ opacity: 1; transform: scale(1); }}
        80% {{ opacity: 1; transform: scale(1); }}
        100% {{ opacity: 0; transform: scale(0.9); visibility: hidden; }}
    }}
    
    .nav-hint-fade {{
        animation: fadeOut 6s forwards;
    }}
    
    /* TOOLTIP */
    [data-testid="stTooltip"] {{
        font-family: 'Inter', sans-serif;
    }}
    
    /* MARKDOWN TEXT */
    .stMarkdown {{
        font-family: 'Inter', sans-serif;
    }}
    
    /* CODE BLOCK */
    .stCode {{
        border-radius: 10px;
    }}
    
    /* PROGRESS BAR */
    .stProgress > div > div {{
        background : transparent !important;
        background-color: transparent !important;
        border-radius: 10px !important;
    }}
    
    /* CHECKBOX */
    .stCheckbox label {{
        font-family: 'Inter', sans-serif;
        font-weight: 500;
    }}
    
    /* RADIO */
    .stRadio label {{
        font-family: 'Inter', sans-serif;
    }}
</style>
<script>
setTimeout(function() {{
    var hint = document.getElementById('navHint');
    if(hint) hint.classList.add('nav-hint-fade');
}}, 5000);
</script>
""", unsafe_allow_html=True)

# ========== INISIALISASI SESSION STATE ==========
if 'last_saved' not in st.session_state:
    st.session_state.last_saved = None
if 'df_original' not in st.session_state:
    st.session_state.df_original = pd.DataFrame()
if 'salesman_list' not in st.session_state:
    st.session_state.salesman_list = []
if 'material_list' not in st.session_state:
    st.session_state.material_list = []
if 'show_stnk_detail' not in st.session_state:
    st.session_state.show_stnk_detail = False
if 'show_bpkb_detail' not in st.session_state:
    st.session_state.show_bpkb_detail = False
if 'show_incomplete_detail' not in st.session_state:
    st.session_state.show_incomplete_detail = False
if 'show_dokumen_belum_lengkap' not in st.session_state:
    st.session_state.show_dokumen_belum_lengkap = False
if 'start_date' not in st.session_state:
    st.session_state.start_date = None
if 'end_date' not in st.session_state:
    st.session_state.end_date = None
if 'delivery_start_date' not in st.session_state:
    st.session_state.delivery_start_date = None
if 'delivery_end_date' not in st.session_state:
    st.session_state.delivery_end_date = None
if 'periode_start' not in st.session_state:
    st.session_state.periode_start = None
if 'periode_end' not in st.session_state:
    st.session_state.periode_end = None
if 'periode_applied' not in st.session_state:
    st.session_state.periode_applied = False
if 'periode_start_applied' not in st.session_state:
    st.session_state.periode_start_applied = None
if 'periode_end_applied' not in st.session_state:
    st.session_state.periode_end_applied = None
if 'df_periode' not in st.session_state:
    st.session_state.df_periode = pd.DataFrame()
if 'periode_label' not in st.session_state:
    st.session_state.periode_label = "Semua Data"

# Inisialisasi session state untuk sinkronisasi
if 'sync_in_progress' not in st.session_state:
    st.session_state.sync_in_progress = False
if 'sync_message' not in st.session_state:
    st.session_state.sync_message = ""
if 'sync_time' not in st.session_state:
    st.session_state.sync_time = ""
if 'sync_success' not in st.session_state:
    st.session_state.sync_success = False
if 'auto_sync_enabled' not in st.session_state:
    st.session_state.auto_sync_enabled = False
if 'last_auto_sync' not in st.session_state:
    st.session_state.last_auto_sync = None

# Inisialisasi session state untuk dropdown
if 'selected_trend_column' not in st.session_state:
    st.session_state.selected_trend_column = 'Tgl DO'
if 'selected_pareto_analysis' not in st.session_state:
    st.session_state.selected_pareto_analysis = 'DO ke STNK'
if 'tracked_chasis' not in st.session_state:
    st.session_state.tracked_chasis = None
if 'tracked_customer' not in st.session_state:
    st.session_state.tracked_customer = None

# PERUBAHAN: Session state untuk status loading data
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False

# Google Sheet ID - FIXED
SPREADSHEET_ID = st.secrets.get("SPREADSHEET_ID", "18DwzgiHRfk7JkVSYAzKGeM2ipu4VM_LwZoEW5qPPUgU")
if 'spreadsheet_id' not in st.session_state:
    st.session_state.spreadsheet_id = SPREADSHEET_ID

# ========== FUNGSI UNTUK GOOGLE SHEETS API ==========
@st.cache_resource
def init_google_sheets():
    """Initialize Google Sheets connection"""
    try:
        if 'gcp_service_account' in st.secrets:
            credentials_dict = dict(st.secrets['gcp_service_account'])
            credentials = service_account.Credentials.from_service_account_info(
                credentials_dict,
                scopes=[
                    'https://www.googleapis.com/auth/spreadsheets',
                    'https://www.googleapis.com/auth/drive'
                ]
            )
            gc = gspread.authorize(credentials)
            return gc
        else:
            credentials = service_account.Credentials.from_service_account_file(
                'credentials.json',
                scopes=[
                    'https://www.googleapis.com/auth/spreadsheets',
                    'https://www.googleapis.com/auth/drive'
                ]
            )
            gc = gspread.authorize(credentials)
            return gc
    except Exception as e:
        st.error(f"❌ Error koneksi Google Sheets: {str(e)[:100]}")
        return None

# ========== FUNGSI SINKRONISASI DATA ==========
def sync_data():
    """Fungsi untuk sinkronisasi data tanpa rerun paksa"""
    try:
        st.cache_data.clear()
        st.session_state.sync_in_progress = True
        st.session_state.sync_message = "🔄 Sedang sinkronisasi data..."
        st.session_state.sync_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        with st.spinner("📥 Mengambil data terbaru dari Google Sheets..."):
            new_data = read_google_sheets_force()
            
            if not new_data.empty:
                st.session_state.df_original = new_data.copy()
                st.session_state.sync_in_progress = False
                st.session_state.sync_message = f"Data berhasil disinkronisasi! ({st.session_state.sync_time})"
                st.session_state.sync_success = True
                st.session_state.last_saved = st.session_state.sync_time
                st.session_state.data_loaded = True
                update_salesman_material_lists(new_data)
                return True, "Data berhasil disinkronisasi!"
            else:
                st.session_state.sync_in_progress = False
                st.session_state.sync_message = "⚠️ Data kosong atau tidak dapat dimuat"
                st.session_state.sync_success = False
                return False, "Data kosong"
    except Exception as e:
        st.session_state.sync_in_progress = False
        st.session_state.sync_message = f"❌ Error sinkronisasi: {str(e)[:100]}"
        st.session_state.sync_success = False
        return False, str(e)

def update_salesman_material_lists(df):
    """Update lists salesman dan material dari dataframe"""
    if 'Nama Salesman' in df.columns:
        existing_salesman = df['Nama Salesman'].dropna().unique().tolist()
        for salesman in existing_salesman:
            if salesman and salesman not in st.session_state.salesman_list:
                st.session_state.salesman_list.append(str(salesman))
    
    if 'Material Description' in df.columns:
        existing_material = df['Material Description'].dropna().unique().tolist()
        for material in existing_material:
            if material and material not in st.session_state.material_list:
                st.session_state.material_list.append(str(material))

def read_google_sheets_force():
    """Membaca data dari Google Sheets tanpa cache (force refresh)"""
    try:
        gc = init_google_sheets()
        if not gc:
            return pd.DataFrame()
        
        spreadsheet = gc.open_by_key(SPREADSHEET_ID)
        worksheet = spreadsheet.sheet1
        records = worksheet.get_all_records()
        
        if records:
            df = pd.DataFrame(records)
            
            # Standardisasi nama kolom sesuai urutan yang diinginkan
            column_mapping = {
                'No': 'No',
                'Tgl DO': 'Tgl DO',
                'Nama Customer': 'Nama Customer',
                'Nama Salesman': 'Nama Salesman',
                'Chasis': 'Chasis',
                'Material Description': 'Material Description',
                'Jenis Pembayaran': 'Jenis Pembayaran',
                'Nama STNK': 'Nama STNK',
                'NOPOL': 'NOPOL',
                'Tgl STNK': 'Tgl STNK',
                'Tgl BPKB': 'Tgl BPKB',
                'Tgl Serah Terima BPKB': 'Tgl Serah Terima BPKB',
                'Tgl Kirim Tagihan': 'Tgl Kirim Tagihan',
                'Tgl Jatuh Tempo': 'Tgl Jatuh Tempo',
                'Tgl Pelunasan': 'Tgl Pelunasan',
                'Tgl Pengajuan Fakpol Approve': 'Tgl Pengajuan Fakpol Approve',
                'Tgl BJ Terima Fakpol': 'Tgl BJ Terima Fakpol',
                'Download MyIsuzuID': 'Download MyIsuzuID',
                'TOSOL': 'TOSOL',
                'Action TOS': 'Action TOS',
                'KSG I': 'KSG I',
                'KSG II': 'KSG II',
                'KSGX 20K': 'KSGX 20K',
                'KSGX 30K': 'KSGX 30K',
                'KSGX 40K': 'KSGX 40K'
            }
            
            df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns}, inplace=True)
            
            # PERUBAHAN: Jangan buat kolom No otomatis!
            # Hanya gunakan kolom No jika memang ada di source data
            if 'No' in df.columns:
                df['No'] = pd.to_numeric(df['No'], errors='coerce').fillna(0).astype(int)
            
            # List kolom text
            text_columns = ['Nama Customer', 'Nama Salesman', 'Chasis', 'Material Description', 
                          'Jenis Pembayaran', 'Nama STNK', 'NOPOL', 'TOSOL', 'Action TOS']
            
            for col in text_columns:
                if col in df.columns:
                    df[col] = df[col].astype(str).str.strip()
                    df[col] = df[col].replace('nan', '').replace('None', '')
            
            # PERUBAHAN: Filter data - WAJIB memiliki Chasis (acuan utama)
            if 'Chasis' in df.columns:
                # Hanya ambil data yang memiliki Chasis (tidak kosong)
                df = df[df['Chasis'].notna() & (df['Chasis'].astype(str).str.strip() != '')]
            
            # Jika setelah filter tidak ada data
            if df.empty:
                st.warning("⚠️ Tidak ada data dengan Chasis yang valid")
                return pd.DataFrame()
            
            # List semua kolom tanggal - FORMAT dd/mm/yy
            date_columns = ['Tgl DO', 'Tgl STNK', 'Tgl BPKB', 'Tgl Serah Terima BPKB', 'Tgl Kirim Tagihan', 
                          'Tgl Jatuh Tempo', 'Tgl Pelunasan', 'Tgl Pengajuan Fakpol Approve',
                          'Tgl BJ Terima Fakpol', 'KSG I', 'KSG II', 'KSGX 20K', 'KSGX 30K', 'KSGX 40K']
            
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce', dayfirst=True)
                    df[col] = df[col].where(df[col].notna(), None)
            
            # Kolom boolean (hanya Download)
            if 'Download MyIsuzuID' in df.columns:
                if df['Download MyIsuzuID'].dtype == 'object':
                    df['Download MyIsuzuID'] = df['Download MyIsuzuID'].apply(lambda x: 
                        str(x).lower() in ['true', 'yes', '1', 'v', '✓', 'x', 'ya', 'sudah', 'true', 't', 'aktif', 'selesai']
                    )
                else:
                    df['Download MyIsuzuID'] = df['Download MyIsuzuID'].astype(bool)
            
            # Tambahkan kolom Status STNK dan Status BPKB otomatis dari tanggal
            if 'Tgl STNK' in df.columns:
                df['Status STNK'] = df['Tgl STNK'].notna()
            
            if 'Tgl BPKB' in df.columns:
                df['Status BPKB'] = df['Tgl BPKB'].notna()
            
            # Tambahkan kolom Tanggal Penjualan untuk kompatibilitas
            if 'Tgl DO' in df.columns and 'Tanggal Penjualan' not in df.columns:
                df['Tanggal Penjualan'] = df['Tgl DO']
            
            return df
        else:
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"❌ Error membaca data: {str(e)[:200]}")
        return pd.DataFrame()

# PERUBAHAN: Fungsi load data yang menyimpan ke session state
def load_data():
    """Load data dan simpan ke session state (hanya jika belum ada data)"""
    if not st.session_state.data_loaded or st.session_state.df_original.empty:
        df = read_google_sheets_force()
        if not df.empty:
            st.session_state.df_original = df.copy()
            st.session_state.data_loaded = True
            update_salesman_material_lists(df)
            return df
    return st.session_state.df_original

# ========== FUNGSI UTILITAS ==========
def calculate_service_status(row):
    """Menghitung status service berdasarkan tanggal KSG"""
    today = datetime.now().date()
    alerts = []
    
    # Cek KSG I (Service 5K)
    if 'KSG I' in row and pd.notna(row.get('KSG I')):
        service_date = row['KSG I']
        if isinstance(service_date, datetime):
            service_date = service_date.date()
        else:
            service_date = pd.to_datetime(service_date).date()
        
        days_diff = (service_date - today).days
        if days_diff <= 7 and days_diff >= 0:
            alerts.append(f"✅ KSG I (5K) mendekati: {days_diff} hari lagi")
        elif days_diff < 0:
            alerts.append(f"⚠️ KSG I (5K) terlambat: {-days_diff} hari")
    
    # Cek KSG II (Service 10K)
    if 'KSG II' in row and pd.notna(row.get('KSG II')):
        service_date = row['KSG II']
        if isinstance(service_date, datetime):
            service_date = service_date.date()
        else:
            service_date = pd.to_datetime(service_date).date()
        
        days_diff = (service_date - today).days
        if days_diff <= 14 and days_diff >= 0:
            alerts.append(f"✅ KSG II (10K) mendekati: {days_diff} hari lagi")
        elif days_diff < 0:
            alerts.append(f"⚠️ KSG II (10K) terlambat: {-days_diff} hari")
    
    # Cek KSGX 20K
    if 'KSGX 20K' in row and pd.notna(row.get('KSGX 20K')):
        service_date = row['KSGX 20K']
        if isinstance(service_date, datetime):
            service_date = service_date.date()
        else:
            service_date = pd.to_datetime(service_date).date()
        
        days_diff = (service_date - today).days
        if days_diff <= 14 and days_diff >= 0:
            alerts.append(f"✅ KSGX 20K mendekati: {days_diff} hari lagi")
        elif days_diff < 0:
            alerts.append(f"⚠️ KSGX 20K terlambat: {-days_diff} hari")
    
    # Cek KSGX 30K
    if 'KSGX 30K' in row and pd.notna(row.get('KSGX 30K')):
        service_date = row['KSGX 30K']
        if isinstance(service_date, datetime):
            service_date = service_date.date()
        else:
            service_date = pd.to_datetime(service_date).date()
        
        days_diff = (service_date - today).days
        if days_diff <= 14 and days_diff >= 0:
            alerts.append(f"✅ KSGX 30K mendekati: {days_diff} hari lagi")
        elif days_diff < 0:
            alerts.append(f"⚠️ KSGX 30K terlambat: {-days_diff} hari")
    
    # Cek KSGX 40K
    if 'KSGX 40K' in row and pd.notna(row.get('KSGX 40K')):
        service_date = row['KSGX 40K']
        if isinstance(service_date, datetime):
            service_date = service_date.date()
        else:
            service_date = pd.to_datetime(service_date).date()
        
        days_diff = (service_date - today).days
        if days_diff <= 14 and days_diff >= 0:
            alerts.append(f"✅ KSGX 40K mendekati: {days_diff} hari lagi")
        elif days_diff < 0:
            alerts.append(f"⚠️ KSGX 40K terlambat: {-days_diff} hari")
    
    return alerts

def calculate_delivery_time_stnk(row):
    """Menghitung waktu dari Tgl DO ke Tgl STNK"""
    tgl_do = None
    tgl_stnk = None
    
    if 'Tgl DO' in row and pd.notna(row.get('Tgl DO')):
        tgl_do = row['Tgl DO']
    
    if 'Tgl STNK' in row and pd.notna(row.get('Tgl STNK')):
        tgl_stnk = row['Tgl STNK']
    
    if tgl_do and tgl_stnk:
        try:
            if isinstance(tgl_do, datetime):
                tgl_do_dt = tgl_do
            else:
                tgl_do_dt = pd.to_datetime(tgl_do)
            
            if isinstance(tgl_stnk, datetime):
                tgl_stnk_dt = tgl_stnk
            else:
                tgl_stnk_dt = pd.to_datetime(tgl_stnk)
            
            if isinstance(tgl_do_dt, datetime) and isinstance(tgl_stnk_dt, datetime):
                delivery_days = (tgl_stnk_dt - tgl_do_dt).days
                return delivery_days if delivery_days >= 0 else None
        except:
            pass
    return None

def calculate_time_difference(row, start_col, end_col):
    """Menghitung selisih hari antara dua kolom tanggal"""
    start_date = None
    end_date = None
    
    if start_col in row and pd.notna(row.get(start_col)):
        start_date = row[start_col]
    
    if end_col in row and pd.notna(row.get(end_col)):
        end_date = row[end_col]
    
    if start_date and end_date:
        try:
            if isinstance(start_date, datetime):
                start_dt = start_date
            else:
                start_dt = pd.to_datetime(start_date)
            
            if isinstance(end_date, datetime):
                end_dt = end_date
            else:
                end_dt = pd.to_datetime(end_date)
            
            if isinstance(start_dt, datetime) and isinstance(end_dt, datetime):
                diff_days = (end_dt - start_dt).days
                return diff_days if diff_days >= 0 else None
        except:
            pass
    return None

def get_process_status(row):
    """Menghitung status proses untuk satu kendaraan"""
    process_steps = []
    
    # Step 1: Tgl DO (Delivery Order)
    if 'Tgl DO' in row and pd.notna(row.get('Tgl DO')):
        process_steps.append({
            'name': 'Delivery Order',
            'status': 'completed',
            'date': row['Tgl DO'],
            'icon': '📋'
        })
    else:
        process_steps.append({
            'name': 'Delivery Order',
            'status': 'pending',
            'date': None,
            'icon': '📋'
        })
    
    # Step 2: STNK
    if 'Status STNK' in row and row.get('Status STNK'):
        process_steps.append({
            'name': 'STNK',
            'status': 'completed',
            'date': row.get('Tgl STNK'),
            'icon': '📄'
        })
    else:
        process_steps.append({
            'name': 'STNK',
            'status': 'pending',
            'date': None,
            'icon': '📄'
        })
    
    # Step 3: BPKB
    if 'Status BPKB' in row and row.get('Status BPKB'):
        process_steps.append({
            'name': 'BPKB',
            'status': 'completed',
            'date': row.get('Tgl BPKB'),
            'icon': '📑'
        })
    else:
        process_steps.append({
            'name': 'BPKB',
            'status': 'pending',
            'date': None,
            'icon': '📑'
        })
    
    # Step 4: Serah Terima BPKB
    if 'Tgl Serah Terima BPKB' in row and pd.notna(row.get('Tgl Serah Terima BPKB')):
        process_steps.append({
            'name': 'Serah Terima BPKB',
            'status': 'completed',
            'date': row.get('Tgl Serah Terima BPKB'),
            'icon': '📦'
        })
    else:
        process_steps.append({
            'name': 'Serah Terima BPKB',
            'status': 'pending',
            'date': None,
            'icon': '📦'
        })
    
    # Step 5: Download
    if 'Download MyIsuzuID' in row and row.get('Download MyIsuzuID'):
        process_steps.append({
            'name': 'Download',
            'status': 'completed',
            'date': None,
            'icon': '📱'
        })
    else:
        process_steps.append({
            'name': 'Download',
            'status': 'pending',
            'date': None,
            'icon': '📱'
        })
    
    # Step 6: TOSOL
    if 'TOSOL' in row and pd.notna(row.get('TOSOL')) and row.get('TOSOL') != '':
        process_steps.append({
            'name': 'TOSOL',
            'status': 'completed',
            'date': None,
            'icon': '📌'
        })
    else:
        process_steps.append({
            'name': 'TOSOL',
            'status': 'pending',
            'date': None,
            'icon': '📌'
        })
    
    # Step 7: Action TOS
    if 'Action TOS' in row and pd.notna(row.get('Action TOS')) and row.get('Action TOS') != '':
        process_steps.append({
            'name': 'Action TOS',
            'status': 'completed',
            'date': None,
            'icon': '⚡'
        })
    else:
        process_steps.append({
            'name': 'Action TOS',
            'status': 'pending',
            'date': None,
            'icon': '⚡'
        })
    
    # Step 8: KSG I (5K)
    if 'KSG I' in row and pd.notna(row.get('KSG I')):
        process_steps.append({
            'name': 'KSG I (5K)',
            'status': 'completed',
            'date': row['KSG I'],
            'icon': '🔧'
        })
    else:
        process_steps.append({
            'name': 'KSG I (5K)',
            'status': 'pending',
            'date': None,
            'icon': '🔧'
        })
    
    # Step 9: KSG II (10K)
    if 'KSG II' in row and pd.notna(row.get('KSG II')):
        process_steps.append({
            'name': 'KSG II (10K)',
            'status': 'completed',
            'date': row['KSG II'],
            'icon': '🔧'
        })
    else:
        process_steps.append({
            'name': 'KSG II (10K)',
            'status': 'pending',
            'date': None,
            'icon': '🔧'
        })
    
    # Step 10: KSGX 20K
    if 'KSGX 20K' in row and pd.notna(row.get('KSGX 20K')):
        process_steps.append({
            'name': 'KSGX 20K',
            'status': 'completed',
            'date': row['KSGX 20K'],
            'icon': '🔧'
        })
    else:
        process_steps.append({
            'name': 'KSGX 20K',
            'status': 'pending',
            'date': None,
            'icon': '🔧'
        })
    
    # Step 11: KSGX 30K
    if 'KSGX 30K' in row and pd.notna(row.get('KSGX 30K')):
        process_steps.append({
            'name': 'KSGX 30K',
            'status': 'completed',
            'date': row['KSGX 30K'],
            'icon': '🔧'
        })
    else:
        process_steps.append({
            'name': 'KSGX 30K',
            'status': 'pending',
            'date': None,
            'icon': '🔧'
        })
    
    # Step 12: KSGX 40K
    if 'KSGX 40K' in row and pd.notna(row.get('KSGX 40K')):
        process_steps.append({
            'name': 'KSGX 40K',
            'status': 'completed',
            'date': row['KSGX 40K'],
            'icon': '🔧'
        })
    else:
        process_steps.append({
            'name': 'KSGX 40K',
            'status': 'pending',
            'date': None,
            'icon': '🔧'
        })
    
    return process_steps

def get_payment_status(row):
    """Menghitung status pembayaran"""
    payment_status = []
    
    if 'Tgl Kirim Tagihan' in row and pd.notna(row.get('Tgl Kirim Tagihan')):
        payment_status.append('✅ Tagihan Dikirim')
    else:
        payment_status.append('❌ Tagihan Belum Dikirim')
    
    if 'Tgl Jatuh Tempo' in row and pd.notna(row.get('Tgl Jatuh Tempo')):
        jatuh_tempo = row['Tgl Jatuh Tempo']
        if isinstance(jatuh_tempo, datetime):
            jatuh_tempo = jatuh_tempo.date()
            today = datetime.now().date()
            days_diff = (jatuh_tempo - today).days
            
            if 'Tgl Pelunasan' in row and pd.notna(row.get('Tgl Pelunasan')):
                payment_status.append('✅ Lunas')
            else:
                if days_diff < 0:
                    payment_status.append(f'⚠️ Melewati Jatuh Tempo ({abs(days_diff)} hari)')
                elif days_diff <= 7:
                    payment_status.append(f'⚠️ Jatuh Tempo {days_diff} hari lagi')
                else:
                    payment_status.append(f'📅 Jatuh Tempo {days_diff} hari lagi')
    
    if 'Tgl Pengajuan Fakpol Approve' in row and pd.notna(row.get('Tgl Pengajuan Fakpol Approve')):
        payment_status.append('✅ Fakpol Diajukan')
    
    if 'Tgl BJ Terima Fakpol' in row and pd.notna(row.get('Tgl BJ Terima Fakpol')):
        payment_status.append('✅ BJ Fakpol Diterima')
    
    return payment_status

def filter_data_by_date_range(df, date_column, start_date, end_date):
    """Filter data berdasarkan rentang tanggal"""
    if date_column not in df.columns:
        st.warning(f"Kolom {date_column} tidak ditemukan")
        return df.copy(), "Semua Data (Kolom Tidak Ditemukan)"
    
    df_filtered = df.copy()
    df_filtered[date_column] = pd.to_datetime(df_filtered[date_column], errors='coerce')
    
    valid_dates = df_filtered[date_column].notna().sum()
    
    if valid_dates == 0:
        st.warning(f"Tidak ada tanggal valid di kolom {date_column}")
        return df_filtered, "Semua Data (Tidak Ada Tanggal Valid)"
    
    if start_date and end_date:
        start_datetime = pd.to_datetime(start_date)
        end_datetime = pd.to_datetime(end_date)
        
        df_filtered = df_filtered[
            (df_filtered[date_column] >= start_datetime) & 
            (df_filtered[date_column] <= end_datetime)
        ]
        
        period_label = f"{start_datetime.strftime('%d/%m/%Y')} - {end_datetime.strftime('%d/%m/%Y')}"
    else:
        period_label = "Semua Data"
    
    return df_filtered, period_label

def create_pareto_chart(df, start_col, end_col, title):
    """Membuat Pareto chart untuk selisih waktu antara dua kolom tanggal"""
    time_diffs = []
    
    for idx, row in df.iterrows():
        diff = calculate_time_difference(row, start_col, end_col)
        if diff is not None and diff >= 0:
            time_diffs.append(diff)
    
    if not time_diffs:
        return None, None, 0
    
    bins = [0, 7, 14, 30, 60, 90, 120, float('inf')]
    labels = ['≤7 hari', '8-14 hari', '15-30 hari', '31-60 hari', 
              '61-90 hari', '91-120 hari', '>120 hari']
    
    diff_series = pd.Series(time_diffs)
    categories = pd.cut(diff_series, bins=bins, labels=labels, right=False)
    
    counts = categories.value_counts()
    
    pareto_df = pd.DataFrame({
        'Kategori': counts.index,
        'Frekuensi': counts.values
    })
    
    pareto_df = pareto_df.sort_values('Frekuensi', ascending=False)
    
    total = pareto_df['Frekuensi'].sum()
    pareto_df['Persentase'] = (pareto_df['Frekuensi'] / total * 100)
    pareto_df['Kumulatif'] = pareto_df['Persentase'].cumsum()
    
    return pareto_df, diff_series, total

def apply_period():
    """Fungsi untuk menerapkan filter periode berdasarkan Tgl DO"""
    if st.session_state.df_original.empty:
        st.session_state.df_periode = pd.DataFrame()
        st.session_state.periode_label = "Tidak Ada Data"
        st.session_state.periode_applied = False
        return
    
    start_date = st.session_state.periode_start
    end_date = st.session_state.periode_end
    
    if start_date and end_date:
        if start_date > end_date:
            st.error("❌ Tanggal mulai harus lebih kecil atau sama dengan tanggal selesai!")
            st.session_state.df_periode = st.session_state.df_original.copy()
            st.session_state.periode_label = "Semua Data (Tanggal Tidak Valid)"
            st.session_state.periode_applied = False
        else:
            df_filtered, label = filter_data_by_date_range(
                st.session_state.df_original, 
                'Tgl DO', 
                start_date, 
                end_date
            )
            
            st.session_state.df_periode = df_filtered
            st.session_state.periode_label = label
            st.session_state.periode_applied = True
            st.session_state.periode_start_applied = start_date
            st.session_state.periode_end_applied = end_date
            
            st.success(f"✅ Periode diterapkan: {label} | Total data: {len(df_filtered)} unit")
    else:
        st.session_state.df_periode = st.session_state.df_original.copy()
        st.session_state.periode_label = "Semua Data"
        st.session_state.periode_applied = False

# ========== HEADER SEDERHANA ==========
st.markdown("""
<div class="main-header">
    <h1>🚛 ASTRA ISUZU TRACKING SYSTEM</h1>
    <p>Monitoring & Tracking Unit Kendaraan</p>
</div>
""", unsafe_allow_html=True)

# ========== KONTROL PANEL ==========
st.markdown('<div class="header-control-panel">', unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])

with col1:
    if st.button("🔄 **SINKRONISASI DATA**", type="primary", use_container_width=True):
        success, message = sync_data()
        if success:
            st.success(message)
            st.rerun()
        else:
            st.error(message)

with col2:
    auto_sync = st.checkbox(
        "Auto-sync (5 menit)",
        value=st.session_state.auto_sync_enabled
    )
    if auto_sync != st.session_state.auto_sync_enabled:
        st.session_state.auto_sync_enabled = auto_sync
        if auto_sync:
            st.session_state.last_auto_sync = datetime.now()
            st.info("Auto-sync diaktifkan")

st.markdown('</div>', unsafe_allow_html=True)

# ========== AUTO SYNC ==========
if st.session_state.auto_sync_enabled and st.session_state.last_auto_sync:
    time_diff = (datetime.now() - st.session_state.last_auto_sync).seconds
    if time_diff > 300:
        st.info("🔄 Auto-sync dalam proses...")
        success, message = sync_data()
        if success:
            st.session_state.last_auto_sync = datetime.now()
            st.success("Auto-sync berhasil!")
        else:
            st.warning("Auto-sync gagal, coba manual sync")
    
    st.divider()
    
    if st.session_state.last_saved:
        st.markdown(f"""
        <div style="background-color: #F0F7FF; padding: 0.75rem; border-radius: 6px; border-left: 3px solid #0055A4;">
            <p style="color: #0055A4; margin-bottom: 0.25rem; font-weight: 600;">🕐 TERAKHIR</p>
            <p style="color: #1E2A3A; font-size: 0.9rem;">{st.session_state.last_saved}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    if 'df_original' in st.session_state and not st.session_state.df_original.empty:
        df_stats = st.session_state.df_original
        st.markdown(f"""
        <div style="background-color: #F0F7FF; padding: 0.75rem; border-radius: 6px;">
            <p style="color: #0055A4; margin-bottom: 0.25rem; font-weight: 600;">📈 STATISTIK</p>
            <p style="color: #1E2A3A; font-size: 0.9rem;">Total Unit: {len(df_stats)}</p>
            <p style="color: #1E2A3A; font-size: 0.9rem;">Salesman: {len(st.session_state.salesman_list)}</p>
            <p style="color: #1E2A3A; font-size: 0.9rem;">Material: {len(st.session_state.material_list)}</p>
        </div>
        """, unsafe_allow_html=True)

# ========== STATUS SINKRONISASI ==========
if st.session_state.sync_message:
    st.markdown(f"""
    <div style="background-color: #F0F7FF; padding: 0.75rem; border-radius: 6px; margin-bottom: 1rem; border-left: 3px solid #0055A4;">
        <div style="display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 1.2rem;">{'🔄' if st.session_state.sync_in_progress else '✅' if st.session_state.sync_success else '❌'}</span>
            <div>
                <p style="color: #0055A4; margin: 0; font-weight: 500;">
                    {st.session_state.sync_message}
                </p>
                {f'<p style="color: #666; margin: 0; font-size: 0.85rem;">{st.session_state.sync_time}</p>' if st.session_state.sync_time else ''}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ========== MAIN APP ==========
df = load_data()

# ========== VALIDASI DATA ==========
if not df.empty:
    # PERUBAHAN: Validasi keberadaan kolom Chasis (acuan utama)
    if 'Chasis' not in df.columns:
        st.error("❌ Kolom 'Chasis' tidak ditemukan dalam data. Aplikasi membutuhkan kolom Chasis untuk identifikasi unit.")
        st.stop()
    
    # PERUBAHAN: Filter data tanpa Chasis (sudah dilakukan di load_data)
    # Tampilkan peringatan jika ada data yang difilter
    if len(df) == 0:
        st.warning("⚠️ Tidak ada data valid setelah filter Chasis. Pastikan setiap unit memiliki nomor Chasis.")
        st.stop()
else:
    st.warning("📊 Data kosong atau tidak dapat dimuat.")
    st.stop()

# ========== TRACKING PER CHASIS & CUSTOMER ==========
st.markdown('<div class="section-header">🔍 TRACKING KENDARAAN</div>', unsafe_allow_html=True)

if 'df_original' in st.session_state and not st.session_state.df_original.empty and 'Chasis' in st.session_state.df_original.columns:
    # Tab untuk dua metode pencarian
    tracking_tab1, tracking_tab2 = st.tabs(["🔑 Pencarian berdasarkan Chasis", "👤 Pencarian berdasarkan Nama Customer"])
    
    with tracking_tab1:
        col1, col2 = st.columns([3, 1])
        with col1:
            chasis_options = st.session_state.df_original['Chasis'].dropna().unique().tolist()
            chasis_options = [x for x in chasis_options if x and x != '']
            chasis_options.sort()
            
            selected_chasis = st.selectbox(
                "🔑 Pilih Nomor Chasis:",
                options=[""] + chasis_options,
                format_func=lambda x: f"🔍 {x}" if x else "--- Pilih Nomor Chasis ---",
                help="Pilih nomor chasis untuk melihat seluruh detail tracking kendaraan",
                key="chasis_select"
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if selected_chasis and st.button("🔍 **Lacak Kendaraan (Chasis)**", use_container_width=True, key="track_chasis_btn"):
                st.session_state.tracked_chasis = selected_chasis
                st.session_state.tracked_customer = None
                st.rerun()
    
    with tracking_tab2:
        col1, col2 = st.columns([3, 1])
        with col1:
            customer_options = st.session_state.df_original['Nama Customer'].dropna().unique().tolist()
            customer_options = [x for x in customer_options if x and x != '' and x != 'nan' and x != 'None']
            customer_options.sort()
            
            selected_customer = st.selectbox(
                "👤 Pilih Nama Customer:",
                options=[""] + customer_options,
                format_func=lambda x: f"👤 {x}" if x else "--- Pilih Nama Customer ---",
                help="Pilih nama customer untuk melihat seluruh detail tracking kendaraan",
                key="customer_select"
            )
            
            st.markdown("atau")
            customer_text_search = st.text_input(
                "🔍 Cari Nama Customer (Ketik langsung):",
                placeholder="Ketik nama customer...",
                key="customer_text_search"
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if (selected_customer or customer_text_search) and st.button("🔍 **Lacak Kendaraan (Customer)**", use_container_width=True, key="track_customer_btn"):
                if customer_text_search:
                    st.session_state.tracked_customer = customer_text_search
                else:
                    st.session_state.tracked_customer = selected_customer
                st.session_state.tracked_chasis = None
                st.rerun()
    
    # Tampilkan hasil tracking berdasarkan Chasis
    if 'tracked_chasis' in st.session_state and st.session_state.tracked_chasis:
        tracked_df = st.session_state.df_original[st.session_state.df_original['Chasis'] == st.session_state.tracked_chasis]
        
        if not tracked_df.empty:
            st.markdown(f"""
            <div class="chasis-highlight">
                <strong>🔍 HASIL TRACKING - CHASIS: {st.session_state.tracked_chasis}</strong>
            </div>
            """, unsafe_allow_html=True)
            
            tracked_row = tracked_df.iloc[0]
            
            col_info1, col_info2, col_info3 = st.columns(3)
            
            with col_info1:
                st.markdown("#### 📋 Informasi Unit")
                tgl_do = tracked_row.get('Tgl DO')
                tgl_do_str = tgl_do.strftime('%d/%m/%Y') if pd.notna(tgl_do) else 'Belum'
                
                st.markdown(f"""
                - **Nama Customer:** {tracked_row.get('Nama Customer', 'Belum')}
                - **Nama Salesman:** {tracked_row.get('Nama Salesman', 'Belum')}
                - **Jenis Pembayaran:** {tracked_row.get('Jenis Pembayaran', 'Belum')}
                - **Material Description:** {tracked_row.get('Material Description', 'Belum')}
                - **Chasis:** {tracked_row.get('Chasis', 'Belum')}
                - **NOPOL:** {tracked_row.get('NOPOL', 'Belum')}
                """)
            
            with col_info2:
                st.markdown("#### 📅 Informasi Dokumen")
                tgl_fakpol = tracked_row.get('Tgl Pengajuan Fakpol Approve')
                tgl_stnk = tracked_row.get('Tgl STNK')
                tgl_bpkb = tracked_row.get('Tgl BPKB')
                tgl_serah_bpkb = tracked_row.get('Tgl Serah Terima BPKB')
                tgl_fakpol_str = tgl_fakpol.strftime('%d/%m/%Y') if pd.notna(tgl_fakpol) else 'Belum'
                tgl_stnk_str = tgl_stnk.strftime('%d/%m/%Y') if pd.notna(tgl_stnk) else 'Belum'
                tgl_bpkb_str = tgl_bpkb.strftime('%d/%m/%Y') if pd.notna(tgl_bpkb) else 'Belum'
                tgl_serah_bpkb_str = tgl_serah_bpkb.strftime('%d/%m/%Y') if pd.notna(tgl_serah_bpkb) else 'Belum'
                
                delivery_days = calculate_delivery_time_stnk(tracked_row)
                delivery_str = f"{delivery_days} hari" if delivery_days is not None else 'Belum'
                
                st.markdown(f"""
                - **Tgl DO:** {tgl_do_str}
                - **Nama STNK:** {tracked_row.get('Nama STNK', 'Belum')}
                - **Tgl Pengajuan Fakpol:** {tgl_fakpol_str}
                - **Tgl STNK:** {tgl_stnk_str}
                - **Tgl BPKB:** {tgl_bpkb_str}
                - **Tgl Serah Terima BPKB:** {tgl_serah_bpkb_str}
                - **Waktu DO ke STNK:** {delivery_str}
                """)
            
            with col_info3:
                st.markdown("#### 💰 Informasi Pembayaran")
                tgl_do = tracked_row.get('Tgl DO')
                tgl_jatuh_tempo = tracked_row.get('Tgl Jatuh Tempo')
                
                top_days = None
                if pd.notna(tgl_do) and pd.notna(tgl_jatuh_tempo):
                    if isinstance(tgl_do, datetime) and isinstance(tgl_jatuh_tempo, datetime):
                        top_days = (tgl_jatuh_tempo - tgl_do).days
                
                top_str = f"{top_days} hari" if top_days is not None else 'Belum'
                
                tgl_kirim = tracked_row.get('Tgl Kirim Tagihan')
                tgl_pelunasan = tracked_row.get('Tgl Pelunasan')
                tgl_bj = tracked_row.get('Tgl BJ Terima Fakpol')
                
                tgl_kirim_str = tgl_kirim.strftime('%d/%m/%Y') if pd.notna(tgl_kirim) else 'Belum'
                tgl_jatuh_tempo_str = tgl_jatuh_tempo.strftime('%d/%m/%Y') if pd.notna(tgl_jatuh_tempo) else 'Belum'
                tgl_pelunasan_str = tgl_pelunasan.strftime('%d/%m/%Y') if pd.notna(tgl_pelunasan) else 'Belum'
                tgl_bj_str = tgl_bj.strftime('%d/%m/%Y') if pd.notna(tgl_bj) else 'Belum'
                
                st.markdown(f"""
                - **TOP (Tenor):** {top_str}
                - **Tgl Jatuh Tempo:** {tgl_jatuh_tempo_str}
                - **Tgl Kirim Tagihan:** {tgl_kirim_str}
                - **Tgl Pelunasan:** {tgl_pelunasan_str}
                """)
            
            st.markdown("#### 📱 Status Download MyIsuzuID")
            status_download = '✅ Selesai' if tracked_row.get('Download MyIsuzuID', False) else '❌ Belum'
            st.markdown(f"""
            <div style="background-color: #F0F7FF; padding: 1rem; border-radius: 8px; border-left: 3px solid #0055A4;">
                <strong>📱 Download MyIsuzuID</strong><br>
                {status_download}
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("#### 📌 Status TOSOL & Action TOS")
            status_tosol = '✅ Selesai' if tracked_row.get('TOSOL') and tracked_row.get('TOSOL') != '' else '❌ Belum'
            status_action = '✅ Selesai' if tracked_row.get('Action TOS') and tracked_row.get('Action TOS') != '' else '❌ Belum'
            
            st.markdown(f"""
            <div style="background-color: #F0F7FF; padding: 1rem; border-radius: 8px; border-left: 3px solid #0055A4; margin-bottom: 1rem;">
                <strong>📌 TOSOL</strong><br>
                {status_tosol} - {tracked_row.get('TOSOL', '') if tracked_row.get('TOSOL') else ''}
            </div>
            <div style="background-color: #F0F7FF; padding: 1rem; border-radius: 8px; border-left: 3px solid #0055A4;">
                <strong>⚡ Action TOS</strong><br>
                {status_action} - {tracked_row.get('Action TOS', '') if tracked_row.get('Action TOS') else ''}
            </div>
            """, unsafe_allow_html=True)

            st.markdown("#### 🕐 Timeline Service Kendaraan")

            services = [
                {'col': 'KSG I', 'name': 'KSG I (5.000 km)'},
                {'col': 'KSG II', 'name': 'KSG II (10.000 km)'},
                {'col': 'KSGX 20K', 'name': 'KSGX 20.000 km'},
                {'col': 'KSGX 30K', 'name': 'KSGX 30.000 km'},
                {'col': 'KSGX 40K', 'name': 'KSGX 40.000 km'}
            ]

            for service in services:
                value = tracked_row.get(service['col'])
                
                if pd.notna(value) and value is not None:
                    status_text = "✅ Selesai"
                    date_text = f" | Tanggal: {value.strftime('%d/%m/%Y') if hasattr(value, 'strftime') else value}"
                    icon = "✅"
                else:
                    status_text = "⏳ Belum"
                    date_text = ""
                    icon = "⏳"
                
                col1, col2 = st.columns([0.9, 0.1])
                with col1:
                    st.markdown(f"🔧 **{service['name']}** - {status_text}{date_text}")
                with col2:
                    st.markdown(icon)

            st.markdown("---")
        else:
            st.warning(f"Tidak ditemukan data dengan chasis: {st.session_state.tracked_chasis}")
            st.session_state.tracked_chasis = None
    
    # Tampilkan hasil tracking berdasarkan Customer
    if 'tracked_customer' in st.session_state and st.session_state.tracked_customer:
        search_term = st.session_state.tracked_customer.lower().strip()
        tracked_df = st.session_state.df_original[
            st.session_state.df_original['Nama Customer'].astype(str).str.lower().str.contains(search_term, na=False)
        ]
        
        if not tracked_df.empty:
            st.markdown(f"""
            <div class="chasis-highlight">
                <strong>👤 HASIL TRACKING - CUSTOMER: {st.session_state.tracked_customer}</strong>
                <br><small>Menampilkan {len(tracked_df)} unit kendaraan</small>
            </div>
            """, unsafe_allow_html=True)
            
            # ========== DAFTAR UNIT KENDARAAN DENGAN COLUMN_CONFIG ==========
            st.markdown("#### 📋 Daftar Unit Kendaraan (DATA TRACKING UNIT)")
            
            # Kolom-kolom yang akan ditampilkan sesuai dengan column_config
            display_columns = [
                'No', 'Tgl DO', 'Nama Customer', 'Nama Salesman', 'Chasis', 
                'Material Description', 'Jenis Pembayaran', 'Nama STNK', 'NOPOL',
                'Tgl STNK', 'Tgl BPKB', 'Tgl Serah Terima BPKB', 'Tgl Kirim Tagihan',
                'Tgl Jatuh Tempo', 'Tgl Pelunasan', 'Tgl Pengajuan Fakpol Approve',
                'Tgl BJ Terima Fakpol', 'Download MyIsuzuID', 'TOSOL', 'Action TOS',
                'KSG I', 'KSG II', 'KSGX 20K', 'KSGX 30K', 'KSGX 40K'
            ]
            
            # Filter kolom yang tersedia di dataframe
            available_columns = [col for col in display_columns if col in tracked_df.columns]
            
            # Buat dataframe untuk ditampilkan
            display_unit_df = tracked_df[available_columns].copy()
            
            # Konversi tipe data untuk column_config
            # No column
            if 'No' in display_unit_df.columns:
                display_unit_df['No'] = pd.to_numeric(display_unit_df['No'], errors='coerce')
            
            # Kolom tanggal
            date_columns = ['Tgl DO', 'Tgl STNK', 'Tgl BPKB', 'Tgl Serah Terima BPKB', 
                           'Tgl Kirim Tagihan', 'Tgl Jatuh Tempo', 'Tgl Pelunasan',
                           'Tgl Pengajuan Fakpol Approve', 'Tgl BJ Terima Fakpol']
            
            for col in date_columns:
                if col in display_unit_df.columns:
                    display_unit_df[col] = pd.to_datetime(display_unit_df[col], errors='coerce')
            
            # Kolom boolean/status
            if 'Download MyIsuzuID' in display_unit_df.columns:
                display_unit_df['Download MyIsuzuID'] = display_unit_df['Download MyIsuzuID'].apply(
                    lambda x: '✅ Selesai' if x == True or x == 1 or str(x).lower() == 'true' else '❌ Belum'
                )
            
            # Kolom TOSOL
            if 'TOSOL' in display_unit_df.columns:
                display_unit_df['TOSOL'] = display_unit_df['TOSOL'].apply(
                    lambda x: '✅ Selesai' if x and str(x).strip() != '' and str(x).lower() not in ['nan', 'none'] else '❌ Belum'
                )
            
            # Kolom Action TOS
            if 'Action TOS' in display_unit_df.columns:
                display_unit_df['Action TOS'] = display_unit_df['Action TOS'].apply(
                    lambda x: '✅ Selesai' if x and str(x).strip() != '' and str(x).lower() not in ['nan', 'none'] else '❌ Belum'
                )
            
            # Column configuration
            column_config = {
                "No": st.column_config.NumberColumn("No", format="%d"),
                "Tgl DO": st.column_config.DateColumn("Tgl DO", format="DD/MM/YYYY"),
                "Nama Customer": st.column_config.TextColumn("Nama Customer"),
                "Nama Salesman": st.column_config.TextColumn("Nama Salesman"),
                "Chasis": st.column_config.TextColumn("Chasis", help="Primary Key - Nomor chasis kendaraan"),
                "Material Description": st.column_config.TextColumn("Material Description"),
                "Jenis Pembayaran": st.column_config.TextColumn("Jenis Pembayaran"),
                "Nama STNK": st.column_config.TextColumn("Nama STNK"),
                "NOPOL": st.column_config.TextColumn("NOPOL"),
                "Tgl STNK": st.column_config.DateColumn("Tgl STNK", format="DD/MM/YYYY"),
                "Tgl BPKB": st.column_config.DateColumn("Tgl BPKB", format="DD/MM/YYYY"),
                "Tgl Serah Terima BPKB": st.column_config.DateColumn("Tgl Serah Terima BPKB", format="DD/MM/YYYY"),
                "Tgl Kirim Tagihan": st.column_config.DateColumn("Tgl Kirim Tagihan", format="DD/MM/YYYY"),
                "Tgl Jatuh Tempo": st.column_config.DateColumn("Tgl Jatuh Tempo", format="DD/MM/YYYY"),
                "Tgl Pelunasan": st.column_config.DateColumn("Tgl Pelunasan", format="DD/MM/YYYY"),
                "Tgl Pengajuan Fakpol Approve": st.column_config.DateColumn("Tgl Pengajuan Fakpol", format="DD/MM/YYYY"),
                "Tgl BJ Terima Fakpol": st.column_config.DateColumn("Tgl BJ Terima Fakpol", format="DD/MM/YYYY"),
                "Download MyIsuzuID": st.column_config.TextColumn("Download MyIsuzuID"),
                "TOSOL": st.column_config.TextColumn("TOSOL"),
                "Action TOS": st.column_config.TextColumn("Action TOS"),
                "KSG I": st.column_config.TextColumn("KSG I (5K)"),
                "KSG II": st.column_config.TextColumn("KSG II (10K)"),
                "KSGX 20K": st.column_config.TextColumn("KSGX 20K"),
                "KSGX 30K": st.column_config.TextColumn("KSGX 30K"),
                "KSGX 40K": st.column_config.TextColumn("KSGX 40K")
            }
            
            # Filter column_config hanya untuk kolom yang tersedia
            filtered_column_config = {k: v for k, v in column_config.items() if k in display_unit_df.columns}
            
            # Tampilkan dataframe dengan column_config
            st.dataframe(
                display_unit_df,
                use_container_width=True,
                hide_index=True,
                column_config=filtered_column_config
            )
            
            # Tombol download
            csv_download = tracked_df[available_columns].to_csv(index=False, encoding='utf8')
            st.download_button(
                label="📥 Download Data Tracking Unit (CSV)",
                data=csv_download,
                file_name=f"data_tracking_unit_{st.session_state.tracked_customer.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                help="Download data tracking unit customer ini",
                use_container_width=True
            )
            
            st.markdown("---")
            
            # ========== TRACKING PER CHASIS UNTUK CUSTOMER ==========
            st.markdown("#### 🔍 Tracking Per Unit Kendaraan")
            st.markdown("Pilih salah satu chasis di bawah untuk melihat detail lengkapnya:")
            
            customer_chasis_list = tracked_df['Chasis'].dropna().unique().tolist()
            customer_chasis_list = [x for x in customer_chasis_list if x and x != '']
            customer_chasis_list.sort()
            
            selected_chasis_detail = st.selectbox(
                "Pilih Nomor Chasis untuk melihat detail lengkap:",
                options=[""] + customer_chasis_list,
                format_func=lambda x: f"🔍 {x}" if x else "--- Pilih Chasis ---",
                key="customer_chasis_select"
            )
            
            if selected_chasis_detail:
                detail_row = tracked_df[tracked_df['Chasis'] == selected_chasis_detail].iloc[0]
                
                st.markdown(f"""
                <div class="chasis-highlight" style="margin-top: 1rem;">
                    <strong>🔍 DETAIL LENGKAP - CHASIS: {selected_chasis_detail}</strong>
                </div>
                """, unsafe_allow_html=True)
                
                col_d1, col_d2, col_d3 = st.columns(3)
                
                with col_d1:
                    st.markdown("#### 📋 Informasi Unit")
                    tgl_do_detail = detail_row.get('Tgl DO')
                    tgl_do_str_detail = tgl_do_detail.strftime('%d/%m/%Y') if pd.notna(tgl_do_detail) else 'Belum'
                    
                    st.markdown(f"""
                    - **Nama Customer:** {detail_row.get('Nama Customer', 'Belum')}
                    - **Nama Salesman:** {detail_row.get('Nama Salesman', 'Belum')}
                    - **Jenis Pembayaran:** {detail_row.get('Jenis Pembayaran', 'Belum')}
                    - **Material Description:** {detail_row.get('Material Description', 'Belum')}
                    - **Chasis:** {detail_row.get('Chasis', 'Belum')}
                    - **NOPOL:** {detail_row.get('NOPOL', 'Belum')}
                    """)
                
                with col_d2:
                    st.markdown("#### 📅 Informasi Dokumen")
                    tgl_fakpol_detail = detail_row.get('Tgl Pengajuan Fakpol Approve')
                    tgl_stnk_detail = detail_row.get('Tgl STNK')
                    tgl_bpkb_detail = detail_row.get('Tgl BPKB')
                    tgl_serah_bpkb_detail = detail_row.get('Tgl Serah Terima BPKB')
                    
                    tgl_fakpol_str_detail = tgl_fakpol_detail.strftime('%d/%m/%Y') if pd.notna(tgl_fakpol_detail) else 'Belum'
                    tgl_stnk_str_detail = tgl_stnk_detail.strftime('%d/%m/%Y') if pd.notna(tgl_stnk_detail) else 'Belum'
                    tgl_bpkb_str_detail = tgl_bpkb_detail.strftime('%d/%m/%Y') if pd.notna(tgl_bpkb_detail) else 'Belum'
                    tgl_serah_bpkb_str_detail = tgl_serah_bpkb_detail.strftime('%d/%m/%Y') if pd.notna(tgl_serah_bpkb_detail) else 'Belum'
                    
                    delivery_days_detail = calculate_delivery_time_stnk(detail_row)
                    delivery_str_detail = f"{delivery_days_detail} hari" if delivery_days_detail is not None else 'Belum'
                    
                    st.markdown(f"""
                    - **Tgl DO:** {tgl_do_str_detail}
                    - **Nama STNK:** {detail_row.get('Nama STNK', 'Belum')}
                    - **Tgl Pengajuan Fakpol:** {tgl_fakpol_str_detail}
                    - **Tgl STNK:** {tgl_stnk_str_detail}
                    - **Tgl BPKB:** {tgl_bpkb_str_detail}
                    - **Tgl Serah Terima BPKB:** {tgl_serah_bpkb_str_detail}
                    - **Waktu DO ke STNK:** {delivery_str_detail}
                    """)
                
                with col_d3:
                    st.markdown("#### 💰 Informasi Pembayaran")
                    tgl_do_detail = detail_row.get('Tgl DO')
                    tgl_jatuh_tempo_detail = detail_row.get('Tgl Jatuh Tempo')
                    
                    top_days_detail = None
                    if pd.notna(tgl_do_detail) and pd.notna(tgl_jatuh_tempo_detail):
                        if isinstance(tgl_do_detail, datetime) and isinstance(tgl_jatuh_tempo_detail, datetime):
                            top_days_detail = (tgl_jatuh_tempo_detail - tgl_do_detail).days
                    
                    top_str_detail = f"{top_days_detail} hari" if top_days_detail is not None else 'Belum'
                    
                    tgl_kirim_detail = detail_row.get('Tgl Kirim Tagihan')
                    tgl_pelunasan_detail = detail_row.get('Tgl Pelunasan')
                    tgl_bj_detail = detail_row.get('Tgl BJ Terima Fakpol')
                    
                    tgl_kirim_str_detail = tgl_kirim_detail.strftime('%d/%m/%Y') if pd.notna(tgl_kirim_detail) else 'Belum'
                    tgl_jatuh_tempo_str_detail = tgl_jatuh_tempo_detail.strftime('%d/%m/%Y') if pd.notna(tgl_jatuh_tempo_detail) else 'Belum'
                    tgl_pelunasan_str_detail = tgl_pelunasan_detail.strftime('%d/%m/%Y') if pd.notna(tgl_pelunasan_detail) else 'Belum'
                    
                    st.markdown(f"""
                    - **TOP (Tenor):** {top_str_detail}
                    - **Tgl Jatuh Tempo:** {tgl_jatuh_tempo_str_detail}
                    - **Tgl Kirim Tagihan:** {tgl_kirim_str_detail}
                    - **Tgl Pelunasan:** {tgl_pelunasan_str_detail}
                    """)
                
                st.markdown("#### 📱 Status Download MyIsuzuID")
                status_download_detail = '✅ Selesai' if detail_row.get('Download MyIsuzuID', False) else '❌ Belum'
                st.markdown(f"""
                <div style="background-color: #F0F7FF; padding: 1rem; border-radius: 8px; border-left: 3px solid #0055A4;">
                    <strong>📱 Download MyIsuzuID</strong><br>
                    {status_download_detail}
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("#### 📌 Status TOSOL & Action TOS")
                status_tosol_detail = '✅ Selesai' if detail_row.get('TOSOL') and detail_row.get('TOSOL') != '' else '❌ Belum'
                status_action_detail = '✅ Selesai' if detail_row.get('Action TOS') and detail_row.get('Action TOS') != '' else '❌ Belum'
                
                st.markdown(f"""
                <div style="background-color: #F0F7FF; padding: 1rem; border-radius: 8px; border-left: 3px solid #0055A4; margin-bottom: 1rem;">
                    <strong>📌 TOSOL</strong><br>
                    {status_tosol_detail} - {detail_row.get('TOSOL', '') if detail_row.get('TOSOL') else ''}
                </div>
                <div style="background-color: #F0F7FF; padding: 1rem; border-radius: 8px; border-left: 3px solid #0055A4;">
                    <strong>⚡ Action TOS</strong><br>
                    {status_action_detail} - {detail_row.get('Action TOS', '') if detail_row.get('Action TOS') else ''}
                </div>
                """, unsafe_allow_html=True)

                st.markdown("#### 🕐 Timeline Service Kendaraan")
                
                services = [
                    {'col': 'KSG I', 'name': 'KSG I (5.000 km)'},
                    {'col': 'KSG II', 'name': 'KSG II (10.000 km)'},
                    {'col': 'KSGX 20K', 'name': 'KSGX 20.000 km'},
                    {'col': 'KSGX 30K', 'name': 'KSGX 30.000 km'},
                    {'col': 'KSGX 40K', 'name': 'KSGX 40.000 km'}
                ]

                for service in services:
                    value = detail_row.get(service['col'])
                    
                    if pd.notna(value) and value is not None:
                        status_text = "✅ Selesai"
                        date_text = f" | Tanggal: {value.strftime('%d/%m/%Y') if hasattr(value, 'strftime') else value}"
                        icon = "✅"
                    else:
                        status_text = "⏳ Belum"
                        date_text = ""
                        icon = "⏳"
                    
                    col1, col2 = st.columns([0.9, 0.1])
                    with col1:
                        st.markdown(f"🔧 **{service['name']}** - {status_text}{date_text}")
                    with col2:
                        st.markdown(icon)
                
                st.markdown("---")
        else:
            st.warning(f"Tidak ditemukan data dengan nama customer: {st.session_state.tracked_customer}")
            st.session_state.tracked_customer = None
else:
    if 'Chasis' not in st.session_state.df_original.columns:
        st.warning("Kolom Chasis tidak ditemukan dalam data. Tracking per chasis tidak dapat dilakukan.")
    else:
        st.info("Tidak ada data yang tersedia untuk tracking kendaraan.")

# ========== PERIODE ANALISIS ==========
st.markdown('<div class="section-header">📅 PERIODE ANALISIS BASED ON DO</div>', unsafe_allow_html=True)

col_periode1, col_periode2, col_periode3 = st.columns([2, 2, 1])

with col_periode1:
    if not st.session_state.df_original.empty and 'Tgl DO' in st.session_state.df_original.columns:
        valid_dates = st.session_state.df_original['Tgl DO'].dropna()
        if not valid_dates.empty:
            default_start = valid_dates.min().date() if isinstance(valid_dates.min(), datetime) else datetime.now().date()
            default_end = valid_dates.max().date() if isinstance(valid_dates.max(), datetime) else datetime.now().date()
        else:
            default_start = datetime.now().date()
            default_end = datetime.now().date()
    else:
        default_start = datetime.now().date()
        default_end = datetime.now().date()
    
    periode_start = st.date_input(
        "📅 Tanggal Mulai:",
        value=st.session_state.periode_start if st.session_state.periode_start else default_start,
        format="DD/MM/YYYY",
        key="periode_start_input"
    )
    st.session_state.periode_start = periode_start

with col_periode2:
    periode_end = st.date_input(
        "📅 Tanggal Selesai:",
        value=st.session_state.periode_end if st.session_state.periode_end else default_end,
        format="DD/MM/YYYY",
        key="periode_end_input"
    )
    st.session_state.periode_end = periode_end

with col_periode3:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("✅ **TERAPKAN**", use_container_width=True, type="primary"):
        apply_period()
        st.rerun()

# Tampilkan periode yang sedang aktif
if st.session_state.periode_applied:
    st.markdown(f"""
    <div style="background-color: #E8F5E9; padding: 0.75rem; border-radius: 6px; margin-bottom: 1rem; border-left: 3px solid #2E7D32;">
        <div style="display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 1.2rem;">✅</span>
            <div>
                <p style="color: #1E2A3A; margin: 0; font-weight: 500;">
                    PERIODE AKTIF: {st.session_state.periode_label}
                </p>
                <p style="color: #1E2A3A; margin: 0; font-size: 0.9rem;">
                    Total Data: {len(st.session_state.df_periode)} unit
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    if st.session_state.df_periode.empty and not st.session_state.df_original.empty:
        st.session_state.df_periode = st.session_state.df_original.copy()
        st.session_state.periode_label = "Semua Data"
    
    st.markdown(f"""
    <div style="background-color: #F0F7FF; padding: 0.75rem; border-radius: 6px; margin-bottom: 1rem; border-left: 3px solid #0055A4;">
        <div style="display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 1.2rem;">ℹ️</span>
            <div>
                <p style="color: #1E2A3A; margin: 0; font-weight: 500;">
                    PERIODE SAAT INI: {st.session_state.periode_label}
                </p>
                <p style="color: #1E2A3A; margin: 0; font-size: 0.9rem;">
                    Total Data: {len(st.session_state.df_periode)} unit (Klik "Terapkan" untuk mengubah)
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Gunakan df_periode dari session state untuk semua analisis
df_periode = st.session_state.df_periode
periode_label = st.session_state.periode_label

# ========== DATA VIEWER (READ-ONLY) ==========
if not df_periode.empty:
    column_order = [
        'No', 'Tgl DO', 'Nama Customer', 'Nama Salesman', 'Chasis', 
        'Material Description', 'Jenis Pembayaran', 'Nama STNK', 'NOPOL',
        'Tgl STNK', 'Tgl BPKB', 'Tgl Serah Terima BPKB', 'Tgl Kirim Tagihan', 'Tgl Jatuh Tempo', 
        'Tgl Pelunasan', 'Tgl Pengajuan Fakpol Approve', 'Tgl BJ Terima Fakpol',
        'Download MyIsuzuID', 'TOSOL', 'Action TOS', 'KSG I', 'KSG II', 'KSGX 20K', 'KSGX 30K', 'KSGX 40K'
    ]
    
    available_columns = [col for col in column_order if col in df_periode.columns]
    display_df = df_periode[available_columns].copy()
    
    date_columns = ['Tgl DO', 'Tgl STNK', 'Tgl BPKB', 'Tgl Serah Terima BPKB', 'Tgl Kirim Tagihan', 
                   'Tgl Jatuh Tempo', 'Tgl Pelunasan', 'Tgl Pengajuan Fakpol Approve',
                   'Tgl BJ Terima Fakpol', 'KSG I', 'KSG II', 'KSGX 20K', 'KSGX 30K', 'KSGX 40K']
    
    for col in date_columns:
        if col in display_df.columns:
            display_df[col] = pd.to_datetime(display_df[col], errors='coerce')
            display_df[col] = display_df[col].dt.strftime('%d/%m/%Y')
            display_df[col] = display_df[col].fillna('Belum')
    
    if 'Download MyIsuzuID' in display_df.columns:
        display_df['Download MyIsuzuID'] = display_df['Download MyIsuzuID'].map(
            {True: '✅ Selesai', False: '❌ Belum', None: '❌ Belum'}
        )
    
    if 'TOSOL' in display_df.columns:
        display_df['TOSOL'] = display_df['TOSOL'].apply(lambda x: '✅ Selesai' if x and x != '' else '❌ Belum')
    
    if 'Action TOS' in display_df.columns:
        display_df['Action TOS'] = display_df['Action TOS'].apply(lambda x: '✅ Selesai' if x and x != '' else '❌ Belum')
    
    st.markdown(f'<div class="section-header">📋 DATA TRACKING UNIT</div>', unsafe_allow_html=True)
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "No": st.column_config.NumberColumn("No", format="%d"),
            "Tgl DO": st.column_config.TextColumn("Tgl DO"),
            "Nama Customer": st.column_config.TextColumn("Nama Customer"),
            "Nama Salesman": st.column_config.TextColumn("Nama Salesman"),
            "Chasis": st.column_config.TextColumn("Chasis", help="Primary Key - Nomor chasis kendaraan"),
            "Material Description": st.column_config.TextColumn("Material Description"),
            "Jenis Pembayaran": st.column_config.TextColumn("Jenis Pembayaran"),
            "Nama STNK": st.column_config.TextColumn("Nama STNK"),
            "NOPOL": st.column_config.TextColumn("NOPOL"),
            "Tgl STNK": st.column_config.TextColumn("Tgl STNK"),
            "Tgl BPKB": st.column_config.TextColumn("Tgl BPKB"),
            "Tgl Serah Terima BPKB": st.column_config.TextColumn("Tgl Serah Terima BPKB"),
            "Tgl Kirim Tagihan": st.column_config.TextColumn("Tgl Kirim Tagihan"),
            "Tgl Jatuh Tempo": st.column_config.TextColumn("Tgl Jatuh Tempo"),
            "Tgl Pelunasan": st.column_config.TextColumn("Tgl Pelunasan"),
            "Tgl Pengajuan Fakpol Approve": st.column_config.TextColumn("Tgl Pengajuan Fakpol"),
            "Tgl BJ Terima Fakpol": st.column_config.TextColumn("Tgl BJ Terima Fakpol"),
            "Download MyIsuzuID": st.column_config.TextColumn("Download MyIsuzuID"),
            "TOSOL": st.column_config.TextColumn("TOSOL"),
            "Action TOS": st.column_config.TextColumn("Action TOS"),
            "KSG I": st.column_config.TextColumn("KSG I (5K)"),
            "KSG II": st.column_config.TextColumn("KSG II (10K)"),
            "KSGX 20K": st.column_config.TextColumn("KSGX 20K"),
            "KSGX 30K": st.column_config.TextColumn("KSGX 30K"),
            "KSGX 40K": st.column_config.TextColumn("KSGX 40K")
        }
    )
    
    st.divider()
    
    df_download = df_periode[available_columns].copy()
    for col in date_columns:
        if col in df_download.columns:
            df_download[col] = pd.to_datetime(df_download[col], errors='coerce')
            df_download[col] = df_download[col].dt.strftime('%d/%m/%Y')
            df_download[col] = df_download[col].fillna('Belum')
    
    if 'Download MyIsuzuID' in df_download.columns:
        df_download['Download MyIsuzuID'] = df_download['Download MyIsuzuID'].map(
            {True: 'Selesai', False: 'Belum', None: 'Belum'}
        )
    
    csv_data = df_download.to_csv(index=False, encoding='utf8')
    st.download_button(
        label="📥 Download Backup (CSV)",
        data=csv_data,
        file_name=f"isuzu_tracking_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
        help="Download data sebagai CSV untuk backup"
    )
else:
    st.info("Tidak ada data yang tersedia untuk ditampilkan pada periode ini.")

# ========== TREND PENJUALAN UNIT ==========
st.markdown('<div class="section-header">📈 TREND ANALISIS</div>', unsafe_allow_html=True)

if not df_periode.empty:
    date_columns_available = ['Tgl DO', 'Tgl STNK', 'Tgl BPKB', 'Tgl Serah Terima BPKB', 'Tgl Kirim Tagihan', 
                             'Tgl Jatuh Tempo', 'Tgl Pelunasan', 'Tgl Pengajuan Fakpol Approve',
                             'Tgl BJ Terima Fakpol', 'KSG I', 'KSG II', 'KSGX 20K', 'KSGX 30K', 'KSGX 40K']
    
    available_date_columns = [col for col in date_columns_available if col in df_periode.columns]
    
    if available_date_columns:
        col_trend1, col_trend2 = st.columns([3, 1])
        
        with col_trend1:
            default_index = 0
            if 'Tgl DO' in available_date_columns:
                default_index = available_date_columns.index('Tgl DO')
            
            selected_trend_column = st.selectbox(
                "📊 Pilih untuk Trend Analysis:",
                options=available_date_columns,
                index=default_index,
                key="trend_column_selector_main",  # PERUBAHAN: key unik
                help="Pilih kolom tanggal yang ingin dianalisis trend-nya"
            )
            st.session_state.selected_trend_column = selected_trend_column

        with col_trend2:
            pass
        
    df_trend = df_periode.copy()
    trend_period_label = periode_label

    if not df_trend.empty and len(df_trend) > 0:
        df_trend = df_trend.copy()
        df_trend[selected_trend_column] = pd.to_datetime(df_trend[selected_trend_column], errors='coerce')
        df_trend = df_trend.dropna(subset=[selected_trend_column])
        
        if len(df_trend) > 0:
            df_trend['Periode'] = df_trend[selected_trend_column].dt.date
            trend_counts = df_trend.groupby('Periode').size().reset_index(name='Jumlah')
            trend_counts = trend_counts.sort_values('Periode')
            
            if len(trend_counts) > 0:
                st.info(f"📊 **Analisis Trend:** {selected_trend_column} | **Periode: {periode_label}** | **Total Data:** {len(df_trend)} | **Rentang:** {trend_counts['Periode'].iloc[0]} s/d {trend_counts['Periode'].iloc[-1]}")
                
                fig_trend = go.Figure()
                
                fig_trend.add_trace(go.Scatter(
                    x=trend_counts['Periode'],
                    y=trend_counts['Jumlah'],
                    mode='lines+markers',
                    name=f'Trend {selected_trend_column}',
                    line=dict(color=ASTRA_BLUE, width=3),
                    marker=dict(size=8, color=ASTRA_BLUE),
                    fill='tozeroy',
                    fillcolor=f'rgba(0, 85, 164, 0.1)'
                ))
                
                fig_trend.update_layout(
                    xaxis_title="Tanggal",
                    yaxis_title="Jumlah",
                    hovermode='x unified',
                    height=450,
                    showlegend=True,
                    template="plotly_white",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    xaxis={'tickangle': 45}
                )
                
                if len(trend_counts) > 0:
                    max_idx = trend_counts['Jumlah'].idxmax()
                    fig_trend.add_annotation(
                        x=trend_counts.loc[max_idx, 'Periode'],
                        y=trend_counts.loc[max_idx, 'Jumlah'],
                        text=f"Puncak: {trend_counts.loc[max_idx, 'Jumlah']}",
                        showarrow=True,
                        arrowhead=2,
                        arrowsize=1,
                        arrowwidth=2,
                        arrowcolor=ACCENT_RED,
                        ax=0,
                        ay=-40
                    )
                
                st.plotly_chart(fig_trend, use_container_width=True, key=f"trend_chart_{selected_trend_column}_{hash(str(df_trend.shape))}_{datetime.now().timestamp()}")                
            else:
                st.warning(f"Tidak ada data untuk periode {periode_label}")
        else:
            st.warning(f"Tidak ada data dengan {selected_trend_column} yang valid untuk periode {periode_label}")
    else:
        st.info("Tidak ada kolom tanggal yang tersedia untuk analisis trend.")

# ========== PARETO CHART - ANALISIS GAP WAKTU PROSES ==========
st.divider()
st.markdown('<div class="section-header">⏱️ ANALISIS GAP WAKTU PROSES</div>', unsafe_allow_html=True)

if not df_periode.empty:
    pareto_analyses = {
        'DO ke STNK': {'start': 'Tgl DO', 'end': 'Tgl STNK', 'title': 'DO → STNK'},
        'STNK ke BPKB': {'start': 'Tgl STNK', 'end': 'Tgl BPKB', 'title': 'STNK → BPKB'},
        'BPKB ke Serah Terima BPKB': {'start': 'Tgl BPKB', 'end': 'Tgl Serah Terima BPKB', 'title': 'BPKB → Serah'},
        'DO ke Jatuh Tempo': {'start': 'Tgl DO', 'end': 'Tgl Jatuh Tempo', 'title': 'DO → JT'},
        'DO ke Pelunasan': {'start': 'Tgl DO', 'end': 'Tgl Pelunasan', 'title': 'DO → Lunas'},
        'Tgl Kirim Tagihan ke Tgl Jatuh Tempo': {'start': 'Tgl Kirim Tagihan', 'end': 'Tgl Jatuh Tempo', 'title': 'Kirim → JT'},
        'Tgl Jatuh Tempo ke Tgl Pelunasan': {'start': 'Tgl Jatuh Tempo', 'end': 'Tgl Pelunasan', 'title': 'JT → Lunas'},
        'Tgl Pengajuan Fakpol ke Tgl BJ Terima Fakpol': {'start': 'Tgl Pengajuan Fakpol Approve', 'end': 'Tgl BJ Terima Fakpol', 'title': 'Fakpol → BJ'},
        'STNK ke KSG I': {'start': 'Tgl STNK', 'end': 'KSG I', 'title': 'STNK → KSG I'},
        'KSG I ke KSG II': {'start': 'KSG I', 'end': 'KSG II', 'title': 'KSG I → II'},
        'KSG II ke KSGX 20K': {'start': 'KSG II', 'end': 'KSGX 20K', 'title': 'KSG II → 20K'},
        'KSGX 20K ke KSGX 30K': {'start': 'KSGX 20K', 'end': 'KSGX 30K', 'title': '20K → 30K'},
        'KSGX 30K ke KSGX 40K': {'start': 'KSGX 30K', 'end': 'KSGX 40K', 'title': '30K → 40K'}
    }
    
    available_analyses = {}
    for key, analysis in pareto_analyses.items():
        if analysis['start'] in df_periode.columns and analysis['end'] in df_periode.columns:
            available_analyses[key] = analysis
    
    if available_analyses:
        col_pareto1, col_pareto2 = st.columns([3, 1])
        
        with col_pareto1:
            selected_pareto = st.selectbox(
                "📊 Pilih Analisis Gap Waktu:",
                options=list(available_analyses.keys()),
                index=0,
                key="pareto_analysis_selector_main"  # PERUBAHAN: key unik
            )
            st.session_state.selected_pareto_analysis = selected_pareto
        
        with col_pareto2:
            pass
        
        df_pareto = df_periode.copy()
        pareto_period_label = periode_label
        
        selected_analysis = available_analyses[selected_pareto]
        start_col = selected_analysis['start']
        end_col = selected_analysis['end']
        title = selected_analysis['title']
        
        pareto_df, diff_series, total_data = create_pareto_chart(df_pareto, start_col, end_col, title)
        
        if pareto_df is not None and total_data > 0:
            st.info(f"📊 **Analisis:** {selected_pareto} | **Periode: {periode_label}** | **Total Data:** {total_data} unit")
            
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                avg_days = diff_series.mean()
                st.metric("⏱️ Rata-rata", f"{avg_days:.1f} hari")
            with col_m2:
                max_days = diff_series.max()
                st.metric("🐢 Terlama", f"{max_days:.0f} hari")
            with col_m3:
                min_days = diff_series.min()
                st.metric("⚡ Tercepat", f"{min_days:.0f} hari")
            
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            # Buat warna gradasi dari ASTRA_BLUE ke DARK_BLUE
            n_bars = len(pareto_df)
            bar_colors = []
            for i in range(n_bars):
                # Interpolasi warna dari ASTRA_BLUE ke DARK_BLUE
                ratio = i / max(n_bars - 1, 1)
                r = int(0 + (0 - 0) * ratio)  # Tidak ada perubahan R
                g = int(85 + (51 - 85) * ratio)  # Hijau: 85 -> 51
                b = int(164 + (102 - 164) * ratio)  # Biru: 164 -> 102
                bar_colors.append(f'rgb({r}, {g}, {b})')
            
            # Bar chart dengan gradasi warna
            fig.add_trace(
                go.Bar(
                    x=pareto_df['Kategori'],
                    y=pareto_df['Frekuensi'],
                    name="Frekuensi",
                    marker=dict(
                        color=bar_colors,
                        line=dict(width=1, color=DARK_BLUE),
                        opacity=0.9
                    ),
                    text=pareto_df['Frekuensi'],
                    textposition='outside',
                    textfont=dict(size=13, weight='bold', color=DARK_BLUE),
                    hovertemplate='<b>%{x}</b><br>Frekuensi: %{y} unit<extra></extra>'
                ),
                secondary_y=False,
            )
            
            # Line chart untuk kumulatif
            fig.add_trace(
                go.Scatter(
                    x=pareto_df['Kategori'],
                    y=pareto_df['Kumulatif'],
                    name="Kumulatif %",
                    mode='lines+markers',
                    line=dict(color=ACCENT_RED, width=3),
                    marker=dict(size=10, color=ACCENT_RED, symbol='circle', 
                                line=dict(width=2, color='white')),
                    text=[f"{v:.1f}%" for v in pareto_df['Kumulatif']],
                    textposition='top center',
                    textfont=dict(size=12, weight='bold', color=ACCENT_RED),
                    hovertemplate='<b>%{x}</b><br>Kumulatif: %{y:.1f}%<extra></extra>'
                ),
                secondary_y=True,
            )
            
            # Garis referensi 80%
            fig.add_hline(
                y=80, 
                line_dash="dash", 
                line_color="#888888", 
                opacity=0.5,
                secondary_y=True
            )
            
            fig.update_layout(
                title=dict(
                    text=f"<b>📊 Pareto Chart - {title}</b><br>",
                    font=dict(size=15, color=TEXT_DARK),
                    x=0.5,
                    xanchor='center'
                ),
                xaxis_title=dict(text="<b>Kategori Waktu</b>", font=dict(size=13, color=TEXT_DARK)),
                yaxis_title=dict(text="<b>Frekuensi (unit)</b>", font=dict(size=13, color=TEXT_DARK)),
                height=480,
                template="plotly_white",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(
                    tickangle=45, 
                    tickfont=dict(size=12, color=TEXT_DARK),
                    title_font=dict(size=13),
                    gridcolor='#E5E5E5',
                    gridwidth=0.5
                ),
                yaxis=dict(
                    tickfont=dict(size=12, color=TEXT_DARK),
                    title_font=dict(size=13),
                    gridcolor='#E5E5E5',
                    gridwidth=0.5,
                    zeroline=True,
                    zerolinecolor='#E5E5E5'
                ),
                hovermode='x unified',
                showlegend=True,
                legend=dict(
                    font=dict(size=12),
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    bgcolor='rgba(255,255,255,0.9)',
                    bordercolor='#E5E5E5',
                    borderwidth=1
                ),
                bargap=0.15
            )
            
            fig.update_yaxes(
                title_text="<b>Persentase Kumulatif (%)</b>", 
                secondary_y=True, 
                range=[0, 110],
                tickfont=dict(size=12, color=TEXT_DARK),
                title_font=dict(size=13),
                gridcolor='#E5E5E5',
                gridwidth=0.5
            )
            
            st.plotly_chart(fig, use_container_width=True, key=f"pareto_chart_{selected_pareto}_{total_data}_{datetime.now().timestamp()}")
            
            with st.expander(f"📋 Top 10 {selected_pareto} Terlama"):
                top_slow_data = []
                for idx, row in df_pareto.iterrows():
                    diff = calculate_time_difference(row, start_col, end_col)
                    if diff is not None and diff >= 0:
                        top_slow_data.append({
                            'Chasis': row.get('Chasis', 'Belum'),
                            'Customer': row.get('Nama Customer', 'Belum'),
                            'Salesman': row.get('Nama Salesman', 'Belum'),
                            'Tgl Mulai': row.get(start_col, 'Belum'),
                            'Tgl Selesai': row.get(end_col, 'Belum'),
                            'Selisih (hari)': diff
                        })
                
                if top_slow_data:
                    top_slow_df = pd.DataFrame(top_slow_data)
                    top_slow_df = top_slow_df.nlargest(10, 'Selisih (hari)')
                    
                    if 'Tgl Mulai' in top_slow_df.columns:
                        top_slow_df['Tgl Mulai'] = pd.to_datetime(top_slow_df['Tgl Mulai']).dt.strftime('%d/%m/%Y')
                        top_slow_df['Tgl Mulai'] = top_slow_df['Tgl Mulai'].fillna('Belum')
                    if 'Tgl Selesai' in top_slow_df.columns:
                        top_slow_df['Tgl Selesai'] = pd.to_datetime(top_slow_df['Tgl Selesai']).dt.strftime('%d/%m/%Y')
                        top_slow_df['Tgl Selesai'] = top_slow_df['Tgl Selesai'].fillna('Belum')
                    
                    st.dataframe(top_slow_df, use_container_width=True, hide_index=True)
        else:
            st.warning(f"Tidak ada data yang valid untuk analisis {selected_pareto} pada periode {periode_label}")
    else:
        st.info("Tidak ada kolom yang tersedia untuk analisis Pareto")
else:
    st.info("Data tidak tersedia untuk analisis Pareto")

# ========== BAGIAN: KELENGKAPAN DOKUMEN (STNK & BPKB OTOMATIS DARI TANGGAL) ==========
st.divider()
st.markdown('<div class="section-header">📄 KELENGKAPAN STNK & BPKB</div>', unsafe_allow_html=True)

if not df_periode.empty:
    stnk_exists = 'Status STNK' in df_periode.columns
    bpkb_exists = 'Status BPKB' in df_periode.columns
    
    if stnk_exists or bpkb_exists:
        col1, col2 = st.columns(2)
        
        with col1:
            if stnk_exists:
                stnk_active = df_periode['Status STNK'].sum() if stnk_exists else 0
                stnk_inactive = len(df_periode) - stnk_active if stnk_exists else 0
                
                st.markdown("""
                <div style="text-align: center; margin-bottom: 10px;">
                    <span style="font-size: 18px; font-weight: 800; color: #003366;">📋 STATUS STNK</span>
                </div>
                """, unsafe_allow_html=True)

                # Donut chart compact dengan teks besar
                fig_stnk = go.Figure()
                
                fig_stnk.add_trace(go.Pie(
                    labels=['Aktif', 'Belum'],
                    values=[stnk_active, stnk_inactive],
                    hole=0.35,  # Diubah dari 0.45 ke 0.55 agar lebih kecil
                    marker=dict(
                        colors=[DARK_BLUE, ACCENT_RED],
                        line=dict(color='white', width=2)
                    ),
                    textinfo='percent',
                    textfont=dict(size=14, color='white', weight='bold'),
                    textposition='inside',
                    hoverinfo='label+percent+value',
                    hoverlabel=dict(
                        bgcolor='white', 
                        font=dict(size=14, color=TEXT_DARK, weight='bold')
                    ),
                    pull=[0.02, 0],
                    rotation=90,
                    sort=False,
                    domain=dict(x=[0, 1], y=[0, 1])
                ))
                
                fig_stnk.update_layout(
                    height=280,  # Diubah dari 320 ke 280
                    showlegend=True,
                    legend=dict(
                        font=dict(size=13, color=TEXT_DARK, weight='bold'),
                        orientation="h",
                        yanchor="bottom",
                        y=-0.12,  # Disesuaikan
                        xanchor="center",
                        x=0.5,
                        bgcolor='rgba(255,255,255,0.9)',
                        bordercolor='#E5E5E5',
                        borderwidth=1
                    ),
                    margin=dict(t=10, b=20, l=10, r=10),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                )
                
                st.plotly_chart(fig_stnk, use_container_width=True, key=f"stnk_chart_{len(df_periode)}_{datetime.now().timestamp()}")
        
        with col2:
            if bpkb_exists:
                bpkb_active = df_periode['Status BPKB'].sum() if bpkb_exists else 0
                bpkb_inactive = len(df_periode) - bpkb_active if bpkb_exists else 0

                st.markdown("""
                <div style="text-align: center; margin-bottom: 10px;">
                    <span style="font-size: 18px; font-weight: 800; color: #003366;">📑 STATUS BPKB</span>
                </div>
                """, unsafe_allow_html=True)                
                fig_bpkb = go.Figure()
                
                fig_bpkb.add_trace(go.Pie(
                    labels=['Aktif', 'Belum'],
                    values=[bpkb_active, bpkb_inactive],
                    hole=0.35,  # Diubah dari 0.45 ke 0.55 agar lebih kecil
                    marker=dict(
                        colors=[DARK_BLUE, ACCENT_RED],
                        line=dict(color='white', width=2)
                    ),
                    textinfo='percent',
                    textfont=dict(size=14, color='white', weight='bold'),
                    textposition='inside',
                    hoverinfo='label+percent+value',
                    hoverlabel=dict(
                        bgcolor='white', 
                        font=dict(size=14, color=TEXT_DARK, weight='bold')
                    ),
                    pull=[0.02, 0],
                    rotation=90,
                    sort=False,
                    domain=dict(x=[0, 1], y=[0, 1])
                ))
                
                fig_bpkb.update_layout(
                    height=280,  # Diubah dari 320 ke 280
                    showlegend=True,
                    legend=dict(
                        font=dict(size=13, color=TEXT_DARK, weight='bold'),
                        orientation="h",
                        yanchor="bottom",
                        y=-0.12,  # Disesuaikan
                        xanchor="center",
                        x=0.5,
                        bgcolor='rgba(255,255,255,0.9)',
                        bordercolor='#E5E5E5',
                        borderwidth=1
                    ),
                    margin=dict(t=10, b=20, l=10, r=10),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                )
                
                st.plotly_chart(fig_bpkb, use_container_width=True, key=f"bpkb_chart_{len(df_periode)}_{datetime.now().timestamp()}")

# ========== BAGIAN: KELENGKAPAN TOS & ACTION TOS ==========
st.markdown('<div class="section-header">📌 KELENGKAPAN TOS & ACTION TOS</div>', unsafe_allow_html=True)

if not df_periode.empty:
    tosol_exists = 'TOS' in df_periode.columns
    action_exists = 'Action TOS' in df_periode.columns
    
    if tosol_exists or action_exists:
        col1, col2 = st.columns(2)
        
        with col1:
            if tosol_exists:
                # Klasifikasi TOS: Pakai, Tidak Pakai, Belum terisi
                tosol_values = df_periode['TOS'].astype(str).str.strip().str.lower()
                
                # Pakai: jika berisi 'pakai' atau 'ya' atau '1' atau 'true'
                pakai_count = tosol_values.apply(lambda x: x in ['pakai', 'ya', '1', 'true', 'pakai', 'pake']).sum()
                
                # Tidak Pakai: jika berisi 'tidak pakai' atau 'tidak' atau 'no' atau '0' atau 'false'
                tidak_pakai_count = tosol_values.apply(lambda x: x in ['tidak pakai', 'tidak', 'no', '0', 'false', 'tdk pakai', 'tidak_pakai']).sum()
                
                # Belum terisi: kosong atau nan
                belum_count = len(df_periode) - pakai_count - tidak_pakai_count
                total = len(df_periode)
                
                # Judul TOS
                st.markdown("""
                <div style="text-align: center; margin-bottom: 10px;">
                    <span style="font-size: 18px; font-weight: 800; color: #003366;">📌 STATUS TOS</span>
                </div>
                """, unsafe_allow_html=True)
                
                # Donut chart compact dengan teks besar
                fig_tosol = go.Figure()
                
                fig_tosol.add_trace(go.Pie(
                    labels=['Pakai', 'Tidak Pakai', 'Belum Terisi'],
                    values=[pakai_count, tidak_pakai_count, belum_count],
                    hole=0.35,  # Diubah dari 0.45 ke 0.55 agar lebih kecil
                    marker=dict(
                        colors=[DARK_BLUE, ACCENT_RED, '#FFA000'],
                        line=dict(color='white', width=2)
                    ),
                    textinfo='percent',
                    textfont=dict(size=13, color='white', weight='bold'),
                    textposition='inside',
                    hoverinfo='label+percent+value',
                    hoverlabel=dict(
                        bgcolor='white', 
                        font=dict(size=14, color=TEXT_DARK, weight='bold')
                    ),
                    pull=[0.02, 0, 0],
                    rotation=90,
                    sort=False,
                    domain=dict(x=[0, 1], y=[0, 1])
                ))
                
                fig_tosol.update_layout(
                    height=280,  # Diubah dari 320 ke 280
                    showlegend=True,
                    legend=dict(
                        font=dict(size=13, color=TEXT_DARK, weight='bold'),
                        orientation="h",
                        yanchor="bottom",
                        y=-0.12,  # Disesuaikan
                        xanchor="center",
                        x=0.5,
                        bgcolor='rgba(255,255,255,0.9)',
                        bordercolor='#E5E5E5',
                        borderwidth=1
                    ),
                    margin=dict(t=10, b=20, l=10, r=10),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                )
                                
                st.plotly_chart(fig_tosol, use_container_width=True, key=f"tosol_chart_{len(df_periode)}_{datetime.now().timestamp()}")
        
        with col2:
            if action_exists:
                # Klasifikasi Action TOS: Delivered, Not Delivered, Belum terisi
                action_values = df_periode['Action TOS'].astype(str).str.strip().str.lower()
                
                # Delivered: jika berisi 'delivered' atau 'terkirim' atau 'kirim' atau 'done'
                delivered_count = action_values.apply(lambda x: x in ['delivered', 'terkirim', 'kirim', 'done', 'selesai', 'yes', '1', 'true']).sum()
                
                # Not Delivered: jika berisi 'not delivered' atau 'belum terkirim' atau 'pending' atau 'no'
                not_delivered_count = action_values.apply(lambda x: x in ['not delivered', 'belum terkirim', 'pending', 'no', '0', 'false', 'belum', 'not_delivered']).sum()
                
                # Belum terisi: kosong atau nan
                belum_count_action = len(df_periode) - delivered_count - not_delivered_count
                total = len(df_periode)
                
                # Judul ACTION TOS
                st.markdown("""
                <div style="text-align: center; margin-bottom: 10px;">
                    <span style="font-size: 18px; font-weight: 800; color: #003366;">⚡ STATUS ACTION TOS</span>
                </div>
                """, unsafe_allow_html=True)
                
                # Donut chart compact dengan teks besar
                fig_action = go.Figure()
                
                fig_action.add_trace(go.Pie(
                    labels=['Delivered', 'Not Delivered', 'Belum Terisi'],
                    values=[delivered_count, not_delivered_count, belum_count_action],
                    hole=0.35,  # Diubah dari 0.45 ke 0.55 agar lebih kecil
                    marker=dict(
                        colors=[DARK_BLUE, ACCENT_RED, '#FFA000'],
                        line=dict(color='white', width=2)
                    ),
                    textinfo='percent',
                    textfont=dict(size=13, color='white', weight='bold'),
                    textposition='inside',
                    hoverinfo='label+percent+value',
                    hoverlabel=dict(
                        bgcolor='white', 
                        font=dict(size=14, color=TEXT_DARK, weight='bold')
                    ),
                    pull=[0.02, 0, 0],
                    rotation=90,
                    sort=False,
                    domain=dict(x=[0, 1], y=[0, 1])
                ))
                
                fig_action.update_layout(
                    height=280,  # Diubah dari 320 ke 280
                    showlegend=True,
                    legend=dict(
                        font=dict(size=13, color=TEXT_DARK, weight='bold'),
                        orientation="h",
                        yanchor="bottom",
                        y=-0.12,  # Disesuaikan
                        xanchor="center",
                        x=0.5,
                        bgcolor='rgba(255,255,255,0.9)',
                        bordercolor='#E5E5E5',
                        borderwidth=1
                    ),
                    margin=dict(t=10, b=20, l=10, r=10),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                )
                
                st.plotly_chart(fig_action, use_container_width=True, key=f"action_tos_chart_{len(df_periode)}_{datetime.now().timestamp()}")

# ========== DASHBOARD ANALYTICS & PERFORMANCE ==========
st.markdown('<div class="section-header">📊 DASHBOARD ANALISIS PERFORMA</div>', unsafe_allow_html=True)

if not df_periode.empty:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 10px;">
            <span style="font-size: 16px; font-weight: 700; color: #003366;">📱 Download MyIsuzuID</span>
        </div>
        """, unsafe_allow_html=True)
        
        if 'Download MyIsuzuID' in df_periode.columns:
            total = len(df_periode)
            sudah_download = df_periode['Download MyIsuzuID'].sum()
            belum_download = total - sudah_download
            
            fig_download = go.Figure(data=[go.Pie(
                labels=['Sudah Download', 'Belum Download'],
                values=[sudah_download, belum_download],
                hole=0.35,
                marker=dict(
                    colors=[DARK_BLUE, ACCENT_RED],
                    line=dict(color='white', width=2)
                ),
                textinfo='percent',
                textfont=dict(size=13, color='white', weight='bold'),
                textposition='inside',
                hovertemplate='<b>%{label}</b><br>%{value} unit (%{percent})<extra></extra>',
                hoverlabel=dict(bgcolor='white', font=dict(size=13, color=TEXT_DARK, weight='bold')),
                pull=[0.02, 0],
                rotation=90
            )])
            
            fig_download.update_layout(
                height=280,
                showlegend=True,
                legend=dict(
                    font=dict(size=11, color=TEXT_DARK),
                    orientation="h",
                    yanchor="bottom",
                    y=-0.12,
                    xanchor="center",
                    x=0.5,
                    bgcolor='rgba(255,255,255,0.9)',
                    bordercolor='#E5E5E5',
                    borderwidth=1
                ),
                margin=dict(t=10, b=20, l=10, r=10),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
            )
            
            st.plotly_chart(fig_download, use_container_width=True, key=f"download_chart_{len(df_periode)}_{datetime.now().timestamp()}")
                
    with col2:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 10px;">
            <span style="font-size: 16px; font-weight: 700; color: #003366;">💰 Distribusi Jenis Pembayaran</span>
        </div>
        """, unsafe_allow_html=True)
        
        if 'Jenis Pembayaran' in df_periode.columns:
            payment_data = df_periode['Jenis Pembayaran'].dropna()
            payment_data = payment_data[payment_data.str.strip() != '']
            
            if not payment_data.empty:
                payment_counts = payment_data.value_counts().reset_index()
                payment_counts.columns = ['Jenis Pembayaran', 'Jumlah Unit']
                
                total_payment = payment_counts['Jumlah Unit'].sum()
                payment_counts['Persentase'] = (payment_counts['Jumlah Unit'] / total_payment * 100).round(1)
                
                colors = [ASTRA_BLUE, DARK_BLUE, '#3D6B9F', '#4A7AB5', '#5A8ACC']
                
                fig_payment = go.Figure(data=[
                    go.Bar(
                        x=payment_counts['Jenis Pembayaran'],
                        y=payment_counts['Jumlah Unit'],
                        marker_color=colors[:len(payment_counts)],
                        text=payment_counts['Jumlah Unit'],
                        textposition='outside',
                        textfont=dict(size=14, color=DARK_BLUE, weight='bold'),
                        hovertemplate='<b>%{x}</b><br>Jumlah: %{y} unit<extra></extra>',
                        hoverlabel=dict(bgcolor='white', font=dict(size=13, color=TEXT_DARK, weight='bold')),
                        width=0.6
                    )
                ])
                
                fig_payment.update_layout(
                    height=280,
                    xaxis=dict(
                        tickangle=45, 
                        tickfont=dict(size=12, color=TEXT_DARK),
                        title_font=dict(size=13)
                    ),
                    yaxis=dict(
                        tickfont=dict(size=11, color=TEXT_DARK),
                        title=dict(text="<b>Unit</b>", font=dict(size=12)),
                        gridcolor='#E5E5E5',
                        gridwidth=0.5
                    ),
                    showlegend=False,
                    margin=dict(t=10, b=40, l=10, r=10),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    bargap=0.25
                )
                
                st.plotly_chart(fig_payment, use_container_width=True, key=f"payment_chart_{hash(str(payment_counts.shape))}_{datetime.now().timestamp()}")
            else:
                st.info("Tidak ada data pembayaran")
        else:
            st.info("Kolom tidak tersedia")
    
    # Baris kedua - Penjualan Unit per Tipe
    st.markdown("""
    <div style="text-align: center; margin: 15px 0 10px 0;">
        <span style="font-size: 16px; font-weight: 800; color: #003366;">📊 Penjualan Unit per Tipe</span>
    </div>
    """, unsafe_allow_html=True)
    
    if 'Material Description' in df_periode.columns:
        df_clean = df_periode.dropna(subset=['Material Description'])
        df_clean = df_clean[df_clean['Material Description'].str.strip() != '']
        
        if len(df_clean) > 0:
            unit_per_material = df_clean['Material Description'].value_counts().reset_index()
            unit_per_material.columns = ['Material Description', 'Jumlah Unit']
            
            # Buat warna gradasi untuk setiap bar
            n_bars = len(unit_per_material)
            bar_colors = []
            for i in range(n_bars):
                ratio = i / max(n_bars - 1, 1)
                g = int(85 + (51 - 85) * ratio)
                b = int(164 + (102 - 164) * ratio)
                bar_colors.append(f'rgb(0, {g}, {b})')
            
            fig_bar = go.Figure(data=[
                go.Bar(
                    x=unit_per_material['Material Description'],
                    y=unit_per_material['Jumlah Unit'],
                    marker=dict(
                        color=bar_colors,
                        line=dict(width=1, color=DARK_BLUE)
                    ),
                    text=unit_per_material['Jumlah Unit'],
                    textposition='outside',
                    textfont=dict(size=13, color=DARK_BLUE, weight='bold'),
                    hovertemplate='<b>%{x}</b><br>Penjualan: %{y} unit<extra></extra>',
                    hoverlabel=dict(bgcolor='white', font=dict(size=13, color=TEXT_DARK, weight='bold')),
                    width=0.6
                )
            ])
            
            fig_bar.update_layout(
                height=400,
                xaxis=dict(
                    tickangle=45, 
                    tickfont=dict(size=12, color=TEXT_DARK),
                    title_font=dict(size=13)
                ),
                yaxis=dict(
                    tickfont=dict(size=11, color=TEXT_DARK),
                    title=dict(text="<b>Jumlah Unit</b>", font=dict(size=12)),
                    gridcolor='#E5E5E5',
                    gridwidth=0.5,
                    zeroline=True,
                    zerolinecolor='#E5E5E5'
                ),
                showlegend=False,
                margin=dict(t=10, b=70, l=10, r=10),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                bargap=0.2
            )
            
            st.plotly_chart(fig_bar, use_container_width=True, key=f"sales_chart_{len(df_clean)}_{datetime.now().timestamp()}")
     
    st.divider()
    st.markdown("### 👥 PERFORMANCE DOWNLOAD APLIKASI MYISUZUID")
    
    if 'Nama Salesman' in df_periode.columns:
        sales_stats = []
        for sales in df_periode['Nama Salesman'].unique():
            if pd.notna(sales) and sales != '':
                sales_data = df_periode[df_periode['Nama Salesman'] == sales]
                total_sales = len(sales_data)
                
                if total_sales > 0:
                    download_sum = sales_data['Download MyIsuzuID'].sum() if 'Download MyIsuzuID' in sales_data.columns else 0
                    download_rate = (download_sum / total_sales * 100) if total_sales > 0 else 0
                    
                    sales_stats.append({
                        'Salesman': sales,
                        'Total Unit': total_sales,
                        'Download Rate MyIsuzuID(%)': round(download_rate, 1)
                    })
        
        if sales_stats:
            sales_df = pd.DataFrame(sales_stats)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📊 Download MyIsuzuID Rate Tertinggi**")
                top_download = sales_df[sales_df['Total Unit'] >= 1].sort_values('Download Rate MyIsuzuID(%)', ascending=False).head(5)
                for idx, row in top_download.iterrows():
                    max_rate = sales_df['Download Rate MyIsuzuID(%)'].max()
                    progress = row['Download Rate MyIsuzuID(%)']/max_rate if max_rate > 0 else 0
                    st.progress(progress, 
                               text=f"{row['Salesman']}: {row['Download Rate MyIsuzuID(%)']:.0f}%")
            
            with col2:
                st.markdown("**📊 Download MyIsuzuID Rate Terendah**")
                # Filter salesman dengan total unit minimal 1
                salesman_with_unit = sales_df[sales_df['Total Unit'] >= 1].copy()
                if not salesman_with_unit.empty:
                    bottom_download = salesman_with_unit.sort_values('Download Rate MyIsuzuID(%)', ascending=True).head(5)
                    for idx, row in bottom_download.iterrows():
                        max_rate = sales_df['Download Rate MyIsuzuID(%)'].max()
                        progress = row['Download Rate MyIsuzuID(%)']/max_rate if max_rate > 0 else 0
                        st.progress(progress, 
                                   text=f"{row['Salesman']}: {row['Download Rate MyIsuzuID(%)']:.0f}%")
                else:
                    st.info("Tidak ada data salesman dengan unit")
            
            with st.expander("📋 Detail Performa Salesman"):
                display_sales_df = sales_df.sort_values('Total Unit', ascending=False)
                st.dataframe(display_sales_df, use_container_width=True)

    st.divider()
    
    st.markdown('<div class="section-header">📊 ANALISIS PENJUALAN PER TIPE PER SALESMAN</div>', unsafe_allow_html=True)

    if not df_periode.empty and 'Nama Salesman' in df_periode.columns and 'Material Description' in df_periode.columns:
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        
        with col_m1:
            total_salesman = df_periode['Nama Salesman'].nunique()
            st.markdown(f"""
            <div class="metric-card">
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <span style="font-size: 1.2rem; margin-right: 8px;">👥</span>
                    <span style="font-size: 0.8rem; font-weight: 600; color: #666;">TOTAL SALESMAN</span>
                </div>
                <div class="metric-value">
                    {total_salesman}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_m2:
            total_tipe = df_periode['Material Description'].nunique()
            st.markdown(f"""
            <div class="metric-card" style="border-left-color: #2E7D32;">
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <span style="font-size: 1.2rem; margin-right: 8px;">🚛</span>
                    <span style="font-size: 0.8rem; font-weight: 600; color: #666;">TIPE UNIT</span>
                </div>
                <div class="metric-value">
                    {total_tipe}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_m3:
            total_unit = len(df_periode)
            st.markdown(f"""
            <div class="metric-card" style="border-left-color: #FFA000;">
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <span style="font-size: 1.2rem; margin-right: 8px;">📦</span>
                    <span style="font-size: 0.8rem; font-weight: 600; color: #666;">TOTAL UNIT</span>
                </div>
                <div class="metric-value">
                    {total_unit}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_m4:
            avg_unit_per_salesman = total_unit / total_salesman if total_salesman > 0 else 0
            st.markdown(f"""
            <div class="metric-card" style="border-left-color: {ACCENT_RED};">
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <span style="font-size: 1.2rem; margin-right: 8px;">📊</span>
                    <span style="font-size: 0.8rem; font-weight: 600; color: #666;">RATA-RATA/SALESMAN</span>
                </div>
                <div class="metric-value">
                    {avg_unit_per_salesman:.1f}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        tab_analisis1, tab_analisis2 = st.tabs([
            "📋 Tabel Penjualan per Salesman",  
            "🏆 Top Performers",
        ])
        
        with tab_analisis1:
            st.markdown("### 📋 Tabel Penjualan Unit per Tipe per Salesman")
            
            sales_material_pivot = pd.crosstab(
                df_periode['Nama Salesman'], 
                df_periode['Material Description'],
                margins=True,
                margins_name='TOTAL UNIT'
            )
            
            if 'TOTAL UNIT' in sales_material_pivot.index:
                tipe_counts = {}
                for salesman in sales_material_pivot.index:
                    if salesman != 'TOTAL UNIT':
                        non_zero = (sales_material_pivot.loc[salesman] > 0).sum()
                        tipe_counts[salesman] = non_zero
                
                tipe_row = pd.Series(index=sales_material_pivot.columns, name='JENIS TIPE')
                for col in sales_material_pivot.columns:
                    if col != 'TOTAL UNIT':
                        tipe_row[col] = ''
                    else:
                        tipe_row[col] = 'TOTAL'
                
                sales_material_pivot = pd.concat([
                    sales_material_pivot.iloc[:-1], 
                    pd.DataFrame([tipe_row]), 
                    sales_material_pivot.iloc[-1:]
                ])
            
            st.dataframe(sales_material_pivot, use_container_width=True)
            
            csv_pivot = sales_material_pivot.reset_index().to_csv(index=False, encoding='utf8')
            st.download_button(
                label="📥 Download Tabel Penjualan per Salesman (CSV)",
                data=csv_pivot,
                file_name=f"penjualan_per_salesman_per_tipe_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                help="Download tabel penjualan per tipe per salesman",
                use_container_width=True
            )
                                
        with tab_analisis2:
            col_top1, col_top2 = st.columns(2)
            
            with col_top1:
                st.markdown("#### 👑 Top Salesman per Tipe Unit")
                st.markdown("*Salesman dengan penjualan terbanyak untuk setiap tipe kendaraan*")
                
                top_sales_per_tipe = []
                for tipe in df_periode['Material Description'].dropna().unique():
                    if pd.notna(tipe) and tipe != '':
                        tipe_data = df_periode[df_periode['Material Description'] == tipe]
                        if not tipe_data.empty:
                            top_sales = tipe_data['Nama Salesman'].value_counts().head(1)
                            for salesman, unit in top_sales.items():
                                total_tipe = len(tipe_data)
                                market_share = (unit / total_tipe * 100)
                                
                                second_place = tipe_data['Nama Salesman'].value_counts().head(2)
                                if len(second_place) > 1:
                                    second_unit = second_place.values[1]
                                    gap = unit - second_unit
                                else:
                                    gap = unit
                                
                                top_sales_per_tipe.append({
                                    'Tipe Unit': tipe,
                                    'Top Salesman': salesman,
                                    'Unit Terjual': unit,
                                    'Total Unit Tipe': total_tipe,
                                    'Kontribusi': f"{market_share:.1f}%",
                                    'Selisih (unit)': gap
                                })
                
                if top_sales_per_tipe:
                    top_sales_df = pd.DataFrame(top_sales_per_tipe)
                    top_sales_df = top_sales_df.sort_values('Unit Terjual', ascending=False)
                    
                    for idx, row in top_sales_df.iterrows():
                        with st.container():
                            col_name, col_val = st.columns([2, 1])
                            with col_name:
                                st.markdown(f"**{row['Tipe Unit']}**")
                                st.caption(f"👤 {row['Top Salesman']}")
                            with col_val:
                                st.markdown(f"**{row['Unit Terjual']} unit**")
                            
                            st.progress(float(row['Kontribusi'].replace('%', ''))/100, 
                                       text=f"Kontribusi: {row['Kontribusi']} dari total tipe unit")
                            st.divider()
            
            with col_top2:
                st.markdown("#### 📊 Top 10 Salesman by Total Unit")
                st.markdown("*Salesman dengan total penjualan unit terbanyak*")
                
                total_per_salesman = df_periode['Nama Salesman'].value_counts().head(10)
                max_total = total_per_salesman.max()
                
                for salesman, unit in total_per_salesman.items():
                    salesman_data = df_periode[df_periode['Nama Salesman'] == salesman]
                    unique_tipes = salesman_data['Material Description'].nunique()
                    top_tipe = salesman_data['Material Description'].value_counts().head(1)
                    tipe_favorit = top_tipe.index[0] if not top_tipe.empty else 'Belum'
                    unit_favorit = top_tipe.values[0] if not top_tipe.empty else 0
                    
                    with st.expander(f"**{salesman}** - {unit} unit"):
                        st.markdown(f"""
                        - 📦 **Total Unit Terjual:** {unit}
                        - 🚛 **Total Tipe yang Terjual:** {unique_tipes} tipe
                        - 🎯 **Tipe Terbanyak Dijual:** {tipe_favorit} ({unit_favorit} unit)
                        """)
                                                
st.markdown('<div class="section-header">📋 DETAIL UNIT YANG BELUM MELAKUKAN PROSES</div>', unsafe_allow_html=True)

if not df_periode.empty:
    st.markdown("""
    <div style="background-color: #F0F7FF; padding: 0.75rem; border-radius: 6px; margin-bottom: 1rem; border-left: 3px solid #0055A4;">
        <p style="color: #1E2A3A; margin: 0; font-size: 0.9rem;">
            Klik tombol di bawah untuk melihat daftar unit yang belum melakukan proses tertentu.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Definisi proses yang akan ditampilkan
    proses_list = [
        {'nama': 'STNK', 'kolom': 'Tgl STNK', 'kondisi': lambda row: pd.isna(row.get('Tgl STNK'))},
        {'nama': 'BPKB', 'kolom': 'Tgl BPKB', 'kondisi': lambda row: pd.isna(row.get('Tgl BPKB'))},
        {'nama': 'Serah Terima BPKB', 'kolom': 'Tgl Serah Terima BPKB', 'kondisi': lambda row: pd.isna(row.get('Tgl Serah Terima BPKB'))},
        {'nama': 'Kirim Tagihan', 'kolom': 'Tgl Kirim Tagihan', 'kondisi': lambda row: pd.isna(row.get('Tgl Kirim Tagihan'))},
        {'nama': 'Pelunasan', 'kolom': 'Tgl Pelunasan', 'kondisi': lambda row: pd.isna(row.get('Tgl Pelunasan'))},
        {'nama': 'Pengajuan Fakpol', 'kolom': 'Tgl Pengajuan Fakpol Approve', 'kondisi': lambda row: pd.isna(row.get('Tgl Pengajuan Fakpol Approve'))},
        {'nama': 'BJ Terima Fakpol', 'kolom': 'Tgl BJ Terima Fakpol', 'kondisi': lambda row: pd.isna(row.get('Tgl BJ Terima Fakpol'))},
        {'nama': 'Download MyIsuzu ID', 'kolom': 'Download MyIsuzuID', 'kondisi': lambda row: not row.get('Download MyIsuzuID', False)},
        {'nama': 'TOS', 'kolom': 'TOS', 'kondisi': lambda row: pd.isna(row.get('TOS')) or row.get('TOS') == '' or row.get('TOS') == 'nan'},
        {'nama': 'Action TOS', 'kolom': 'Action TOS', 'kondisi': lambda row: pd.isna(row.get('Action TOS')) or row.get('Action TOS') == '' or row.get('Action TOS') == 'nan'},
        {'nama': 'KSG I', 'kolom': 'KSG I', 'kondisi': lambda row: pd.isna(row.get('KSG I'))},
        {'nama': 'KSG II', 'kolom': 'KSG II', 'kondisi': lambda row: pd.isna(row.get('KSG II'))},
        {'nama': 'KSGX 20K', 'kolom': 'KSGX 20K', 'kondisi': lambda row: pd.isna(row.get('KSGX 20K'))},
        {'nama': 'KSGX 30K', 'kolom': 'KSGX 30K', 'kondisi': lambda row: pd.isna(row.get('KSGX 30K'))},
        {'nama': 'KSGX 40K', 'kolom': 'KSGX 40K', 'kondisi': lambda row: pd.isna(row.get('KSGX 40K'))}
    ]
    
    # Membuat tombol dalam grid 3 kolom
    cols = st.columns(3)
    button_states = {}
    
    for idx, proses in enumerate(proses_list):
        col_idx = idx % 3
        with cols[col_idx]:
            # PERUBAHAN: menggunakan key yang lebih spesifik
            if st.button(f"📋 {proses['nama']}", key=f"btn_{proses['nama'].replace(' ', '_')}_{idx}", use_container_width=True):
                button_states[proses['nama']] = not button_states.get(proses['nama'], False)
                for other in proses_list:
                    if other['nama'] != proses['nama']:
                        button_states[other['nama']] = False

    st.divider()
    
    # Tampilkan detail berdasarkan tombol yang ditekan
    for proses in proses_list:
        if button_states.get(proses['nama'], False):
            st.markdown(f"""
            <div style="background-color: #FFF5E5; padding: 1rem; border-radius: 6px; margin-bottom: 1rem; border-left: 3px solid #CC0000;">
                <strong>📋 DAFTAR UNIT YANG BELUM {proses['nama'].upper()}</strong>
            </div>
            """, unsafe_allow_html=True)
            
            # Filter data yang belum melakukan proses
            if proses['kolom'] in df_periode.columns:
                if proses['nama'] == 'Download MyIsuzu ID':
                    inactive_df = df_periode[df_periode[proses['kolom']] == False].copy()
                elif proses['nama'] in ['TOS', 'Action TOS']:
                    inactive_df = df_periode[
                        (df_periode[proses['kolom']].isna()) | 
                        (df_periode[proses['kolom']].astype(str).str.strip() == '') |
                        (df_periode[proses['kolom']].astype(str).str.strip() == 'nan') |
                        (df_periode[proses['kolom']].astype(str).str.strip() == 'None')
                    ].copy()
                else:
                    inactive_df = df_periode[df_periode[proses['kolom']].isna()].copy()
                
                if not inactive_df.empty:
                    st.warning(f"⚠️ **{len(inactive_df)} unit dengan {proses['nama']} belum selesai:**")
                    
                    # Kolom yang ditampilkan
                    display_cols = ['Tgl DO', 'Chasis', 'Material Description', 'Nama Customer', 'Nama Salesman']
                    available_cols = [col for col in display_cols if col in inactive_df.columns]
                    
                    if available_cols:
                        display_inactive = inactive_df[available_cols].copy()
                        
                        # Format tanggal
                        if 'Tgl DO' in display_inactive.columns:
                            display_inactive['Tgl DO'] = pd.to_datetime(display_inactive['Tgl DO'], errors='coerce')
                            display_inactive['Tgl DO'] = display_inactive['Tgl DO'].dt.strftime('%d/%m/%Y')
                            display_inactive['Tgl DO'] = display_inactive['Tgl DO'].fillna('Belum')
                        
                        # Isi nilai kosong
                        display_inactive = display_inactive.fillna('Belum')
                        
                        st.dataframe(display_inactive, use_container_width=True, hide_index=True)
                        
                        # Tombol download
                        csv_data = inactive_df[available_cols].to_csv(index=False, encoding='utf8')
                        st.download_button(
                            label=f"📥 Download List {proses['nama']} Belum Selesai",
                            data=csv_data,
                            file_name=f"{proses['nama'].lower().replace(' ', '_')}_belum_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv",
                            key=f"download_{proses['nama'].replace(' ', '_')}_{datetime.now().timestamp()}"  # PERUBAHAN: key unik dengan timestamp
                        )                    
                    else:
                        st.info("Tidak ada kolom yang tersedia untuk ditampilkan.")
                else:
                    st.success(f"🎉 Semua unit sudah memiliki {proses['nama']}!")
            else:
                st.info(f"Kolom {proses['kolom']} tidak ditemukan dalam data.")

    st.divider()
st.markdown('<div class="section-header">🔍 FILTER DATA</div>', unsafe_allow_html=True)

if not df_periode.empty:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if 'Material Description' in df_periode.columns:
            material_options = df_periode['Material Description'].dropna().unique().tolist()
            material_options = [x for x in material_options if x and x != '']
            material_filter = st.multiselect(
                "Filter Material Description:",
                options=material_options,
                default=[],
                key="filter_material_main"  # PERUBAHAN: key unik
            )
    
    with col2:
        if 'Nama Salesman' in df_periode.columns:
            salesman_options = df_periode['Nama Salesman'].dropna().unique().tolist()
            salesman_options = [x for x in salesman_options if x and x != '']
            salesman_filter = st.multiselect(
                "Filter Nama Salesman:",
                options=salesman_options,
                default=[],
                key="filter_salesman_main"  # PERUBAHAN: key unik
            )
    
    with col3:
        if 'Nama Customer' in df_periode.columns:
            customer_options = df_periode['Nama Customer'].dropna().unique().tolist()
            customer_options = [x for x in customer_options if x and x != '' and x != 'nan' and x != 'None']
            customer_options.sort()
            customer_filter = st.multiselect(
                "Filter Nama Customer:",
                options=customer_options,
                default=[],
                key="filter_customer_main"  # PERUBAHAN: key unik
            )
            
    filtered_df = df_periode.copy()
    
    if 'Material Description' in df_periode.columns and material_filter:
        filtered_df = filtered_df[filtered_df['Material Description'].isin(material_filter)]
    
    if 'Nama Salesman' in df_periode.columns and salesman_filter:
        filtered_df = filtered_df[filtered_df['Nama Salesman'].isin(salesman_filter)]
    
    if 'Nama Customer' in df_periode.columns and customer_filter:
        filtered_df = filtered_df[filtered_df['Nama Customer'].isin(customer_filter)]
    
    st.info(f"📊 **{len(filtered_df)} data** ditemukan berdasarkan filter")
    
    available_columns = [col for col in column_order if col in filtered_df.columns]
    display_filtered_df = filtered_df[available_columns].copy() if not filtered_df.empty else pd.DataFrame()
    
    if not display_filtered_df.empty:
        for col in date_columns:
            if col in display_filtered_df.columns:
                display_filtered_df[col] = pd.to_datetime(display_filtered_df[col], errors='coerce')
                display_filtered_df[col] = display_filtered_df[col].dt.strftime('%d/%m/%Y')
                display_filtered_df[col] = display_filtered_df[col].fillna('Belum')
        
        if 'Download MyIsuzuID' in display_filtered_df.columns:
            display_filtered_df['Download MyIsuzuID'] = display_filtered_df['Download MyIsuzuID'].map(
                {True: '✅ Selesai', False: '❌ Belum', None: '❌ Belum'}
            )
        
        if 'TOS' in display_filtered_df.columns:
            display_filtered_df['TOS'] = display_filtered_df['TOS'].apply(lambda x: '✅ Selesai' if x and x != '' else '❌ Belum')
        
        if 'Action TOS' in display_filtered_df.columns:
            display_filtered_df['Action TOS'] = display_filtered_df['Action TOS'].apply(lambda x: '✅ Selesai' if x and x != '' else '❌ Belum')
        
        st.dataframe(display_filtered_df, use_container_width=True, hide_index=True)
else:
    st.info("Tidak ada data yang tersedia untuk difilter.")

st.divider()

# ========== FOOTER SEDERHANA ==========
st.divider()
current_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
st.markdown(f"""
<div class="footer">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
        <div>
            <strong>🚛 Astra Isuzu Tracking System</strong>
        </div>
        <div>
            Terakhir refresh: {current_time}<br>
            Data Periode: {len(df_periode)} unit | Total Semua: {len(df) if not df.empty else 0} unit<br>
        </div>
    </div>
    <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.1);">
        <p style="margin: 0; font-size: 0.85rem; text-align: center;">© 2026 Astra Isuzu Tracking System</p>
    </div>
</div>
""", unsafe_allow_html=True) 