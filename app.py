import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import date, timedelta

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Nifty Technical Screener Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  .block-container { padding-top: 0.8rem; padding-bottom: 0.8rem; }
  div[data-testid="metric-container"] {
    background: #161b2e; border-radius: 8px;
    padding: 10px 14px; border: 1px solid #252d4a;
  }
  div[data-testid="metric-container"] label { font-size: 11px !important; color: #7b88b0 !important; }
  div[data-testid="metric-container"] [data-testid="metric-value"] { font-size: 20px !important; }
  .section-title {
    font-size: 13px; font-weight: 700; letter-spacing: 0.08em;
    color: #7b88b0; text-transform: uppercase; margin: 12px 0 6px;
  }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TICKER UNIVERSE DEFINITIONS 
# ═══════════════════════════════════════════════════════════════════════════════
NIFTY100 = [
    'RELIANCE','TCS','HDFCBANK','BHARTIARTL','ICICIBANK','INFOSYS','SBIN','HINDUNILVR',
    'ITC','LT','KOTAKBANK','AXISBANK','BAJFINANCE','MARUTI','ASIANPAINT','TITAN',
    'SUNPHARMA','NESTLEIND','WIPRO','HCLTECH','NTPC','POWERGRID','TECHM','ONGC',
    'COALINDIA','BAJAJFINSV','ADANIENT','ADANIPORTS','ULTRACEMCO','JSWSTEEL',
    'TATAMOTORS','TATASTEEL','INDUSINDBK','HDFCLIFE','SBILIFE','DIVISLAB','DRREDDY',
    'CIPLA','APOLLOHOSP','EICHERMOT','GRASIM','HINDALCO','HEROMOTOCO','BPCL',
    'BAJAJ-AUTO','TATACONSUM','BRITANNIA','VEDL','UPL','SHREECEM','ICICIGI','BOSCHLTD',
    'SIEMENS','HAVELLS','PIIND','GODREJCP','DABUR','MARICO','MCDOWELL-N','COLPAL',
    'AMBUJACEM','ACC','INDIGO','TATAPOWER','GAIL','IOC','SBICARD','BANDHANBNK',
    'BANKBARODA','PNB','MUTHOOTFIN','CHOLAFIN','TORNTPHARM','LUPIN','BIOCON','ALKEM',
    'AUROPHARMA','ZYDUSLIFE','GLAXO','PAGEIND','VOLTAS','CROMPTON','POLYCAB',
    'CUMMINSIND','ABB','BHEL','HAL','BEL','CONCOR','ADANIGREEN','IRFC','PFC',
    'RECLTD','M&M','TRENT'
]

NIFTY_MIDCAP150 = [
    'AARTIIND','AARTIDRUGS','ABCAPITAL','ABFRL','AEGISCHEM','AJANTPHARM','APLAPOLLO',
    'APLLTD','ASTRAL','ATUL','AUBANK','BALKRISIND','BALRAMCHIN','BATAINDIA','BERGEPAINT',
    'BSOFT','BRIGADE','CANBK','CANFINHOME','CASTROLIND','CEATLTD','CGPOWER','CHAMBLFERT',
    'COFORGE','CRAFTSMAN','CRISIL','CYIENT','DATAPATTNS','DEEPAKNTR','DELHIVERY','DIXON',
    'DLF','EIDPARRY','ELGIEQUIP','EMAMILTD','ENDURANCE','ENGINERSIN','ESCORTS','EXIDEIND',
    'FEDERALBNK','FLUOROCHEM','FORTIS','GICRE','GNFC','GODREJIND','GODREJPROP','GRANULES',
    'GRINDWELL','GSFC','GSPL','HAPPSTMNDS','HEG','HFCL','HUDCO','IDFCFIRSTB','IEX','IIFL',
    'INDHOTEL','INDIANB','INDIAMART','INTELLECT','JBCHEPHARM','JKCEMENT','JKLAKSHMI',
    'JKPAPER','JSL','JUBLFOOD','KAJARIACER','KALPATPOWR','KANSAINER','KEC','KIMS',
    'KPITTECH','KRBL','LALPATHLAB','LAURUSLABS','LICHSGFIN','LINDEINDIA','LTIM','LTTS',
    'M&MFIN','MANAPPURAM','MCX','METROBRAND','METROPOLIS','MFSL','MOTILALOFS','MRF',
    'NATCOPHARM','NAVINFLUOR','NBCC','NCC','NIACL','NLCINDIA','NMDC','NOCIL','OBEROIRLTY',
    'OFSS','OIL','OLECTRA','PCBL','PERSISTENT','PETRONET','PFIZER','PHOENIXLTD','POLYMED',
    'PRAJIND','PRESTIGE','PVRINOX','RADICO','RAMCOCEM','RAYMOND','REDINGTON','RELAXO',
    'RITES','ROUTE','SAIL','SCHAEFFLER','SOBHA','SONATSOFTW','STLTECH','SUDARSCHEM',
    'SUMICHEM','SUNDARMFIN','SUNDRMFAST','SUNTV','SUPREMEIND','SUZLON','SYNGENE','TANLA',
    'TATACHEM','TATACOMM','TATAELXSI','TEAMLEASE','TIMKEN','TORNTPOWER','TRENT','TRIDENT',
    'TVSMOTOR','UBL','UJJIVANSFB','UNIONBANK','VBL','VGUARD','VINATIORGA','WELCORP',
    'YESBANK','ZEEL','ZYDUSWELL','DIXONTECH','JYOTHYLAB','APTUS','CAMPUS','CHALET','SENCO',
    'SIGNATURE','SAPPHIRE'
]

NIFTY_LMC250 = list(dict.fromkeys(NIFTY100 + NIFTY_MIDCAP150))

UNIVERSES = {
    "🏆 Nifty 100":             set(NIFTY100),
    "🥈 Nifty MidCap 150":     set(NIFTY_MIDCAP150),
    "🌐 Nifty LargeMidCap 250": set(NIFTY_LMC250),
}

# ═══════════════════════════════════════════════════════════════════════════════
# DATA LOADING
# ═══════════════════════════════════════════════════════════════════════════════
DATA_FILE  = "Master_Data.parquet"

@st.cache_data(ttl=3600, show_spinner="Loading Master_Data.parquet…")
def load_data():
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame(), "FILE_MISSING"
    try:
        df = pd.read_parquet(DATA_FILE)
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values(["Ticker", "Date"]).reset_index(drop=True)
        return df, None
    except Exception as e:
        return pd.DataFrame(), str(e)

master_df, err = load_data()

if err == "FILE_MISSING":
    st.error("### ⚠️ Master_Data.parquet not found. Please run the GitHub action.")
    st.stop()
elif err:
    st.error(f"Error reading data file: {err}")
    st.stop()

# ═══════════════════════════════════════════════════════════════════════════════
# INDICATOR CONFIG & 6 CATEGORIES
# ═══════════════════════════════════════════════════════════════════════════════
# (Column in DataFrame, UI Label)
INDICATOR_MAPPINGS = [
    # Price
    ("Open", "Open Price"), ("High", "High Price"), ("Low", "Low Price"), ("Close", "Close Price"),
    
    # Trend
    ("SMA_20", "SMA 20"), ("SMA_50", "SMA 50"), ("SMA_200", "SMA 200"), 
    ("EMA_20", "EMA 20"), ("EMA_50", "EMA 50"), ("MACD", "MACD Line"), 
    ("MACD_Hist", "MACD Histogram"), ("ADX_14", "ADX 14"), 
    ("Supertrend", "Supertrend"), ("Aroon_Up", "Aroon Up"),
    
    # Momentum
    ("RSI_14", "RSI 14"), ("Stoch_K", "Stochastic %K"), ("Stoch_D", "Stochastic %D"),
    ("StochRSI_K", "StochRSI %K"), ("StochRSI_D", "StochRSI %D"), ("CCI_20", "CCI 20"),
    ("WillR_14", "Williams %R"), ("ROC_12", "ROC 12"), ("AO", "Awesome Oscillator"),
    ("MOM_10", "Momentum 10"), ("PPO", "Price Oscillator (PPO)"), ("UO", "Ultimate Oscillator"),
    
    # Volatility
    ("ATR_14", "ATR 14"), ("BB_Upper", "Bollinger Upper"), ("BB_Lower", "Bollinger Lower"),
    ("BB_Width", "Bollinger Width"), ("KC_Upper", "Keltner Upper"), ("KC_Lower", "Keltner Lower"),
    ("Donchian_Upper", "Donchian Upper"), ("StdDev_20", "Std Deviation 20"),
    
    # Volume
    ("Volume", "Volume"), ("OBV", "On Balance Volume"), ("AD", "Accumulation/Distribution"),
    ("MFI_14", "Money Flow Index"), ("CMF_20", "Chaikin Money Flow"), ("PVT", "Price Volume Trend"),
    ("PVI", "Positive Volume Index"), ("NVI", "Negative Volume Index"), 
    ("VWAP", "VWAP"), ("Vol_SMA_20", "Volume SMA 20"),
    
    # System / Risk
    ("TRIX", "TRIX 30"), ("Elder_Bull", "Elder Bull Power"), ("Elder_Bear", "Elder Bear Power"),
    ("+DI_14", "+DI 14"), ("-DI_14", "-DI 14")
]

ind_meta = {k: v for k, v in INDICATOR_MAPPINGS}
label_to_col = {v: k for k, v in INDICATOR_MAPPINGS}

# Groupings for the Slicers sidebar
SLICER_GROUPS = {
    "📈 1. Trend Indicators":     ["SMA_20", "SMA_50", "SMA_200", "EMA_20", "EMA_50", "MACD", "MACD_Hist", "ADX_14", "Supertrend", "Aroon_Up"],
    "🚀 2. Momentum & Osc":       ["RSI_14", "Stoch_K", "Stoch_D", "StochRSI_K", "StochRSI_D", "CCI_20", "WillR_14", "ROC_12", "AO", "MOM_10", "PPO", "UO"],
    "🌪️ 3. Volatility":          ["ATR_14", "BB_Upper", "BB_Lower", "BB_Width", "KC_Upper", "KC_Lower", "Donchian_Upper", "StdDev_20"],
    "📊 4. Volume & Flow":        ["Volume", "OBV", "AD", "MFI_14", "CMF_20", "PVT", "PVI", "NVI", "VWAP", "Vol_SMA_20"],
    "🧱 5. Price Action":         ["Open", "High", "Low", "Close"],
    "⚖️ 6. System & Risk":        ["TRIX", "Elder_Bull", "Elder_Bear", "+DI_14", "-DI_14"],
}

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
date_min = master_df["Date"].min().date()
date_max = master_df["Date"].max().date()

with st.sidebar:
    st.header("🎛️ Screener Filters")

    st.markdown('<div class="section-title">🗂️ Index Universe</div>', unsafe_allow_html=True)
    universe_choice = st.radio("universe", list(UNIVERSES.keys()), index=2, label_visibility="collapsed")
    selected_tickers = UNIVERSES[universe_choice]
    universe_df = master_df[master_df["Ticker"].isin(selected_tickers)].copy()
    
    st.divider()

    st.markdown('<div class="section-title">📅 Date Range</div>', unsafe_allow_html=True)
    view_mode = st.radio("View mode", ["Latest Day Only", "Date Range"], horizontal=True, label_visibility="collapsed")

    if view_mode == "Latest Day Only":
        selected_start = selected_end = date_max
    else:
        c1, c2 = st.columns(2)
        with c1: selected_start = st.date_input("From", value=date_max - timedelta(days=30), min_value=date_min, max_value=date_max)
        with c2: selected_end = st.date_input("To", value=date_max, min_value=date_min, max_value=date_max)

    st.divider()

    st.markdown('<div class="section-title">🔍 Slicer Mode</div>', unsafe_allow_html=True)
    filter_mode = st.radio("Mode", ["Slider (Range)", "Typed Condition"], label_visibility="collapsed")
    st.divider()

    active_slider_filters = {}
    active_cond_filters   = {}

    for grp_name, cols in SLICER_GROUPS.items():
        with st.expander(grp_name, expanded=False):
            for col in cols:
                if col not in universe_df.columns: continue
                label = ind_meta[col]
                
                if filter_mode == "Slider (Range)":
                    vals = universe_df[col].dropna()
                    if vals.empty or vals.nunique() < 2: continue
                    data_min, data_max = float(vals.min()), float(vals.max())
                    step = round((data_max - data_min) / 200, 4) or 0.01
                    sel = st.slider(label, min_value=round(data_min,2), max_value=round(data_max,2), value=(round(data_min,2), round(data_max,2)), step=step, key=f"sl_{col}")
                    if sel[0] > data_min or sel[1] < data_max:
                        active_slider_filters[col] = sel
                else:
                    op = st.selectbox(label, ["—", ">", "<", ">=", "<=", "=", "Between"], key=f"op_{col}")
                    if op == "Between":
                        c1, c2 = st.columns(2)
                        v1 = c1.number_input("From", value=0.0, key=f"v1_{col}")
                        v2 = c2.number_input("To", value=100.0, key=f"v2_{col}")
                        active_cond_filters[col] = ("between", v1, v2)
                    elif op != "—":
                        v1 = st.number_input(f"Value", value=0.0, key=f"v_{col}")
                        active_cond_filters[col] = (op, v1, None)

    if st.button("🔄 Reset All", width="stretch"):
        st.cache_data.clear()
        st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# DATA FILTERING
# ═══════════════════════════════════════════════════════════════════════════════
date_filtered = universe_df[
    (universe_df["Date"].dt.date >= selected_start) & 
    (universe_df["Date"].dt.date <= selected_end)
].copy()

# Add Chg% dynamically
date_filtered = date_filtered.sort_values(["Ticker", "Date"])
date_filtered["PrevClose"] = date_filtered.groupby("Ticker")["Close"].shift(1)
date_filtered["Chg%"] = ((date_filtered["Close"] - date_filtered["PrevClose"]) / date_filtered["PrevClose"] * 100).round(2)
if view_mode == "Latest Day Only":
    date_filtered = date_filtered.groupby("Ticker").tail(1)

working = date_filtered.copy()

for col, (lo, hi) in active_slider_filters.items():
    if col in working.columns: working = working[(working[col] >= lo) & (working[col] <= hi)]

OP_MAP = {">": lambda s,v1,v2: s>v1, "<": lambda s,v1,v2: s<v1, ">=": lambda s,v1,v2: s>=v1, "<=": lambda s,v1,v2: s<=v1, "=": lambda s,v1,v2: s==v1, "between": lambda s,v1,v2: (s>=v1)&(s<=v2)}
for col, (op, v1, v2) in active_cond_filters.items():
    if col in working.columns: working = working[OP_MAP[op](working[col], v1, v2)]

filtered = working.copy()

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
st.title("📊 Nifty Technical Screener Pro")

# CUSTOM DISPLAY COLUMNS WIDGET
st.markdown("### ⚙️ Customize Display Columns")
default_cols = ["Close Price", "Chg%", "Volume", "RSI 14", "MACD", "ATR 14", "SMA 20", "VWAP"]
all_ui_labels = [label for col, label in INDICATOR_MAPPINGS] + ["Chg%"]

selected_ui_labels = st.multiselect(
    "Select the indicators you want to display in the data table below:",
    options=["Ticker", "Date"] + all_ui_labels,
    default=["Ticker", "Date"] + default_cols
)

# Build the display dataframe
display_cols_internal = []
for label in selected_ui_labels:
    if label in ("Ticker", "Date", "Chg%"):
        display_cols_internal.append(label)
    else:
        display_cols_internal.append(label_to_col[label])

st.divider()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Stocks in Universe", universe_df["Ticker"].nunique())
c2.metric("Rows Match Filters", len(filtered))
c3.metric("🟢 Advancing", int((filtered["Chg%"] > 0).sum()) if "Chg%" in filtered.columns else 0)
c4.metric("🔴 Declining", int((filtered["Chg%"] < 0).sum()) if "Chg%" in filtered.columns else 0)

st.subheader("📋 Results Data Table")

if filtered.empty:
    st.warning("No rows match the current filters.")
else:
    # Restrict to user selected columns that actually exist in the dataframe
    final_cols = [c for c in display_cols_internal if c in filtered.columns]
    display_df = filtered[final_cols].copy()
    
    # Rename headers dynamically back to human readable for the table
    rename_dict = {k: v for k, v in INDICATOR_MAPPINGS}
    display_df = display_df.rename(columns=rename_dict)
    
    if "Date" in display_df.columns:
        display_df["Date"] = display_df["Date"].dt.strftime("%d-%b-%Y")

    st.dataframe(display_df, width="stretch", height=500)

st.divider()

st.subheader("⬇️ Downloads")
dl1, dl2 = st.columns(2)
with dl1:
    if not display_df.empty:
        st.download_button("📄 Download View (CSV)", data=display_df.to_csv(index=False).encode("utf-8"), file_name=f"Custom_View_{selected_start}.csv", width="stretch")
with dl2:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "rb") as f:
            st.download_button("📦 Download Full Master_Data.parquet", data=f.read(), file_name="Master_Data.parquet", width="stretch")
