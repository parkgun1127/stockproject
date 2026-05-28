import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import numpy as np

# ── 페이지 설정 ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="삼성전자 집중 분석",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;600&family=Noto+Sans+KR:wght@300;400;700&display=swap');

:root {
    --bg-primary: #0a0e1a;
    --bg-secondary: #111827;
    --bg-card: #161d2e;
    --accent-green: #00d4aa;
    --accent-red: #ff4d6d;
    --accent-blue: #3b82f6;
    --accent-yellow: #f59e0b;
    --accent-cyan: #06b6d4;
    --text-primary: #e2e8f0;
    --text-muted: #64748b;
    --border: #1e293b;
    --samsung-blue: #1428A0;
    --samsung-blue-light: #4f6bdf;
}

html, body, .stApp {
    background-color: var(--bg-primary) !important;
    font-family: 'Noto Sans KR', sans-serif;
    color: var(--text-primary);
}

section[data-testid="stSidebar"] {
    background-color: var(--bg-secondary) !important;
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] * { color: var(--text-primary) !important; }

div[data-testid="metric-container"] {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px 20px;
    transition: all 0.2s ease;
}
div[data-testid="metric-container"]:hover {
    border-color: var(--samsung-blue-light);
    transform: translateY(-2px);
}
div[data-testid="metric-container"] label {
    color: var(--text-muted) !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.68rem !important;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: var(--text-primary) !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 1.35rem !important;
    font-weight: 600;
}
div[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.82rem !important;
}

.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-card);
    border-radius: 10px;
    gap: 4px;
    padding: 4px;
    border: 1px solid var(--border);
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text-muted) !important;
    border-radius: 8px !important;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
    letter-spacing: 0.04em;
    border: none !important;
}
.stTabs [aria-selected="true"] {
    background: var(--samsung-blue) !important;
    color: white !important;
}

.stSelectbox > div > div,
.stMultiSelect > div > div {
    background: var(--bg-card) !important;
    border-color: var(--border) !important;
    color: var(--text-primary) !important;
}

hr { border-color: var(--border) !important; }

/* ── 헤더 배너 ── */
.samsung-header {
    background: linear-gradient(135deg, #0a0e1a 0%, #0d1a4a 40%, #1a0e2e 100%);
    border: 1px solid #1e3a8a;
    border-radius: 20px;
    padding: 36px 44px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}
.samsung-header::before {
    content: '';
    position: absolute;
    top: -80px; right: -80px;
    width: 320px; height: 320px;
    background: radial-gradient(circle, rgba(20,40,160,0.25) 0%, transparent 70%);
    pointer-events: none;
}
.samsung-header::after {
    content: '';
    position: absolute;
    bottom: -60px; left: 30%;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(6,182,212,0.08) 0%, transparent 70%);
    pointer-events: none;
}
.samsung-logo-text {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.35em;
    color: #4f6bdf;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.samsung-title {
    font-family: 'Noto Sans KR', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    color: #e2e8f0;
    margin: 0;
    letter-spacing: -0.03em;
    line-height: 1.2;
}
.samsung-ticker {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.9rem;
    color: #64748b;
    margin: 6px 0 0 0;
}
.badge-row { display: flex; gap: 10px; margin-top: 16px; flex-wrap: wrap; }
.badge {
    display: inline-block;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.62rem;
    padding: 4px 12px;
    border-radius: 20px;
    letter-spacing: 0.1em;
}
.badge-blue {
    background: rgba(20,40,160,0.25);
    border: 1px solid rgba(79,107,223,0.5);
    color: #818cf8;
}
.badge-green {
    background: rgba(0,212,170,0.1);
    border: 1px solid rgba(0,212,170,0.35);
    color: #00d4aa;
}
.badge-yellow {
    background: rgba(245,158,11,0.1);
    border: 1px solid rgba(245,158,11,0.35);
    color: #f59e0b;
}

/* ── 섹션 타이틀 ── */
.section-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.67rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: #4f6bdf;
    margin: 24px 0 14px 0;
    padding-bottom: 8px;
    border-bottom: 1px solid #1e293b;
}

/* ── 투자 의견 카드 ── */
.opinion-card {
    background: linear-gradient(135deg, #161d2e 0%, #1a1f35 100%);
    border: 1px solid #1e3a5f;
    border-radius: 14px;
    padding: 22px 26px;
    margin-bottom: 14px;
    position: relative;
    overflow: hidden;
}
.opinion-card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
    border-radius: 14px 0 0 14px;
}
.opinion-card.buy::before { background: #00d4aa; }
.opinion-card.hold::before { background: #f59e0b; }
.opinion-card.sell::before { background: #ff4d6d; }
.opinion-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 6px;
}
.opinion-card.buy .opinion-label { color: #00d4aa; }
.opinion-card.hold .opinion-label { color: #f59e0b; }
.opinion-card.sell .opinion-label { color: #ff4d6d; }
.opinion-title {
    font-family: 'Noto Sans KR', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: #e2e8f0;
    margin: 0 0 6px 0;
}
.opinion-desc {
    font-family: 'Noto Sans KR', sans-serif;
    font-size: 0.78rem;
    color: #94a3b8;
    line-height: 1.6;
    margin: 0;
}

/* ── 재무 테이블 ── */
.fin-table-wrap {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
}

/* ── 볼린저 밴드 레전드 ── */
.bb-legend {
    display: flex; gap: 18px; flex-wrap: wrap;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    color: #64748b;
    margin-bottom: 8px;
}
.bb-dot {
    display: inline-block;
    width: 10px; height: 10px;
    border-radius: 50%;
    margin-right: 5px;
    vertical-align: middle;
}

/* ── 뉴스 카드 ── */
.news-item {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 10px;
    transition: border-color 0.2s;
}
.news-item:hover { border-color: #4f6bdf; }
.news-date {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.63rem;
    color: #475569;
    letter-spacing: 0.05em;
}
.news-title {
    font-family: 'Noto Sans KR', sans-serif;
    font-size: 0.85rem;
    color: #e2e8f0;
    margin: 4px 0 0 0;
}
</style>
""", unsafe_allow_html=True)

# ── 상수 ─────────────────────────────────────────────────────────────────────
TICKER        = "005930.KS"
TICKER_KRX    = "KRX: 005930"
PEERS = {
    "삼성전자":    "005930.KS",
    "SK하이닉스":  "000660.KS",
    "인텔":        "INTC",
    "TSMC":        "TSM",
    "퀄컴":        "QCOM",
    "NVIDIA":      "NVDA",
}

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="IBM Plex Mono, monospace", color="#94a3b8", size=11),
    legend=dict(bgcolor="rgba(17,24,39,0.85)", bordercolor="#1e293b",
                borderwidth=1, font=dict(size=11)),
    xaxis=dict(gridcolor="#1a2035", linecolor="#1e293b", showgrid=True, zeroline=False),
    yaxis=dict(gridcolor="#1a2035", linecolor="#1e293b", showgrid=True, zeroline=False),
    margin=dict(l=10, r=10, t=44, b=10),
    hovermode="x unified",
)

# ── 데이터 로드 ───────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_ohlcv(ticker: str, period: str) -> pd.DataFrame:
    df = yf.download(ticker, period=period, progress=False, auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

@st.cache_data(ttl=600)
def load_info(ticker: str) -> dict:
    try:
        return yf.Ticker(ticker).info
    except Exception:
        return {}

@st.cache_data(ttl=600)
def load_financials(ticker: str):
    t = yf.Ticker(ticker)
    try:
        inc = t.financials
    except Exception:
        inc = pd.DataFrame()
    try:
        bs = t.balance_sheet
    except Exception:
        bs = pd.DataFrame()
    try:
        cf = t.cashflow
    except Exception:
        cf = pd.DataFrame()
    return inc, bs, cf

@st.cache_data(ttl=300)
def load_peers(period: str) -> dict:
    result = {}
    for name, ticker in PEERS.items():
        df = yf.download(ticker, period=period, progress=False, auto_adjust=True)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        if not df.empty:
            result[name] = df
    return result

def safe_series(s):
    """MultiIndex 컬럼 대비 안전 추출"""
    if isinstance(s, pd.DataFrame):
        return s.squeeze()
    return s

def calc_technical(df: pd.DataFrame) -> pd.DataFrame:
    """기술 지표 계산"""
    close = safe_series(df["Close"]).dropna()
    vol   = safe_series(df["Volume"]).dropna() if "Volume" in df.columns else None

    out = pd.DataFrame(index=close.index)
    out["Close"] = close.values

    # 이동평균
    for w in [5, 20, 60, 120]:
        out[f"MA{w}"] = close.rolling(w).mean().values

    # 볼린저 밴드 (20일, 2σ)
    ma20 = close.rolling(20).mean()
    std20 = close.rolling(20).std()
    out["BB_upper"] = (ma20 + 2 * std20).values
    out["BB_lower"] = (ma20 - 2 * std20).values
    out["BB_mid"]   = ma20.values

    # RSI (14일)
    delta = close.diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    rs    = gain / loss.replace(0, np.nan)
    out["RSI"] = (100 - 100 / (1 + rs)).values

    # MACD (12-26-9)
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd  = ema12 - ema26
    signal= macd.ewm(span=9, adjust=False).mean()
    out["MACD"]        = macd.values
    out["MACD_signal"] = signal.values
    out["MACD_hist"]   = (macd - signal).values

    # OBV
    if vol is not None:
        vol_aligned = vol.reindex(close.index).fillna(0)
        sign = np.sign(close.diff().fillna(0))
        out["OBV"] = (sign * vol_aligned).cumsum().values

    # ATR (14일)
    if "High" in df.columns and "Low" in df.columns:
        hi = safe_series(df["High"]).reindex(close.index)
        lo = safe_series(df["Low"]).reindex(close.index)
        prev_close = close.shift(1)
        tr = pd.concat([hi - lo, (hi - prev_close).abs(), (lo - prev_close).abs()], axis=1).max(axis=1)
        out["ATR"] = tr.rolling(14).mean().values

    if vol is not None:
        out["Volume"] = vol.reindex(close.index).values

    return out

# ── 사이드바 ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="font-family:IBM Plex Mono;font-size:0.65rem;letter-spacing:0.2em;color:#4f6bdf;text-transform:uppercase;margin-bottom:12px;">⚙ 분석 설정</div>', unsafe_allow_html=True)

    period_map = {
        "3개월": "3mo", "6개월": "6mo",
        "1년": "1y", "2년": "2y", "5년": "5y",
    }
    period_label = st.selectbox("분석 기간", list(period_map.keys()), index=2)
    period = period_map[period_label]

    st.markdown("---")
    st.markdown('<div style="font-family:IBM Plex Mono;font-size:0.65rem;letter-spacing:0.2em;color:#4f6bdf;text-transform:uppercase;margin-bottom:8px;">차트 표시 옵션</div>', unsafe_allow_html=True)
    show_bb     = st.toggle("볼린저 밴드", value=True)
    show_ma     = st.toggle("이동평균선", value=True)
    show_volume = st.toggle("거래량", value=True)
    show_rsi    = st.toggle("RSI", value=True)
    show_macd   = st.toggle("MACD", value=True)

    st.markdown("---")
    st.markdown(
        '<div style="font-family:IBM Plex Mono;font-size:0.63rem;color:#475569;line-height:1.9;">'
        '종목코드: 005930.KS<br>데이터: Yahoo Finance<br>갱신: 5분<br><br>'
        '⚠ 투자 참고용 정보입니다.</div>',
        unsafe_allow_html=True,
    )

# ── 데이터 로드 ───────────────────────────────────────────────────────────────
with st.spinner("삼성전자 데이터 수집 중..."):
    df_raw  = load_ohlcv(TICKER, period)
    info    = load_info(TICKER)
    df_tech = calc_technical(df_raw)
    peers   = load_peers(period)

if df_raw.empty:
    st.error("데이터를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.")
    st.stop()

close_s   = safe_series(df_raw["Close"]).dropna()
last_price = float(close_s.iloc[-1])
prev_price = float(close_s.iloc[-2]) if len(close_s) > 1 else last_price
chg_1d     = (last_price - prev_price) / prev_price * 100
chg_total  = (last_price - float(close_s.iloc[0])) / float(close_s.iloc[0]) * 100

# ── 헤더 ─────────────────────────────────────────────────────────────────────
market_cap = info.get("marketCap", 0)
if market_cap >= 1e12:
    mcap_str = f"₩{market_cap/1e12:.1f}조"
elif market_cap >= 1e8:
    mcap_str = f"₩{market_cap/1e8:.0f}억"
else:
    mcap_str = "N/A"

pe_str  = f"PER {info.get('trailingPE', 0):.1f}x" if info.get("trailingPE") else "PER N/A"
div_str = f"배당 {info.get('dividendYield', 0)*100:.2f}%" if info.get("dividendYield") else "배당 N/A"

st.markdown(f"""
<div class="samsung-header">
    <div class="samsung-logo-text">Samsung Electronics · Deep Dive Analysis</div>
    <p class="samsung-title">삼성전자</p>
    <p class="samsung-ticker">{TICKER_KRX} &nbsp;·&nbsp; {datetime.now().strftime('%Y-%m-%d %H:%M')} 기준</p>
    <div class="badge-row">
        <span class="badge badge-blue">KOSPI 대형주</span>
        <span class="badge badge-blue">반도체 · 가전 · 디스플레이</span>
        <span class="badge badge-green">{mcap_str}</span>
        <span class="badge badge-yellow">{pe_str}</span>
        <span class="badge badge-yellow">{div_str}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── 상단 KPI 메트릭 ───────────────────────────────────────────────────────────
c1, c2, c3, c4, c5, c6 = st.columns(6)

week52_high = float(close_s.rolling(min(252, len(close_s))).max().iloc[-1])
week52_low  = float(close_s.rolling(min(252, len(close_s))).min().iloc[-1])

vol_s  = safe_series(df_raw["Volume"]).dropna() if "Volume" in df_raw.columns else None
avg_vol = int(vol_s.rolling(20).mean().iloc[-1]) if vol_s is not None else 0

daily_ret = close_s.pct_change().dropna()
volatility = float(daily_ret.std() * np.sqrt(252) * 100)
sharpe = float((daily_ret.mean() * 252) / (daily_ret.std() * np.sqrt(252))) if daily_ret.std() > 0 else 0

c1.metric("현재가", f"₩{last_price:,.0f}", f"{chg_1d:+.2f}% (1일)")
c2.metric("기간 수익률", f"{chg_total:+.2f}%", f"{period_label} 기준")
c3.metric("52주 고점", f"₩{week52_high:,.0f}", f"{((last_price-week52_high)/week52_high*100):+.1f}%")
c4.metric("52주 저점", f"₩{week52_low:,.0f}", f"{((last_price-week52_low)/week52_low*100):+.1f}%")
c5.metric("연환산 변동성", f"{volatility:.1f}%")
c6.metric("샤프지수", f"{sharpe:.2f}")

# ── 탭 ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📉 기술적 분석",
    "🏦 재무 분석",
    "🌐 동종업체 비교",
    "📊 투자 심층 지표",
    "💡 투자 의견",
])

# ════════════════════════════════════════════════════════════════
# TAB 1 : 기술적 분석
# ════════════════════════════════════════════════════════════════
with tab1:
    # 서브플롯 구성
    row_heights = [0.45]
    specs_list  = [[{"secondary_y": True}]]
    if show_volume:
        row_heights += [0.12]
        specs_list  += [[{"secondary_y": False}]]
    if show_rsi:
        row_heights += [0.18]
        specs_list  += [[{"secondary_y": False}]]
    if show_macd:
        row_heights += [0.25]
        specs_list  += [[{"secondary_y": False}]]

    n_rows = len(row_heights)
    fig = make_subplots(
        rows=n_rows, cols=1,
        shared_xaxes=True,
        row_heights=row_heights,
        specs=specs_list,
        vertical_spacing=0.03,
    )

    # ── 캔들스틱 ──
    if "Open" in df_raw.columns and "High" in df_raw.columns and "Low" in df_raw.columns:
        fig.add_trace(go.Candlestick(
            x=df_tech.index,
            open=safe_series(df_raw["Open"]).reindex(df_tech.index),
            high=safe_series(df_raw["High"]).reindex(df_tech.index),
            low=safe_series(df_raw["Low"]).reindex(df_tech.index),
            close=df_tech["Close"],
            name="삼성전자",
            increasing_line_color="#00d4aa",
            decreasing_line_color="#ff4d6d",
            increasing_fillcolor="#00d4aa",
            decreasing_fillcolor="#ff4d6d",
        ), row=1, col=1)

    # ── 이동평균 ──
    if show_ma:
        ma_styles = {
            "MA5":  ("#06b6d4", "solid",  1.2),
            "MA20": ("#f59e0b", "solid",  1.5),
            "MA60": ("#a78bfa", "dot",    1.5),
            "MA120":("#fb923c", "dot",    1.5),
        }
        for col_name, (color, dash, width) in ma_styles.items():
            if col_name in df_tech.columns:
                fig.add_trace(go.Scatter(
                    x=df_tech.index, y=df_tech[col_name],
                    mode="lines", name=col_name,
                    line=dict(color=color, width=width, dash=dash),
                    opacity=0.85,
                ), row=1, col=1)

    # ── 볼린저 밴드 ──
    if show_bb and "BB_upper" in df_tech.columns:
        fig.add_trace(go.Scatter(
            x=df_tech.index, y=df_tech["BB_upper"],
            mode="lines", name="BB Upper",
            line=dict(color="#334155", width=1),
            showlegend=False,
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df_tech.index, y=df_tech["BB_lower"],
            mode="lines", name="BB Band",
            line=dict(color="#334155", width=1),
            fill="tonexty",
            fillcolor="rgba(59,130,246,0.06)",
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df_tech.index, y=df_tech["BB_mid"],
            mode="lines", name="BB Mid",
            line=dict(color="#475569", width=1, dash="dot"),
            showlegend=False,
        ), row=1, col=1)

    current_row = 2

    # ── 거래량 ──
    if show_volume and "Volume" in df_tech.columns:
        vol_colors = ["#00d4aa" if c >= p else "#ff4d6d"
                      for c, p in zip(df_tech["Close"], df_tech["Close"].shift(1).fillna(df_tech["Close"]))]
        fig.add_trace(go.Bar(
            x=df_tech.index, y=df_tech["Volume"],
            name="거래량", marker_color=vol_colors, opacity=0.65,
            showlegend=False,
        ), row=current_row, col=1)
        fig.update_yaxes(title_text="거래량", row=current_row, col=1,
                         gridcolor="#1a2035", linecolor="#1e293b", title_font=dict(size=10))
        current_row += 1

    # ── RSI ──
    if show_rsi and "RSI" in df_tech.columns:
        fig.add_trace(go.Scatter(
            x=df_tech.index, y=df_tech["RSI"],
            mode="lines", name="RSI(14)",
            line=dict(color="#06b6d4", width=1.5),
        ), row=current_row, col=1)
        fig.add_hrect(y0=70, y1=100, fillcolor="rgba(255,77,109,0.07)",
                      line_width=0, row=current_row, col=1)
        fig.add_hrect(y0=0, y1=30, fillcolor="rgba(0,212,170,0.07)",
                      line_width=0, row=current_row, col=1)
        fig.add_hline(y=70, line_dash="dot", line_color="#ff4d6d",
                      line_width=1, row=current_row, col=1)
        fig.add_hline(y=30, line_dash="dot", line_color="#00d4aa",
                      line_width=1, row=current_row, col=1)
        fig.update_yaxes(title_text="RSI", range=[0, 100],
                         row=current_row, col=1,
                         gridcolor="#1a2035", linecolor="#1e293b", title_font=dict(size=10))
        current_row += 1

    # ── MACD ──
    if show_macd and "MACD" in df_tech.columns:
        hist_colors = ["#00d4aa" if v >= 0 else "#ff4d6d" for v in df_tech["MACD_hist"]]
        fig.add_trace(go.Bar(
            x=df_tech.index, y=df_tech["MACD_hist"],
            name="MACD Hist", marker_color=hist_colors, opacity=0.65,
        ), row=current_row, col=1)
        fig.add_trace(go.Scatter(
            x=df_tech.index, y=df_tech["MACD"],
            mode="lines", name="MACD",
            line=dict(color="#3b82f6", width=1.5),
        ), row=current_row, col=1)
        fig.add_trace(go.Scatter(
            x=df_tech.index, y=df_tech["MACD_signal"],
            mode="lines", name="Signal",
            line=dict(color="#f59e0b", width=1.5),
        ), row=current_row, col=1)
        fig.update_yaxes(title_text="MACD", row=current_row, col=1,
                         gridcolor="#1a2035", linecolor="#1e293b", title_font=dict(size=10))

    # 공통 레이아웃
    fig.update_layout(
        **{k: v for k, v in CHART_LAYOUT.items() if k not in ("xaxis", "yaxis")},
        title=dict(text="<b>삼성전자 기술적 분석 차트</b>", font=dict(size=14, color="#e2e8f0")),
        height=250 + 120 * (n_rows - 1),
        xaxis_rangeslider_visible=False,
    )
    for i in range(1, n_rows + 1):
        fig.update_xaxes(gridcolor="#1a2035", linecolor="#1e293b", row=i, col=1)
    fig.update_yaxes(gridcolor="#1a2035", linecolor="#1e293b", row=1, col=1)

    st.plotly_chart(fig, use_container_width=True)

    # 최신 지표 스냅샷
    st.markdown('<div class="section-title">현재 기술 지표 스냅샷</div>', unsafe_allow_html=True)
    last = df_tech.iloc[-1]
    s1, s2, s3, s4, s5 = st.columns(5)
    s1.metric("RSI (14)", f"{last.get('RSI', float('nan')):.1f}", help="70↑ 과매수 · 30↓ 과매도")
    s2.metric("MACD", f"{last.get('MACD', float('nan')):.0f}")
    s3.metric("Signal", f"{last.get('MACD_signal', float('nan')):.0f}")
    s4.metric("BB 상단", f"₩{last.get('BB_upper', float('nan')):,.0f}")
    s5.metric("BB 하단", f"₩{last.get('BB_lower', float('nan')):,.0f}")

    # 20/60 골든크로스 여부
    if "MA20" in df_tech.columns and "MA60" in df_tech.columns:
        ma20_last = df_tech["MA20"].dropna().iloc[-1]
        ma60_last = df_tech["MA60"].dropna().iloc[-1]
        cross_status = "🟢 골든크로스 (MA20 > MA60)" if ma20_last > ma60_last else "🔴 데드크로스 (MA20 < MA60)"
        st.info(f"**이동평균 크로스 상태:** {cross_status}  |  MA20 ₩{ma20_last:,.0f}  /  MA60 ₩{ma60_last:,.0f}")

# ════════════════════════════════════════════════════════════════
# TAB 2 : 재무 분석
# ════════════════════════════════════════════════════════════════
with tab2:
    inc, bs, cf = load_financials(TICKER)

    def fmt_krw(v):
        if pd.isna(v): return "—"
        abs_v = abs(v)
        if abs_v >= 1e12: return f"{'↑' if v > 0 else ''}{v/1e12:.2f}조"
        if abs_v >= 1e8:  return f"{v/1e8:.0f}억"
        return f"{v:,.0f}"

    # ── 손익계산서 ──
    if not inc.empty:
        st.markdown('<div class="section-title">손익계산서 (연간)</div>', unsafe_allow_html=True)
        rows_to_show = ["Total Revenue", "Gross Profit", "Operating Income", "Net Income"]
        labels = {"Total Revenue": "매출액", "Gross Profit": "매출총이익",
                  "Operating Income": "영업이익", "Net Income": "순이익"}
        avail = [r for r in rows_to_show if r in inc.index]
        if avail:
            inc_disp = inc.loc[avail].copy()
            inc_disp.index = [labels.get(r, r) for r in avail]
            inc_disp.columns = [str(c)[:7] for c in inc_disp.columns]

            # 막대 차트
            fig_inc = go.Figure()
            colors_bar = ["#3b82f6", "#00d4aa", "#f59e0b", "#a78bfa"]
            for i, row_name in enumerate(inc_disp.index):
                vals = inc_disp.loc[row_name].apply(lambda x: x/1e12 if not pd.isna(x) else None)
                fig_inc.add_trace(go.Bar(
                    x=inc_disp.columns.tolist(), y=vals.tolist(),
                    name=row_name, marker_color=colors_bar[i % len(colors_bar)],
                    opacity=0.85,
                ))
            fig_inc.update_layout(
                **CHART_LAYOUT,
                title=dict(text="<b>연간 손익 추이 (조원)</b>", font=dict(size=13, color="#e2e8f0")),
                barmode="group", height=340,
                yaxis_title="금액 (조원)",
            )
            st.plotly_chart(fig_inc, use_container_width=True)

            # 수치 테이블
            disp_fmt = inc_disp.applymap(lambda x: fmt_krw(x) if not pd.isna(x) else "—")
            st.dataframe(disp_fmt, use_container_width=True)

    # ── 현금흐름 ──
    if not cf.empty:
        st.markdown('<div class="section-title">현금흐름표 (연간)</div>', unsafe_allow_html=True)
        cf_rows = ["Operating Cash Flow", "Investing Cash Flow", "Financing Cash Flow",
                   "Free Cash Flow", "Capital Expenditure"]
        cf_labels = {
            "Operating Cash Flow": "영업현금흐름",
            "Investing Cash Flow": "투자현금흐름",
            "Financing Cash Flow": "재무현금흐름",
            "Free Cash Flow": "잉여현금흐름 (FCF)",
            "Capital Expenditure": "설비투자 (CAPEX)",
        }
        avail_cf = [r for r in cf_rows if r in cf.index]
        if avail_cf:
            cf_disp = cf.loc[avail_cf].copy()
            cf_disp.index = [cf_labels.get(r, r) for r in avail_cf]
            cf_disp.columns = [str(c)[:7] for c in cf_disp.columns]

            fig_cf = go.Figure()
            cf_colors = ["#00d4aa", "#ff4d6d", "#f59e0b", "#3b82f6", "#a78bfa"]
            for i, row_name in enumerate(cf_disp.index):
                vals = cf_disp.loc[row_name].apply(lambda x: x/1e12 if not pd.isna(x) else None)
                bar_colors = ["#00d4aa" if (v is not None and v >= 0) else "#ff4d6d" for v in vals]
                fig_cf.add_trace(go.Bar(
                    x=cf_disp.columns.tolist(), y=vals.tolist(),
                    name=row_name, marker_color=cf_colors[i % len(cf_colors)],
                    opacity=0.8,
                ))
            fig_cf.update_layout(
                **CHART_LAYOUT,
                title=dict(text="<b>현금흐름 추이 (조원)</b>", font=dict(size=13, color="#e2e8f0")),
                barmode="group", height=320,
                yaxis_title="금액 (조원)",
            )
            st.plotly_chart(fig_cf, use_container_width=True)

    # ── 재무 건전성 주요 지표 ──
    st.markdown('<div class="section-title">주요 밸류에이션 지표</div>', unsafe_allow_html=True)
    v1, v2, v3, v4, v5, v6 = st.columns(6)
    v1.metric("PER", f"{info.get('trailingPE', 0):.1f}x" if info.get("trailingPE") else "N/A")
    v2.metric("Forward PER", f"{info.get('forwardPE', 0):.1f}x" if info.get("forwardPE") else "N/A")
    v3.metric("PBR", f"{info.get('priceToBook', 0):.2f}x" if info.get("priceToBook") else "N/A")
    v4.metric("ROE", f"{info.get('returnOnEquity', 0)*100:.1f}%" if info.get("returnOnEquity") else "N/A")
    v5.metric("ROA", f"{info.get('returnOnAssets', 0)*100:.1f}%" if info.get("returnOnAssets") else "N/A")
    v6.metric("부채비율", f"{info.get('debtToEquity', 0):.1f}%" if info.get("debtToEquity") else "N/A")

# ════════════════════════════════════════════════════════════════
# TAB 3 : 동종업체 비교
# ════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-title">동종업체 정규화 수익률 비교</div>', unsafe_allow_html=True)

    fig_peer = go.Figure()
    peer_colors = ["#4f6bdf", "#00d4aa", "#f59e0b", "#ff4d6d", "#a78bfa", "#fb923c"]
    for i, (name, df_p) in enumerate(peers.items()):
        c = safe_series(df_p["Close"]).dropna()
        norm = c / c.iloc[0] * 100
        is_samsung = name == "삼성전자"
        fig_peer.add_trace(go.Scatter(
            x=norm.index, y=norm.values,
            mode="lines", name=name,
            line=dict(
                color=peer_colors[i % len(peer_colors)],
                width=3 if is_samsung else 1.8,
                dash="solid" if is_samsung else "dot",
            ),
            opacity=1.0 if is_samsung else 0.75,
        ))
    fig_peer.add_hline(y=100, line_dash="dot", line_color="#334155", line_width=1)
    fig_peer.update_layout(
        **CHART_LAYOUT,
        title=dict(text=f"<b>글로벌 반도체 동종업체 수익률 비교 ({period_label})</b>",
                   font=dict(size=14, color="#e2e8f0")),
        height=440, yaxis_title="기준치 (100 = 시작점)",
    )
    st.plotly_chart(fig_peer, use_container_width=True)

    # 수익률 비교 테이블
    st.markdown('<div class="section-title">수익률 · 변동성 비교 테이블</div>', unsafe_allow_html=True)
    peer_stats = []
    for name, df_p in peers.items():
        c = safe_series(df_p["Close"]).dropna()
        ret = (c.iloc[-1] - c.iloc[0]) / c.iloc[0] * 100
        vol = c.pct_change().dropna().std() * np.sqrt(252) * 100
        dd  = ((c / c.cummax()) - 1).min() * 100
        peer_stats.append({
            "종목": name,
            "수익률(%)": f"{ret:+.2f}%",
            "변동성(%)": f"{vol:.2f}%",
            "최대낙폭(%)": f"{dd:.2f}%",
            "현재가": f"{float(c.iloc[-1]):,.2f}",
        })
    st.dataframe(pd.DataFrame(peer_stats), use_container_width=True, hide_index=True)

    # 삼성전자 vs TSMC vs SK하이닉스 상관계수
    st.markdown('<div class="section-title">삼성전자 vs 동종업체 일간 수익률 상관계수</div>', unsafe_allow_html=True)
    ret_dict = {}
    for name, df_p in peers.items():
        c = safe_series(df_p["Close"]).dropna()
        ret_dict[name] = c.pct_change().dropna()
    ret_peer_df = pd.DataFrame(ret_dict).dropna()
    corr_peer = ret_peer_df.corr()

    fig_corr = go.Figure(go.Heatmap(
        z=corr_peer.values,
        x=corr_peer.columns.tolist(),
        y=corr_peer.index.tolist(),
        colorscale=[[0, "#ff4d6d"], [0.5, "#1e293b"], [1, "#00d4aa"]],
        zmin=-1, zmax=1,
        text=[[f"{v:.2f}" for v in row] for row in corr_peer.values],
        texttemplate="%{text}",
        textfont=dict(size=11, family="IBM Plex Mono"),
        colorbar=dict(thickness=12, tickfont=dict(family="IBM Plex Mono", size=10)),
    ))
    fig_corr.update_layout(
        **CHART_LAYOUT,
        title=dict(text="<b>동종업체 수익률 상관계수</b>", font=dict(size=13, color="#e2e8f0")),
        height=380,
    )
    st.plotly_chart(fig_corr, use_container_width=True)

# ════════════════════════════════════════════════════════════════
# TAB 4 : 투자 심층 지표
# ════════════════════════════════════════════════════════════════
with tab4:
    col_l, col_r = st.columns(2)

    # ── 낙폭 (Drawdown) ──
    with col_l:
        st.markdown('<div class="section-title">낙폭 (Drawdown) 추이</div>', unsafe_allow_html=True)
        dd_s = (close_s / close_s.cummax() - 1) * 100
        fig_dd = go.Figure(go.Scatter(
            x=dd_s.index, y=dd_s.values,
            mode="lines", fill="tozeroy",
            fillcolor="rgba(255,77,109,0.12)",
            line=dict(color="#ff4d6d", width=1.8),
            name="낙폭",
        ))
        fig_dd.update_layout(
            **CHART_LAYOUT,
            title=dict(text="<b>낙폭 추이</b>", font=dict(size=13, color="#e2e8f0")),
            height=300, showlegend=False,
            yaxis_title="낙폭 (%)",
        )
        st.plotly_chart(fig_dd, use_container_width=True)

    # ── 일간 수익률 분포 ──
    with col_r:
        st.markdown('<div class="section-title">일간 수익률 분포</div>', unsafe_allow_html=True)
        daily_pct = close_s.pct_change().dropna() * 100
        fig_hist = go.Figure(go.Histogram(
            x=daily_pct.values, nbinsx=60,
            marker=dict(color="#4f6bdf", opacity=0.75, line=dict(color="#1e293b", width=0.3)),
        ))
        mean_ret = float(daily_pct.mean())
        fig_hist.add_vline(x=mean_ret, line_dash="dash", line_color="#f59e0b",
                           annotation_text=f"평균 {mean_ret:.3f}%",
                           annotation_font_color="#f59e0b")
        fig_hist.update_layout(
            **CHART_LAYOUT,
            title=dict(text="<b>일간 수익률 분포</b>", font=dict(size=13, color="#e2e8f0")),
            height=300, showlegend=False,
            xaxis_title="일간 수익률 (%)",
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    # ── 롤링 변동성 ──
    st.markdown('<div class="section-title">롤링 변동성 (30일 / 60일 연환산)</div>', unsafe_allow_html=True)
    roll30 = daily_pct.rolling(30).std() * np.sqrt(252)
    roll60 = daily_pct.rolling(60).std() * np.sqrt(252)
    fig_vol = go.Figure()
    fig_vol.add_trace(go.Scatter(
        x=roll30.index, y=roll30.values * 100,
        mode="lines", name="30일 변동성",
        line=dict(color="#06b6d4", width=1.8),
        fill="tozeroy", fillcolor="rgba(6,182,212,0.07)",
    ))
    fig_vol.add_trace(go.Scatter(
        x=roll60.index, y=roll60.values * 100,
        mode="lines", name="60일 변동성",
        line=dict(color="#a78bfa", width=1.5, dash="dot"),
    ))
    fig_vol.update_layout(
        **CHART_LAYOUT,
        title=dict(text="<b>롤링 변동성 (연환산 %)</b>", font=dict(size=13, color="#e2e8f0")),
        height=300, yaxis_title="변동성 (%)",
    )
    st.plotly_chart(fig_vol, use_container_width=True)

    # ── OBV ──
    if "OBV" in df_tech.columns:
        st.markdown('<div class="section-title">OBV (On-Balance Volume)</div>', unsafe_allow_html=True)
        fig_obv = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                row_heights=[0.6, 0.4], vertical_spacing=0.04)
        fig_obv.add_trace(go.Scatter(
            x=df_tech.index, y=df_tech["Close"],
            mode="lines", name="종가",
            line=dict(color="#e2e8f0", width=1.5),
        ), row=1, col=1)
        fig_obv.add_trace(go.Scatter(
            x=df_tech.index, y=df_tech["OBV"],
            mode="lines", name="OBV",
            line=dict(color="#00d4aa", width=1.5),
            fill="tozeroy", fillcolor="rgba(0,212,170,0.07)",
        ), row=2, col=1)
        fig_obv.update_layout(
            **{k: v for k, v in CHART_LAYOUT.items() if k not in ("xaxis", "yaxis")},
            title=dict(text="<b>종가 vs OBV 다이버전스 분석</b>", font=dict(size=13, color="#e2e8f0")),
            height=360,
        )
        for r in [1, 2]:
            fig_obv.update_xaxes(gridcolor="#1a2035", linecolor="#1e293b", row=r, col=1)
            fig_obv.update_yaxes(gridcolor="#1a2035", linecolor="#1e293b", row=r, col=1)
        st.plotly_chart(fig_obv, use_container_width=True)
        st.caption("OBV가 주가보다 먼저 상승(하락)하면 강세(약세) 다이버전스 신호로 해석됩니다.")

    # ── ATR ──
    if "ATR" in df_tech.columns:
        st.markdown('<div class="section-title">ATR (Average True Range · 14일)</div>', unsafe_allow_html=True)
        atr_pct = df_tech["ATR"] / df_tech["Close"] * 100
        fig_atr = go.Figure(go.Scatter(
            x=df_tech.index, y=atr_pct,
            mode="lines", name="ATR %",
            line=dict(color="#fb923c", width=1.8),
            fill="tozeroy", fillcolor="rgba(251,146,60,0.07)",
        ))
        fig_atr.update_layout(
            **CHART_LAYOUT,
            title=dict(text="<b>ATR % (일일 평균 변동폭 / 종가)</b>", font=dict(size=13, color="#e2e8f0")),
            height=280, showlegend=False, yaxis_title="ATR %",
        )
        st.plotly_chart(fig_atr, use_container_width=True)

# ════════════════════════════════════════════════════════════════
# TAB 5 : 투자 의견
# ════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-title">기술적 투자 의견 (자동 분석)</div>', unsafe_allow_html=True)
    st.caption("⚠️ 아래 의견은 기술적 지표를 기반으로 자동 생성된 참고 정보입니다. 실제 투자 결정에는 반드시 전문가 상담을 받으세요.")

    last_row = df_tech.iloc[-1]
    rsi_val  = last_row.get("RSI", 50)
    macd_val = last_row.get("MACD", 0)
    sig_val  = last_row.get("MACD_signal", 0)
    ma20_v   = last_row.get("MA20", last_price)
    ma60_v   = last_row.get("MA60", last_price)
    bb_upper = last_row.get("BB_upper", last_price * 1.05)
    bb_lower = last_row.get("BB_lower", last_price * 0.95)

    signals = []

    # RSI 신호
    if rsi_val < 30:
        signals.append(("buy", "RSI 과매도 구간", f"RSI가 {rsi_val:.1f}로 30 아래입니다. 과매도 상태로 반등 가능성이 있습니다.", 1))
    elif rsi_val > 70:
        signals.append(("sell", "RSI 과매수 구간", f"RSI가 {rsi_val:.1f}로 70 위입니다. 단기 과열 상태로 조정 가능성이 있습니다.", -1))
    else:
        signals.append(("hold", "RSI 중립 구간", f"RSI가 {rsi_val:.1f}로 중립 구간(30~70)에 위치합니다.", 0))

    # MACD 신호
    if macd_val > sig_val:
        signals.append(("buy", "MACD 골든크로스", "MACD 선이 시그널 선 위에 있습니다. 단기 상승 모멘텀이 우세합니다.", 1))
    else:
        signals.append(("sell", "MACD 데드크로스", "MACD 선이 시그널 선 아래에 있습니다. 단기 하락 압력이 존재합니다.", -1))

    # MA 크로스
    if ma20_v > ma60_v:
        signals.append(("buy", "이동평균 골든크로스 (MA20 > MA60)", f"단기 이동평균(MA20: ₩{ma20_v:,.0f})이 중기(MA60: ₩{ma60_v:,.0f}) 위에 위치합니다.", 1))
    else:
        signals.append(("sell", "이동평균 데드크로스 (MA20 < MA60)", f"단기 이동평균(MA20: ₩{ma20_v:,.0f})이 중기(MA60: ₩{ma60_v:,.0f}) 아래에 위치합니다.", -1))

    # 볼린저 밴드 위치
    bb_pct = (last_price - bb_lower) / (bb_upper - bb_lower) * 100 if bb_upper != bb_lower else 50
    if bb_pct > 90:
        signals.append(("sell", "볼린저 밴드 상단 근접", f"현재가(₩{last_price:,.0f})가 볼린저 밴드 상단(₩{bb_upper:,.0f}) 근처입니다. 단기 매도 신호.", -1))
    elif bb_pct < 10:
        signals.append(("buy", "볼린저 밴드 하단 근접", f"현재가(₩{last_price:,.0f})가 볼린저 밴드 하단(₩{bb_lower:,.0f}) 근처입니다. 반등 가능성.", 1))
    else:
        signals.append(("hold", "볼린저 밴드 중간 구간", f"현재가가 볼린저 밴드 내 {bb_pct:.0f}% 위치합니다. 방향성 중립.", 0))

    # 종합 점수
    score = sum(s[3] for s in signals)
    if score >= 2:
        overall_label, overall_color = "📈 종합 매수 의견", "#00d4aa"
    elif score <= -2:
        overall_label, overall_color = "📉 종합 매도 의견", "#ff4d6d"
    else:
        overall_label, overall_color = "⏸ 종합 중립 의견", "#f59e0b"

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#0d1a3a,#111827);border:2px solid {overall_color}33;
    border-radius:16px;padding:24px 32px;margin-bottom:24px;text-align:center;">
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.65rem;letter-spacing:0.2em;
        color:#64748b;text-transform:uppercase;margin-bottom:8px;">종합 투자 의견</div>
        <div style="font-family:'Noto Sans KR',sans-serif;font-size:1.7rem;font-weight:700;color:{overall_color};">
            {overall_label}
        </div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.8rem;color:#64748b;margin-top:8px;">
            신호 스코어: {score:+d} / 4개 지표 기반
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 개별 신호 카드
    for sentiment, title, desc, _ in signals:
        st.markdown(f"""
        <div class="opinion-card {sentiment}">
            <div class="opinion-label">{'▲ 매수 신호' if sentiment=='buy' else '▼ 매도 신호' if sentiment=='sell' else '◆ 중립 신호'}</div>
            <p class="opinion-title">{title}</p>
            <p class="opinion-desc">{desc}</p>
        </div>
        """, unsafe_allow_html=True)

    # 지지/저항 레벨
    st.markdown('<div class="section-title">주요 지지 · 저항 레벨</div>', unsafe_allow_html=True)
    r1, r2, r3, r4 = st.columns(4)
    r1.metric("1차 저항 (BB 상단)", f"₩{bb_upper:,.0f}")
    r2.metric("단기 이동평균 (MA20)", f"₩{ma20_v:,.0f}")
    r3.metric("중기 이동평균 (MA60)", f"₩{ma60_v:,.0f}")
    r4.metric("1차 지지 (BB 하단)", f"₩{bb_lower:,.0f}")

    # 가격 레벨 시각화
    fig_level = go.Figure()
    n_pts = min(120, len(close_s))
    sub_close = close_s.iloc[-n_pts:]
    fig_level.add_trace(go.Scatter(
        x=sub_close.index, y=sub_close.values,
        mode="lines", name="종가", line=dict(color="#e2e8f0", width=2),
    ))
    levels = [
        (bb_upper, "#ff4d6d", "BB 상단 (저항)", "dot"),
        (ma20_v,   "#f59e0b", "MA20",          "dash"),
        (ma60_v,   "#a78bfa", "MA60",           "dash"),
        (bb_lower, "#00d4aa", "BB 하단 (지지)", "dot"),
    ]
    for lv, color, label, dash in levels:
        fig_level.add_hline(y=lv, line_dash=dash, line_color=color,
                            line_width=1.5,
                            annotation_text=f" {label} ₩{lv:,.0f}",
                            annotation_font_color=color,
                            annotation_font_size=10)
    fig_level.update_layout(
        **CHART_LAYOUT,
        title=dict(text="<b>주요 지지·저항 레벨 (최근 120거래일)</b>", font=dict(size=13, color="#e2e8f0")),
        height=360, showlegend=False, yaxis_title="가격 (₩)",
    )
    st.plotly_chart(fig_level, use_container_width=True)
