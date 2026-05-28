import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import numpy as np

# ── 페이지 설정 ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="글로벌 주식 비교 대시보드",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS 커스텀 스타일 ─────────────────────────────────────────────────────────
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
    --text-primary: #e2e8f0;
    --text-muted: #64748b;
    --border: #1e293b;
}

html, body, .stApp {
    background-color: var(--bg-primary) !important;
    font-family: 'Noto Sans KR', sans-serif;
    color: var(--text-primary);
}

/* 사이드바 */
section[data-testid="stSidebar"] {
    background-color: var(--bg-secondary) !important;
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] * {
    color: var(--text-primary) !important;
}

/* 메트릭 카드 */
div[data-testid="metric-container"] {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px 20px;
    transition: border-color 0.2s;
}
div[data-testid="metric-container"]:hover {
    border-color: var(--accent-blue);
}
div[data-testid="metric-container"] label {
    color: var(--text-muted) !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: var(--text-primary) !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 1.4rem !important;
    font-weight: 600;
}
div[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.85rem !important;
}

/* 헤더 */
h1, h2, h3 { color: var(--text-primary) !important; }

/* 탭 */
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
    font-size: 0.8rem;
    letter-spacing: 0.05em;
    border: none !important;
}
.stTabs [aria-selected="true"] {
    background: var(--accent-blue) !important;
    color: white !important;
}

/* 선택 박스, 슬라이더 */
.stSelectbox > div > div, .stMultiSelect > div > div {
    background: var(--bg-card) !important;
    border-color: var(--border) !important;
    color: var(--text-primary) !important;
}

/* 구분선 */
hr { border-color: var(--border) !important; }

/* 데이터프레임 */
.stDataFrame { border: 1px solid var(--border) !important; border-radius: 10px; }

/* 헤더 배너 */
.dashboard-header {
    background: linear-gradient(135deg, #0f1729 0%, #1a2744 50%, #0f1729 100%);
    border: 1px solid #1e3a5f;
    border-radius: 16px;
    padding: 32px 40px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}
.dashboard-header::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(59,130,246,0.08) 0%, transparent 70%);
    pointer-events: none;
}
.header-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.8rem;
    font-weight: 600;
    color: #e2e8f0;
    margin: 0;
    letter-spacing: -0.02em;
}
.header-subtitle {
    font-family: 'Noto Sans KR', sans-serif;
    font-size: 0.85rem;
    color: #64748b;
    margin: 8px 0 0 0;
    letter-spacing: 0.02em;
}
.header-badge {
    display: inline-block;
    background: rgba(0, 212, 170, 0.1);
    border: 1px solid rgba(0, 212, 170, 0.3);
    color: #00d4aa;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    padding: 3px 10px;
    border-radius: 20px;
    letter-spacing: 0.1em;
    margin-top: 12px;
}

/* 섹션 타이틀 */
.section-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #3b82f6;
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 1px solid #1e293b;
}

/* 정보 카드 */
.info-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 16px;
}

/* 수익률 뱃지 */
.return-positive { color: #00d4aa; font-weight: 700; }
.return-negative { color: #ff4d6d; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# ── 상수 정의 ─────────────────────────────────────────────────────────────────
KR_STOCKS = {
    "삼성전자": "005930.KS",
    "SK하이닉스": "000660.KS",
    "LG에너지솔루션": "373220.KS",
    "삼성바이오로직스": "207940.KS",
    "현대차": "005380.KS",
    "POSCO홀딩스": "005490.KS",
    "카카오": "035720.KS",
    "네이버(NAVER)": "035420.KS",
    "셀트리온": "068270.KS",
    "KB금융": "105560.KS",
    "KODEX 200": "069500.KS",
    "KODEX 반도체": "091160.KS",
}

US_STOCKS = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "NVIDIA": "NVDA",
    "Amazon": "AMZN",
    "Alphabet (Google)": "GOOGL",
    "Meta": "META",
    "Tesla": "TSLA",
    "Berkshire Hathaway": "BRK-B",
    "JPMorgan Chase": "JPM",
    "S&P 500 ETF (SPY)": "SPY",
    "QQQ (나스닥100)": "QQQ",
    "ARK Innovation": "ARKK",
}

PERIODS = {
    "1개월": "1mo",
    "3개월": "3mo",
    "6개월": "6mo",
    "1년": "1y",
    "2년": "2y",
    "5년": "5y",
}

COLORS_PALETTE = [
    "#3b82f6", "#00d4aa", "#f59e0b", "#ff4d6d",
    "#a78bfa", "#fb923c", "#34d399", "#f472b6",
    "#60a5fa", "#4ade80", "#facc15", "#f87171",
]

# ── 데이터 로드 함수 ───────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_stock_data(tickers: list, period: str) -> dict:
    data = {}
    for ticker in tickers:
        try:
            df = yf.download(ticker, period=period, progress=False, auto_adjust=True)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                data[ticker] = df
        except Exception:
            pass
    return data

@st.cache_data(ttl=300)
def get_stock_info(ticker: str) -> dict:
    try:
        info = yf.Ticker(ticker).info
        return info
    except Exception:
        return {}

def calc_returns(df: pd.DataFrame) -> dict:
    """수익률 계산"""
    close = df["Close"].dropna()
    if close.empty or len(close) < 2:
        return {}
    first, last = float(close.iloc[0]), float(close.iloc[-1])
    total_return = (last - first) / first * 100
    daily_returns = close.pct_change().dropna()
    volatility = float(daily_returns.std() * np.sqrt(252) * 100)
    max_dd = float(((close / close.cummax()) - 1).min() * 100)
    sharpe = float((daily_returns.mean() * 252) / (daily_returns.std() * np.sqrt(252))) if daily_returns.std() > 0 else 0
    return {
        "total_return": total_return,
        "last_price": last,
        "volatility": volatility,
        "max_drawdown": max_dd,
        "sharpe": sharpe,
    }

def normalize_series(series: pd.Series) -> pd.Series:
    return series / series.iloc[0] * 100

# ── 차트 공통 레이아웃 ─────────────────────────────────────────────────────────
CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="IBM Plex Mono, monospace", color="#94a3b8", size=11),
    legend=dict(
        bgcolor="rgba(17,24,39,0.8)", bordercolor="#1e293b",
        borderwidth=1, font=dict(size=11)
    ),
    xaxis=dict(gridcolor="#1e293b", linecolor="#1e293b", showgrid=True, zeroline=False),
    yaxis=dict(gridcolor="#1e293b", linecolor="#1e293b", showgrid=True, zeroline=False),
    margin=dict(l=10, r=10, t=40, b=10),
    hovermode="x unified",
)

# ── 사이드바 ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="section-title">📊 종목 선택</div>', unsafe_allow_html=True)
    
    kr_selected_names = st.multiselect(
        "🇰🇷 한국 주식",
        options=list(KR_STOCKS.keys()),
        default=["삼성전자", "SK하이닉스", "현대차"],
        max_selections=6,
    )
    
    us_selected_names = st.multiselect(
        "🇺🇸 미국 주식",
        options=list(US_STOCKS.keys()),
        default=["Apple", "NVIDIA", "S&P 500 ETF (SPY)"],
        max_selections=6,
    )
    
    st.markdown("---")
    st.markdown('<div class="section-title">⚙️ 설정</div>', unsafe_allow_html=True)
    
    period_label = st.selectbox("기간 선택", options=list(PERIODS.keys()), index=3)
    period = PERIODS[period_label]
    
    chart_type = st.radio(
        "차트 종류",
        ["정규화 수익률", "가격 차트", "캔들스틱"],
        index=0,
    )
    
    show_volume = st.toggle("거래량 표시", value=True)
    show_ma = st.toggle("이동평균선 (20/60일)", value=True)
    
    st.markdown("---")
    st.markdown(
        '<div style="font-family:IBM Plex Mono;font-size:0.65rem;color:#475569;line-height:1.8;">'
        '데이터 제공: Yahoo Finance<br>5분마다 자동 갱신<br>투자 참고용 정보입니다.</div>',
        unsafe_allow_html=True,
    )

# ── 선택 종목 ticker 취합 ─────────────────────────────────────────────────────
kr_tickers = [KR_STOCKS[n] for n in kr_selected_names]
us_tickers = [US_STOCKS[n] for n in us_selected_names]
all_tickers = kr_tickers + us_tickers
ticker_name_map = {v: k for k, v in {**KR_STOCKS, **US_STOCKS}.items()}

if not all_tickers:
    st.warning("사이드바에서 종목을 1개 이상 선택해 주세요.")
    st.stop()

# ── 데이터 로드 ───────────────────────────────────────────────────────────────
with st.spinner("시장 데이터 불러오는 중..."):
    raw_data = load_stock_data(all_tickers, period)

valid_tickers = [t for t in all_tickers if t in raw_data]
if not valid_tickers:
    st.error("데이터를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.")
    st.stop()

# ── 헤더 ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="dashboard-header">
    <p class="header-title">📈 글로벌 주식 비교 대시보드</p>
    <p class="header-subtitle">한국 · 미국 주요 종목 수익률 및 리스크 분석</p>
    <div class="header-badge">LIVE · {datetime.now().strftime('%Y-%m-%d %H:%M')} KST</div>
</div>
""", unsafe_allow_html=True)

# ── 탭 구성 ───────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📊 수익률 비교", "📉 차트 분석", "📋 종목 상세", "🔥 상관관계"])

# ════════════════════════════════════════════════════════════════
# TAB 1: 수익률 비교
# ════════════════════════════════════════════════════════════════
with tab1:
    # 수익률 계산
    returns_data = []
    for ticker in valid_tickers:
        r = calc_returns(raw_data[ticker])
        if r:
            name = ticker_name_map.get(ticker, ticker)
            market = "🇰🇷 KR" if ticker in kr_tickers else "🇺🇸 US"
            returns_data.append({
                "티커": ticker, "종목명": name, "시장": market,
                **r
            })

    df_returns = pd.DataFrame(returns_data)

    # 요약 메트릭
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        best = df_returns.loc[df_returns["total_return"].idxmax()]
        st.metric("최고 수익률", best["종목명"], f"+{best['total_return']:.2f}%")
    with col2:
        worst = df_returns.loc[df_returns["total_return"].idxmin()]
        delta_str = f"{worst['total_return']:.2f}%"
        st.metric("최저 수익률", worst["종목명"], delta_str, delta_color="inverse")
    with col3:
        avg_kr = df_returns[df_returns["시장"] == "🇰🇷 KR"]["total_return"].mean()
        avg_us = df_returns[df_returns["시장"] == "🇺🇸 US"]["total_return"].mean()
        leader = "🇰🇷 한국" if avg_kr > avg_us else "🇺🇸 미국"
        st.metric("수익률 우세", leader, f"KR {avg_kr:.1f}% / US {avg_us:.1f}%")
    with col4:
        best_sharpe = df_returns.loc[df_returns["sharpe"].idxmax()]
        st.metric("최고 샤프지수", best_sharpe["종목명"], f"{best_sharpe['sharpe']:.2f}")

    st.markdown("<br>", unsafe_allow_html=True)

    # 수익률 막대 차트
    df_sorted = df_returns.sort_values("total_return", ascending=True)
    colors = ["#ff4d6d" if v < 0 else "#00d4aa" for v in df_sorted["total_return"]]
    bar_labels = [f"{'🇰🇷' if m=='🇰🇷 KR' else '🇺🇸'} {n}" for n, m in zip(df_sorted["종목명"], df_sorted["시장"])]

    fig_bar = go.Figure(go.Bar(
        x=df_sorted["total_return"],
        y=bar_labels,
        orientation="h",
        marker=dict(color=colors, line=dict(width=0)),
        text=[f"{v:+.2f}%" for v in df_sorted["total_return"]],
        textposition="outside",
        textfont=dict(family="IBM Plex Mono", size=11),
        hovertemplate="<b>%{y}</b><br>수익률: %{x:.2f}%<extra></extra>",
    ))
    fig_bar.update_layout(
        **CHART_LAYOUT,
        title=dict(text=f"<b>총 수익률 비교 ({period_label})</b>", font=dict(size=14, color="#e2e8f0")),
        height=max(350, len(df_sorted) * 45),
        xaxis_title="수익률 (%)",
        showlegend=False,
        xaxis=dict(**CHART_LAYOUT["xaxis"], ticksuffix="%"),
    )
    fig_bar.add_vline(x=0, line_color="#334155", line_width=1.5)
    st.plotly_chart(fig_bar, use_container_width=True)

    # 리스크-수익률 버블차트
    st.markdown('<div class="section-title">리스크 vs 수익률 분석</div>', unsafe_allow_html=True)
    fig_scatter = go.Figure()
    for i, row in df_returns.iterrows():
        color = "#3b82f6" if row["시장"] == "🇺🇸 US" else "#00d4aa"
        fig_scatter.add_trace(go.Scatter(
            x=[row["volatility"]], y=[row["total_return"]],
            mode="markers+text",
            marker=dict(size=max(14, abs(row["sharpe"]) * 10 + 14), color=color, opacity=0.8,
                        line=dict(width=1.5, color="white")),
            text=[row["종목명"].split("(")[0].strip()],
            textposition="top center",
            textfont=dict(size=10, family="IBM Plex Mono"),
            name=row["종목명"],
            hovertemplate=f"<b>{row['종목명']}</b><br>수익률: {row['total_return']:.2f}%<br>변동성: {row['volatility']:.2f}%<br>샤프: {row['sharpe']:.2f}<extra></extra>",
        ))
    fig_scatter.update_layout(
        **CHART_LAYOUT,
        title=dict(text="<b>리스크-수익률 산점도</b>  (버블 크기 = 샤프지수)", font=dict(size=14, color="#e2e8f0")),
        height=420,
        xaxis_title="연환산 변동성 (%)",
        yaxis_title="총 수익률 (%)",
        showlegend=False,
    )
    fig_scatter.add_hline(y=0, line_dash="dash", line_color="#334155", line_width=1)
    st.plotly_chart(fig_scatter, use_container_width=True)

    # 요약 테이블
    st.markdown('<div class="section-title">수익률 요약 테이블</div>', unsafe_allow_html=True)
    display_df = df_returns[["종목명", "시장", "last_price", "total_return", "volatility", "max_drawdown", "sharpe"]].copy()
    display_df.columns = ["종목명", "시장", "현재가", "수익률(%)", "변동성(%)", "최대낙폭(%)", "샤프지수"]
    display_df = display_df.sort_values("수익률(%)", ascending=False).reset_index(drop=True)
    display_df["현재가"] = display_df["현재가"].apply(lambda x: f"{x:,.2f}")
    display_df["수익률(%)"] = display_df["수익률(%)"].apply(lambda x: f"{x:+.2f}%")
    display_df["변동성(%)"] = display_df["변동성(%)"].apply(lambda x: f"{x:.2f}%")
    display_df["최대낙폭(%)"] = display_df["최대낙폭(%)"].apply(lambda x: f"{x:.2f}%")
    display_df["샤프지수"] = display_df["샤프지수"].apply(lambda x: f"{x:.2f}")
    st.dataframe(display_df, use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════════════════════
# TAB 2: 차트 분석
# ════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-title">가격 차트</div>', unsafe_allow_html=True)

    if chart_type == "정규화 수익률":
        fig = go.Figure()
        for i, ticker in enumerate(valid_tickers):
            df = raw_data[ticker]
            close = df["Close"].dropna()
            if isinstance(close, pd.DataFrame):
                close = close.squeeze()
            norm = normalize_series(close)
            name = ticker_name_map.get(ticker, ticker)
            flag = "🇰🇷" if ticker in kr_tickers else "🇺🇸"
            color = COLORS_PALETTE[i % len(COLORS_PALETTE)]
            fig.add_trace(go.Scatter(
                x=norm.index, y=norm.values,
                mode="lines", name=f"{flag} {name}",
                line=dict(color=color, width=2),
                hovertemplate=f"<b>{name}</b><br>%{{x|%Y-%m-%d}}<br>기준: %{{y:.1f}}<extra></extra>",
            ))
        fig.add_hline(y=100, line_dash="dot", line_color="#475569", line_width=1)
        fig.update_layout(
            **CHART_LAYOUT,
            title=dict(text="<b>정규화 수익률 비교</b>  (기준시점 = 100)", font=dict(size=14, color="#e2e8f0")),
            height=500,
            yaxis_title="기준치 (100 = 시작점)",
        )
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "가격 차트":
        n_cols = 2
        rows = (len(valid_tickers) + 1) // n_cols
        specs = [[{"secondary_y": show_volume}] * n_cols for _ in range(rows)]
        fig = make_subplots(rows=rows, cols=n_cols, specs=specs, vertical_spacing=0.08, horizontal_spacing=0.05)
        for idx, ticker in enumerate(valid_tickers):
            row, col = idx // n_cols + 1, idx % n_cols + 1
            df = raw_data[ticker]
            close = df["Close"].dropna()
            if isinstance(close, pd.DataFrame):
                close = close.squeeze()
            name = ticker_name_map.get(ticker, ticker)
            color = COLORS_PALETTE[idx % len(COLORS_PALETTE)]
            fig.add_trace(go.Scatter(
                x=close.index, y=close.values, mode="lines",
                name=name, line=dict(color=color, width=1.8), showlegend=True,
            ), row=row, col=col)
            if show_ma and len(close) > 60:
                for win, c in [(20, "#f59e0b"), (60, "#a78bfa")]:
                    ma = close.rolling(win).mean()
                    fig.add_trace(go.Scatter(
                        x=ma.index, y=ma.values, mode="lines", name=f"MA{win}",
                        line=dict(color=c, width=1, dash="dash"), showlegend=(idx == 0),
                    ), row=row, col=col)
            if show_volume and "Volume" in df.columns:
                vol = df["Volume"].dropna()
                if isinstance(vol, pd.DataFrame):
                    vol = vol.squeeze()
                fig.add_trace(go.Bar(
                    x=vol.index, y=vol.values, name="거래량",
                    marker_color="rgba(59,130,246,0.25)", showlegend=False,
                ), row=row, col=col, secondary_y=True)
        fig.update_layout(
            **CHART_LAYOUT,
            title=dict(text="<b>개별 가격 차트</b>", font=dict(size=14, color="#e2e8f0")),
            height=300 * rows,
        )
        for ax in fig.layout:
            if "yaxis" in ax:
                fig.layout[ax].update(gridcolor="#1e293b", linecolor="#1e293b")
        st.plotly_chart(fig, use_container_width=True)

    else:  # 캔들스틱
        selected = st.selectbox(
            "캔들스틱 종목 선택",
            options=valid_tickers,
            format_func=lambda t: f"{'🇰🇷' if t in kr_tickers else '🇺🇸'} {ticker_name_map.get(t, t)}"
        )
        df = raw_data[selected]
        name = ticker_name_map.get(selected, selected)
        close = df["Close"].dropna()
        if isinstance(close, pd.DataFrame):
            close = close.squeeze()

        specs_c = [[{"secondary_y": True}]] if show_volume else [[{}]]
        fig = make_subplots(rows=1, cols=1, specs=specs_c)

        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df["Open"].squeeze() if isinstance(df["Open"], pd.DataFrame) else df["Open"],
            high=df["High"].squeeze() if isinstance(df["High"], pd.DataFrame) else df["High"],
            low=df["Low"].squeeze() if isinstance(df["Low"], pd.DataFrame) else df["Low"],
            close=close,
            name=name,
            increasing_line_color="#00d4aa",
            decreasing_line_color="#ff4d6d",
        ))
        if show_ma and len(close) > 60:
            for win, c in [(20, "#f59e0b"), (60, "#a78bfa")]:
                ma = close.rolling(win).mean()
                fig.add_trace(go.Scatter(
                    x=ma.index, y=ma.values, mode="lines", name=f"MA{win}",
                    line=dict(color=c, width=1.5, dash="dash"),
                ))
        if show_volume and "Volume" in df.columns:
            vol = df["Volume"].dropna()
            if isinstance(vol, pd.DataFrame):
                vol = vol.squeeze()
            fig.add_trace(go.Bar(
                x=vol.index, y=vol.values, name="거래량",
                marker_color="rgba(100,116,139,0.3)",
            ), secondary_y=True)
        fig.update_layout(
            **CHART_LAYOUT,
            title=dict(text=f"<b>{name} 캔들스틱 차트</b>", font=dict(size=14, color="#e2e8f0")),
            height=550,
            xaxis_rangeslider_visible=False,
        )
        st.plotly_chart(fig, use_container_width=True)

# ════════════════════════════════════════════════════════════════
# TAB 3: 종목 상세
# ════════════════════════════════════════════════════════════════
with tab3:
    selected_detail = st.selectbox(
        "상세 조회 종목",
        options=valid_tickers,
        format_func=lambda t: f"{'🇰🇷' if t in kr_tickers else '🇺🇸'} {ticker_name_map.get(t, t)}"
    )

    with st.spinner("종목 정보 로딩 중..."):
        info = get_stock_info(selected_detail)

    name = ticker_name_map.get(selected_detail, selected_detail)
    df = raw_data[selected_detail]
    close = df["Close"].dropna()
    if isinstance(close, pd.DataFrame):
        close = close.squeeze()
    r = calc_returns(df)

    st.markdown(f"### {'🇰🇷' if selected_detail in kr_tickers else '🇺🇸'} {name}")

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("현재가", f"{r.get('last_price', 0):,.2f}")
    col2.metric("총 수익률", f"{r.get('total_return', 0):+.2f}%")
    col3.metric("연환산 변동성", f"{r.get('volatility', 0):.2f}%")
    col4.metric("최대 낙폭", f"{r.get('max_drawdown', 0):.2f}%")
    col5.metric("샤프지수", f"{r.get('sharpe', 0):.2f}")

    # 기업 기본 정보
    if info:
        st.markdown('<div class="section-title" style="margin-top:24px;">기업 정보</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            mktcap = info.get("marketCap", 0)
            if mktcap:
                if mktcap >= 1e12:
                    mktcap_str = f"${mktcap/1e12:.2f}T"
                elif mktcap >= 1e9:
                    mktcap_str = f"${mktcap/1e9:.2f}B"
                else:
                    mktcap_str = f"${mktcap/1e6:.0f}M"
                st.metric("시가총액", mktcap_str)
        with c2:
            pe = info.get("trailingPE")
            if pe:
                st.metric("P/E Ratio", f"{pe:.2f}x")
        with c3:
            div = info.get("dividendYield")
            if div:
                st.metric("배당수익률", f"{div*100:.2f}%")

    # 이동평균 리본 차트
    st.markdown('<div class="section-title" style="margin-top:16px;">이동평균 분석</div>', unsafe_allow_html=True)
    fig_ma = go.Figure()
    ma_configs = [(5, "#3b82f6"), (20, "#f59e0b"), (60, "#a78bfa"), (120, "#fb923c")]
    fig_ma.add_trace(go.Scatter(
        x=close.index, y=close.values, mode="lines", name="종가",
        line=dict(color="#e2e8f0", width=1.5),
    ))
    for win, color in ma_configs:
        if len(close) > win:
            ma = close.rolling(win).mean()
            fig_ma.add_trace(go.Scatter(
                x=ma.index, y=ma.values, mode="lines", name=f"MA{win}",
                line=dict(color=color, width=1.2, dash="dot"),
            ))
    fig_ma.update_layout(
        **CHART_LAYOUT,
        title=dict(text=f"<b>{name} 이동평균 리본</b>", font=dict(size=13, color="#e2e8f0")),
        height=380,
    )
    st.plotly_chart(fig_ma, use_container_width=True)

    # 일간 수익률 분포
    col_a, col_b = st.columns(2)
    daily_ret = close.pct_change().dropna() * 100
    if isinstance(daily_ret, pd.DataFrame):
        daily_ret = daily_ret.squeeze()

    with col_a:
        fig_hist = go.Figure(go.Histogram(
            x=daily_ret.values, nbinsx=50,
            marker=dict(color="#3b82f6", opacity=0.7, line=dict(color="#1e293b", width=0.3)),
            name="일간 수익률",
        ))
        fig_hist.update_layout(
            **CHART_LAYOUT,
            title=dict(text="<b>일간 수익률 분포</b>", font=dict(size=13, color="#e2e8f0")),
            height=320, showlegend=False,
            xaxis_title="일간 수익률 (%)",
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    with col_b:
        # MDD 드로다운 차트
        drawdown = (close / close.cummax() - 1) * 100
        if isinstance(drawdown, pd.DataFrame):
            drawdown = drawdown.squeeze()
        fig_dd = go.Figure(go.Scatter(
            x=drawdown.index, y=drawdown.values,
            mode="lines", fill="tozeroy",
            fillcolor="rgba(255,77,109,0.15)",
            line=dict(color="#ff4d6d", width=1.5),
            name="낙폭",
        ))
        fig_dd.update_layout(
            **CHART_LAYOUT,
            title=dict(text="<b>낙폭(Drawdown) 추이</b>", font=dict(size=13, color="#e2e8f0")),
            height=320, showlegend=False,
            yaxis_title="낙폭 (%)",
        )
        st.plotly_chart(fig_dd, use_container_width=True)

# ════════════════════════════════════════════════════════════════
# TAB 4: 상관관계
# ════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-title">수익률 상관관계 히트맵</div>', unsafe_allow_html=True)

    if len(valid_tickers) < 2:
        st.info("상관관계 분석은 2개 이상의 종목이 필요합니다.")
    else:
        # 수익률 데이터프레임 구성
        returns_dict = {}
        for ticker in valid_tickers:
            close = raw_data[ticker]["Close"].dropna()
            if isinstance(close, pd.DataFrame):
                close = close.squeeze()
            ret = close.pct_change().dropna()
            name = ticker_name_map.get(ticker, ticker).split("(")[0].strip()
            returns_dict[name] = ret

        ret_df = pd.DataFrame(returns_dict).dropna()
        corr = ret_df.corr()

        # 히트맵
        mask = np.triu(np.ones(corr.shape), k=1).astype(bool)
        z_masked = corr.values.copy()
        z_masked[mask] = None

        fig_heat = go.Figure(go.Heatmap(
            z=z_masked,
            x=corr.columns.tolist(),
            y=corr.index.tolist(),
            colorscale=[
                [0.0, "#ff4d6d"], [0.3, "#1e293b"], [0.5, "#1e3a5f"],
                [0.7, "#1e4a6f"], [1.0, "#00d4aa"],
            ],
            zmin=-1, zmax=1,
            text=[[f"{v:.2f}" if v is not None else "" for v in row] for row in z_masked],
            texttemplate="%{text}",
            textfont=dict(size=11, family="IBM Plex Mono"),
            hoverongaps=False,
            colorbar=dict(tickfont=dict(family="IBM Plex Mono", size=10), thickness=12),
        ))
        fig_heat.update_layout(
            **CHART_LAYOUT,
            title=dict(text="<b>일간 수익률 상관계수 (하삼각)</b>", font=dict(size=14, color="#e2e8f0")),
            height=max(400, len(valid_tickers) * 55 + 100),
        )
        st.plotly_chart(fig_heat, use_container_width=True)

        # 롤링 상관계수 (2개 선택 시)
        if len(valid_tickers) >= 2:
            st.markdown('<div class="section-title">롤링 상관계수 (30일)</div>', unsafe_allow_html=True)
            cols = st.columns(2)
            names = list(returns_dict.keys())
            with cols[0]:
                t1 = st.selectbox("종목 A", names, index=0)
            with cols[1]:
                t2 = st.selectbox("종목 B", names, index=min(1, len(names)-1))

            if t1 != t2 and t1 in ret_df.columns and t2 in ret_df.columns:
                rolling_corr = ret_df[t1].rolling(30).corr(ret_df[t2])
                fig_roll = go.Figure(go.Scatter(
                    x=rolling_corr.index, y=rolling_corr.values,
                    mode="lines", fill="tozeroy",
                    fillcolor="rgba(59,130,246,0.1)",
                    line=dict(color="#3b82f6", width=2),
                ))
                fig_roll.add_hline(y=0, line_dash="dot", line_color="#475569", line_width=1)
                fig_roll.update_layout(
                    **CHART_LAYOUT,
                    title=dict(text=f"<b>{t1} ↔ {t2}  30일 롤링 상관계수</b>", font=dict(size=13, color="#e2e8f0")),
                    height=320, showlegend=False,
                    yaxis=dict(**CHART_LAYOUT["yaxis"], range=[-1, 1]),
                )
                st.plotly_chart(fig_roll, use_container_width=True)

        # 포트폴리오 수익률 (동일 비중)
        st.markdown('<div class="section-title">동일비중 포트폴리오 수익률</div>', unsafe_allow_html=True)
        port_ret = ret_df.mean(axis=1)
        port_cum = (1 + port_ret).cumprod() * 100

        kr_names = [ticker_name_map.get(t, t).split("(")[0].strip() for t in kr_tickers if t in valid_tickers]
        us_names = [ticker_name_map.get(t, t).split("(")[0].strip() for t in us_tickers if t in valid_tickers]

        fig_port = go.Figure()
        if kr_names:
            kr_cols = [c for c in kr_names if c in ret_df.columns]
            if kr_cols:
                kr_cum = (1 + ret_df[kr_cols].mean(axis=1)).cumprod() * 100
                fig_port.add_trace(go.Scatter(
                    x=kr_cum.index, y=kr_cum.values, mode="lines", name="🇰🇷 KR 포트폴리오",
                    line=dict(color="#00d4aa", width=2),
                ))
        if us_names:
            us_cols = [c for c in us_names if c in ret_df.columns]
            if us_cols:
                us_cum = (1 + ret_df[us_cols].mean(axis=1)).cumprod() * 100
                fig_port.add_trace(go.Scatter(
                    x=us_cum.index, y=us_cum.values, mode="lines", name="🇺🇸 US 포트폴리오",
                    line=dict(color="#3b82f6", width=2),
                ))
        fig_port.add_trace(go.Scatter(
            x=port_cum.index, y=port_cum.values, mode="lines", name="🌐 통합 포트폴리오",
            line=dict(color="#f59e0b", width=2, dash="dot"),
        ))
        fig_port.add_hline(y=100, line_dash="dot", line_color="#475569", line_width=1)
        fig_port.update_layout(
            **CHART_LAYOUT,
            title=dict(text="<b>동일비중 포트폴리오 누적 수익률</b>  (기준 = 100)", font=dict(size=13, color="#e2e8f0")),
            height=380,
        )
        st.plotly_chart(fig_port, use_container_width=True)
