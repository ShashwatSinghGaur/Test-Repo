import yfinance as yf
import pandas as pd
import pandas_ta_classic as ta
import numpy as np
from datetime import date, timedelta
import os, gc

# --- TICKERS ---
NIFTY100 = [
    'RELIANCE.NS','TCS.NS','HDFCBANK.NS','BHARTIARTL.NS','ICICIBANK.NS',
    'INFOSYS.NS','SBIN.NS','HINDUNILVR.NS','ITC.NS','LT.NS','KOTAKBANK.NS',
    'AXISBANK.NS','BAJFINANCE.NS','MARUTI.NS','ASIANPAINT.NS','TITAN.NS',
    'SUNPHARMA.NS','NESTLEIND.NS','WIPRO.NS','HCLTECH.NS','NTPC.NS',
    'POWERGRID.NS','TECHM.NS','ONGC.NS','COALINDIA.NS','BAJAJFINSV.NS',
    'ADANIENT.NS','ADANIPORTS.NS','ULTRACEMCO.NS','JSWSTEEL.NS','TATAMOTORS.NS',
    'TATASTEEL.NS','INDUSINDBK.NS','HDFCLIFE.NS','SBILIFE.NS','DIVISLAB.NS',
    'DRREDDY.NS','CIPLA.NS','APOLLOHOSP.NS','EICHERMOT.NS','GRASIM.NS',
    'HINDALCO.NS','HEROMOTOCO.NS','BPCL.NS','BAJAJ-AUTO.NS','TATACONSUM.NS',
    'BRITANNIA.NS','VEDL.NS','UPL.NS','SHREECEM.NS','ICICIGI.NS','BOSCHLTD.NS',
    'SIEMENS.NS','HAVELLS.NS','PIIND.NS','GODREJCP.NS','DABUR.NS','MARICO.NS',
    'MCDOWELL-N.NS','COLPAL.NS','AMBUJACEM.NS','ACC.NS','INDIGO.NS','TATAPOWER.NS',
    'GAIL.NS','IOC.NS','SBICARD.NS','BANDHANBNK.NS','BANKBARODA.NS','PNB.NS',
    'MUTHOOTFIN.NS','CHOLAFIN.NS','TORNTPHARM.NS','LUPIN.NS','BIOCON.NS',
    'ALKEM.NS','AUROPHARMA.NS','ZYDUSLIFE.NS','GLAXO.NS','PAGEIND.NS','VOLTAS.NS',
    'CROMPTON.NS','POLYCAB.NS','CUMMINSIND.NS','ABB.NS','BHEL.NS','HAL.NS',
    'BEL.NS','CONCOR.NS','ADANIGREEN.NS','IRFC.NS','PFC.NS','RECLTD.NS',
    'M&M.NS','TRENT.NS',
]

NIFTY_MIDCAP150 = [
    'AARTIIND.NS','AARTIDRUGS.NS','ABCAPITAL.NS','ABFRL.NS','AEGISCHEM.NS',
    'AJANTPHARM.NS','APLAPOLLO.NS','APLLTD.NS','ASTRAL.NS','ATUL.NS','AUBANK.NS',
    'BALKRISIND.NS','BALRAMCHIN.NS','BATAINDIA.NS','BERGEPAINT.NS','BSOFT.NS',
    'BRIGADE.NS','CANBK.NS','CANFINHOME.NS','CASTROLIND.NS','CEATLTD.NS',
    'CGPOWER.NS','CHAMBLFERT.NS','COFORGE.NS','CRAFTSMAN.NS','CRISIL.NS',
    'CYIENT.NS','DATAPATTNS.NS','DEEPAKNTR.NS','DELHIVERY.NS','DIXON.NS',
    'DLF.NS','EIDPARRY.NS','ELGIEQUIP.NS','EMAMILTD.NS','ENDURANCE.NS',
    'ENGINERSIN.NS','ESCORTS.NS','EXIDEIND.NS','FEDERALBNK.NS','FLUOROCHEM.NS',
    'FORTIS.NS','GICRE.NS','GNFC.NS','GODREJIND.NS','GODREJPROP.NS','GRANULES.NS',
    'GRINDWELL.NS','GSFC.NS','GSPL.NS','HAPPSTMNDS.NS','HEG.NS','HFCL.NS',
    'HUDCO.NS','IDFCFIRSTB.NS','IEX.NS','IIFL.NS','INDHOTEL.NS','INDIANB.NS',
    'INDIAMART.NS','INTELLECT.NS','JBCHEPHARM.NS','JKCEMENT.NS','JKLAKSHMI.NS',
    'JKPAPER.NS','JSL.NS','JUBLFOOD.NS','KAJARIACER.NS','KALPATPOWR.NS',
    'KANSAINER.NS','KEC.NS','KIMS.NS','KPITTECH.NS','KRBL.NS','LALPATHLAB.NS',
    'LAURUSLABS.NS','LICHSGFIN.NS','LINDEINDIA.NS','LTIM.NS','LTTS.NS','M&MFIN.NS',
    'MANAPPURAM.NS','MCX.NS','METROBRAND.NS','METROPOLIS.NS','MFSL.NS',
    'MOTILALOFS.NS','MRF.NS','NATCOPHARM.NS','NAVINFLUOR.NS','NBCC.NS','NCC.NS',
    'NIACL.NS','NLCINDIA.NS','NMDC.NS','NOCIL.NS','OBEROIRLTY.NS','OFSS.NS',
    'OIL.NS','OLECTRA.NS','PCBL.NS','PERSISTENT.NS','PETRONET.NS','PFIZER.NS',
    'PHOENIXLTD.NS','POLYMED.NS','PRAJIND.NS','PRESTIGE.NS','PVRINOX.NS',
    'RADICO.NS','RAMCOCEM.NS','RAYMOND.NS','REDINGTON.NS','RELAXO.NS','RITES.NS',
    'ROUTE.NS','SAIL.NS','SCHAEFFLER.NS','SOBHA.NS','SONATSOFTW.NS','STLTECH.NS',
    'SUDARSCHEM.NS','SUMICHEM.NS','SUNDARMFIN.NS','SUNDRMFAST.NS','SUNTV.NS',
    'SUPREMEIND.NS','SUZLON.NS','SYNGENE.NS','TANLA.NS','TATACHEM.NS',
    'TATACOMM.NS','TATAELXSI.NS','TEAMLEASE.NS','TIMKEN.NS','TORNTPOWER.NS',
    'TRENT.NS','TRIDENT.NS','TVSMOTOR.NS','UBL.NS','UJJIVANSFB.NS','UNIONBANK.NS',
    'VBL.NS','VGUARD.NS','VINATIORGA.NS','WELCORP.NS','YESBANK.NS','ZEEL.NS',
    'ZYDUSWELL.NS','DIXONTECH.NS','JYOTHYLAB.NS','APTUS.NS','CAMPUS.NS',
    'CHALET.NS','SENCO.NS','SIGNATURE.NS','SAPPHIRE.NS',
]

ALL_TICKERS = list(dict.fromkeys(NIFTY100 + NIFTY_MIDCAP150))
DATA_FILE   = "Master_Data.parquet"

BUFFER_START  = date(2020, 5, 1)   
DISPLAY_START = date(2021, 1, 1)   

def add_all_indicators(df):
    """Calculates exactly 50 technical indicators using pandas_ta_classic"""
    # ── 1. TREND (10) ──
    df['SMA_20'] = ta.sma(df['Close'], length=20)
    df['SMA_50'] = ta.sma(df['Close'], length=50)
    df['SMA_200'] = ta.sma(df['Close'], length=200)
    df['EMA_20'] = ta.ema(df['Close'], length=20)
    df['EMA_50'] = ta.ema(df['Close'], length=50)
    
    macd = ta.macd(df['Close'])
    if macd is not None and not macd.empty:
        df['MACD'] = macd.iloc[:, 0]
        df['MACD_Hist'] = macd.iloc[:, 1]
    else:
        df['MACD'] = np.nan; df['MACD_Hist'] = np.nan

    adx = ta.adx(df['High'], df['Low'], df['Close'])
    if adx is not None and not adx.empty:
        df['ADX_14'] = adx.iloc[:, 0]
        df['+DI_14'] = adx.iloc[:, 1] 
        df['-DI_14'] = adx.iloc[:, 2] 
    else:
        df['ADX_14'] = np.nan; df['+DI_14'] = np.nan; df['-DI_14'] = np.nan

    st = ta.supertrend(df['High'], df['Low'], df['Close'])
    df['Supertrend'] = st.iloc[:, 0] if st is not None and not st.empty else np.nan

    aroon = ta.aroon(df['High'], df['Low'])
    df['Aroon_Up'] = aroon.iloc[:, 1] if aroon is not None and not aroon.empty else np.nan

    # ── 2. MOMENTUM (12) ──
    df['RSI_14'] = ta.rsi(df['Close'], length=14)
    
    stoch = ta.stoch(df['High'], df['Low'], df['Close'])
    if stoch is not None and not stoch.empty:
        df['Stoch_K'] = stoch.iloc[:, 0]
        df['Stoch_D'] = stoch.iloc[:, 1]
    else:
        df['Stoch_K'] = np.nan; df['Stoch_D'] = np.nan

    stochrsi = ta.stochrsi(df['Close'])
    if stochrsi is not None and not stochrsi.empty:
        df['StochRSI_K'] = stochrsi.iloc[:, 0]
        df['StochRSI_D'] = stochrsi.iloc[:, 1]
    else:
        df['StochRSI_K'] = np.nan; df['StochRSI_D'] = np.nan

    df['CCI_20'] = ta.cci(df['High'], df['Low'], df['Close'], length=20)
    df['WillR_14'] = ta.willr(df['High'], df['Low'], df['Close'], length=14)
    df['ROC_12'] = ta.roc(df['Close'], length=12)
    df['AO'] = ta.ao(df['High'], df['Low'])
    df['MOM_10'] = ta.mom(df['Close'], length=10)
    
    ppo = ta.ppo(df['Close'])
    df['PPO'] = ppo.iloc[:, 0] if ppo is not None and not ppo.empty else np.nan
    df['UO'] = ta.uo(df['High'], df['Low'], df['Close'])

    # ── 3. VOLATILITY (8) ──
    df['ATR_14'] = ta.atr(df['High'], df['Low'], df['Close'], length=14)
    
    bbands = ta.bbands(df['Close'], length=20)
    if bbands is not None and not bbands.empty:
        df['BB_Lower'] = bbands.iloc[:, 0]
        df['BB_Upper'] = bbands.iloc[:, 2]
        df['BB_Width'] = bbands.iloc[:, 3]
    else:
        df['BB_Lower'] = np.nan; df['BB_Upper'] = np.nan; df['BB_Width'] = np.nan

    kc = ta.kc(df['High'], df['Low'], df['Close'])
    if kc is not None and not kc.empty:
        df['KC_Lower'] = kc.iloc[:, 0]
        df['KC_Upper'] = kc.iloc[:, 2]
    else:
        df['KC_Lower'] = np.nan; df['KC_Upper'] = np.nan

    donchian = ta.donchian(df['High'], df['Low'])
    df['Donchian_Upper'] = donchian.iloc[:, 2] if donchian is not None and not donchian.empty else np.nan
    df['StdDev_20'] = ta.stdev(df['Close'], length=20)

    # ── 4. VOLUME (9) ──
    df['OBV'] = ta.obv(df['Close'], df['Volume'])
    df['AD'] = ta.ad(df['High'], df['Low'], df['Close'], df['Volume'])
    df['MFI_14'] = ta.mfi(df['High'], df['Low'], df['Close'], df['Volume'], length=14)
    df['CMF_20'] = ta.cmf(df['High'], df['Low'], df['Close'], df['Volume'], length=20)
    df['PVT'] = ta.pvt(df['Close'], df['Volume'])
    df['PVI'] = ta.pvi(df['Close'], df['Volume'])
    df['NVI'] = ta.nvi(df['Close'], df['Volume'])
    df['VWAP'] = ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'])
    df['Vol_SMA_20'] = ta.sma(df['Volume'], length=20)

    # ── 5. PRICE ACTION / SYSTEM RISK (6) ──
    trix = ta.trix(df['Close'], length=30)
    df['TRIX'] = trix.iloc[:, 0] if trix is not None and not trix.empty else np.nan

    eri = ta.eri(df['High'], df['Low'], df['Close'])
    if eri is not None and not eri.empty:
        df['Elder_Bull'] = eri.iloc[:, 0]
        df['Elder_Bear'] = eri.iloc[:, 1]
    else:
        df['Elder_Bull'] = np.nan; df['Elder_Bear'] = np.nan

    return df.round(2)

def compress(df):
    for col in df.select_dtypes('float64').columns:
        df[col] = df[col].astype('float32')
    return df

def get_fetch_start():
    if os.path.exists(DATA_FILE):
        try:
            existing = pd.read_parquet(DATA_FILE, columns=['Date'])
            existing['Date'] = pd.to_datetime(existing['Date'])
            last_date = existing['Date'].max().date()
            if last_date < date(2026, 1, 1):
                 print(f"File is too old ({last_date}). Forcing full fetch.")
                 return BUFFER_START, False
            fetch_from = last_date - timedelta(days=5)
            return fetch_from, True
        except Exception:
            pass
    return BUFFER_START, False

def main():
    today = date.today()
    fetch_start, is_incremental = get_fetch_start()
    print(f"Fetching from {fetch_start} to {today}...")

    new_frames = []
    chunk_size = 15 

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

                    if is_incremental:
                        hist = yf.download(ticker, start=BUFFER_START.strftime('%Y-%m-%d'),
                                           end=(fetch_start - timedelta(days=1)).strftime('%Y-%m-%d'),
                                           auto_adjust=True, progress=False)
                        if isinstance(hist.columns, pd.MultiIndex): hist.columns = hist.columns.get_level_values(0)
                        combined = pd.concat([hist[['Open','High','Low','Close','Volume']], df_t]).sort_index()
                        combined = combined[~combined.index.duplicated(keep='last')]
                        df_indicators = add_all_indicators(combined)
                    else:
                        df_indicators = add_all_indicators(df_t)

                    df_final = df_indicators[df_indicators.index >= pd.Timestamp(DISPLAY_START)]
                    
                    if not df_final.empty:
                        df_final.insert(0, 'Ticker', ticker.replace('.NS',''))
                        df_final = df_final.reset_index().rename(columns={'Date':'Date', 'index':'Date'})
                        df_final['Date'] = pd.to_datetime(df_final['Date']).dt.strftime('%Y-%m-%d')
                        new_frames.append(compress(df_final))
                except Exception as e: 
                    print(f"Skipping {ticker}: {e}")
                    continue
        except Exception: continue
        gc.collect()

    if not new_frames:
        print("No new data.")
        return

    result_df = pd.concat(new_frames, ignore_index=True)
    
    if is_incremental and os.path.exists(DATA_FILE):
        existing_df = pd.read_parquet(DATA_FILE)
        existing_df['Date'] = pd.to_datetime(existing_df['Date']).dt.strftime('%Y-%m-%d')
        overlap_dates = set(result_df['Date'].unique())
        master_df = pd.concat([existing_df[~existing_df['Date'].isin(overlap_dates)], result_df])
    else:
        master_df = result_df

    master_df.sort_values(['Ticker','Date']).to_parquet(DATA_FILE, index=False)
    print("✅ Successfully Updated Master_Data.parquet")

if __name__ == "__main__":
    main()
