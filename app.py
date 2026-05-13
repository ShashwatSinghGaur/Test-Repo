import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import date, timedelta

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Nifty Technical Screener",
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
  .cond-row { display: flex; gap: 6px; align-items: center; margin-bottom: 4px; }
  hr { border-color: #252d4a; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TICKER UNIVERSE DEFINITIONS  (no .NS suffix — matches Ticker col in Excel)
# ═══════════════════════════════════════════════════════════════════════════════
NIFTY100 = [
    'RELIANCE','TCS','HDFCBANK','BHARTIARTL','ICICIBANK',
    'INFOSYS','SBIN','HINDUNILVR','ITC','LT',
    'KOTAKBANK','AXISBANK','BAJFINANCE','MARUTI','ASIANPAINT',
    'TITAN','SUNPHARMA','NESTLEIND','WIPRO','HCLTECH',
    'NTPC','POWERGRID','TECHM','ONGC','COALINDIA',
    'BAJAJFINSV','ADANIENT','ADANIPORTS','ULTRACEMCO','JSWSTEEL',
    'TATAMOTORS','TATASTEEL','INDUSINDBK','HDFCLIFE','SBILIFE',
    'DIVISLAB','DRREDDY','CIPLA','APOLLOHOSP','EICHERMOT',
    'GRASIM','HINDALCO','HEROMOTOCO','BPCL','BAJAJ-AUTO',
    'TATACONSUM','BRITANNIA','VEDL','UPL','SHREECEM',
    'ICICIGI','BOSCHLTD','SIEMENS','HAVELLS','PIIND',
    'GODREJCP','DABUR','MARICO','MCDOWELL-N','COLPAL',
    'AMBUJACEM','ACC','INDIGO','TATAPOWER','GAIL',
    'IOC','SBICARD','BANDHANBNK','BANKBARODA','PNB',
    'MUTHOOTFIN','CHOLAFIN','TORNTPHARM','LUPIN','BIOCON',
    'ALKEM','AUROPHARMA','ZYDUSLIFE','GLAXO','PAGEIND',
    'VOLTAS','CROMPTON','POLYCAB','CUMMINSIND','ABB',
    'BHEL','HAL','BEL','CONCOR','ADANIGREEN',
    'IRFC','PFC','RECLTD','M&M','TRENT',
]

NIFTY_MIDCAP150 = [
    'AARTIIND','AARTIDRUGS','ABCAPITAL','ABFRL','AEGISCHEM',
    'AJANTPHARM','APLAPOLLO','APLLTD','ASTRAL','ATUL',
    'AUBANK','BALKRISIND','BALRAMCHIN','BATAINDIA','BERGEPAINT',
    'BSOFT','BRIGADE','CANBK','CANFINHOME','CASTROLIND',
    'CEATLTD','CGPOWER','CHAMBLFERT','COFORGE','CRAFTSMAN',
    'CRISIL','CYIENT','DATAPATTNS','DEEPAKNTR','DELHIVERY',
    'DIXON','DLF','EIDPARRY','ELGIEQUIP','EMAMILTD','ENDURANCE',
    'ENGINERSIN','ESCORTS','EXIDEIND','FEDERALBNK','FLUOROCHEM',
    'FORTIS','GICRE','GNFC','GODREJIND','GODREJPROP','GRANULES',
    'GRINDWELL','GSFC','GSPL','HAPPSTMNDS','HEG','HFCL','HUDCO',
    'IDFCFIRSTB','IEX','IIFL','INDHOTEL','INDIANB','INDIAMART',
    'INTELLECT','JBCHEPHARM','JKCEMENT','JKLAKSHMI','JKPAPER',
    'JSL','JUBLFOOD','KAJARIACER','KALPATPOWR','KANSAINER','KEC',
    'KIMS','KPITTECH','KRBL','LALPATHLAB','LAURUSLABS','LICHSGFIN',
    'LINDEINDIA','LTIM','LTTS','M&MFIN','MANAPPURAM','MCX',
    'METROBRAND','METROPOLIS','MFSL','MOTILALOFS','MRF',
    'NATCOPHARM','NAVINFLUOR','NBCC','NCC','NIACL','NLCINDIA',
    'NMDC','NOCIL','OBEROIRLTY','OFSS','OIL','OLECTRA','PCBL',
    'PERSISTENT','PETRONET','PFIZER','PHOENIXLTD','POLYMED',
    'PRAJIND','PRESTIGE','PVRINOX','RADICO','RAMCOCEM','RAYMOND',
    'REDINGTON','RELAXO','RITES','ROUTE','SAIL','SCHAEFFLER',
    'SOBHA','SONATSOFTW','STLTECH','SUDARSCHEM','SUMICHEM',
    'SUNDARMFIN','SUNDRMFAST','SUNTV','SUPREMEIND','SUZLON',
    'SYNGENE','TANLA','TATACHEM','TATACOMM','TATAELXSI',
    'TEAMLEASE','TIMKEN','TORNTPOWER','TRENT','TRIDENT',
    'TVSMOTOR','UBL','UJJIVANSFB','UNIONBANK','VBL','VGUARD',
    'VINATIORGA','WELCORP','YESBANK','ZEEL','ZYDUSWELL',
    'DIXONTECH','JYOTHYLAB','APTUS','CAMPUS','CHALET','SENCO',
    'SIGNATURE','SAPPHIRE',
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
DATA_FILE  = "Master_Data.xlsx"
SHEET_NAME = "Nifty LMC 250"

@st.cache_data(ttl=3600, show_spinner="Loading Master_Data.xlsx…")
def load_data():
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame(), "FILE_MISSING"
    try:
        df = pd.read_excel(DATA_FILE, sheet_name=SHEET_NAME, engine="openpyxl")
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values(["Ticker", "Date"]).reset_index(drop=True)
        return df, None
    except Exception as e:
        return pd.DataFrame(), str(e)

master_df, err = load_data()

# ═══════════════════════════════════════════════════════════════════════════════
# ERROR STATES
# ═══════════════════════════════════════════════════════════════════════════════
st.title("📊 Nifty Technical Screener")

if err == "FILE_MISSING":
    st.error("""
    ### ⚠️ Master_Data.xlsx not found

    **Quick fix — Run the GitHub Action manually (first time only):**
    1. Go to your GitHub repository → **Actions** tab
    2. Click **"Daily Nifty Data Update"** in the left list
    3. Click **"Run workflow"** → **"Run workflow"**
    4. Wait ~10 minutes → `Master_Data.xlsx` will appear in your repo
    5. Come back here and reboot the Streamlit app

    Also ensure the workflow file is at `.github/workflows/daily_update.yml`
    """)
    st.stop()
elif err:
    st.error(f"Error reading data file: {err}")
    st.stop()
elif master_df.empty:
    st.warning("Data file is empty. Re-run the GitHub Action.")
    st.stop()

# ═══════════════════════════════════════════════════════════════════════════════
# SIGNAL COMPUTATION
# ═══════════════════════════════════════════════════════════════════════════════
def compute_signal(row):
    b, s = 0, 0
    rsi = row.get("RSI_14")
    if pd.notna(rsi):
        if rsi < 40: b += 1
        elif rsi > 60: s += 1
    mfi = row.get("MFI_14")
    if pd.notna(mfi):
        if mfi < 40: b += 1
        elif mfi > 60: s += 1
    cci = row.get("CCI_20")
    if pd.notna(cci):
        if cci < -80: b += 1
        elif cci > 80: s += 1
    wr = row.get("Williams_R_14")
    if pd.notna(wr):
        if wr < -80: b += 1
        elif wr > -20: s += 1
    cmf = row.get("CMF_20")
    if pd.notna(cmf):
        if cmf > 0.1: b += 1
        elif cmf < -0.1: s += 1
    adx = row.get("ADX_14"); pdi = row.get("+DI_14"); ndi = row.get("-DI_14")
    if pd.notna(adx) and adx > 25 and pd.notna(pdi) and pd.notna(ndi):
        if pdi > ndi: b += 1
        else: s += 1
    cl = row.get("Close"); sma20 = row.get("SMA_20")
    if pd.notna(cl) and pd.notna(sma20):
        if cl > sma20: b += 1
        else: s += 1
    if b > s + 1: return "BUY"
    if s > b + 1: return "SELL"
    return "NEUTRAL"

# ═══════════════════════════════════════════════════════════════════════════════
# INDICATOR CONFIG
# ═══════════════════════════════════════════════════════════════════════════════
ALL_INDICATOR_COLS = [
    ("RSI_14",        "RSI 14",         0.0,   100.0),
    ("MFI_14",        "MFI 14",         0.0,   100.0),
    ("CCI_20",        "CCI 20",        -500.0, 500.0),
    ("ROC_12",        "ROC 12 (%)",    -100.0, 100.0),
    ("Williams_R_14", "Williams %R",   -100.0, 0.0),
    ("Stoch_K_14",    "Stochastic %K",  0.0,   100.0),
    ("Stoch_D_3",     "Stochastic %D",  0.0,   100.0),
    ("ADX_14",        "ADX 14",         0.0,   100.0),
    ("+DI_14",        "+DI 14",         0.0,   100.0),
    ("-DI_14",        "-DI 14",         0.0,   100.0),
    ("ATR_14",        "ATR 14",         None,  None),
    ("CMF_20",        "CMF 20",        -1.0,   1.0),
    ("OBV",           "OBV",            None,  None),
    ("VWAP",          "VWAP",           None,  None),
    ("StdDev_20",     "Std Dev 20",     None,  None),
    ("Close",         "Close Price",    None,  None),
    ("SMA_20",        "SMA 20",         None,  None),
    ("SMA_50",        "SMA 50",         None,  None),
    ("SMA_100",       "SMA 100",        None,  None),
    ("EMA_20",        "EMA 20",         None,  None),
    ("EMA_50",        "EMA 50",         None,  None),
    ("EMA_100",       "EMA 100",        None,  None),
    ("DEMA_20",       "DEMA 20",        None,  None),
    ("DEMA_50",       "DEMA 50",        None,  None),
    ("DEMA_100",      "DEMA 100",       None,  None),
]

SLICER_GROUPS = {
    "📈 Momentum":       ["RSI_14","MFI_14","CCI_20","ROC_12","Williams_R_14","Stoch_K_14","Stoch_D_3"],
    "💪 Trend Strength": ["ADX_14","+DI_14","-DI_14","ATR_14"],
    "💰 Volume & Flow":  ["CMF_20","OBV","VWAP"],
    "📉 Volatility":     ["StdDev_20"],
    "📊 Price & MAs":    ["Close","SMA_20","SMA_50","EMA_20","EMA_50","DEMA_20","DEMA_50"],
}

ind_meta = {c[0]: c for c in ALL_INDICATOR_COLS}

DISPLAY_COLS = [
    "Ticker","Date","Open","High","Low","Close","Volume","Chg%",
    "SMA_20","EMA_20","DEMA_20","VWAP",
    "RSI_14","MFI_14","CCI_20","ROC_12",
    "Williams_R_14","Stoch_K_14","Stoch_D_3",
    "ADX_14","+DI_14","-DI_14","ATR_14",
    "CMF_20","OBV","StdDev_20","Signal",
]

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
date_min = master_df["Date"].min().date()
date_max = master_df["Date"].max().date()

with st.sidebar:
    st.header("🎛️ Filters & Slicers")

    # ── Index Universe selector ────────────────────────────────────────────────
    st.markdown('<div class="section-title">🗂️ Index Universe (Screener)</div>', unsafe_allow_html=True)
    universe_choice = st.radio(
        "universe",
        list(UNIVERSES.keys()),
        index=2,                   # default: LargeMidCap 250
        label_visibility="collapsed",
        key="universe_choice",
    )
    selected_tickers = UNIVERSES[universe_choice]
    universe_df      = master_df[master_df["Ticker"].isin(selected_tickers)].copy()
    universe_count   = universe_df["Ticker"].nunique()
    st.caption(f"{universe_count} stocks in selected universe")

    st.divider()

    # ── Date range ─────────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">📅 Date Range</div>', unsafe_allow_html=True)
    view_mode = st.radio(
        "View mode",
        ["Latest Day Only", "Date Range (Historical)"],
        horizontal=True, label_visibility="collapsed"
    )

    if view_mode == "Latest Day Only":
        selected_start = date_max
        selected_end   = date_max
    else:
        col_a, col_b = st.columns(2)
        with col_a:
            selected_start = st.date_input(
                "From", value=date_max - timedelta(days=30),
                min_value=date_min, max_value=date_max, key="d_start"
            )
        with col_b:
            selected_end = st.date_input(
                "To", value=date_max,
                min_value=date_min, max_value=date_max, key="d_end"
            )
        if selected_start > selected_end:
            st.error("'From' date must be before 'To' date.")
            st.stop()

    st.divider()

    # ── Search & Signal ────────────────────────────────────────────────────────
    search     = st.text_input("🔍 Search Ticker", placeholder="e.g. RELIANCE, TCS")
    sig_filter = st.selectbox("🚦 Signal Filter", ["ALL","BUY","SELL","NEUTRAL"])

    st.divider()

    # ── Filter mode ────────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">🔢 Filter Mode</div>', unsafe_allow_html=True)
    filter_mode = st.radio(
        "Choose how to filter indicators",
        ["Slider (Range)", "Typed Condition (>, <, between)"],
        label_visibility="collapsed"
    )

    st.divider()

    # ── Build filters ──────────────────────────────────────────────────────────
    active_slider_filters = {}
    active_cond_filters   = {}

    if filter_mode == "Slider (Range)":
        st.markdown('<div class="section-title">📊 Indicator Slicers</div>', unsafe_allow_html=True)
        for grp_name, cols in SLICER_GROUPS.items():
            with st.expander(grp_name, expanded=(grp_name == "📈 Momentum")):
                for col in cols:
                    if col not in universe_df.columns:
                        continue
                    _, label, d_min, d_max = ind_meta.get(col, (col, col, None, None))
                    vals = universe_df[col].dropna()
                    if vals.empty or vals.nunique() < 2:
                        continue
                    data_min = float(vals.min())
                    data_max = float(vals.max())
                    lo = d_min if d_min is not None else data_min
                    hi = d_max if d_max is not None else data_max
                    lo = max(lo, data_min); hi = min(hi, data_max)
                    if lo >= hi: lo, hi = data_min, data_max
                    step = round((data_max - data_min) / 200, 4) or 0.01
                    sel = st.slider(
                        label,
                        min_value=round(data_min, 2),
                        max_value=round(data_max, 2),
                        value=(round(lo, 2), round(hi, 2)),
                        step=step, key=f"sl_{col}"
                    )
                    if sel[0] > data_min or sel[1] < data_max:
                        active_slider_filters[col] = sel

    else:
        st.markdown('<div class="section-title">🔢 Typed Conditions</div>', unsafe_allow_html=True)
        st.caption("Set condition per indicator. Leave operator as '—' to skip.")
        OPERATOR_OPTIONS = ["—", "> Greater than", "< Less than",
                            ">= Greater than or equal", "<= Less than or equal",
                            "= Equal to", "Between (inclusive)"]
        for grp_name, cols in SLICER_GROUPS.items():
            with st.expander(grp_name, expanded=(grp_name == "📈 Momentum")):
                for col in cols:
                    if col not in universe_df.columns:
                        continue
                    _, label, _, _ = ind_meta.get(col, (col, col, None, None))
                    st.markdown(f"**{label}**")
                    op = st.selectbox("Operator", OPERATOR_OPTIONS,
                                      key=f"op_{col}", label_visibility="collapsed")
                    if op == "—":
                        continue
                    if op == "Between (inclusive)":
                        c1, c2 = st.columns(2)
                        v1 = c1.number_input("From", value=0.0, key=f"v1_{col}", label_visibility="collapsed")
                        v2 = c2.number_input("To",   value=100.0, key=f"v2_{col}", label_visibility="collapsed")
                        active_cond_filters[col] = ("between", v1, v2)
                    else:
                        v1 = st.number_input(f"Value for {label}", value=0.0,
                                             key=f"v_{col}", label_visibility="collapsed")
                        sym = op.split()[0]
                        active_cond_filters[col] = (sym, v1, None)

    st.divider()
    if st.button("🔄 Reset All Filters", width="stretch"):
        st.cache_data.clear()
        st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# FILTER DATA  (scoped to selected universe)
# ═══════════════════════════════════════════════════════════════════════════════

# 1. Date filter
date_filtered = universe_df[
    (universe_df["Date"].dt.date >= selected_start) &
    (universe_df["Date"].dt.date <= selected_end)
].copy()

# 2. Chg% computation
if view_mode == "Latest Day Only":
    prev_snap = (
        universe_df.groupby("Ticker")
        .apply(lambda g: g.sort_values("Date")["Close"].iloc[-2]
               if len(g) >= 2 else np.nan)
        .reset_index(name="PrevClose")
    )
    working = date_filtered.groupby("Ticker").tail(1).copy()
    working = working.merge(prev_snap, on="Ticker", how="left")
    working["Chg%"] = ((working["Close"] - working["PrevClose"]) /
                       working["PrevClose"] * 100).round(2)
    working.drop(columns=["PrevClose"], inplace=True, errors="ignore")
else:
    date_filtered = date_filtered.sort_values(["Ticker","Date"])
    date_filtered["PrevClose"] = date_filtered.groupby("Ticker")["Close"].shift(1)
    date_filtered["Chg%"] = (
        (date_filtered["Close"] - date_filtered["PrevClose"]) /
        date_filtered["PrevClose"] * 100
    ).round(2)
    date_filtered.drop(columns=["PrevClose"], inplace=True, errors="ignore")
    working = date_filtered.copy()

# 3. Signal
working["Signal"] = working.apply(compute_signal, axis=1)

# 4. Ticker search
if search.strip():
    q = search.upper().strip()
    working = working[working["Ticker"].str.contains(q, na=False)]

# 5. Signal filter
if sig_filter != "ALL":
    working = working[working["Signal"] == sig_filter]

# 6. Slider filters
for col, (lo, hi) in active_slider_filters.items():
    if col in working.columns:
        working = working[(working[col] >= lo) & (working[col] <= hi)]

# 7. Typed condition filters
OP_MAP = {
    ">":       lambda s, v1, v2: s > v1,
    "<":       lambda s, v1, v2: s < v1,
    ">=":      lambda s, v1, v2: s >= v1,
    "<=":      lambda s, v1, v2: s <= v1,
    "=":       lambda s, v1, v2: s == v1,
    "between": lambda s, v1, v2: (s >= v1) & (s <= v2),
}
for col, (op, v1, v2) in active_cond_filters.items():
    if col in working.columns:
        mask = OP_MAP[op](working[col], v1, v2)
        working = working[mask]

filtered = working.copy()

# ═══════════════════════════════════════════════════════════════════════════════
# DASHBOARD HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
def latest_snapshot(tickers_set):
    """Latest-day row per ticker for the given index, with Signal + Chg%."""
    sub = master_df[master_df["Ticker"].isin(tickers_set)].copy()
    prev = (
        sub.groupby("Ticker")
        .apply(lambda g: g.sort_values("Date")["Close"].iloc[-2]
               if len(g) >= 2 else np.nan)
        .reset_index(name="PrevClose")
    )
    snap = sub.groupby("Ticker").tail(1).copy()
    snap = snap.merge(prev, on="Ticker", how="left")
    snap["Chg%"] = ((snap["Close"] - snap["PrevClose"]) /
                    snap["PrevClose"] * 100).round(2)
    snap.drop(columns=["PrevClose"], inplace=True, errors="ignore")
    snap["Signal"] = snap.apply(compute_signal, axis=1)
    return snap

def index_stats(snap):
    total  = len(snap)
    adv    = int((snap["Chg%"] > 0).sum())
    dec    = int((snap["Chg%"] < 0).sum())
    unch   = total - adv - dec
    buy_c  = int((snap["Signal"] == "BUY").sum())
    sell_c = int((snap["Signal"] == "SELL").sum())
    neut_c = int((snap["Signal"] == "NEUTRAL").sum())
    avg_r  = snap["RSI_14"].mean() if "RSI_14" in snap.columns else None
    avg_a  = snap["ADX_14"].mean() if "ADX_14" in snap.columns else None
    return dict(total=total, adv=adv, dec=dec, unch=unch,
                buy=buy_c, sell=sell_c, neut=neut_c,
                avg_rsi=avg_r, avg_adx=avg_a)

def render_index_detail(label, snap):
    """Detailed breakdown card for one index inside the dashboard."""
    s = index_stats(snap)
    st.markdown(f"### {label}")
    m = st.columns(9)
    m[0].metric("Stocks",       s["total"])
    m[1].metric("🟢 Advancing", s["adv"])
    m[2].metric("🔴 Declining", s["dec"])
    m[3].metric("⚪ Unchanged", s["unch"])
    m[4].metric("🟢 BUY",       s["buy"])
    m[5].metric("🔴 SELL",      s["sell"])
    m[6].metric("🟡 NEUTRAL",   s["neut"])
    m[7].metric("Avg RSI", f"{s['avg_rsi']:.1f}" if s["avg_rsi"] is not None else "—")
    m[8].metric("Avg ADX", f"{s['avg_adx']:.1f}" if s["avg_adx"] is not None else "—")

    g1, g2 = st.columns(2)
    with g1:
        st.markdown("**🏆 Top 5 Gainers**")
        top = snap.nlargest(5, "Chg%")[["Ticker","Close","Chg%","Signal"]].reset_index(drop=True)
        st.dataframe(top, hide_index=True, width="stretch")
    with g2:
        st.markdown("**💔 Top 5 Losers**")
        bot = snap.nsmallest(5, "Chg%")[["Ticker","Close","Chg%","Signal"]].reset_index(drop=True)
        st.dataframe(bot, hide_index=True, width="stretch")

    # BUY / SELL lists
    b1, b2 = st.columns(2)
    with b1:
        st.markdown("**🟢 BUY Signal Stocks**")
        buys = snap[snap["Signal"] == "BUY"][["Ticker","Close","Chg%","RSI_14","ADX_14"]].reset_index(drop=True)
        if buys.empty:
            st.caption("None today")
        else:
            st.dataframe(buys, hide_index=True, width="stretch")
    with b2:
        st.markdown("**🔴 SELL Signal Stocks**")
        sells = snap[snap["Signal"] == "SELL"][["Ticker","Close","Chg%","RSI_14","ADX_14"]].reset_index(drop=True)
        if sells.empty:
            st.caption("None today")
        else:
            st.dataframe(sells, hide_index=True, width="stretch")

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN TABS
# ═══════════════════════════════════════════════════════════════════════════════
tab_screener, tab_dashboard = st.tabs(["🔍 Screener", "📊 Dashboard"])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1  — SCREENER
# ─────────────────────────────────────────────────────────────────────────────
with tab_screener:

    shown    = len(filtered)
    adv      = int((filtered["Chg%"] > 0).sum()) if "Chg%" in filtered.columns else 0
    dec      = int((filtered["Chg%"] < 0).sum()) if "Chg%" in filtered.columns else 0
    buy_ct   = int((filtered["Signal"] == "BUY").sum())
    sell_ct  = int((filtered["Signal"] == "SELL").sum())
    neut_ct  = int((filtered["Signal"] == "NEUTRAL").sum())
    avg_rsi  = filtered["RSI_14"].mean() if "RSI_14" in filtered.columns and not filtered["RSI_14"].isna().all() else None
    avg_adx  = filtered["ADX_14"].mean() if "ADX_14" in filtered.columns and not filtered["ADX_14"].isna().all() else None

    date_label = (
        f"{selected_start.strftime('%d-%b-%Y')}"
        if selected_start == selected_end
        else f"{selected_start.strftime('%d-%b-%Y')} → {selected_end.strftime('%d-%b-%Y')}"
    )

    st.caption(
        f"📅 **{date_label}**  ·  "
        f"🗂️ Universe: **{universe_choice}** ({universe_count} stocks)  ·  "
        f"Data refreshed daily via GitHub Actions"
    )

    c1,c2,c3,c4,c5,c6,c7,c8,c9 = st.columns(9)
    c1.metric("Universe",      universe_count)
    c2.metric("Rows Shown",    shown)
    c3.metric("🟢 Advancing",  adv)
    c4.metric("🔴 Declining",  dec)
    c5.metric("🟢 BUY",        buy_ct)
    c6.metric("🔴 SELL",       sell_ct)
    c7.metric("🟡 NEUTRAL",    neut_ct)
    c8.metric("Avg RSI",  f"{avg_rsi:.1f}" if avg_rsi is not None else "—")
    c9.metric("Avg ADX",  f"{avg_adx:.1f}" if avg_adx is not None else "—")

    st.divider()

    # Active filter banner
    active_tags = []
    for col, (lo, hi) in active_slider_filters.items():
        _, label, _, _ = ind_meta.get(col, (col,col,None,None))
        active_tags.append(f"**{label}**: {lo:.2f} – {hi:.2f}")
    for col, (op, v1, v2) in active_cond_filters.items():
        _, label, _, _ = ind_meta.get(col, (col,col,None,None))
        if op == "between":
            active_tags.append(f"**{label}**: {v1} ≤ x ≤ {v2}")
        else:
            active_tags.append(f"**{label}** {op} {v1}")
    if active_tags:
        st.info("Active filters: " + "  |  ".join(active_tags))

    # Main table
    st.subheader(f"📋 {shown} rows match your filters")
    present_cols = [c for c in DISPLAY_COLS if c in filtered.columns]
    display = filtered[present_cols].copy()

    sc1, sc2, _ = st.columns([3, 1, 5])
    with sc1:
        sort_options = [c for c in present_cols if c not in ("Ticker","Signal","Date")]
        default_sort = "Chg%" if "Chg%" in sort_options else sort_options[0]
        sort_col = st.selectbox("Sort by", sort_options,
                                index=sort_options.index(default_sort), key="sort_col")
    with sc2:
        sort_asc = st.checkbox("Asc ↑", value=False, key="sort_asc")

    display = display.sort_values(sort_col, ascending=sort_asc, na_position="last")

    if display.empty:
        st.warning("No rows match the current filters. Widen your date range or relax indicator conditions.")
    else:
        def style_table(df):
            styles = pd.DataFrame("", index=df.index, columns=df.columns)
            if "Signal" in df.columns:
                styles["Signal"] = df["Signal"].map({
                    "BUY":     "color:#00ffa3;font-weight:bold",
                    "SELL":    "color:#ff3b5c;font-weight:bold",
                    "NEUTRAL": "color:#ffcc00;font-weight:bold",
                }).fillna("")
            if "Chg%" in df.columns:
                styles["Chg%"] = df["Chg%"].apply(
                    lambda v: "color:#00ffa3" if pd.notna(v) and v > 0
                    else ("color:#ff3b5c" if pd.notna(v) and v < 0 else ""))
            if "RSI_14" in df.columns:
                styles["RSI_14"] = df["RSI_14"].apply(
                    lambda v: "color:#00ffa3" if pd.notna(v) and v < 30
                    else ("color:#ff3b5c" if pd.notna(v) and v > 70 else ""))
            if "CMF_20" in df.columns:
                styles["CMF_20"] = df["CMF_20"].apply(
                    lambda v: "color:#00ffa3" if pd.notna(v) and v > 0.1
                    else ("color:#ff3b5c" if pd.notna(v) and v < -0.1 else ""))
            if "ADX_14" in df.columns:
                styles["ADX_14"] = df["ADX_14"].apply(
                    lambda v: "color:#00ffa3" if pd.notna(v) and v > 25 else "")
            return styles

        num_cols = display.select_dtypes("number").columns
        fmt = {c: "{:.2f}" for c in num_cols}
        if "OBV"    in fmt: fmt["OBV"]    = "{:,.0f}"
        if "Volume" in fmt: fmt["Volume"] = "{:,.0f}"
        if "Chg%"   in fmt: fmt["Chg%"]   = "{:+.2f}%"
        if "Date" in display.columns:
            display["Date"] = display["Date"].dt.strftime("%d-%b-%Y")

        MAX_STYLED_CELLS = 200_000
        total_cells = display.shape[0] * display.shape[1]

        if total_cells <= MAX_STYLED_CELLS:
            pd.set_option("styler.render.max_elements", total_cells)
            styled = display.style.apply(style_table, axis=None).format(fmt, na_rep="—")
            st.dataframe(styled, width="stretch", height=580)
        else:
            st.info(
                f"ℹ️ {len(display):,} rows across a wide date range — "
                f"colour-coding disabled above {MAX_STYLED_CELLS // display.shape[1]:,} rows. "
                f"Data is complete and accurate."
            )
            fmt_display = display.copy()
            for col, f in fmt.items():
                if col in fmt_display.columns:
                    try:
                        fmt_display[col] = fmt_display[col].apply(
                            lambda v, f=f: f.format(v) if pd.notna(v) else "—"
                        )
                    except Exception:
                        pass
            st.dataframe(fmt_display, width="stretch", height=580)

    st.divider()

    # Downloads
    st.subheader("⬇️ Downloads")

    # Build a clean slug for filenames: "Nifty100", "NiftyMidCap150", "NiftyLMC250"
    _universe_slug = (
        universe_choice
        .replace("🏆 ", "").replace("🥈 ", "").replace("🌐 ", "")
        .replace(" ", "")
    )
    _date_slug = f"{selected_start}_{selected_end}"

    st.caption(
        f"All downloads are scoped to **{universe_choice}** ({universe_count} stocks) "
        f"for the period **{date_label}**."
    )

    dl1, dl2, dl3 = st.columns(3)

    # Button 1 — what's visible in the table (sorted + signal/indicator filtered)
    with dl1:
        if not display.empty:
            st.download_button(
                "📄 Filtered View (CSV)",
                data=display.to_csv(index=False).encode("utf-8"),
                file_name=f"{_universe_slug}_Filtered_{_date_slug}.csv",
                mime="text/csv", width="stretch",
                help=f"{len(display):,} rows — exactly what's shown in the table above"
            )
        else:
            st.button("📄 Filtered View (CSV)", disabled=True, width="stretch")

    # Button 2 — all universe+date rows before signal/indicator filters
    with dl2:
        if not filtered.empty:
            st.download_button(
                "📊 Full Universe Selection (CSV)",
                data=filtered.to_csv(index=False).encode("utf-8"),
                file_name=f"{_universe_slug}_Full_{_date_slug}.csv",
                mime="text/csv", width="stretch",
                help=f"{len(filtered):,} rows — all {universe_choice} stocks for the selected date range, all indicators included"
            )
        else:
            st.button("📊 Full Universe Selection (CSV)", disabled=True, width="stretch")

    # Button 3 — raw master file (all 250 stocks, full history)
    with dl3:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "rb") as f:
                master_bytes = f.read()
            st.download_button(
                "📦 Master_Data.xlsx (All 250 stocks, full history)",
                data=master_bytes, file_name="Master_Data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                width="stretch",
                help="Raw unfiltered file — all Nifty LMC 250 stocks from 2021 onwards"
            )
        else:
            st.button("📦 Master_Data.xlsx", disabled=True, width="stretch",
                      help="File not found on server")

    st.divider()
    st.caption(
        f"📡 Source: Yahoo Finance via yfinance  ·  "
        f"🤖 Auto-updated daily at 6 PM IST via GitHub Actions  ·  "
        f"📅 Data available: {date_min.strftime('%d-%b-%Y')} → {date_max.strftime('%d-%b-%Y')}"
    )

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2  — DASHBOARD  (always latest-day, all 3 indices)
# ─────────────────────────────────────────────────────────────────────────────
with tab_dashboard:

    st.caption(
        f"Latest available trading day: **{date_max.strftime('%d-%b-%Y')}**  ·  "
        f"All three indices shown simultaneously — independent of Screener filters"
    )

    # Pre-compute snapshots (cached implicitly via master_df which is cached)
    snap100 = latest_snapshot(UNIVERSES["🏆 Nifty 100"])
    snap150 = latest_snapshot(UNIVERSES["🥈 Nifty MidCap 150"])
    snap250 = latest_snapshot(UNIVERSES["🌐 Nifty LargeMidCap 250"])

    # ── Side-by-side summary cards ─────────────────────────────────────────────
    st.subheader("📈 Market Overview — Latest Day")
    d1, d2, d3 = st.columns(3)

    def summary_card(col, label, snap):
        s = index_stats(snap)
        t = s["total"]
        pct = lambda x: f"({round(x/t*100)}%)" if t else ""
        with col:
            st.markdown(f"**{label}**")
            st.metric("Total Stocks",    t)
            st.metric("🟢 Advancing",   f"{s['adv']}  {pct(s['adv'])}")
            st.metric("🔴 Declining",   f"{s['dec']}  {pct(s['dec'])}")
            st.metric("⚪ Unchanged",   f"{s['unch']} {pct(s['unch'])}")
            st.metric("🟢 BUY Signal",  f"{s['buy']}  {pct(s['buy'])}")
            st.metric("🔴 SELL Signal", f"{s['sell']} {pct(s['sell'])}")
            st.metric("🟡 NEUTRAL",     f"{s['neut']} {pct(s['neut'])}")
            st.metric("Avg RSI", f"{s['avg_rsi']:.1f}" if s["avg_rsi"] is not None else "—")
            st.metric("Avg ADX", f"{s['avg_adx']:.1f}" if s["avg_adx"] is not None else "—")

    summary_card(d1, "🏆 Nifty 100",             snap100)
    summary_card(d2, "🥈 Nifty MidCap 150",      snap150)
    summary_card(d3, "🌐 Nifty LargeMidCap 250", snap250)

    st.divider()

    # ── Signal distribution comparison table ──────────────────────────────────
    st.subheader("📊 Signal Distribution Comparison")
    cmp_rows = []
    for lbl, snap in [("Nifty 100", snap100), ("Nifty MidCap 150", snap150), ("Nifty LMC 250", snap250)]:
        s = index_stats(snap)
        t = s["total"]
        cmp_rows.append({
            "Index":      lbl,
            "Total":      t,
            "Advancing":  s["adv"],
            "Declining":  s["dec"],
            "BUY":        s["buy"],
            "SELL":       s["sell"],
            "NEUTRAL":    s["neut"],
            "BUY %":      f"{round(s['buy']/t*100)}%"  if t else "—",
            "SELL %":     f"{round(s['sell']/t*100)}%" if t else "—",
            "Avg RSI":    f"{s['avg_rsi']:.1f}" if s["avg_rsi"] is not None else "—",
            "Avg ADX":    f"{s['avg_adx']:.1f}" if s["avg_adx"] is not None else "—",
        })
    st.dataframe(pd.DataFrame(cmp_rows), hide_index=True, width="stretch")

    st.divider()

    # ── Per-index detailed breakdown (nested tabs) ─────────────────────────────
    st.subheader("🔎 Detailed Breakdown by Index")
    idx_tab1, idx_tab2, idx_tab3 = st.tabs([
        "🏆 Nifty 100",
        "🥈 Nifty MidCap 150",
        "🌐 Nifty LargeMidCap 250",
    ])
    with idx_tab1:
        render_index_detail("🏆 Nifty 100", snap100)
    with idx_tab2:
        render_index_detail("🥈 Nifty MidCap 150", snap150)
    with idx_tab3:
        render_index_detail("🌐 Nifty LargeMidCap 250", snap250)

    st.divider()
    st.caption(
        f"📡 Source: Yahoo Finance via yfinance  ·  "
        f"🤖 Auto-updated daily at 6 PM IST via GitHub Actions  ·  "
        f"📅 Data available: {date_min.strftime('%d-%b-%Y')} → {date_max.strftime('%d-%b-%Y')}"
    )
