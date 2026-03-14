import numpy as np
import pandas as pd
import streamlit as st
import streamlit_shadcn_ui as ui
from streamlit_shadcn_ui import select, input
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import xarray as xr
import tempfile
import os

# ══════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="ClimaDuel — Dataset Comparison",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --bg:      #080c14;
    --bg2:     #0e1420;
    --bg3:     #141b2d;
    --border:  #1e2d4a;
    --col-a:   #00e5ff;
    --col-b:   #ff6b35;
    --col-neu: #c8d4f0;
    --col-dim: #5a6a8a;
    --pos:     #22d3a5;
    --neg:     #f43f5e;
}

[data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at 20% 20%, rgba(0,229,255,0.07), transparent 40%),
                radial-gradient(circle at 80% 80%, rgba(124,58,237,0.07), transparent 40%),
                linear-gradient(180deg, #0a0f1f 0%, #060912 100%);
}
[data-testid="stHeader"] { background: transparent; }

[data-testid="stSidebar"] {
    background: linear-gradient(160deg, #0d1528 0%, #0a1020 50%, #091018 100%) !important;
    border-right: 2px solid #1e3a6e !important;
}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stMarkdown div,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] p { color: #dde8ff !important; }
[data-testid="stSidebar"] hr {
    border: none !important;
    border-top: 1px solid #1e3a5f !important;
    margin: 0.8rem 0 !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: #0e1624 !important;
    border: 1px solid #2a3f6a !important;
    color: #c8d4f0 !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] > div:hover {
    border-color: #00e5ff !important;
}
[data-testid="stSidebar"] input[type="number"],
[data-testid="stSidebar"] input[type="text"] {
    background: #0e1624 !important;
    border: 1px solid #2a3f6a !important;
    color: #e8f0ff !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] input:focus {
    border-color: #00e5ff !important;
    box-shadow: 0 0 10px rgba(0,229,255,0.25) !important;
}
[data-testid="stSidebar"] .stButton > button {
    background: linear-gradient(135deg, rgba(0,229,255,0.15), rgba(124,58,237,0.15)) !important;
    border: 1px solid rgba(0,229,255,0.6) !important;
    color: #00e5ff !important;
    font-weight: 700 !important;
    border-radius: 10px !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: linear-gradient(135deg, rgba(0,229,255,0.3), rgba(124,58,237,0.3)) !important;
    box-shadow: 0 0 18px rgba(0,229,255,0.35) !important;
}

#MainMenu, footer, header { visibility: hidden; }

.page-hero {
    background: linear-gradient(135deg, #0e1420 0%, #141b2d 100%);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.page-hero::before {
    content: '';
    position: absolute; top:0; left:0; right:0; bottom:0;
    background: radial-gradient(ellipse at top left, rgba(0,229,255,0.06) 0%, transparent 60%),
                radial-gradient(ellipse at bottom right, rgba(255,107,53,0.06) 0%, transparent 60%);
    pointer-events: none;
}
.page-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 3.8rem;
    letter-spacing: 3px;
    margin: 0;
    background: linear-gradient(90deg, var(--col-a), #a78bfa, var(--col-b));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1;
}
.page-sub {
    font-family: 'DM Sans', sans-serif;
    color: var(--col-dim);
    font-size: 0.95rem;
    margin: 0.5rem 0 0 0;
}
.ds-card {
    border-radius: 14px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 0.8rem;
    border: 1px solid;
    position: relative;
    overflow: hidden;
}
.ds-card-a {
    background: linear-gradient(135deg, rgba(0,229,255,0.08) 0%, rgba(0,229,255,0.03) 100%);
    border-color: rgba(0,229,255,0.3);
}
.ds-card-b {
    background: linear-gradient(135deg, rgba(255,107,53,0.08) 0%, rgba(255,107,53,0.03) 100%);
    border-color: rgba(255,107,53,0.3);
}
.ds-label { font-family:'Bebas Neue',sans-serif; font-size:1.1rem; letter-spacing:2px; margin:0 0 0.2rem 0; }
.ds-label-a { color: var(--col-a); }
.ds-label-b { color: var(--col-b); }
.ds-value { font-family:'DM Sans',sans-serif; font-size:2rem; font-weight:600; color:#e8f0ff; margin:0; }
.ds-sub   { font-family:'DM Sans',sans-serif; font-size:0.78rem; color:var(--col-dim); margin:0; }

.sec-head {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.5rem;
    letter-spacing: 2px;
    color: var(--col-neu);
    border-bottom: 1px solid var(--border);
    padding-bottom: 0.4rem;
    margin: 2rem 0 1rem 0;
}
.insight-card {
    background: var(--bg3);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.5rem;
}
.insight-icon  { font-size: 1.6rem; margin-bottom: 0.3rem; }
.insight-title { font-family:'Bebas Neue',sans-serif; letter-spacing:1.5px; font-size:0.85rem; color:var(--col-dim); margin:0; }
.insight-body  { font-family:'DM Sans',sans-serif; font-size:0.9rem; color:var(--col-neu); margin:0.3rem 0 0 0; line-height:1.5; }
.insight-val-pos { color:var(--pos); font-weight:600; }
.insight-val-neg { color:var(--neg); font-weight:600; }
.insight-val-a   { color:var(--col-a); font-weight:600; }
.insight-val-b   { color:var(--col-b); font-weight:600; }

.verdict {
    background: linear-gradient(135deg, rgba(124,58,237,0.12) 0%, rgba(124,58,237,0.05) 100%);
    border: 1px solid rgba(124,58,237,0.4);
    border-radius: 14px;
    padding: 1.4rem 1.8rem;
    margin-top: 1.5rem;
}
.verdict-title { font-family:'Bebas Neue',sans-serif; font-size:1.3rem; letter-spacing:2px; color:#a78bfa; margin:0 0 0.6rem 0; }
.verdict-body  { font-family:'DM Sans',sans-serif; font-size:0.92rem; color:var(--col-neu); line-height:1.7; margin:0; }

.badge { display:inline-block; padding:0.15rem 0.7rem; border-radius:20px; font-family:'Bebas Neue',sans-serif; font-size:0.85rem; letter-spacing:1.5px; margin-right:0.4rem; }
.badge-a { background:rgba(0,229,255,0.15); color:var(--col-a); border:1px solid rgba(0,229,255,0.4); }
.badge-b { background:rgba(255,107,53,0.15); color:var(--col-b); border:1px solid rgba(255,107,53,0.4); }

h1,h2,h3,h4 { color: #e8f0ff !important; }
p, label, .stMarkdown { color: var(--col-neu) !important; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════

def safe_polyfit(x, y):
    """Return (slope, intercept) or (0, mean) if polyfit fails."""
    try:
        arr = np.array(y, dtype=float)
        if len(arr) < 2 or np.std(arr) == 0:
            return 0.0, float(np.nanmean(arr))
        c = np.polyfit(x, arr, 1)
        return float(c[0]), float(c[1])
    except (np.linalg.LinAlgError, Exception):
        return 0.0, float(np.nanmean(y))


# ══════════════════════════════════════════════════════════════
# DATA FUNCTIONS
# ══════════════════════════════════════════════════════════════

@st.cache_data
def generate_dataset(variable: str, start_year: int, n_years: int) -> xr.Dataset:
    """Generate realistic synthetic climate dataset."""
    n_years = max(1, int(n_years))
    seed = start_year % 100
    np.random.seed(seed)
    lats  = np.linspace(-90, 90, 37)
    lons  = np.linspace(-180, 180, 72)
    times = pd.date_range(f"{start_year}-01-01", periods=n_years * 12, freq="MS")
    lat2d, lon2d = np.meshgrid(lats, lons, indexing="ij")

    base = (
        28 * np.cos(np.radians(lat2d))
        - 12 * np.abs(np.cos(np.radians(lat2d * 2)))
        + 4  * np.sin(np.radians(lon2d * 0.6))
    )
    data = np.zeros((len(times), len(lats), len(lons)), dtype=np.float32)
    for t_idx, ts in enumerate(times):
        seasonal = 9 * np.sin(2 * np.pi * (ts.month - 3) / 12) * np.cos(np.radians(lat2d))
        trend    = 0.025 * (t_idx / 12)
        noise    = np.random.normal(0, 1.8, base.shape)
        data[t_idx] = base + seasonal + trend + noise

    if variable == "Precipitation":
        data = np.clip((data + 38) * 0.16, 0, 22).astype(np.float32)
        units, long_name = "mm/day", "Precipitation"
    elif variable == "Wind Speed":
        data = np.abs(data * 0.32 + 5.2).astype(np.float32)
        units, long_name = "m/s", "Wind Speed"
    else:
        units, long_name = "°C", "Temperature"

    return xr.Dataset(
        {"value": (["time", "lat", "lon"], data, {"units": units, "long_name": long_name})},
        coords={"time": times, "lat": lats, "lon": lons},
    )


@st.cache_data
def load_nc(file_bytes: bytes, fname: str) -> xr.Dataset:
    with tempfile.NamedTemporaryFile(suffix=".nc", delete=False) as f:
        f.write(file_bytes)
        tmp = f.name
    ds = xr.open_dataset(tmp)
    os.unlink(tmp)
    return ds


def compute_full_comparison(ds_a: xr.Dataset, ds_b: xr.Dataset,
                             label_a: str, label_b: str) -> dict:
    """
    Master comparison function.
    Extracts every metric needed for all charts and insights.
    Fully guarded against edge cases (1-year, constant data, etc.)
    """
    def extract(ds):
        v       = ds["value"].values.flatten()
        v       = v[~np.isnan(v)]
        v       = v if len(v) > 0 else np.array([0.0])

        ann     = ds["value"].mean(dim=["lat", "lon"]).groupby("time.year").mean()
        mon     = ds["value"].mean(dim=["lat", "lon"]).groupby("time.month").mean()
        zm      = ds["value"].mean(dim=["time", "lon"]).values
        ts      = ds["value"].mean(dim=["lat", "lon"]).values

        ann_yrs  = ann["year"].values.tolist()
        ann_vals = ann.values.tolist()

        # Pad monthly to 12 if fewer months exist
        mon_vals = mon.values.tolist()
        while len(mon_vals) < 12:
            mon_vals.append(mon_vals[-1] if mon_vals else 0.0)
        mon_vals = mon_vals[:12]

        # Safe trend
        x_ts = np.arange(len(ts))
        slope, _ = safe_polyfit(x_ts, ts)
        trend = slope * 120  # per decade

        # Safe skew/kurtosis
        s = pd.Series(v)
        try:
            skew = float(s.skew())
        except Exception:
            skew = 0.0
        try:
            kurt = float(s.kurtosis())
        except Exception:
            kurt = 0.0

        return dict(
            flat        = v,
            mean        = float(np.nanmean(v)),
            median      = float(np.nanmedian(v)),
            std         = float(np.nanstd(v)) if len(v) > 1 else 0.0,
            minimum     = float(np.nanmin(v)),
            maximum     = float(np.nanmax(v)),
            q25         = float(np.nanpercentile(v, 25)),
            q75         = float(np.nanpercentile(v, 75)),
            skew        = skew,
            kurtosis    = kurt,
            annual_years= ann_yrs,
            annual_vals = ann_vals,
            monthly_vals= mon_vals,
            zonal_mean  = zm.tolist(),
            lats        = ds["lat"].values.tolist(),
            lons        = ds["lon"].values.tolist(),
            ts          = ts.tolist(),
            n_years     = int(ds.time.dt.year.max() - ds.time.dt.year.min() + 1),
            year_start  = int(ds.time.dt.year.min()),
            year_end    = int(ds.time.dt.year.max()),
            n_points    = len(v),
            trend       = trend,
        )

    ea = extract(ds_a)
    eb = extract(ds_b)
    units     = ds_a["value"].attrs.get("units", "")
    long_name = ds_a["value"].attrs.get("long_name", "Variable")

    return dict(
        a            = ea,
        b            = eb,
        label_a      = label_a,
        label_b      = label_b,
        units        = units,
        long_name    = long_name,
        delta_mean   = ea["mean"]  - eb["mean"],
        delta_std    = ea["std"]   - eb["std"],
        delta_trend  = ea["trend"] - eb["trend"],
        warmer       = label_a if ea["mean"]  > eb["mean"]  else label_b,
        more_variable= label_a if ea["std"]   > eb["std"]   else label_b,
        faster_warming=label_a if ea["trend"] > eb["trend"] else label_b,
    )


# ══════════════════════════════════════════════════════════════
# CHART CONSTANTS
# ══════════════════════════════════════════════════════════════
_BG  = "#080c14"
_BG2 = "#0e1420"
_BG3 = "#141b2d"
_GR  = "#1e2d4a"
_CA  = "#00e5ff"
_CB  = "#ff6b35"
_FT  = "#c8d4f0"
_DIM = "#5a6a8a"
_DARK = dict(paper_bgcolor=_BG2, plot_bgcolor=_BG3, font=dict(color=_FT, family="DM Sans"))
_MN   = dict(l=10, r=10, t=50, b=10)

def _ax(**kw):
    base = dict(gridcolor=_GR, zerolinecolor=_GR, color=_FT, showgrid=True)
    base.update(kw)
    return base


# ══════════════════════════════════════════════════════════════
# CHART FUNCTIONS
# ══════════════════════════════════════════════════════════════

def chart_annual_trend(r):
    fig = go.Figure()
    for key, col, lbl in [("a", _CA, r["label_a"]), ("b", _CB, r["label_b"])]:
        yrs  = r[key]["annual_years"]
        vals = r[key]["annual_vals"]
        fig.add_trace(go.Scatter(
            x=yrs, y=vals, name=lbl, mode="lines+markers",
            line=dict(color=col, width=2.5), marker=dict(size=5, color=col),
            hovertemplate=f"{lbl} %{{x}}: %{{y:.2f}} {r['units']}<extra></extra>",
        ))
        # Safe trend line
        if len(vals) >= 2:
            x = np.arange(len(vals))
            slope, intercept = safe_polyfit(x, vals)
            trend_y = (slope * x + intercept).tolist()
            fig.add_trace(go.Scatter(
                x=yrs, y=trend_y, name=f"{lbl} trend", mode="lines",
                line=dict(color=col, width=1.2, dash="dot"),
                hoverinfo="skip",
            ))
    fig.update_layout(
        **_DARK,
        title=dict(text="Annual Global Mean — Trend Over Time",
                   font=dict(color=_FT, size=14, family="Bebas Neue"), x=0.01),
        xaxis=_ax(title="Year"), yaxis=_ax(title=r["units"]),
        legend=dict(bgcolor="rgba(0,0,0,0.4)", font=dict(color=_FT)),
        hovermode="x unified", margin=_MN, height=360,
    )
    return fig


def chart_seasonal(r):
    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=months, y=r["a"]["monthly_vals"], name=r["label_a"],
        marker_color=_CA, opacity=0.85,
        hovertemplate=f"{r['label_a']} %{{x}}: %{{y:.2f}} {r['units']}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        x=months, y=r["b"]["monthly_vals"], name=r["label_b"],
        marker_color=_CB, opacity=0.85,
        hovertemplate=f"{r['label_b']} %{{x}}: %{{y:.2f}} {r['units']}<extra></extra>",
    ))
    fig.update_layout(
        **_DARK,
        title=dict(text="Seasonal Cycle — Monthly Climatology",
                   font=dict(color=_FT, size=14, family="Bebas Neue"), x=0.01),
        barmode="group", xaxis=_ax(title="Month"), yaxis=_ax(title=r["units"]),
        legend=dict(bgcolor="rgba(0,0,0,0.4)", font=dict(color=_FT)),
        margin=_MN, height=340,
    )
    return fig


def chart_histogram(r):
    fig = go.Figure()
    for key, col, lbl in [("a", _CA, r["label_a"]), ("b", _CB, r["label_b"])]:
        vals = r[key]["flat"]
        mean_val = float(np.nanmean(vals))
        fig.add_trace(go.Histogram(
            x=vals, name=lbl, nbinsx=50,
            marker_color=col, opacity=0.55,
            hovertemplate=f"{lbl}: %{{x:.2f}} {r['units']}<extra></extra>",
        ))
        fig.add_vline(
            x=mean_val, line_color=col, line_dash="dash", line_width=1.5,
            annotation_text=f"{lbl} μ={mean_val:.2f}",
            annotation_font_color=col, annotation_font_size=10,
        )
    fig.update_layout(
        **_DARK,
        title=dict(text="Value Distribution — Histogram Overlay",
                   font=dict(color=_FT, size=14, family="Bebas Neue"), x=0.01),
        barmode="overlay", xaxis=_ax(title=r["units"]), yaxis=_ax(title="Count"),
        legend=dict(bgcolor="rgba(0,0,0,0.4)", font=dict(color=_FT)),
        margin=_MN, height=340,
    )
    return fig


def chart_stats_pie(r):
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "domain"}, {"type": "domain"}]],
        subplot_titles=["Mean Value Share", "Variability Share (Std Dev)"],
    )
    for ci, (vals, title) in enumerate([
        ([abs(r["a"]["mean"]), abs(r["b"]["mean"])], "Mean"),
        ([max(r["a"]["std"], 1e-9), max(r["b"]["std"], 1e-9)], "Std"),
    ], 1):
        fig.add_trace(go.Pie(
            labels=[r["label_a"], r["label_b"]], values=vals, name=title,
            hole=0.55,
            marker=dict(colors=[_CA, _CB], line=dict(color=_BG, width=3)),
            textfont=dict(color=_FT, size=12, family="DM Sans"),
            hovertemplate="%{label}: %{value:.3f} (%{percent})<extra></extra>",
        ), row=1, col=ci)
    fig.update_layout(
        **_DARK,
        title=dict(text="Proportional Share — Mean & Variability",
                   font=dict(color=_FT, size=14, family="Bebas Neue"), x=0.01),
        legend=dict(bgcolor="rgba(0,0,0,0.4)", font=dict(color=_FT)),
        margin=dict(l=10, r=10, t=60, b=10), height=360,
    )
    fig.update_annotations(font=dict(color=_FT, family="Bebas Neue", size=12))
    return fig


def chart_seasonal_pie(r):
    def season_means(mo):
        mo = list(mo) + [mo[-1]] * (12 - len(mo))  # pad to 12
        djf = float(np.mean([mo[11], mo[0], mo[1]]))
        mam = float(np.mean([mo[2],  mo[3], mo[4]]))
        jja = float(np.mean([mo[5],  mo[6], mo[7]]))
        son = float(np.mean([mo[8],  mo[9], mo[10]]))
        raw = [djf, mam, jja, son]
        mn  = min(raw)
        shifted = [max(v - mn + 0.01, 0.01) for v in raw]
        return shifted, raw

    sa, ra = season_means(r["a"]["monthly_vals"])
    sb, rb = season_means(r["b"]["monthly_vals"])
    season_labels = ["DJF (Winter)", "MAM (Spring)", "JJA (Summer)", "SON (Autumn)"]
    season_cols   = ["#60a5fa", "#34d399", "#f59e0b", "#f87171"]

    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "domain"}, {"type": "domain"}]],
        subplot_titles=[f"Seasonal — {r['label_a']}", f"Seasonal — {r['label_b']}"],
    )
    for ci, (sv, rv) in enumerate([(sa, ra), (sb, rb)], 1):
        fig.add_trace(go.Pie(
            labels=season_labels, values=sv,
            hole=0.50,
            marker=dict(colors=season_cols, line=dict(color=_BG, width=3)),
            textfont=dict(color=_FT, size=11, family="DM Sans"),
            customdata=rv,
            hovertemplate="%{label}<br>Mean: %{customdata:.2f}<extra></extra>",
        ), row=1, col=ci)
    fig.update_layout(
        **_DARK,
        title=dict(text="Seasonal Contribution — DJF / MAM / JJA / SON",
                   font=dict(color=_FT, size=14, family="Bebas Neue"), x=0.01),
        legend=dict(bgcolor="rgba(0,0,0,0.4)", font=dict(color=_FT)),
        margin=dict(l=10, r=10, t=60, b=10), height=380,
    )
    fig.update_annotations(font=dict(color=_FT, family="Bebas Neue", size=12))
    return fig


def chart_zonal(r):
    lats_a = np.array(r["a"]["lats"])
    lats_b = np.array(r["b"]["lats"])
    zm_a   = np.array(r["a"]["zonal_mean"])
    zm_b   = np.array(r["b"]["zonal_mean"])
    zm_b_i = np.interp(lats_a, lats_b, zm_b)
    diff   = zm_a - zm_b_i

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=zm_a, y=lats_a, name=r["label_a"], mode="lines",
        line=dict(color=_CA, width=2.5), fill="tozerox",
        fillcolor="rgba(0,229,255,0.07)",
        hovertemplate=f"{r['label_a']} Lat:%{{y:.1f}}°: %{{x:.2f}} {r['units']}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=zm_b, y=lats_b, name=r["label_b"], mode="lines",
        line=dict(color=_CB, width=2.5), fill="tozerox",
        fillcolor="rgba(255,107,53,0.07)",
        hovertemplate=f"{r['label_b']} Lat:%{{y:.1f}}°: %{{x:.2f}} {r['units']}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=diff, y=lats_a, name="A − B", mode="lines",
        line=dict(color="#a78bfa", width=1.5, dash="dot"),
        hovertemplate="Diff Lat:%{y:.1f}°: %{x:.2f}<extra></extra>",
    ))
    fig.add_vline(x=0, line_color=_GR, line_width=1)
    fig.update_layout(
        **_DARK,
        title=dict(text="Zonal Mean Profile — Latitude vs Value",
                   font=dict(color=_FT, size=14, family="Bebas Neue"), x=0.01),
        xaxis=_ax(title=r["units"]), yaxis=_ax(title="Latitude (°)"),
        legend=dict(bgcolor="rgba(0,0,0,0.4)", font=dict(color=_FT)),
        margin=_MN, height=380,
    )
    return fig


def chart_box(r):
    fig = go.Figure()
    for key, col, lbl in [("a", _CA, r["label_a"]), ("b", _CB, r["label_b"])]:
        vals = r[key]["flat"][:5000]
        r_int = int(col[1:3], 16)
        g_int = int(col[3:5], 16)
        b_int = int(col[5:7], 16)
        fig.add_trace(go.Box(
            y=vals, name=lbl, marker_color=col, line_color=col,
            fillcolor=f"rgba({r_int},{g_int},{b_int},0.18)",
            boxmean="sd",
            hovertemplate=f"{lbl}: %{{y:.2f}} {r['units']}<extra></extra>",
        ))
    fig.update_layout(
        **_DARK,
        title=dict(text="Statistical Spread — Box & Whisker",
                   font=dict(color=_FT, size=14, family="Bebas Neue"), x=0.01),
        yaxis=_ax(title=r["units"]),
        legend=dict(bgcolor="rgba(0,0,0,0.4)", font=dict(color=_FT)),
        margin=_MN, height=360,
    )
    return fig


def chart_radar(r):
    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec","Jan"]
    ma = r["a"]["monthly_vals"] + [r["a"]["monthly_vals"][0]]
    mb = r["b"]["monthly_vals"] + [r["b"]["monthly_vals"][0]]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=ma, theta=months, name=r["label_a"],
        fill="toself", line=dict(color=_CA, width=2),
        fillcolor="rgba(0,229,255,0.12)",
        hovertemplate=f"{r['label_a']} %{{theta}}: %{{r:.2f}} {r['units']}<extra></extra>",
    ))
    fig.add_trace(go.Scatterpolar(
        r=mb, theta=months, name=r["label_b"],
        fill="toself", line=dict(color=_CB, width=2),
        fillcolor="rgba(255,107,53,0.12)",
        hovertemplate=f"{r['label_b']} %{{theta}}: %{{r:.2f}} {r['units']}<extra></extra>",
    ))
    fig.update_layout(
        **_DARK,
        polar=dict(
            bgcolor=_BG3,
            radialaxis=dict(color=_FT, gridcolor=_GR, linecolor=_GR),
            angularaxis=dict(color=_FT, gridcolor=_GR),
        ),
        title=dict(text="Seasonal Fingerprint — Polar Radar",
                   font=dict(color=_FT, size=14, family="Bebas Neue"), x=0.01),
        legend=dict(bgcolor="rgba(0,0,0,0.4)", font=dict(color=_FT)),
        margin=dict(l=40, r=40, t=60, b=40), height=420,
    )
    return fig


def chart_cdf(r):
    fig = go.Figure()
    for key, col, lbl in [("a", _CA, r["label_a"]), ("b", _CB, r["label_b"])]:
        vals = np.sort(r[key]["flat"])
        cdf  = np.linspace(0, 1, len(vals))
        idx  = np.linspace(0, len(vals) - 1, min(500, len(vals)), dtype=int)
        fig.add_trace(go.Scatter(
            x=vals[idx], y=cdf[idx], name=lbl, mode="lines",
            line=dict(color=col, width=2.5),
            hovertemplate=f"{lbl}: %{{x:.2f}} {r['units']} → P=%{{y:.3f}}<extra></extra>",
        ))
    fig.update_layout(
        **_DARK,
        title=dict(text="Cumulative Distribution Function (CDF)",
                   font=dict(color=_FT, size=14, family="Bebas Neue"), x=0.01),
        xaxis=_ax(title=r["units"]), yaxis=_ax(title="Cumulative Probability", range=[0, 1]),
        legend=dict(bgcolor="rgba(0,0,0,0.4)", font=dict(color=_FT)),
        margin=_MN, height=340,
    )
    return fig


def chart_stats_donut(r):
    wins_a, wins_b = 0, 0
    details = []

    if r["a"]["mean"] > r["b"]["mean"]:
        wins_a += 1
        details.append(f"{r['label_a']} warmer by {abs(r['delta_mean']):.2f} {r['units']}")
    else:
        wins_b += 1
        details.append(f"{r['label_b']} warmer by {abs(r['delta_mean']):.2f} {r['units']}")

    if r["a"]["std"] < r["b"]["std"]:
        wins_a += 1
        details.append(f"{r['label_a']} more stable (lower σ)")
    else:
        wins_b += 1
        details.append(f"{r['label_b']} more stable (lower σ)")

    if r["a"]["trend"] > r["b"]["trend"]:
        wins_a += 1
        details.append(f"{r['label_a']} warms faster ({r['a']['trend']:+.3f}/decade)")
    else:
        wins_b += 1
        details.append(f"{r['label_b']} warms faster ({r['b']['trend']:+.3f}/decade)")

    range_a = r["a"]["maximum"] - r["a"]["minimum"]
    range_b = r["b"]["maximum"] - r["b"]["minimum"]
    if range_a > range_b:
        wins_a += 1
        details.append(f"{r['label_a']} has larger value range")
    else:
        wins_b += 1
        details.append(f"{r['label_b']} has larger value range")

    fig = go.Figure(go.Pie(
        labels=[f"{r['label_a']} wins", f"{r['label_b']} wins"],
        values=[wins_a, wins_b],
        hole=0.6,
        marker=dict(colors=[_CA, _CB], line=dict(color=_BG, width=4)),
        textfont=dict(color=_FT, size=13, family="DM Sans"),
        hovertemplate="%{label}: %{value} metrics<extra></extra>",
    ))
    fig.add_annotation(
        text=f"{wins_a}–{wins_b}",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=22, color=_FT, family="Bebas Neue"),
    )
    fig.update_layout(
        **_DARK,
        title=dict(text="Overall Scorecard — Which Dataset Leads?",
                   font=dict(color=_FT, size=14, family="Bebas Neue"), x=0.01),
        legend=dict(bgcolor="rgba(0,0,0,0.4)", font=dict(color=_FT)),
        margin=_MN, height=340,
    )
    return fig, wins_a, wins_b, details


def generate_insights(r) -> list:
    a, b   = r["a"], r["b"]
    la, lb = r["label_a"], r["label_b"]
    u      = r["units"]
    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

    dm     = abs(r["delta_mean"])
    warmer = la if r["delta_mean"] > 0 else lb
    pos_neg = "pos" if r["delta_mean"] > 0 else "neg"

    ta, tb = a["trend"], b["trend"]
    sa, sb = a["std"],   b["std"]
    more_var = la if sa > sb else lb

    peak_a   = months[int(np.argmax(a["monthly_vals"]))]
    peak_b   = months[int(np.argmax(b["monthly_vals"]))]
    trough_a = months[int(np.argmin(a["monthly_vals"]))]
    trough_b = months[int(np.argmin(b["monthly_vals"]))]

    return [
        dict(icon="🌡️", title="MEAN VALUE DIFFERENCE",
             body=(f"<span class='insight-val-a'>{la}</span> averages <b>{a['mean']:.2f} {u}</b> vs "
                   f"<span class='insight-val-b'>{lb}</span>'s <b>{b['mean']:.2f} {u}</b>. "
                   f"<span class='insight-val-{pos_neg}'>{warmer} is warmer by {dm:.2f} {u}</span>.")),
        dict(icon="📈", title="LONG-TERM WARMING TREND",
             body=(f"<span class='insight-val-a'>{la}</span>: <b>{ta:+.3f} {u}/decade</b>. "
                   f"<span class='insight-val-b'>{lb}</span>: <b>{tb:+.3f} {u}/decade</b>. "
                   f"{'Both show warming.' if ta > 0 and tb > 0 else 'Trends diverge between periods.'}")),
        dict(icon="📊", title="CLIMATE VARIABILITY",
             body=(f"<span class='insight-val-a'>{la}</span> σ=<b>{sa:.3f}</b>, "
                   f"<span class='insight-val-b'>{lb}</span> σ=<b>{sb:.3f}</b>. "
                   f"<span class='insight-val-neg'>{more_var}</span> shows {abs(sa-sb):.3f} {u} more variability.")),
        dict(icon="⚡", title="EXTREME VALUES",
             body=(f"<span class='insight-val-a'>{la}</span>: <b>{a['minimum']:.1f}</b> to <b>{a['maximum']:.1f} {u}</b>. "
                   f"<span class='insight-val-b'>{lb}</span>: <b>{b['minimum']:.1f}</b> to <b>{b['maximum']:.1f} {u}</b>. "
                   f"Peak difference: <b>{abs(a['maximum']-b['maximum']):.2f} {u}</b>.")),
        dict(icon="🌸", title="SEASONAL PEAKS",
             body=(f"<span class='insight-val-a'>{la}</span> peaks in <b>{peak_a}</b>, troughs in <b>{trough_a}</b>. "
                   f"<span class='insight-val-b'>{lb}</span> peaks in <b>{peak_b}</b>, troughs in <b>{trough_b}</b>. "
                   f"{'Seasonal timing aligned.' if peak_a == peak_b else f'Peaks offset by {abs(months.index(peak_a)-months.index(peak_b))} months.'}")),
        dict(icon="📐", title="DISTRIBUTION SHAPE",
             body=(f"<span class='insight-val-a'>{la}</span>: skew=<b>{a['skew']:.2f}</b>, kurtosis=<b>{a['kurtosis']:.2f}</b>. "
                   f"<span class='insight-val-b'>{lb}</span>: skew=<b>{b['skew']:.2f}</b>, kurtosis=<b>{b['kurtosis']:.2f}</b>.")),
    ]


# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style='font-family:"Bebas Neue",sans-serif; font-size:1.6rem;
                letter-spacing:2px; color:#00e5ff; margin-bottom:0.2rem;'>
    CLIMADUEL
    </div>
    <div style='font-size:0.75rem; color:#5a6a8a; margin-bottom:1rem;'>
    Dataset Comparison Engine
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    variable = select(
        label="🌡️ Climate Variable",
        options=["Temperature", "Precipitation", "Wind Speed"],
        key="climate_variable_select",
    )

    # ── DATASET A ──
    st.markdown("---")
    st.markdown("""
    <div style='border-left:3px solid #00e5ff; padding:0.4rem 0.8rem;
                background:rgba(0,229,255,0.06); border-radius:0 8px 8px 0; margin-bottom:0.5rem;'>
      <span style='font-family:"Bebas Neue",sans-serif; font-size:1.1rem;
                   letter-spacing:2px; color:#00e5ff;'>🔵 DATASET A</span>
    </div>
    """, unsafe_allow_html=True)
    ds_a    = None
    label_a = "Dataset A"

    up_a = st.file_uploader("Upload Dataset A (.nc)", type=["nc"], key="up_a")
    if up_a:
        ds_a    = load_nc(up_a.read(), up_a.name)
        nvars   = list(ds_a.data_vars)
        var_a   = select(
            label="Variable A",
            options=nvars,
            key="va",
        )
        ds_a    = ds_a.rename({var_a: "value"}) if var_a != "value" else ds_a
        label_a = input(
            default_value=up_a.name,
            type="text",
            placeholder="Label A",
            key="la",
        )
    else:
        yr_a_s = input(
            default_value="2000",
            type="text",
            placeholder="Year A",
            key="yas",
        )
        try:
            yr_a_int = int(yr_a_s)
        except ValueError:
            st.error("Enter a valid year e.g. 2000")
            st.stop()
        label_a = input(
            default_value=f"Year {yr_a_int}",
            type="text",
            placeholder="Label A",
            key="la",
        )
        ds_a = generate_dataset(variable, yr_a_int, 1)
    # ── DATASET B ──
    st.markdown("---")
    st.markdown("""
    <div style='border-left:3px solid #ff6b35; padding:0.4rem 0.8rem;
                background:rgba(255,107,53,0.06); border-radius:0 8px 8px 0; margin-bottom:0.5rem;'>
      <span style='font-family:"Bebas Neue",sans-serif; font-size:1.1rem;
                   letter-spacing:2px; color:#ff6b35;'>🟡 DATASET B</span>
    </div>
    """, unsafe_allow_html=True)
    ds_b    = None
    label_b = "Dataset B"

    up_b = st.file_uploader("Upload Dataset B (.nc)", type=["nc"], key="up_b")
    if up_b:
        ds_b    = load_nc(up_b.read(), up_b.name)
        nvars   = list(ds_b.data_vars)
        var_b   = select(
            label="Variable B",
            options=nvars,
            key="vb",
        )
        ds_b    = ds_b.rename({var_b: "value"}) if var_b != "value" else ds_b
        label_b = input(
            default_value=up_b.name,
            type="text",
            placeholder="Label B",
            key="lb",
        )
    else:
        yr_b_s = input(
            default_value="2020",
            type="text",
            placeholder="Year B",
            key="ybs",
        )
        try:
            yr_b_int = int(yr_b_s)
        except ValueError:
            st.error("Enter a valid year e.g. 2020")
            st.stop()
        label_b = input(
            default_value=f"Year {yr_b_int}",
            type="text",
            placeholder="Label B",
            key="lb",
        )
        ds_b = generate_dataset(variable, yr_b_int, 1) 

    st.markdown("---")
    run = ui.button(
        text="⚡ RUN COMPARISON",
        key="run_comparison_button",
    )


# ══════════════════════════════════════════════════════════════
# MAIN PAGE
# ══════════════════════════════════════════════════════════════
st.markdown("""
<div class='page-hero'>
  <p class='page-title'>CLIMADUEL</p>
  <p class='page-sub'>Full-spectrum comparison · spatial · temporal · statistical · seasonal</p>
</div>
""", unsafe_allow_html=True)

if not run:
    st.markdown("""
    <div style='text-align:center; padding:4rem 2rem; color:#5a6a8a; font-family:"DM Sans",sans-serif;'>
      <div style='font-size:4rem; margin-bottom:1rem;'>🔬</div>
      <div style='font-size:1.2rem; margin-bottom:0.5rem; color:#c8d4f0;'>
        Configure your two datasets in the sidebar
      </div>
      <div style='font-size:0.9rem;'>
        Choose variable · Set years · Hit RUN COMPARISON
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── COMPUTE ──
with st.spinner("🔬 Running full comparison analysis..."):
    r = compute_full_comparison(ds_a, ds_b, label_a, label_b)

# ── BADGES ──
st.markdown(f"""
<div style='margin-bottom:1rem;'>
  <span class='badge badge-a'>🔵 {label_a}</span>
  <span style='color:#5a6a8a; font-family:"DM Sans"; font-size:1rem;'>vs</span>
  <span class='badge badge-b'>🟡 {label_b}</span>
  <span style='color:#5a6a8a; font-family:"DM Sans"; font-size:0.85rem; margin-left:0.8rem;'>
    {r["long_name"]} · {r["a"]["n_years"]} yr vs {r["b"]["n_years"]} yr
  </span>
</div>
""", unsafe_allow_html=True)

# ── METRIC CARDS ──
metric_cols = st.columns(4)
for col, (lbl, va, vb, unit) in zip(metric_cols, [
    ("Global Mean",   f"{r['a']['mean']:.2f}",   f"{r['b']['mean']:.2f}",   r["units"]),
    ("Std Deviation", f"{r['a']['std']:.3f}",    f"{r['b']['std']:.3f}",    r["units"]),
    ("Max Value",     f"{r['a']['maximum']:.2f}", f"{r['b']['maximum']:.2f}", r["units"]),
    ("Trend",         f"{r['a']['trend']:+.3f}",  f"{r['b']['trend']:+.3f}",  f"{r['units']}/decade"),
]):
    col.markdown(f"""
    <div class='ds-card ds-card-a'>
      <p class='ds-label ds-label-a'>🔵 {lbl} — A</p>
      <p class='ds-value'>{va}</p><p class='ds-sub'>{unit}</p>
    </div>
    <div class='ds-card ds-card-b'>
      <p class='ds-label ds-label-b'>🟡 {lbl} — B</p>
      <p class='ds-value'>{vb}</p><p class='ds-sub'>{unit}</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ── SECTION 1: TEMPORAL ──
st.markdown("<div class='sec-head'>📈 TEMPORAL ANALYSIS</div>", unsafe_allow_html=True)
st.plotly_chart(chart_annual_trend(r), use_container_width=True)
c1, c2 = st.columns(2)
with c1:
    st.plotly_chart(chart_seasonal(r), use_container_width=True)
with c2:
    st.plotly_chart(chart_radar(r), use_container_width=True)

# ── SECTION 2: SPATIAL & DISTRIBUTION ──
st.markdown("<div class='sec-head'>🌐 SPATIAL & DISTRIBUTION</div>", unsafe_allow_html=True)
c3, c4 = st.columns(2)
with c3:
    st.plotly_chart(chart_zonal(r), use_container_width=True)
with c4:
    st.plotly_chart(chart_box(r), use_container_width=True)
c5, c6 = st.columns(2)
with c5:
    st.plotly_chart(chart_histogram(r), use_container_width=True)
with c6:
    st.plotly_chart(chart_cdf(r), use_container_width=True)

# ── SECTION 3: PIE CHARTS ──
st.markdown("<div class='sec-head'>🥧 PROPORTIONAL INSIGHTS</div>", unsafe_allow_html=True)
c7, c8 = st.columns(2)
with c7:
    st.plotly_chart(chart_stats_pie(r), use_container_width=True)
with c8:
    st.plotly_chart(chart_seasonal_pie(r), use_container_width=True)

fig_score, wins_a, wins_b, score_details = chart_stats_donut(r)
cs1, cs2 = st.columns([1, 1.4])
with cs1:
    st.plotly_chart(fig_score, use_container_width=True)
with cs2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-family:"Bebas Neue",sans-serif; font-size:1.1rem;
                letter-spacing:1.5px; color:#c8d4f0; margin-bottom:0.8rem;'>
    METRIC BREAKDOWN
    </div>""", unsafe_allow_html=True)
    for icon, detail in zip(["🌡️", "📉", "🚀", "↔️"], score_details):
        st.markdown(f"""
        <div style='background:#141b2d; border:1px solid #1e2d4a; border-radius:10px;
                    padding:0.7rem 1rem; margin-bottom:0.5rem;
                    font-family:"DM Sans"; font-size:0.88rem; color:#c8d4f0;'>
          {icon} {detail}
        </div>""", unsafe_allow_html=True)

# ── SECTION 4: INSIGHTS ──
st.markdown("<div class='sec-head'>🧠 DATA INSIGHTS</div>", unsafe_allow_html=True)
insights = generate_insights(r)
for i in range(0, len(insights), 2):
    ci1, ci2 = st.columns(2)
    for col, idx in [(ci1, i), (ci2, i + 1)]:
        if idx < len(insights):
            ins = insights[idx]
            col.markdown(f"""
            <div class='insight-card'>
              <div class='insight-icon'>{ins['icon']}</div>
              <p class='insight-title'>{ins['title']}</p>
              <p class='insight-body'>{ins['body']}</p>
            </div>""", unsafe_allow_html=True)

# ── SECTION 5: VERDICT ──
winner = label_a if wins_a >= wins_b else label_b
dm     = abs(r["delta_mean"])
dt     = abs(r["delta_trend"])
w_col  = "#00e5ff" if winner == label_a else "#ff6b35"

st.markdown(f"""
<div class='verdict'>
  <p class='verdict-title'>⚖️ FINAL VERDICT</p>
  <p class='verdict-body'>
    Across <b>4 key metrics</b>, <b style='color:{w_col};'>{winner}</b>
    leads with <b>{max(wins_a, wins_b)}</b> wins vs {min(wins_a, wins_b)}.
    <br><br>
    The two datasets differ by <b>{dm:.2f} {r["units"]}</b> in global mean —
    {"a climatologically significant gap" if dm > 1 else "a small but measurable difference"}.
    Warming trends diverge by <b>{dt:.3f} {r["units"]}/decade</b>, suggesting
    {"a notable shift in climate trajectory" if dt > 0.05 else "broadly similar long-term trends"}.
    <br><br>
    {label_a} spans <b>{r["a"]["year_start"]}–{r["a"]["year_end"]}</b> ({r["a"]["n_years"]} yr) ·
    {label_b} spans <b>{r["b"]["year_start"]}–{r["b"]["year_end"]}</b> ({r["b"]["n_years"]} yr).
    {"The later period shows measurable warming relative to the earlier baseline."
     if r["b"]["year_start"] > r["a"]["year_start"]
     else "Dataset A represents the more recent climate period."}
  </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style='text-align:center; color:#2a3a5a; font-family:"DM Sans"; font-size:0.75rem; margin-top:2rem; padding:1rem;'>
  ClimaDuel · PyClimaExplorer · Technex '26, IIT (BHU)
</div>
""", unsafe_allow_html=True)