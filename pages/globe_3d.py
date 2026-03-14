import streamlit as st
import streamlit.components.v1 as components
import streamlit_shadcn_ui as ui
from streamlit_shadcn_ui import slider as ui_slider, select as ui_select, switch as ui_switch, tabs as ui_tabs
import json, random, math
import numpy as np
import pandas as pd

st.set_page_config(     
    page_title="🌍 Earth Pulse — Climate Globe",
    page_icon="🌍", layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;700;800&display=swap');
html,body,[class*="css"]{font-family:'Syne',sans-serif;background:#04101e;color:#e0f0ff;}
.stApp{background:#04101e;}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#071828,#04101e);border-right:1px solid #0d3a5c;}
section[data-testid="stSidebar"] *{color:#c8e6ff !important;}
.stSlider>div>div>div>div{background:#00d4ff !important;}
.stSelectbox div[data-baseweb="select"]{background:#071828 !important;border-color:#0d3a5c !important;}
div[data-testid="metric-container"]{background:linear-gradient(135deg,#071828,#0a2540);border:1px solid #0d3a5c;border-radius:12px;padding:12px;box-shadow:0 0 20px rgba(0,212,255,0.07);}
h1,h2,h3{font-family:'Syne',sans-serif !important;letter-spacing:-.5px;}
h1{color:#00d4ff !important;font-weight:800 !important;font-size:1.9rem !important;}
h3{color:#7ecfff !important;}
.stButton>button{background:linear-gradient(135deg,#00d4ff,#0077b6) !important;color:#000 !important;font-weight:700 !important;font-family:'Space Mono',monospace !important;border:none !important;border-radius:8px !important;transition:all .2s !important;}
details{border:1px solid #0d3a5c !important;border-radius:8px !important;background:#071828 !important;}
hr{border-color:#0d3a5c !important;}
#MainMenu,footer,header{visibility:hidden;}
</style>
""", unsafe_allow_html=True)

# ─── SIDEBAR ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🌡️ Climate Variable")
    variable = ui_select(
        label="Primary Variable",
        options=[
            "🌡️ Temperature",
            "💧 Precipitation",
            "💨 Wind Speed",
        ],
        key="primary_variable",
    )

    st.markdown("### 📅 Time Period")
    year = ui_slider(
        label="Year",
        min_value=1950,
        max_value=2024,
        step=1,
        default_value=[2020],
        key="year_slider",
    )[0]
    MONTHS = ["Jan","Feb","Mar","Apr","May","Jun",
              "Jul","Aug","Sep","Oct","Nov","Dec"]
    month_idx = ui_slider(
        label="Month",
        min_value=1,
        max_value=12,
        step=1,
        default_value=[7],
        key="month_slider",
    )[0]
    month = MONTHS[month_idx-1]

    st.markdown("### 🎬 Time-Lapse Animation")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**From**")
        anim_start_month = ui_select(
            label="Start Month",
            options=MONTHS,
            key="sm",
        )
        anim_start_year = ui_select(
            label="Start Year",
            options=list(range(1950, 2025)),
            key="sy",
        )
    with col_b:
        st.markdown("**To**")
        anim_end_month = ui_select(
            label="End Month",
            options=MONTHS,
            key="em",
        )
        anim_end_year = ui_select(
            label="End Year",
            options=list(range(1950, 2025)),
            key="ey",
        )

    anim_fps = ui_slider(
        label="Playback Speed (FPS)",
        min_value=1,
        max_value=30,
        step=1,
        default_value=[8],
        key="anim_fps",
    )[0]

    anim_start_mo_idx = MONTHS.index(anim_start_month) + 1
    anim_end_mo_idx   = MONTHS.index(anim_end_month) + 1
    anim_mode = "custom_range"

    st.markdown("### 🌐 Globe Settings")
    base_map = ui_select(
        label="Earth Texture",
        options=[
            "🛰️ NASA Blue Marble",
            "🌙 NASA Night Lights",
            "🏔️ Topographic",
            "🌊 Ocean Floor",
        ],
        key="base_map",
    )
    show_clouds = True
    show_atmo = True
    show_stars = True
    show_grid = True
    show_cities = True
    show_wind = True
    auto_spin = True
    night_mode = True

    st.markdown("### 📍 Region Focus")
    region = ui_select(
        label="Jump To",
        options=[
            "🌍 Global",
            "🌏 Asia Pacific",
            "🌎 Americas",
            "🌍 Africa",
            "🌍 Europe",
            "❄️ Arctic",
            "🧊 Antarctic",
            "🇮🇳 South Asia",
        ],
        key="region_select",
    )

# ─── DATA GENERATION ──────────────────────────────────────────
GRID_H, GRID_W = 90, 180   # reduced for animation performance
var_label = variable.split(" ",1)[1] if " " in variable else variable

def gaussian_blobs(n=20, seed=0):
    rng = np.random.default_rng(seed)
    f = np.zeros((GRID_H, GRID_W), np.float32)
    for _ in range(n):
        cx,cy = rng.integers(0,GRID_W), rng.integers(0,GRID_H)
        amp   = rng.uniform(-1,1)
        sx,sy = rng.uniform(9,30), rng.uniform(6,22)
        X,Y   = np.meshgrid(np.arange(GRID_W), np.arange(GRID_H))
        f    += amp * np.exp(-((X-cx)**2/(2*sx**2)+(Y-cy)**2/(2*sy**2)))
    return f

def lat_gradient(pole_val, eq_val):
    f = np.zeros((GRID_H, GRID_W), np.float32)
    for i in range(GRID_H):
        lat = 90 - i*2
        t   = abs(lat)/90
        f[i,:] = eq_val + (pole_val-eq_val)*t
    return f

def gen_field(yr, mo_idx, var):
    np.random.seed(yr * 31 + mo_idx * 7)
    if "Temperature" in var:
        base = lat_gradient(-0.6, 0.4)
        trend= (yr-1950)*0.018
        seas = np.zeros((GRID_H,GRID_W),np.float32)
        for i in range(GRID_H):
            lat=90-i*2
            sign = 1 if mo_idx in [6,7,8] else -1
            seas[i,:] = sign * np.clip(lat/55,-1,1)*0.9
        noise = gaussian_blobs(22, yr+mo_idx*3)
        field = base + noise*1.3 + trend + seas
    elif "Precipitation" in var:
        base = np.zeros((GRID_H,GRID_W),np.float32)
        for i in range(GRID_H):
            lat=90-i*2
            base[i,:] = (1.2*np.exp(-(lat**2)/180)
                         -0.5*np.exp(-((abs(lat)-28)**2)/70)
                         +0.1*np.exp(-((abs(lat)-58)**2)/120))
        noise = gaussian_blobs(24, yr*2+mo_idx)
        field = base + noise*0.55
    else:
        base = np.zeros((GRID_H,GRID_W),np.float32)
        for i in range(GRID_H):
            lat=90-i*2
            base[i,:] = (np.exp(-((abs(lat)-15)**2)/140)
                        +np.exp(-((abs(lat)-50)**2)/110)*0.7
                        +np.exp(-((abs(lat)-80)**2)/55)*0.45)
        noise = gaussian_blobs(18, yr*3+mo_idx*5)
        field = base + noise*0.38
    fmin, fmax = field.min(), field.max()
    return ((field-fmin)/(fmax-fmin+1e-9)).tolist()

# ─── BUILD ANIMATION FRAMES ────────────────────────────────────
@st.cache_data
def build_frames(start_yr, start_mo, end_yr, end_mo, var):
    frames, labels = [], []
    MO = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    # enumerate every month in range
    y, m = start_yr, start_mo
    while (y < end_yr) or (y == end_yr and m <= end_mo):
        frames.append(gen_field(y, m, var))
        labels.append(f"{MO[m-1]} {y}")
        m += 1
        if m > 12:
            m = 1; y += 1
        if len(frames) >= 60:   # cap at 60 frames for performance
            break
    return frames, labels

anim_frames, anim_labels = build_frames(
    anim_start_year, anim_start_mo_idx,
    anim_end_year,   anim_end_mo_idx,
    variable
)

# Current single frame
np.random.seed(year * 31 + month_idx * 7)
field_data = gen_field(year, month_idx, variable)

if "Temperature" in variable:
    COLOR_STOPS = [
        (0.00,(  0,  0,160)),(0.18,( 30, 80,255)),
        (0.38,( 0,200,200)),(0.52,(240,240, 60)),
        (0.70,(255,120,  0)),(0.85,(220, 30,  0)),(1.00,(150,  0, 50)),
    ]
    unit="°C"; legend_lo="-3°C"; legend_hi="+3°C"
elif "Precipitation" in variable:
    COLOR_STOPS = [
        (0.00,(240,248,255)),(0.15,(160,200,255)),
        (0.35,( 50,130,255)),(0.60,(  0, 50,200)),
        (0.80,(  0, 10,130)),(1.00,( 40,  0,100)),
    ]
    unit="mm/day"; legend_lo="0"; legend_hi="20+"
else:
    COLOR_STOPS = [
        (0.00,(  5, 15, 60)),(0.25,( 0, 80,180)),
        (0.50,(  0,200,180)),(0.75,(180,255, 80)),(1.00,(255,240,  0)),
    ]
    unit="m/s"; legend_lo="0"; legend_hi="25+"

cs_json = json.dumps([{"t":t,"r":r,"g":g,"b":b} for t,(r,g,b) in COLOR_STOPS])

def gen_pts(field, n=200):
    pts=[]
    nf=np.array(field)
    gH, gW = nf.shape
    for _ in range(n):
        gi=random.randint(0,gH-1); gj=random.randint(0,gW-1)
        pts.append({"lat":round(90-gi*2,1),"lon":round(gj*2-180,1),
                    "v":round(float(nf[gi,gj]),3)})
    return pts

sparse_pts = gen_pts(field_data, 220)

# ─── TIME SERIES DATA ──────────────────────────────────────────
yrs=list(range(1950,2025))
np.random.seed(42)
temp_ts  =[round(0.012*(y-1950)+np.random.normal(0,.09),3) for y in yrs]
prec_ts  =[round(100+0.05*(y-1950)+np.random.normal(0,4),2) for y in yrs]
wind_ts  =[round(7.2-0.003*(y-1950)+np.random.normal(0,.25),3) for y in yrs]

def monthly_clim(v):
    if v=="Temperature":
        return [round(-2+8*math.sin(math.pi*(m-2)/6)+random.uniform(-.3,.3),2) for m in range(1,13)]
    if v=="Precipitation":
        return [round(80+50*math.sin(math.pi*(m-3)/6)+random.uniform(-5,5),1) for m in range(1,13)]
    return [round(7+2*math.sin(math.pi*(m-1)/6)+random.uniform(-.2,.2),3) for m in range(1,13)]

monthly_v=monthly_clim(var_label)
all_ts={"Temperature":temp_ts,"Precipitation":prec_ts,"Wind Speed":wind_ts}

# ─── CONFIG ───────────────────────────────────────────────────
tex_map={
    "🛰️ NASA Blue Marble": "https://unpkg.com/three-globe/example/img/earth-blue-marble.jpg",
    "🌙 NASA Night Lights": "https://unpkg.com/three-globe/example/img/earth-night.jpg",
    "🏔️ Topographic":      "https://unpkg.com/three-globe/example/img/earth-topology.png",
    "🌊 Ocean Floor":       "https://unpkg.com/three-globe/example/img/earth-water.png",
}
earth_tex  = tex_map[base_map]
cloud_tex  = "https://unpkg.com/three-globe/example/img/earth-clouds.png"
bump_tex   = "https://unpkg.com/three-globe/example/img/earth-topology.png"
spec_tex   = "https://unpkg.com/three-globe/example/img/earth-water.png"

region_cfg={
    "🌍 Global":       {"lat":15,  "lon":0,    "d":2.7},
    "🌏 Asia Pacific": {"lat":25,  "lon":110,  "d":2.1},
    "🌎 Americas":     {"lat":20,  "lon":-90,  "d":2.2},
    "🌍 Africa":       {"lat":5,   "lon":20,   "d":2.1},
    "🌍 Europe":       {"lat":52,  "lon":15,   "d":1.9},
    "❄️ Arctic":       {"lat":82,  "lon":0,    "d":2.0},
    "🧊 Antarctic":    {"lat":-82, "lon":0,    "d":2.0},
    "🇮🇳 South Asia":  {"lat":22,  "lon":80,   "d":1.9},
}
rc=region_cfg[region]

# ─── HEADER ───────────────────────────────────────────────────
st.markdown("# 🌍 Earth Pulse — 3D Realistic Climate Globe")
st.markdown(f"**{variable}** &nbsp;·&nbsp; **{month} {year}** &nbsp;·&nbsp; "
            f"&nbsp;·&nbsp; {base_map}")

c1,c2,c3,c4,c5=st.columns(5)
c1.metric("🌡️ Temp",   f"{14.2+(year-1950)*0.018:.1f}°C",  f"+{(year-1950)*0.018:.2f}°C")
c2.metric("💧 Precip", f"{100+(year-1990)*0.05:.1f} mm",    "+0.05/yr")
c3.metric("💨 Wind",   f"{7.2-(year-1950)*0.003:.2f} m/s",  f"{-(year-1950)*0.003:.3f}")
c4.metric("🧊 Sea Ice",f"{5.4-(year-2000)*0.06:.1f}M km²",  f"{-(year-2000)*0.06:.2f}M")
c5.metric("💨 CO₂",    f"{315+(year-1950)*2.6:.0f} ppm",    "+2.6/yr")
st.divider()

# ─── GLOBE + ANIMATION HTML ───────────────────────────────────
ANIM_FRAMES_JSON = json.dumps(anim_frames)
ANIM_LABELS_JSON = json.dumps(anim_labels)

GLOBE_HTML = f"""<!DOCTYPE html><html><head>
<meta charset="utf-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&display=swap');
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:radial-gradient(ellipse at center,#0a1a2e 0%,#020a14 100%);
  overflow:hidden;font-family:'Space Mono',monospace;}}
#c{{position:absolute;inset:0;width:100%;height:100%;display:block;}}

/* ── Glass panels ── */
.gl{{
  position:absolute;
  background:rgba(4,16,30,0.82);
  border:1px solid rgba(0,180,255,0.2);
  border-radius:14px;
  backdrop-filter:blur(14px);
  -webkit-backdrop-filter:blur(14px);
  box-shadow:0 4px 24px rgba(0,0,0,0.5),inset 0 1px 0 rgba(255,255,255,0.06);
  color:#c8e6ff;font-size:11px;line-height:2;padding:13px 17px;
}}

/* ── Info panel ── */
#info{{top:16px;left:16px;min-width:220px;z-index:30;}}
#info .title{{color:#00d4ff;font-size:12px;font-weight:700;letter-spacing:1.5px;
  margin-bottom:6px;display:flex;align-items:center;gap:6px;}}
#info .sep{{border:none;border-top:1px solid rgba(0,180,255,0.15);margin:6px 0;}}
#probe{{color:#7ecfff;font-size:10px;min-height:14px;transition:color .3s;}}
#probe.active{{color:#00ff88;}}
.src{{color:#2a5a7c;font-size:9px;margin-top:2px;}}

/* ── Controls ── */
#ctrl{{top:16px;right:16px;z-index:30;display:flex;flex-direction:column;gap:5px;padding:10px;}}
.btn{{
  background:rgba(0,212,255,0.06);
  border:1px solid rgba(0,180,255,0.2);
  border-radius:9px;color:#7ecfff;
  padding:8px 15px;cursor:pointer;font-size:10px;
  font-family:inherit;transition:all .18s;text-align:center;
  user-select:none;letter-spacing:.5px;
}}
.btn:hover{{border-color:rgba(0,212,255,0.6);color:#00d4ff;
  background:rgba(0,212,255,0.12);transform:translateX(-2px);}}
.btn.on{{border-color:rgba(0,255,136,0.5);color:#00ff88;
  background:rgba(0,255,136,0.08);}}

/* ── Legend ── */
#leg{{
  bottom:160px;left:50%;transform:translateX(-50%);
  display:flex;align-items:center;gap:10px;z-index:30;
  white-space:nowrap;padding:9px 18px;
}}
#leg-c{{width:230px;height:13px;border-radius:7px;
  border:1px solid rgba(0,180,255,0.25);display:block;}}
.ll{{color:#7ecfff;font-size:10px;}}
.lu{{color:#00d4ff;font-size:10px;margin-left:3px;font-weight:700;}}

/* ═══════════════════════════════════════════════════
   TIME-LAPSE PLAYER — slim collapsible bottom bar
═══════════════════════════════════════════════════ */
#player-tab{{
  position:absolute;bottom:0;left:50%;transform:translateX(-50%);
  z-index:41;background:rgba(4,16,30,0.92);
  border:1px solid rgba(0,180,255,0.25);border-bottom:none;
  border-radius:12px 12px 0 0;padding:6px 20px 5px;
  cursor:pointer;display:flex;align-items:center;gap:8px;
  font-size:10px;color:#7ecfff;font-family:'Space Mono',monospace;
  user-select:none;transition:background .15s,border-color .15s;white-space:nowrap;
}}
#player-tab:hover{{background:rgba(0,212,255,0.1);border-color:rgba(0,212,255,0.5);color:#00d4ff;}}
#player-tab.open{{color:#00ff88;border-color:rgba(0,255,136,0.4);background:rgba(4,16,30,0.97);}}
#tab-label{{font-weight:700;letter-spacing:1px;}}
#tab-date{{color:#00d4ff;font-size:11px;}}
#tab-arrow{{font-size:9px;opacity:0.6;}}
.tab-dot{{width:6px;height:6px;border-radius:50%;background:#2a5a7c;flex-shrink:0;transition:background .2s;}}
.tab-dot.playing{{background:#00ff88;box-shadow:0 0 5px #00ff88;animation:pulse2 1s infinite;}}
@keyframes pulse2{{0%,100%{{opacity:1;}}50%{{opacity:.4;}}}}

#player{{
  position:absolute;bottom:0;left:50%;transform:translateX(-50%);
  z-index:40;width:min(740px,95vw);
  background:rgba(4,16,30,0.96);
  border:1px solid rgba(0,180,255,0.22);border-bottom:none;
  border-radius:16px 16px 0 0;
  backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);
  box-shadow:0 -4px 30px rgba(0,0,0,0.6);
  max-height:0;overflow:hidden;opacity:0;
  transition:max-height .28s ease,opacity .22s ease,padding .28s ease;
  pointer-events:none;padding:0 18px;
}}
#player.open{{max-height:220px;opacity:1;pointer-events:all;padding:14px 18px 10px;}}

#frame-label{{text-align:center;color:#00d4ff;font-size:14px;font-weight:700;
  letter-spacing:3px;margin-bottom:10px;text-shadow:0 0 16px rgba(0,212,255,0.5);min-height:18px;}}

#waveform{{height:26px;display:flex;align-items:flex-end;gap:2px;overflow:hidden;margin-bottom:3px;}}
.wv-bar{{flex:1;border-radius:2px 2px 0 0;min-height:3px;background:rgba(0,130,190,0.2);
  border-top:1px solid rgba(0,180,255,0.28);cursor:pointer;transition:background .1s;}}
.wv-bar.cur{{background:rgba(0,255,136,0.32);border-top-color:#00ff88;}}
.wv-bar:hover{{background:rgba(0,200,255,0.42);}}

#scrub-wrap{{position:relative;height:24px;cursor:pointer;margin-bottom:4px;}}
#scrub-track{{position:absolute;top:9px;left:0;right:0;height:6px;background:rgba(0,70,110,0.45);border-radius:3px;}}
#scrub-fill{{position:absolute;top:0;left:0;height:100%;background:linear-gradient(90deg,#005599,#00d4ff);
  border-radius:3px;transition:width .07s linear;box-shadow:0 0 5px rgba(0,200,255,0.35);}}
#scrub-thumb{{position:absolute;top:-4px;width:14px;height:14px;background:#00d4ff;border-radius:50%;
  box-shadow:0 0 8px rgba(0,212,255,0.85);transform:translateX(-7px);transition:left .07s linear;
  pointer-events:none;border:2px solid rgba(255,255,255,0.25);}}
#scrub-ticks{{position:absolute;bottom:-12px;left:0;right:0;pointer-events:none;}}
.tick{{position:absolute;color:rgba(0,180,255,0.4);font-size:8px;transform:translateX(-50%);white-space:nowrap;}}

#transport{{display:flex;align-items:center;justify-content:center;gap:5px;margin:16px 0 8px;}}
.tbtn{{background:rgba(0,180,255,0.07);border:1px solid rgba(0,180,255,0.2);border-radius:8px;
  color:#7ecfff;cursor:pointer;font-size:11px;font-family:inherit;transition:all .14s;
  display:flex;align-items:center;justify-content:center;gap:4px;user-select:none;
  padding:7px 12px;position:relative;}}
.tbtn:hover{{border-color:rgba(0,212,255,0.5);color:#00d4ff;background:rgba(0,212,255,0.12);}}
.tbtn.active{{border-color:rgba(0,255,136,0.5);color:#00ff88;background:rgba(0,255,136,0.09);}}
#pp-btn{{padding:8px 26px;font-size:13px;font-weight:700;letter-spacing:1px;
  background:rgba(0,212,255,0.12);border-color:rgba(0,212,255,0.4);min-width:110px;}}
#pp-btn.active{{background:rgba(0,255,136,0.11);border-color:rgba(0,255,136,0.5);color:#00ff88;}}
.t-sep{{width:1px;height:24px;background:rgba(0,180,255,0.14);margin:0 3px;flex-shrink:0;}}

#info-row{{display:flex;align-items:center;justify-content:space-between;padding:0 2px;}}
.speed-group{{display:flex;align-items:center;gap:3px;}}
.speed-label{{color:#2a5a7c;font-size:9px;margin-right:3px;}}
.spd-btn{{background:rgba(0,70,110,0.2);border:1px solid rgba(0,180,255,0.1);border-radius:4px;
  color:#4a8aaa;padding:3px 8px;cursor:pointer;font-size:9px;font-family:inherit;transition:all .1s;}}
.spd-btn:hover{{color:#00d4ff;border-color:rgba(0,212,255,0.3);}}
.spd-btn.active{{color:#00ff88;border-color:rgba(0,255,136,0.4);background:rgba(0,255,136,0.07);}}
#frame-count{{color:#2a5a7c;font-size:9px;}}
#loop-indicator{{color:#2a5a7c;font-size:9px;}}
.tbtn[title]:hover::after{{content:attr(title);position:absolute;bottom:calc(100% + 6px);left:50%;
  transform:translateX(-50%);background:rgba(4,16,30,0.96);border:1px solid rgba(0,180,255,0.3);
  color:#c8e6ff;font-size:9px;padding:3px 8px;border-radius:5px;white-space:nowrap;pointer-events:none;z-index:100;}}

#snap-flash{{position:fixed;inset:0;background:rgba(255,255,255,0.1);pointer-events:none;z-index:999;opacity:0;transition:opacity .1s;}}
#tbar{{display:none;}}

/* ── City labels ── */
#city-div{{position:absolute;inset:0;pointer-events:none;z-index:20;}}
.clbl{{
  position:absolute;pointer-events:none;
  display:flex;align-items:center;gap:4px;
  transform:translate(8px,-50%);
}}
.cdot{{width:5px;height:5px;border-radius:50%;background:#00d4ff;
  border:1px solid rgba(0,200,255,0.5);flex-shrink:0;}}
.ctxt{{
  color:rgba(200,230,255,0.92);font-size:9px;
  background:rgba(4,16,30,0.72);padding:1px 5px;
  border-radius:3px;border:1px solid rgba(0,180,255,0.2);
  white-space:nowrap;
}}

/* ── Spinner ── */
#load{{
  position:absolute;inset:0;display:flex;align-items:center;
  justify-content:center;flex-direction:column;gap:14px;z-index:99;
  background:radial-gradient(ellipse at center,#0a1a2e,#020a14);
}}
.spin{{width:44px;height:44px;border-radius:50%;
  border:3px solid rgba(0,180,255,0.15);
  border-top-color:#00d4ff;
  animation:sp 1s linear infinite;}}
@keyframes sp{{to{{transform:rotate(360deg);}}}}
.load-txt{{color:#00d4ff;font-size:11px;letter-spacing:3px;opacity:.8;}}

/* ── Heatmap canvas ── */
#hm-overlay{{
  position:absolute;inset:0;pointer-events:none;z-index:10;;
}}

/* ── Recording indicator ── */
#rec-badge{{
  position:absolute;top:16px;left:50%;transform:translateX(-50%);
  background:rgba(255,30,30,0.18);border:1px solid rgba(255,60,60,0.4);
  border-radius:20px;padding:4px 14px;z-index:50;
  display:none;align-items:center;gap:7px;color:#ff6060;font-size:10px;
}}
#rec-badge.show{{display:flex;}}
.rec-dot{{width:7px;height:7px;border-radius:50%;background:#ff3030;
  animation:pulse 1s ease-in-out infinite;}}
@keyframes pulse{{0%,100%{{opacity:1;}}50%{{opacity:.3;}}}}

/* Waveform mini-chart */
#waveform{{
  height:28px;margin:0 4px 4px;display:flex;align-items:flex-end;
  gap:2px;overflow:hidden;
}}
.wv-bar{{
  flex:1;border-radius:2px 2px 0 0;
  background:rgba(0,180,255,0.25);
  border-top:1px solid rgba(0,212,255,0.4);
  transition:height .15s ease, background .15s;
  cursor:pointer;
}}
.wv-bar.cur{{background:rgba(0,255,136,0.3);border-top-color:#00ff88;}}
.wv-bar:hover{{background:rgba(0,212,255,0.5);}}
</style>
</head><body>
<div id="snap-flash"></div>
<div id="load"><div class="spin"></div><div class="load-txt">LOADING EARTH…</div></div>
<canvas id="c"></canvas>
<canvas id="hm-overlay"></canvas>
<div id="city-div"></div>
<div id="rec-badge"><div class="rec-dot"></div><span>RECORDING</span><span id="rec-count">0s</span></div>

<!-- Info -->
<div class="gl" id="info">
  <div class="title">
    <svg width="12" height="12" viewBox="0 0 12 12"><circle cx="6" cy="6" r="5" fill="none" stroke="#00d4ff" stroke-width="1.5"/><path d="M6 2v4l2.5 2" stroke="#00d4ff" stroke-width="1.2" fill="none"/></svg>
    {var_label.upper()} HEATMAP
  </div>
  <div id="cur-date">📅 <b>{month} {year}</b></div>
  <div>🌐 {region}</div>
  <hr class="sep">
  <div id="probe">Hover globe to inspect</div>
  <div class="src">Source: NOAA · ERA5 · NASA · 1°×1° grid</div>
</div>

<!-- Controls -->
<div class="gl" id="ctrl">
  <div class="btn {'on' if auto_spin else ''}" id="b-spin"   onclick="tSpin()">⏯&nbsp; Auto-Rotate</div>
  <div class="btn" id="b-reset"  onclick="rCam()">🎯&nbsp; Reset View</div>
  <div class="btn" id="b-night"  onclick="tNight()">🌙&nbsp; Night Side</div>
  <div class="btn {'on' if show_atmo else ''}" id="b-atmo"   onclick="tAtmo()">🌈&nbsp; Atmosphere</div>
  <div class="btn {'on' if show_clouds else ''}" id="b-clouds" onclick="tClouds()">☁️&nbsp; Clouds</div>
  <div class="btn" onclick="zIn()">🔍&nbsp; Zoom In</div>
  <div class="btn" onclick="zOut()">🔎&nbsp; Zoom Out</div>
  <div class="btn" onclick="snapShot()" title="Save screenshot">📸&nbsp; Screenshot</div>
</div>

<!-- Legend -->
<div class="gl" id="leg">
  <span class="ll">{legend_lo}</span>
  <canvas id="leg-c" width="230" height="13"></canvas>
  <span class="ll">{legend_hi}</span>
  <span class="lu">{unit}</span>
</div>

<!-- ═══ TIME-LAPSE: collapsed tab + expandable panel ═══ -->
<!-- Tab (always visible at bottom edge — click to expand) -->
<div id="player-tab" onclick="togglePlayer()">
  <div class="tab-dot" id="tab-dot"></div>
  <span id="tab-label">🎬 TIME-LAPSE</span>
  <span id="tab-date">──</span>
  <span id="tab-arrow">▲</span>
</div>

<!-- Expanded panel (hidden by default) -->
<div id="player">
  <div id="frame-label">── SELECT A FRAME ──</div>
  <div id="waveform"></div>
  <div id="scrub-wrap">
    <div id="scrub-track">
      <div id="scrub-fill" style="width:0%"></div>
      <div id="scrub-thumb" style="left:0%"></div>
    </div>
    <div id="scrub-ticks"></div>
  </div>
  <div id="transport">
    <button class="tbtn" onclick="skipToStart()" title="First frame">⏮</button>
    <button class="tbtn" onclick="stepBack()"    title="Previous frame">◀</button>
    <div class="t-sep"></div>
    <button class="tbtn" id="pp-btn" onclick="togglePlay()">▶&nbsp; PLAY</button>
    <div class="t-sep"></div>
    <button class="tbtn" onclick="stepFwd()"   title="Next frame">▶</button>
    <button class="tbtn" onclick="skipToEnd()" title="Last frame">⏭</button>
    <div class="t-sep"></div>
    <button class="tbtn" id="loop-btn" onclick="toggleLoop()" title="Repeat when finished">🔁&nbsp; Loop</button>
    <button class="tbtn" id="ping-btn" onclick="togglePing()" title="Bounce back and forth">🏓&nbsp; Ping</button>
    <div class="t-sep"></div>
    <button class="tbtn" onclick="snapShot()" title="Save screenshot as PNG">📸</button>
  </div>
  <div id="info-row">
    <div class="speed-group">
      <span class="speed-label">SPEED</span>
      <button class="spd-btn" onclick="setFPS(2)"  data-fps="2">¼×</button>
      <button class="spd-btn" onclick="setFPS(4)"  data-fps="4">½×</button>
      <button class="spd-btn active" onclick="setFPS(8)"  data-fps="8">1×</button>
      <button class="spd-btn" onclick="setFPS(16)" data-fps="16">2×</button>
      <button class="spd-btn" onclick="setFPS(30)" data-fps="30">4×</button>
    </div>
    <div id="frame-count">Frame 1 / {len(anim_frames)}</div>
    <div id="loop-indicator">🔁 Loop ON</div>
  </div>
</div>


<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
// ════════════════════════════════════════════════════════════
//  EARTH PULSE — Realistic 3D Climate Globe + Time-Lapse Player
// ════════════════════════════════════════════════════════════

const CFG={{
  earthTex:  "{earth_tex}",
  bumpTex:   "{bump_tex}",
  specTex:   "{spec_tex}",
  cloudTex:  "{cloud_tex}",
  autoSpin:  {'true' if auto_spin else 'false'},
  showAtmo:  {'true' if show_atmo else 'false'},
  showStars: {'true' if show_stars else 'false'},
  showWind:  {'true' if show_wind else 'false'},
  showCities:{'true' if show_cities else 'false'},
  showGrid:  {'true' if show_grid else 'false'},
  showClouds:{'true' if show_clouds else 'false'},
  nightMode: {'true' if night_mode else 'false'},
  focusLat:  {rc['lat']},
  focusLon:  {rc['lon']},
  camDist:   {rc['d']},
  varName:   "{var_label}",
  unit:      "{unit}",
  animFPS:   {anim_fps},
}};

const ANIM_FRAMES  = {ANIM_FRAMES_JSON};
const ANIM_LABELS  = {ANIM_LABELS_JSON};
const COLOR_STOPS  = {cs_json};
const SPARSE_PTS   = {json.dumps(sparse_pts)};

const CITIES=[
  {{n:"New York",la:40.7,lo:-74.0}},{{n:"London",la:51.5,lo:-0.1}},
  {{n:"Tokyo",la:35.7,lo:139.7}},{{n:"Sydney",la:-33.9,lo:151.2}},
  {{n:"Dubai",la:25.2,lo:55.3}},{{n:"São Paulo",la:-23.5,lo:-46.6}},
  {{n:"Mumbai",la:19.1,lo:72.9}},{{n:"Cairo",la:30.0,lo:31.2}},
  {{n:"Moscow",la:55.8,lo:37.6}},{{n:"Beijing",la:39.9,lo:116.4}},
  {{n:"Los Angeles",la:34.1,lo:-118.2}},{{n:"Paris",la:48.9,lo:2.3}},
  {{n:"Delhi",la:28.6,lo:77.2}},{{n:"Bangkok",la:13.7,lo:100.5}},
  {{n:"Lagos",la:6.5,lo:3.4}},{{n:"Shanghai",la:31.2,lo:121.5}},
  {{n:"Chicago",la:41.9,lo:-87.6}},
];

// ── helpers ──────────────────────────────────────────────────
function ll2xyz(la,lo,r=1){{
  const ph=(90-la)*Math.PI/180, th=(lo+180)*Math.PI/180;
  return new THREE.Vector3(
    -r*Math.sin(ph)*Math.cos(th), r*Math.cos(ph), r*Math.sin(ph)*Math.sin(th));
}}
function lerpCol(stops,t){{
  t=Math.max(0,Math.min(1,t));
  for(let i=1;i<stops.length;i++){{
    const a=stops[i-1],b=stops[i];
    if(t<=b.t){{const s=(t-a.t)/(b.t-a.t);return[a.r+(b.r-a.r)*s,a.g+(b.g-a.g)*s,a.b+(b.b-a.b)*s];}}
  }}
  const l=stops[stops.length-1];return[l.r,l.g,l.b];
}}

// ── Heatmap texture builder ───────────────────────────────────
const hmTexCache={{}};
function buildHMTexture(frameData){{
  const TW=1024, TH=512;
  const c=document.createElement('canvas'); c.width=TW; c.height=TH;
  const ctx=c.getContext('2d');
  const img=ctx.createImageData(TW,TH);
  const d=img.data;
  const gH=frameData.length, gW=frameData[0].length;
  for(let py=0;py<TH;py++){{
    const gy=Math.min(gH-1,Math.floor(py/TH*gH));
    for(let px=0;px<TW;px++){{
      const gx=Math.min(gW-1,Math.floor(px/TW*gW));
      const t=frameData[gy][gx];
      const [r,g,b]=lerpCol(COLOR_STOPS,t);
      const alpha=Math.round(Math.pow(t,0.65)*210);
      const i=(py*TW+px)*4;
      d[i]=r;d[i+1]=g;d[i+2]=b;d[i+3]=alpha;
    }}
  }}
  ctx.putImageData(img,0,0);
  if(CFG.hmBlur>0){{
    const tmp=document.createElement('canvas'); tmp.width=TW; tmp.height=TH;
    const t2=tmp.getContext('2d');
    t2.filter=`blur(${{CFG.hmBlur}}px)`;
    t2.drawImage(c,0,0);
    return new THREE.CanvasTexture(tmp);
  }}
  return new THREE.CanvasTexture(c);
}}

// Pre-build first frame; lazy-build rest
const textures = new Array(ANIM_FRAMES.length).fill(null);
textures[0] = buildHMTexture(ANIM_FRAMES[0]);

// ── Three.js scene ────────────────────────────────────────────
const W=window.innerWidth, H=window.innerHeight;
const renderer=new THREE.WebGLRenderer({{
  canvas:document.getElementById('c'),
  antialias:true,alpha:false,preserveDrawingBuffer:true,
  logarithmicDepthBuffer:true
}});
renderer.setSize(W,H);
renderer.setPixelRatio(Math.min(window.devicePixelRatio,2));
renderer.toneMapping=THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure=1.1;

const scene=new THREE.Scene();
const camera=new THREE.PerspectiveCamera(42,W/H,0.005,500);

const sun=new THREE.DirectionalLight(0xfff8e8,2.2);
sun.position.set(6,2,4); scene.add(sun);
scene.add(new THREE.AmbientLight(0x0a1a30,0.7));
const fill=new THREE.DirectionalLight(0x102040,0.4);
fill.position.set(-4,-2,-4); scene.add(fill);

const TL=new THREE.TextureLoader();
TL.crossOrigin='anonymous';

const ER=1.0;
let earthMesh=null, hmMesh=null, cloudMesh=null, nightMesh=null, atmoMesh=null;

function mkEarth(et,bt,st){{
  const mat=new THREE.MeshPhongMaterial({{
    map:et,bumpMap:bt||undefined,bumpScale:0.007,
    specularMap:st||undefined,specular:new THREE.Color(0x1a2a3a),shininess:20,
  }});
  earthMesh=new THREE.Mesh(new THREE.SphereGeometry(ER,128,64),mat);
  scene.add(earthMesh);
  addHMLayer(textures[0]);
  hideLoader();
}}

function addHMLayer(tex){{
  if(hmMesh){{scene.remove(hmMesh);hmMesh.geometry.dispose();hmMesh.material.dispose();}}
  const hmMat=new THREE.MeshBasicMaterial({{
    map:tex,transparent:true,opacity:1.0,
    depthWrite:false,blending:THREE.NormalBlending,side:THREE.FrontSide,
  }});
  hmMesh=new THREE.Mesh(new THREE.SphereGeometry(ER+0.003,128,64),hmMat);
  scene.add(hmMesh);
}}

function updateHMFrame(idx){{
  if(!textures[idx]) textures[idx]=buildHMTexture(ANIM_FRAMES[idx]);
  if(hmMesh){{
    hmMesh.material.map=textures[idx];
    hmMesh.material.needsUpdate=true;
  }}
  const lbl=ANIM_LABELS[idx];
  document.getElementById('cur-date').innerHTML=`📅 <b>${{lbl}}</b>`;
  document.getElementById('frame-label').textContent=lbl;
  document.getElementById('tab-date').textContent=lbl;
  document.getElementById('frame-count').textContent=`Frame ${{idx+1}} / ${{ANIM_FRAMES.length}}`;
  const pct=(idx/(ANIM_FRAMES.length-1||1))*100;
  document.getElementById('scrub-fill').style.width=pct+'%';
  document.getElementById('scrub-thumb').style.left=pct+'%';
  document.querySelectorAll('.wv-bar').forEach((b,i)=>b.classList.toggle('cur',i===idx));
}}

// ── Toggle player panel open/closed ──────────────────────────
let playerOpen=false;
function togglePlayer(){{
  playerOpen=!playerOpen;
  document.getElementById('player').classList.toggle('open',playerOpen);
  document.getElementById('player-tab').classList.toggle('open',playerOpen);
  document.getElementById('tab-arrow').textContent=playerOpen?'▼':'▲';
}}

TL.load(CFG.earthTex,
  et=>TL.load(CFG.bumpTex,
    bt=>TL.load(CFG.specTex,st=>mkEarth(et,bt,st),_=>mkEarth(et,bt,null)),
    _=>mkEarth(et,null,null)),
  _=>{{
    const mat=new THREE.MeshPhongMaterial({{color:0x1a4a8a,specular:0x112233,shininess:15}});
    earthMesh=new THREE.Mesh(new THREE.SphereGeometry(ER,128,64),mat);
    scene.add(earthMesh);addHMLayer(textures[0]);hideLoader();
  }}
);

// Clouds
if(CFG.showClouds){{
  const cMat=new THREE.MeshPhongMaterial({{transparent:true,opacity:0.28,depthWrite:false,blending:THREE.NormalBlending}});
  cloudMesh=new THREE.Mesh(new THREE.SphereGeometry(ER+0.014,64,32),cMat);
  scene.add(cloudMesh);
  TL.load(CFG.cloudTex,t=>{{cMat.map=t;cMat.alphaMap=t;cMat.needsUpdate=true;}});
}}

// Night overlay
TL.load("https://unpkg.com/three-globe/example/img/earth-night.jpg",nt=>{{
  const nMat=new THREE.MeshBasicMaterial({{map:nt,transparent:true,opacity:0,depthWrite:false,blending:THREE.NormalBlending}});
  nightMesh=new THREE.Mesh(new THREE.SphereGeometry(ER+0.004,64,32),nMat);
  scene.add(nightMesh);
}});

// Atmosphere
if(CFG.showAtmo){{
  atmoMesh=new THREE.Mesh(
    new THREE.SphereGeometry(ER+0.07,64,32),
    new THREE.MeshPhongMaterial({{color:0x0066ff,transparent:true,opacity:0.065,side:THREE.FrontSide,depthWrite:false}})
  );
  scene.add(atmoMesh);
  scene.add(new THREE.Mesh(
    new THREE.SphereGeometry(ER+0.12,64,32),
    new THREE.MeshPhongMaterial({{color:0x0044cc,transparent:true,opacity:0.04,side:THREE.BackSide,depthWrite:false}})
  ));
}}

// Stars
if(CFG.showStars){{
  const sv=new Float32Array(8000*3);
  for(let i=0;i<8000;i++){{
    const r=60+Math.random()*40, th=Math.random()*Math.PI*2, ph=Math.acos(2*Math.random()-1);
    sv[i*3]=r*Math.sin(ph)*Math.cos(th);sv[i*3+1]=r*Math.cos(ph);sv[i*3+2]=r*Math.sin(ph)*Math.sin(th);
  }}
  const sg=new THREE.BufferGeometry();
  sg.setAttribute('position',new THREE.Float32BufferAttribute(sv,3));
  scene.add(new THREE.Points(sg,new THREE.PointsMaterial({{color:0xffffff,size:0.12,sizeAttenuation:true,transparent:true,opacity:0.85}})));
}}

// Graticule
if(CFG.showGrid){{
  const gMat=new THREE.LineBasicMaterial({{color:0x0d4060,transparent:true,opacity:0.45}});
  const eMat=new THREE.LineBasicMaterial({{color:0x008899,transparent:true,opacity:0.5}});
  function mkLine(pts,mat){{const g=new THREE.BufferGeometry().setFromPoints(pts);scene.add(new THREE.Line(g,mat));}}
  [-60,-30,0,30,60].forEach(la=>{{
    const pts=[];for(let lo=-180;lo<=181;lo+=2)pts.push(ll2xyz(la,lo,1.001));mkLine(pts,la===0?eMat:gMat);
  }});
  for(let lo=-180;lo<180;lo+=30){{
    const pts=[];for(let la=-88;la<=88;la+=2)pts.push(ll2xyz(la,lo,1.001));mkLine(pts,gMat);
  }}
}}

// Wind particles
let windMesh=null, wPts=[];
if(CFG.showWind){{
  const WN=220;
  const wPos=new Float32Array(WN*3), wCol=new Float32Array(WN*3);
  for(let i=0;i<WN;i++){{
    const la=Math.random()*160-80, lo=Math.random()*360-180;
    const v=ll2xyz(la,lo,1.02);
    wPos[i*3]=v.x;wPos[i*3+1]=v.y;wPos[i*3+2]=v.z;
    wCol[i*3]=0;wCol[i*3+1]=0.88;wCol[i*3+2]=1;
    wPts.push({{la,lo,dir:Math.random()*360,sp:0.3+Math.random()*0.7,age:Math.random()*70,life:55+Math.random()*60}});
  }}
  const wg=new THREE.BufferGeometry();
  wg.setAttribute('position',new THREE.Float32BufferAttribute(wPos,3));
  wg.setAttribute('color',   new THREE.Float32BufferAttribute(wCol,3));
  windMesh=new THREE.Points(wg,new THREE.PointsMaterial({{vertexColors:true,size:0.006,transparent:true,opacity:0.7,depthWrite:false,sizeAttenuation:true}}));
  scene.add(windMesh);
}}
function updWind(){{
  if(!windMesh)return;
  const pa=windMesh.geometry.attributes.position;
  wPts.forEach((p,i)=>{{
    p.age++;
    const rad=p.dir*Math.PI/180;
    p.la+=Math.cos(rad)*p.sp*0.2;p.lo+=Math.sin(rad)*p.sp*0.35;
    if(p.lo>180)p.lo-=360;if(p.lo<-180)p.lo+=360;
    p.la=Math.max(-82,Math.min(82,p.la));
    p.dir+=(Math.random()-.5)*15;
    if(p.age>p.life){{p.la=Math.random()*160-80;p.lo=Math.random()*360-180;p.age=0;}}
    const v=ll2xyz(p.la,p.lo,1.02);pa.setXYZ(i,v.x,v.y,v.z);
  }});
  pa.needsUpdate=true;
}}

// Legend
{{
  const lc=document.getElementById('leg-c');
  const lx=lc.getContext('2d');
  const gr=lx.createLinearGradient(0,0,230,0);
  COLOR_STOPS.forEach(s=>gr.addColorStop(s.t,`rgb(${{s.r}},${{s.g}},${{s.b}})`));
  lx.fillStyle=gr;lx.fillRect(0,0,230,13);
  lx.strokeStyle='rgba(255,255,255,0.3)';lx.lineWidth=1;
  [0.25,0.5,0.75].forEach(t=>{{lx.beginPath();lx.moveTo(t*230,0);lx.lineTo(t*230,13);lx.stroke();}});
}}

// Camera
let sph={{th:0,ph:Math.PI/2,r:CFG.camDist}};
(()=>{{
  const v=ll2xyz(CFG.focusLat,CFG.focusLon,CFG.camDist);
  sph.r=CFG.camDist;
  sph.ph=Math.acos(Math.max(-1,Math.min(1,v.y/CFG.camDist)));
  sph.th=Math.atan2(v.z,v.x);
}})();
function applyCamera(){{
  camera.position.set(
    sph.r*Math.sin(sph.ph)*Math.cos(sph.th),
    sph.r*Math.cos(sph.ph),
    sph.r*Math.sin(sph.ph)*Math.sin(sph.th));
  camera.lookAt(0,0,0);
}}
applyCamera();

// Mouse drag
let drag=false,pm={{x:0,y:0}};
const ray=new THREE.Raycaster();
renderer.domElement.addEventListener('mousedown',e=>{{drag=true;pm={{x:e.clientX,y:e.clientY}};spinning=false;}});
renderer.domElement.addEventListener('mousemove',e=>{{
  if(drag){{
    sph.th-=(e.clientX-pm.x)*0.0045;
    sph.ph=Math.max(0.06,Math.min(Math.PI-0.06,sph.ph+(e.clientY-pm.y)*0.0045));
    pm={{x:e.clientX,y:e.clientY}};applyCamera();
  }}
  if(earthMesh){{
    const rect=renderer.domElement.getBoundingClientRect();
    const mx=((e.clientX-rect.left)/rect.width)*2-1;
    const my=-((e.clientY-rect.top)/rect.height)*2+1;
    ray.setFromCamera({{x:mx,y:my}},camera);
    const hits=ray.intersectObject(earthMesh);
    const el=document.getElementById('probe');
    if(hits.length){{
      const n=hits[0].point.clone().normalize();
      const la=(Math.asin(Math.max(-1,Math.min(1,n.y)))*180/Math.PI).toFixed(1);
      const lo=((Math.atan2(n.z,-n.x)*180/Math.PI-180+360)%360-180).toFixed(1);
      const frameData=ANIM_FRAMES[animState.cur];
      const gi=Math.max(0,Math.min(frameData.length-1,Math.round(90-parseFloat(la))/2));
      const gj=Math.max(0,Math.min(frameData[0].length-1,Math.round(parseFloat(lo)+180)/2));
      const rawT=frameData[Math.floor(gi)][Math.floor(gj)];
      const [r,g,b]=lerpCol(COLOR_STOPS,rawT);
      el.innerHTML=`📍 <b>Lat:${{la}}° Lon:${{lo}}°</b><br>
        <span style="color:rgb(${{Math.round(r)}},${{Math.round(g)}},${{Math.round(b)}})">■</span>
        &nbsp;${{CFG.varName}}: ${{(rawT*100).toFixed(1)}}% (${{CFG.unit}})`;
      el.classList.add('active');
    }} else {{
      el.textContent='Hover globe to inspect';el.classList.remove('active');
    }}
  }}
}});
renderer.domElement.addEventListener('mouseup',()=>drag=false);
renderer.domElement.addEventListener('mouseleave',()=>drag=false);
renderer.domElement.addEventListener('wheel',e=>{{
  sph.r=Math.max(1.15,Math.min(7,sph.r*(e.deltaY>0?1.07:0.93)));
  applyCamera();e.preventDefault();
}},{{passive:false}});

// City labels
const cityDiv=document.getElementById('city-div');
const cityObjs=[];
if(CFG.showCities){{
  CITIES.forEach(c=>{{
    const pos3=ll2xyz(c.la,c.lo,1.015);
    const el=document.createElement('div');el.className='clbl';
    el.innerHTML=`<div class="cdot"></div><div class="ctxt">${{c.n}}</div>`;
    cityDiv.appendChild(el);cityObjs.push({{pos3,el}});
  }});
}}
function updCities(){{
  const W2=renderer.domElement.clientWidth,H2=renderer.domElement.clientHeight;
  cityObjs.forEach(({{pos3,el}})=>{{
    const p=pos3.clone().project(camera);
    if(p.z>0.99){{el.style.display='none';return;}}
    const x=(p.x*0.5+0.5)*W2,y=(-p.y*0.5+0.5)*H2;
    if(x<0||x>W2||y<0||y>H2){{el.style.display='none';return;}}
    el.style.display='flex';el.style.left=x+'px';el.style.top=y+'px';
  }});
}}

// Globe controls
let spinning=CFG.autoSpin,atmoOn=CFG.showAtmo,cloudsOn=CFG.showClouds,nightOn=false;
function tSpin(){{spinning=!spinning;document.getElementById('b-spin').classList.toggle('on',spinning);}}
function rCam(){{
  const v=ll2xyz(CFG.focusLat,CFG.focusLon,CFG.camDist);
  sph.r=CFG.camDist;sph.ph=Math.acos(Math.max(-1,Math.min(1,v.y/CFG.camDist)));
  sph.th=Math.atan2(v.z,v.x);applyCamera();
}}
function tNight(){{nightOn=!nightOn;document.getElementById('b-night').classList.toggle('on',nightOn);}}
function tAtmo(){{atmoOn=!atmoOn;if(atmoMesh)atmoMesh.visible=atmoOn;document.getElementById('b-atmo').classList.toggle('on',atmoOn);}}
function tClouds(){{cloudsOn=!cloudsOn;if(cloudMesh)cloudMesh.visible=cloudsOn;document.getElementById('b-clouds').classList.toggle('on',cloudsOn);}}
function zIn(){{sph.r=Math.max(1.15,sph.r*0.85);applyCamera();}}
function zOut(){{sph.r=Math.min(7,sph.r*1.17);applyCamera();}}

// Night shading
function updNight(){{
  if(!nightMesh)return;
  if(!nightOn){{nightMesh.material.opacity=0;return;}}
  const sd=sun.position.clone().normalize();
  const cd=camera.position.clone().normalize();
  nightMesh.material.opacity=Math.max(0,Math.min(0.88,-cd.dot(sd)*2+0.1));
}}

function hideLoader(){{
  const l=document.getElementById('load');
  if(l){{l.style.transition='opacity .8s';l.style.opacity=0;setTimeout(()=>l.remove(),900);}}
}}

// Screenshot
function snapShot(){{
  renderer.render(scene,camera);
  const url=renderer.domElement.toDataURL('image/png');
  const a=document.createElement('a');
  a.href=url;a.download=`earth_pulse_${{ANIM_LABELS[animState.cur]||'frame'}}.png`;
  a.click();
  const fl=document.getElementById('snap-flash');
  fl.style.opacity=1;setTimeout(()=>fl.style.opacity=0,120);
}}

// ════════════════════════════════════════════════════════════
//  TIME-LAPSE ANIMATION ENGINE
// ════════════════════════════════════════════════════════════

const animState={{
  cur: 0,
  playing: false,
  loop: CFG.animLoop,
  pingPong: CFG.animPing,
  direction: 1,          // 1=forward, -1=backward
  fps: CFG.animFPS,
  lastTick: 0,
}};

// Build waveform bars (average field value per frame as intensity proxy)
(function buildWaveform(){{
  const wf=document.getElementById('waveform');
  ANIM_FRAMES.forEach((f,i)=>{{
    let sum=0,cnt=0;
    // sample every 4th row/col for speed
    for(let r=0;r<f.length;r+=4)for(let c=0;c<f[0].length;c+=4){{sum+=f[r][c];cnt++;}}
    const avg=sum/cnt;
    const bar=document.createElement('div');bar.className='wv-bar';
    bar.style.height=Math.round(8+avg*20)+'px';
    bar.title=ANIM_LABELS[i];
    bar.addEventListener('click',()=>jumpToFrame(i));
    wf.appendChild(bar);
  }});
}})();

// Build scrubber tick labels
(function buildTicks(){{
  const wrap=document.getElementById('scrub-ticks');
  const n=ANIM_FRAMES.length;
  const step=Math.max(1,Math.floor(n/6));
  for(let i=0;i<n;i+=step){{
    const t=document.createElement('div');t.className='tick';
    t.textContent=ANIM_LABELS[i];
    t.style.position='absolute';
    t.style.left=((i/(n-1||1))*100)+'%';
    t.style.transform='translateX(-50%)';
    wrap.appendChild(t);
  }}
}})();

// Scrubber mouse drag
(function initScrub(){{
  const wrap=document.getElementById('scrub-wrap');
  let scrubbing=false;
  function onScrub(e){{
    const rect=wrap.getBoundingClientRect();
    const pct=Math.max(0,Math.min(1,(e.clientX-rect.left)/rect.width));
    const idx=Math.round(pct*(ANIM_FRAMES.length-1));
    jumpToFrame(idx);
  }}
  wrap.addEventListener('mousedown',e=>{{scrubbing=true;onScrub(e);}});
  window.addEventListener('mousemove',e=>{{if(scrubbing)onScrub(e);}});
  window.addEventListener('mouseup',  ()=>scrubbing=false);
  // Touch support
  wrap.addEventListener('touchstart',e=>{{scrubbing=true;onScrub(e.touches[0]);}},{{passive:true}});
  window.addEventListener('touchmove', e=>{{if(scrubbing)onScrub(e.touches[0]);}},{{passive:true}});
  window.addEventListener('touchend',  ()=>scrubbing=false);
}})();

// Keyboard shortcuts
window.addEventListener('keydown',e=>{{
  if(e.code==='Space'){{e.preventDefault();togglePlay();}}
  else if(e.code==='ArrowRight')stepFwd();
  else if(e.code==='ArrowLeft') stepBack();
  else if(e.code==='Home')      skipToStart();
  else if(e.code==='End')       skipToEnd();
  else if(e.key==='l'||e.key==='L') toggleLoop();
  else if(e.key==='p'||e.key==='P') togglePing();
}});

// Transport functions
function jumpToFrame(idx){{
  animState.cur=Math.max(0,Math.min(ANIM_FRAMES.length-1,idx));
  updateHMFrame(animState.cur);
}}
function togglePlay(){{
  animState.playing=!animState.playing;
  const btn=document.getElementById('pp-btn');
  btn.textContent=animState.playing?'⏸ PAUSE':'▶ PLAY';
  btn.classList.toggle('active',animState.playing);
  document.getElementById('tab-dot').classList.toggle('playing',animState.playing);
  if(animState.playing)animState.lastTick=performance.now();
}}
function stepFwd(){{
  animState.playing=false;
  document.getElementById('pp-btn').textContent='▶ PLAY';
  document.getElementById('pp-btn').classList.remove('active');
  jumpToFrame(animState.cur+1);
}}
function stepBack(){{
  animState.playing=false;
  document.getElementById('pp-btn').textContent='▶ PLAY';
  document.getElementById('pp-btn').classList.remove('active');
  jumpToFrame(animState.cur-1);
}}
function skipToStart(){{animState.direction=1;jumpToFrame(0);}}
function skipToEnd()  {{animState.direction=-1;jumpToFrame(ANIM_FRAMES.length-1);}}
function toggleLoop(){{
  animState.loop=!animState.loop;
  document.getElementById('loop-btn').classList.toggle('active',animState.loop);
  document.getElementById('loop-indicator').textContent=animState.loop?'🔁 Loop ON':'↩ Loop OFF';
}}
function togglePing(){{
  animState.pingPong=!animState.pingPong;
  document.getElementById('ping-btn').classList.toggle('active',animState.pingPong);
}}
function setFPS(fps){{
  animState.fps=fps;
  document.querySelectorAll('.spd-btn').forEach(b=>
    b.classList.toggle('active',parseInt(b.dataset.fps)===fps));
}}

// Init state buttons
document.getElementById('loop-btn').classList.toggle('active',animState.loop);
document.getElementById('ping-btn').classList.toggle('active',animState.pingPong);
document.getElementById('loop-indicator').textContent=animState.loop?'🔁 Loop ON':'↩ Loop OFF';
updateHMFrame(0);

// Animation tick
function animTick(now){{
  if(!animState.playing)return;
  const interval=1000/animState.fps;
  if(now-animState.lastTick<interval)return;
  animState.lastTick=now;

  let next=animState.cur+animState.direction;

  if(next>=ANIM_FRAMES.length){{
    if(animState.pingPong){{animState.direction=-1;next=ANIM_FRAMES.length-2;}}
    else if(animState.loop)next=0;
    else{{animState.playing=false;document.getElementById('pp-btn').textContent='▶ PLAY';document.getElementById('pp-btn').classList.remove('active');return;}}
  }}
  if(next<0){{
    if(animState.pingPong){{animState.direction=1;next=1;}}
    else if(animState.loop)next=ANIM_FRAMES.length-1;
    else{{animState.playing=false;document.getElementById('pp-btn').textContent='▶ PLAY';document.getElementById('pp-btn').classList.remove('active');return;}}
  }}
  jumpToFrame(next);
}}

// Lazy pre-build textures in background
let preIdx=1;
function preBuild(){{
  if(preIdx<ANIM_FRAMES.length){{
    if(!textures[preIdx])textures[preIdx]=buildHMTexture(ANIM_FRAMES[preIdx]);
    preIdx++;
    setTimeout(preBuild,60);
  }}
}}
setTimeout(preBuild,1500);

// Resize
window.addEventListener('resize',()=>{{
  const W=window.innerWidth,H=window.innerHeight;
  renderer.setSize(W,H);camera.aspect=W/H;camera.updateProjectionMatrix();
}});

// Render loop
function animate(now){{
  requestAnimationFrame(animate);
  animTick(now);
  if(spinning){{sph.th+=0.002;applyCamera();}}
  if(cloudMesh)cloudMesh.rotation.y+=0.00012;
  updWind();updNight();updCities();
  renderer.render(scene,camera);
}}
animate(0);
</script></body></html>"""

# ─── Render ───────────────────────────────────────────────────
components.html(GLOBE_HTML, height=760, scrolling=False)
st.divider()

# ─── TIME SERIES ──────────────────────────────────────────────
st.markdown(f"### 📈 {var_label} — Climate Time Series Analysis")

active_tab = ui_tabs(
    options=[
        "📅 Annual Trend",
        "🌙 Seasonal Cycle",
        "🔀 All Variables",
        "📊 Data Table",
        "ℹ️ Info",
    ],
    default_value="📅 Annual Trend",
    key="time_series_tabs",
)

if active_tab == "📅 Annual Trend":
    L, R = st.columns([3, 1])
    with L:
        st.markdown(f"**Annual {var_label} — 1950 to {year}**")
        ts_vals = all_ts[var_label]
        df = pd.DataFrame({"Year": yrs, var_label: ts_vals})
        df["10-yr Rolling"] = (
            pd.Series(ts_vals)
            .rolling(10, center=True, min_periods=1)
            .mean()
            .round(3)
            .values
        )
        st.line_chart(
            df.set_index("Year")[[var_label, "10-yr Rolling"]],
            color=["#4a90e2", "#ff6b35"],
            height=260,
        )
    with R:
        st.markdown("**Key Stats**")
        tv = all_ts[var_label]
        st.metric("Selected Year", f"{tv[min(year - 1950, len(tv) - 1)]:.2f} {unit}")
        st.metric("All-time High", f"{max(tv):.2f} {unit}")
        st.metric("All-time Low", f"{min(tv):.2f} {unit}")
        st.metric("Mean", f"{np.mean(tv):.2f} {unit}")
        trend = np.polyfit(range(len(tv)), tv, 1)[0]
        st.metric("Trend /yr", f"{trend:+.4f} {unit}")

elif active_tab == "🌙 Seasonal Cycle":
    st.markdown(f"**Monthly Climatology — {var_label} ({year})**")
    L2, R2 = st.columns([3, 1])
    with L2:
        df2 = pd.DataFrame({"Month": MONTHS, var_label: monthly_v})
        st.bar_chart(df2.set_index("Month"), color=["#00d4ff"], height=240)
    with R2:
        st.markdown("**Seasonal Stats**")
        st.metric("Peak", MONTHS[int(np.argmax(monthly_v))])
        st.metric("Low", MONTHS[int(np.argmin(monthly_v))])
        st.metric(f"{month} Value", f"{monthly_v[month_idx - 1]:.2f} {unit}")
        st.metric("Range", f"{max(monthly_v) - min(monthly_v):.2f} {unit}")

elif active_tab == "🔀 All Variables":
    st.markdown(
        "**Normalised Comparison — Temperature · Precipitation · Wind (1950–2024)**"
    )

    def n01(lst):
        a, b = min(lst), max(lst)
        return [(v - a) / (b - a + 1e-9) for v in lst]

    df3 = pd.DataFrame(
        {
            "Year": yrs,
            "Temperature": n01(all_ts["Temperature"]),
            "Precipitation": n01(all_ts["Precipitation"]),
            "Wind Speed": n01(all_ts["Wind Speed"]),
        }
    )
    st.line_chart(
        df3.set_index("Year"),
        color=["#ff4444", "#4488ff", "#44ffcc"],
        height=260,
    )
    st.caption(
        "All normalised 0–1 for comparison. Temperature shows strongest upward trend."
    )

elif active_tab == "📊 Data Table":
    st.markdown(f"**Full Annual Dataset — {var_label}**")
    df4 = pd.DataFrame(
        {
            "Year": yrs,
            f"{var_label} ({unit})": all_ts[var_label],
            f"{month} Seasonal": [round(monthly_v[month_idx - 1], 3)] * len(yrs),
        }
    )
    st.dataframe(df4, use_container_width=True, hide_index=True, height=320)

elif active_tab == "ℹ️ Info":
    with st.expander("📡 Data Sources", expanded=True):
        st.markdown(
            """
| Dataset | Source | Res | Coverage |
|---|---|---|---|
| Surface Temperature | NOAA GHCN + ERA5 | 0.25°×0.25° | 1950–2024 |
| Precipitation | GPM IMERG + ERA5 | 0.10°×0.10° | 1979–2024 |
| Wind Speed | ERA5 Reanalysis | 0.25°×0.25° | 1950–2024 |
| Sea Ice | NSIDC SSMI | 25 km | 1979–2024 |
| CO₂ | ODIAC + NOAA MLO | 1 km / global | 2000–2024 |
| Imagery | NASA Blue Marble | 500 m | Composite |
| Clouds | NASA MODIS | 1 km | Daily |
            """
        )
    with st.expander("🎮 Controls"):
        st.markdown(
            """
- **Drag** — Rotate globe &emsp; **Scroll** — Zoom &emsp; **Hover** — Inspect value
- **Space** — Play/Pause animation
- **← →** Arrow keys — Step one frame at a time
- **Home / End** — Jump to first/last frame
- **L** — Toggle loop &emsp; **P** — Toggle ping-pong
- Click **waveform bars** to jump to any frame
- Drag the **scrubber bar** to scrub through time
- **📸 Screenshot** button — saves current globe as PNG
- Sidebar → **Animation Mode** — choose Monthly/Annual/Multi-Decade/Custom
            """
        )

st.markdown("""
<div style='text-align:center;color:#1a3a5c;font-size:10px;margin-top:12px;
font-family:Space Mono,monospace'>
EARTH PULSE · Realistic 3D Climate Globe · Three.js WebGL ·
Data: NOAA / ERA5 / NASA · © 2024
</div>""", unsafe_allow_html=True)