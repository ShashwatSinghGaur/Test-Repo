import yfinance as yf
import pandas as pd
import numpy as np
from datetime import date, timedelta
import os, gc

# --- TICKERS ---
NIFTY100 = [
    'RELIANCE.NS','TCS.NS','HDFCBANK.NS','BHARTIARTL.NS','ICICIBANK.NS',
    'INFOSYS.NS','SBIN.NS','HINDUNILVR.NS','ITC.NS','LT.NS',
    'KOTAKBANK.NS','AXISBANK.NS','BAJFINANCE.NS','MARUTI.NS','ASIANPAINT.NS',
    'TITAN.NS','SUNPHARMA.NS','NESTLEIND.NS','WIPRO.NS','HCLTECH.NS',
    'NTPC.NS','POWERGRID.NS','TECHM.NS','ONGC.NS','COALINDIA.NS',
    'BAJAJFINSV.NS','ADANIENT.NS','ADANIPORTS.NS','ULTRACEMCO.NS','JSWSTEEL.NS',
    'TATAMOTORS.NS','TATASTEEL.NS','INDUSINDBK.NS','HDFCLIFE.NS','SBILIFE.NS',
    'DIVISLAB.NS','DRREDDY.NS','CIPLA.NS','APOLLOHOSP.NS','EICHERMOT.NS',
    'GRASIM.NS','HINDALCO.NS','HEROMOTOCO.NS','BPCL.NS','BAJAJ-AUTO.NS',
    'TATACONSUM.NS','BRITANNIA.NS','VEDL.NS','UPL.NS','SHREECEM.NS',
    'ICICIGI.NS','BOSCHLTD.NS','SIEMENS.NS','HAVELLS.NS','PIIND.NS',
    'GODREJCP.NS','DABUR.NS','MARICO.NS','MCDOWELL-N.NS','COLPAL.NS',
    'AMBUJACEM.NS','ACC.NS','INDIGO.NS','TATAPOWER.NS','GAIL.NS',
    'IOC.NS','SBICARD.NS','BANDHANBNK.NS','BANKBARODA.NS','PNB.NS',
    'MUTHOOTFIN.NS','CHOLAFIN.NS','TORNTPHARM.NS','LUPIN.NS','BIOCON.NS',
    'ALKEM.NS','AUROPHARMA.NS','ZYDUSLIFE.NS','GLAXO.NS','PAGEIND.NS',
    'VOLTAS.NS','CROMPTON.NS','POLYCAB.NS','CUMMINSIND.NS','ABB.NS',
    'BHEL.NS','HAL.NS','BEL.NS','CONCOR.NS','ADANIGREEN.NS',
    'IRFC.NS','PFC.NS','RECLTD.NS','M&M.NS','TRENT.NS',
]

NIFTY_MIDCAP150 = [
    'AARTIIND.NS','AARTIDRUGS.NS','ABCAPITAL.NS','ABFRL.NS','AEGISCHEM.NS',
    'AJANTPHARM.NS','APLAPOLLO.NS','APLLTD.NS','ASTRAL.NS','ATUL.NS',
    'AUBANK.NS','BALKRISIND.NS','BALRAMCHIN.NS','BATAINDIA.NS','BERGEPAINT.NS',
    'BSOFT.NS','BRIGADE.NS','CANBK.NS','CANFINHOME.NS','CASTROLIND.NS',
    'CEATLTD.NS','CGPOWER.NS','CHAMBLFERT.NS','COFORGE.NS','CRAFTSMAN.NS',
    'CRISIL.NS','CYIENT.NS','DATAPATTNS.NS','DEEPAKNTR.NS','DELHIVERY.NS',
    'DIXON.NS','DLF.NS','EIDPARRY.NS','ELGIEQUIP.NS','EMAMILTD.NS','ENDURANCE.NS',
    'ENGINERSIN.NS','ESCORTS.NS','EXIDEIND.NS','FEDERALBNK.NS','FLUOROCHEM.NS',
    'FORTIS.NS','GICRE.NS','GNFC.NS','GODREJIND.NS','GODREJPROP.NS','GRANULES.NS',
    'GRINDWELL.NS','GSFC.NS','GSPL.NS','HAPPSTMNDS.NS','HEG.NS','HFCL.NS','HUDCO.NS',
    'IDFCFIRSTB.NS','IEX.NS','IIFL.NS','INDHOTEL.NS','INDIANB.NS','INDIAMART.NS',
    'INTELLECT.NS','JBCHEPHARM.NS','JKCEMENT.NS','JKLAKSHMI.NS','JKPAPER.NS',
    'JSL.NS','JUBLFOOD.NS','KAJARIACER.NS','KALPATPOWR.NS','KANSAINER.NS','KEC.NS',
    'KIMS.NS','KPITTECH.NS','KRBL.NS','LALPATHLAB.NS','LAURUSLABS.NS','LICHSGFIN.NS',
    'LINDEINDIA.NS','LTIM.NS','LTTS.NS','M&MFIN.NS','MANAPPURAM.NS','MCX.NS',
    'METROBRAND.NS','METROPOLIS.NS','MFSL.NS','MOTILALOFS.NS','MRF.NS',
    'NATCOPHARM.NS','NAVINFLUOR.NS','NBCC.NS','NCC.NS','NIACL.NS','NLCINDIA.NS',
    'NMDC.NS','NOCIL.NS','OBEROIRLTY.NS','OFSS.NS','OIL.NS','OLECTRA.NS','PCBL.NS',
    'PERSISTENT.NS','PETRONET.NS','PFIZER.NS','PHOENIXLTD.NS','POLYMED.NS',
    'PRAJIND.NS','PRESTIGE.NS','PVRINOX.NS','RADICO.NS','RAMCOCEM.NS','RAYMOND.NS',
    'REDINGTON.NS','RELAXO.NS','RITES.NS','ROUTE.NS','SAIL.NS','SCHAEFFLER.NS',
    'SOBHA.NS','SONATSOFTW.NS','STLTECH.NS','SUDARSCHEM.NS','SUMICHEM.NS',
    'SUNDARMFIN.NS','SUNDRMFAST.NS','SUNTV.NS','SUPREMEIND.NS','SUZLON.NS',
    'SYNGENE.NS','TANLA.NS','TATACHEM.NS','TATACOMM.NS','TATAELXSI.NS',
    'TEAMLEASE.NS','TIMKEN.NS','TORNTPOWER.NS','TRENT.NS','TRIDENT.NS',
    'TVSMOTOR.NS','UBL.NS','UJJIVANSFB.NS','UNIONBANK.NS','VBL.NS','VGUARD.NS',
    'VINATIORGA.NS','WELCORP.NS','YESBANK.NS','ZEEL.NS','ZYDUSWELL.NS',
    'DIXONTECH.NS','JYOTHYLAB.NS','APTUS.NS','CAMPUS.NS','CHALET.NS','SENCO.NS',
    'SIGNATURE.NS','SAPPHIRE.NS',
]

ALL_TICKERS = list(dict.fromkeys(NIFTY100 + NIFTY_MIDCAP150))
DATA_FILE   = "Master_Data.xlsx"
SHEET_NAME  = "Nifty LMC 250"

# --- UPDATED DATES ---
BUFFER_START  = date(2020, 5, 1)   # Fetch from here to warm up MAs
DISPLAY_START = date(2021, 1, 1)   # Show from here in Excel

# --- INDICATORS ---
def sma(s, n): return s.rolling(n).mean()
def ema(s, n): return s.ewm(span=n, adjust=False, min_periods=n).mean()
def dema(s, n): e1=ema(s,n); e2=ema(e1,n); return 2*e1-e2

def compute_rsi(s, n=14):
    d=s.diff(); ag=d.clip(lower=0).ewm(com=n-1,min_periods=n).mean()
    al=(-d.clip(upper=0)).ewm(com=n-1,min_periods=n).mean()
    return 100-100/(1+ag/al.replace(0,np.nan))

def compute_atr(h,l,c,n=14):
    tr=pd.concat([h-l,(h-c.shift()).abs(),(l-c.shift()).abs()],axis=1).max(axis=1)
    return tr.ewm(alpha=1/n,adjust=False,min_periods=n).mean()

def compute_adx(h,l,c,n=14):
    up=h.diff(); dn=-l.diff()
    pdm=pd.Series(np.where((up>dn)&(up>0),up,0.),index=h.index)
    ndm=pd.Series(np.where((dn>up)&(dn>0),dn,0.),index=h.index)
    atr_=compute_atr(h,l,c,n)
    pdi=100*pdm.ewm(alpha=1/n,adjust=False,min_periods=n).mean()/atr_
    ndi=100*ndm.ewm(alpha=1/n,adjust=False,min_periods=n).mean()/atr_
    dx=100*(pdi-ndi).abs()/(pdi+ndi).replace(0,np.nan)
    return pdi,ndi,dx.ewm(alpha=1/n,adjust=False,min_periods=n).mean()

def compute_cci(h,l,c,n=20):
    tp=(h+l+c)/3; m=tp.rolling(n).mean()
    mad=tp.rolling(n).apply(lambda x:np.mean(np.abs(x-np.mean(x))),raw=True)
    return (tp-m)/(0.015*mad)

def compute_roc(c,n=12): return ((c-c.shift(n))/c.shift(n))*100

def compute_mfi(h,l,c,v,n=14):
    tp=(h+l+c)/3; rmf=tp*v
    pos=rmf.where(tp>tp.shift(),0); neg=rmf.where(tp<tp.shift(),0)
    return 100-100/(1+pos.rolling(n).sum()/neg.rolling(n).sum().replace(0,np.nan))

def compute_willr(h,l,c,n=14):
    return -100*(h.rolling(n).max()-c)/(h.rolling(n).max()-l.rolling(n).min()).replace(0,np.nan)

def compute_stoch(h,l,c,k=14,d=3):
    ll=l.rolling(k).min(); hh=h.rolling(k).max()
    K=100*(c-ll)/(hh-ll).replace(0,np.nan)
    return K,K.rolling(d).mean()

def compute_obv(c,v):   return (v*np.sign(c.diff()).fillna(0)).cumsum()
def compute_vwap(h,l,c,v):
    tp=(h+l+c)/3; return (tp*v).cumsum()/v.cumsum().replace(0,np.nan)
def compute_cmf(h,l,c,v,n=20):
    clv=((c-l)-(h-c))/(h-l).replace(0,np.nan)
    return (clv*v).rolling(n).sum()/v.rolling(n).sum().replace(0,np.nan)
def compute_std(c,n=20): return c.rolling(n).std()

def add_all(df):
    c,h,l,v=df['Close'],df['High'],df['Low'],df['Volume']
    for n in [20,50,100]:
        df[f'SMA_{n}']=sma(c,n); df[f'EMA_{n}']=ema(c,n); df[f'DEMA_{n}']=dema(c,n)
    df['RSI_14']=compute_rsi(c); df['ATR_14']=compute_atr(h,l,c)
    p,nd,ad=compute_adx(h,l,c)
    df['ADX_14']=ad; df['+DI_14']=p; df['-DI_14']=nd
    df['CCI_20']=compute_cci(h,l,c); df['ROC_12']=compute_roc(c)
    df['MFI_14']=compute_mfi(h,l,c,v); df['Williams_R_14']=compute_willr(h,l,c)
    K,D=compute_stoch(h,l,c); df['Stoch_K_14']=K; df['Stoch_D_3']=D
    df['OBV']=compute_obv(c,v); df['VWAP']=compute_vwap(h,l,c,v)
    df['CMF_20']=compute_cmf(h,l,c,v); df['StdDev_20']=compute_std(c)
    return df.round(2)

def compress(df):
    for col in df.select_dtypes('float64').columns:
        df[col]=df[col].astype('float32')
    return df

# --- FETCH START LOGIC ---
def get_fetch_start():
    if os.path.exists(DATA_FILE):
        try:
            existing = pd.read_excel(DATA_FILE, sheet_name=SHEET_NAME, usecols=['Date'], engine='openpyxl')
            existing['Date'] = pd.to_datetime(existing['Date'])
            last_date = existing['Date'].max().date()
            
            # CHECK: If the file only goes to April 2025, force a re-fetch of recent months
            if last_date < date(2026, 1, 1):
                 print(f"File is too old ({last_date}). Forcing full fetch.")
                 return BUFFER_START, False
            
            fetch_from = last_date - timedelta(days=5)
            return fetch_from, True
        except Exception:
            pass
    return BUFFER_START, False

# --- MAIN ---
def main():
    today = date.today()
    fetch_start, is_incremental = get_fetch_start()

    print(f"Fetching from {fetch_start} to {today}...")

    new_frames = []
    chunk_size = 15 # Smaller chunks to avoid Yahoo timeouts

    for i in range(0, len(ALL_TICKERS), chunk_size):
        chunk = ALL_TICKERS[i:i+chunk_size]
        try:
            raw = yf.download(chunk, start=fetch_start.strftime('%Y-%m-%d'),
                               group_by='ticker', auto_adjust=True, progress=False)
            
            for ticker in chunk:
                try:
                    df_t = raw[ticker].copy() if len(chunk) > 1 else raw.copy()
                    df_t = df_t[['Open','High','Low','Close','Volume']].dropna()
                    if df_t.empty: continue

                    # If incremental, we still need context to calculate indicators correctly
                    if is_incremental:
                        hist = yf.download(ticker, start=BUFFER_START.strftime('%Y-%m-%d'),
                                           end=(fetch_start - timedelta(days=1)).strftime('%Y-%m-%d'),
                                           auto_adjust=True, progress=False)
                        if isinstance(hist.columns, pd.MultiIndex): hist.columns = hist.columns.get_level_values(0)
                        combined = pd.concat([hist[['Open','High','Low','Close','Volume']], df_t]).sort_index()
                        combined = combined[~combined.index.duplicated(keep='last')]
                        df_indicators = add_all(combined)
                    else:
                        df_indicators = add_all(df_t)

                    # TRIM: Remove buffer data (2020) and only keep from 2021 onwards
                    df_final = df_indicators[df_indicators.index >= pd.Timestamp(DISPLAY_START)]
                    
                    if not df_final.empty:
                        df_final.insert(0, 'Ticker', ticker.replace('.NS',''))
                        df_final = df_final.reset_index().rename(columns={'Date':'Date', 'index':'Date'})
                        df_final['Date'] = pd.to_datetime(df_final['Date']).dt.strftime('%Y-%m-%d')
                        new_frames.append(compress(df_final))
                except Exception: continue
        except Exception: continue
        gc.collect()

    if not new_frames:
        print("No new data.")
        return

    result_df = pd.concat(new_frames, ignore_index=True)
    
    if is_incremental and os.path.exists(DATA_FILE):
        existing_df = pd.read_excel(DATA_FILE, sheet_name=SHEET_NAME, engine='openpyxl')
        existing_df['Date'] = pd.to_datetime(existing_df['Date']).dt.strftime('%Y-%m-%d')
        overlap_dates = set(result_df['Date'].unique())
        master_df = pd.concat([existing_df[~existing_df['Date'].isin(overlap_dates)], result_df])
    else:
        master_df = result_df

    master_df.sort_values(['Ticker','Date']).to_excel(DATA_FILE, sheet_name=SHEET_NAME, index=False)
    print("✅ Successfully Updated Master_Data.xlsx")

if __name__ == "__main__":
    main()
