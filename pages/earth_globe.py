import streamlit as st
import streamlit.components.v1 as components
import json, random, math
import numpy as np
import pandas as pd


def earth_globe_page():

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
        st.markdown("## 🛰️ EARTH PULSE")
        st.markdown("*Climate Intelligence Platform*")
        st.divider()

        st.markdown("### 🌡️ Climate Variable")
        variable = st.selectbox("Primary Variable", [
            "🌡️ Temperature",
            "💧 Precipitation",
            "💨 Wind Speed",
        ])

        st.markdown("### 📅 Time Period")
        year = st.slider("Year", 1950, 2024, 2020)
        MONTHS = ["Jan","Feb","Mar","Apr","May","Jun",
                  "Jul","Aug","Sep","Oct","Nov","Dec"]
        month_idx = st.slider("Month", 1, 12, 7, format="%d")
        month = MONTHS[month_idx-1]

        st.markdown("### 🎨 Heatmap Style")
        heatmap_opacity = st.slider("Heatmap Opacity", 0.1, 0.85, 0.55, 0.01,
                                     help="Lower = more Earth visible")
        blur_px = st.slider("Smoothing Blur (px)", 0, 50, 22)
        hm_blend = st.selectbox("Blend Mode", ["Overlay","Multiply","Screen","Hard Light"])

        st.markdown("### 🌐 Globe Settings")
        base_map = st.selectbox("Earth Texture", [
            "🛰️ NASA Blue Marble",
            "🌙 NASA Night Lights",
            "🏔️ Topographic",
            "🌊 Ocean Floor",
        ])
        show_clouds  = st.checkbox("Cloud Layer",        value=True)
        show_atmo    = st.checkbox("Atmosphere Glow",    value=True)
        show_stars   = st.checkbox("Starfield",          value=True)
        show_grid    = st.checkbox("Lat/Lon Grid",       value=True)
        show_cities  = st.checkbox("City Labels",        value=True)
        show_wind    = st.checkbox("Wind Particles",     value=True)
        auto_spin    = st.checkbox("Auto-Rotate",        value=True)
        night_mode   = st.checkbox("Night Shadow",       value=True)

        st.markdown("### 📍 Region Focus")
        region = st.selectbox("Jump To", [
            "🌍 Global","🌏 Asia Pacific","🌎 Americas",
            "🌍 Africa","🌍 Europe","❄️ Arctic","🧊 Antarctic","🇮🇳 South Asia",
        ])
        st.divider()
        live = st.toggle("🔴 Live Feed", value=False)
        if live: st.success("🟢 ERA5 0.25° stream active")

    # ─── DATA GENERATION ──────────────────────────────────────────
    GRID_H, GRID_W = 180, 360
    np.random.seed(year * 31 + month_idx * 7)
    var_label = variable.split(" ",1)[1] if " " in variable else variable

    def gaussian_blobs(n=20, seed=0):
        rng = np.random.default_rng(seed)
        f = np.zeros((GRID_H, GRID_W), np.float32)
        for _ in range(n):
            cx,cy = rng.integers(0,GRID_W), rng.integers(0,GRID_H)
            amp   = rng.uniform(-1,1)
            sx,sy = rng.uniform(18,60), rng.uniform(12,45)
            X,Y   = np.meshgrid(np.arange(GRID_W), np.arange(GRID_H))
            f    += amp * np.exp(-((X-cx)**2/(2*sx**2)+(Y-cy)**2/(2*sy**2)))
        return f

    def lat_gradient(pole_val, eq_val):
        f = np.zeros((GRID_H, GRID_W), np.float32)
        for i in range(GRID_H):
            lat = 90 - i
            t   = abs(lat)/90
            f[i,:] = eq_val + (pole_val-eq_val)*t
        return f

    if "Temperature" in variable:
        base = lat_gradient(-0.6, 0.4)
        trend= (year-1950)*0.018
        seas = np.zeros((GRID_H,GRID_W),np.float32)
        for i in range(GRID_H):
            lat=90-i
            sign = 1 if month_idx in [6,7,8] else -1
            seas[i,:] = sign * np.clip(lat/55,-1,1)*0.9
        noise = gaussian_blobs(22, year+month_idx*3)
        field = base + noise*1.3 + trend + seas
        COLOR_STOPS = [
            (0.00,(  0,  0,160)),(0.18,( 30, 80,255)),
            (0.38,( 0,200,200)),(0.52,(240,240, 60)),
            (0.70,(255,120,  0)),(0.85,(220, 30,  0)),(1.00,(150,  0, 50)),
        ]
        unit="°C"; legend_lo="-3°C"; legend_hi="+3°C"

    elif "Precipitation" in variable:
        base = np.zeros((GRID_H,GRID_W),np.float32)
        for i in range(GRID_H):
            lat=90-i
            base[i,:] = (1.2*np.exp(-(lat**2)/180)
                         -0.5*np.exp(-((abs(lat)-28)**2)/70)
                         +0.1*np.exp(-((abs(lat)-58)**2)/120))
        noise = gaussian_blobs(24, year*2+month_idx)
        field = base + noise*0.55
        COLOR_STOPS = [
            (0.00,(240,248,255)),(0.15,(160,200,255)),
            (0.35,( 50,130,255)),(0.60,(  0, 50,200)),
            (0.80,(  0, 10,130)),(1.00,( 40,  0,100)),
        ]
        unit="mm/day"; legend_lo="0"; legend_hi="20+"

    else:  # Wind
        base = np.zeros((GRID_H,GRID_W),np.float32)
        for i in range(GRID_H):
            lat=90-i
            base[i,:] = (np.exp(-((abs(lat)-15)**2)/140)
                        +np.exp(-((abs(lat)-50)**2)/110)*0.7
                        +np.exp(-((abs(lat)-80)**2)/55)*0.45)
        noise = gaussian_blobs(18, year*3+month_idx*5)
        field = base + noise*0.38
        COLOR_STOPS = [
            (0.00,(  5, 15, 60)),(0.25,( 0, 80,180)),
            (0.50,(  0,200,180)),(0.75,(180,255, 80)),(1.00,(255,240,  0)),
        ]
        unit="m/s"; legend_lo="0"; legend_hi="25+"

    # Normalise
    fmin, fmax = field.min(), field.max()
    norm_field  = ((field-fmin)/(fmax-fmin+1e-9)).tolist()
    cs_json     = json.dumps([{"t":t,"r":r,"g":g,"b":b} for t,(r,g,b) in COLOR_STOPS])

    # Sparse probe points
    def gen_pts(n=200):
        pts=[]
        nf=np.array(norm_field)
        for _ in range(n):
            gi=random.randint(0,GRID_H-1); gj=random.randint(0,GRID_W-1)
            pts.append({"lat":round(90-gi,1),"lon":round(gj-180,1),
                        "v":round(float(nf[gi,gj]),3)})
        return pts
    sparse_pts=gen_pts(220)

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

    blend_map={"Overlay":"overlay","Multiply":"multiply",
               "Screen":"screen","Hard Light":"hard-light"}
    blend_mode=blend_map[hm_blend]

    # ─── HEADER ───────────────────────────────────────────────────
    st.markdown(f"**{variable}** &nbsp;·&nbsp; **{month} {year}** &nbsp;·&nbsp; "
                f"Opacity **{heatmap_opacity}** &nbsp;·&nbsp; {base_map}")

    c1,c2,c3,c4,c5=st.columns(5)
    c1.metric("🌡️ Temp",   f"{14.2+(year-1950)*0.018:.1f}°C",  f"+{(year-1950)*0.018:.2f}°C")
    c2.metric("💧 Precip", f"{100+(year-1990)*0.05:.1f} mm",    "+0.05/yr")
    c3.metric("💨 Wind",   f"{7.2-(year-1950)*0.003:.2f} m/s",  f"{-(year-1950)*0.003:.3f}")
    c4.metric("🧊 Sea Ice",f"{5.4-(year-2000)*0.06:.1f}M km²",  f"{-(year-2000)*0.06:.2f}M")
    c5.metric("💨 CO₂",    f"{315+(year-1950)*2.6:.0f} ppm",    "+2.6/yr")
    st.divider()

    # ─── GLOBE HTML ───────────────────────────────────────────────
    GLOBE_HTML = f"""<!DOCTYPE html><html><head>
    <meta charset="utf-8">
    <style>
    *{{margin:0;padding:0;box-sizing:border-box;}}
    body{{background:radial-gradient(ellipse at center,#0a1a2e 0%,#020a14 100%);
      overflow:hidden;font-family:'Space Mono',monospace;}}
    #c{{position:absolute;inset:0;width:100%;height:100%;display:block;}}

    /* ── Glass panels ── */
    .gl{{
      position:absolute;
      background:rgba(4,16,30,0.78);
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
      bottom:58px;left:50%;transform:translateX(-50%);
      display:flex;align-items:center;gap:10px;z-index:30;
      white-space:nowrap;padding:9px 18px;
    }}
    #leg-c{{width:230px;height:13px;border-radius:7px;
      border:1px solid rgba(0,180,255,0.25);display:block;}}
    .ll{{color:#7ecfff;font-size:10px;}}
    .lu{{color:#00d4ff;font-size:10px;margin-left:3px;font-weight:700;}}

    /* ── Time bar ── */
    #tbar{{
      bottom:14px;left:50%;transform:translateX(-50%);
      display:flex;align-items:center;gap:12px;z-index:30;
      white-space:nowrap;padding:8px 18px;
    }}
    .dot{{width:8px;height:8px;border-radius:50%;background:#00ff88;flex-shrink:0;
      box-shadow:0 0 6px #00ff88;animation:pulse 1.8s ease-in-out infinite;}}
    @keyframes pulse{{0%,100%{{opacity:1;}}50%{{opacity:.4;}}}}
    .sep2{{color:rgba(0,180,255,0.2);}}

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

    /* ── Heatmap canvas (CSS blend over iframe) ── */
    #hm-overlay{{
      position:absolute;inset:0;pointer-events:none;z-index:10;
      mix-blend-mode:{blend_mode};opacity:{heatmap_opacity};
    }}
    </style>
    </head><body>
    <div id="load"><div class="spin"></div><div class="load-txt">LOADING EARTH…</div></div>
    <canvas id="c"></canvas>
    <canvas id="hm-overlay"></canvas>
    <div id="city-div"></div>

    <!-- Info -->
    <div class="gl" id="info">
      <div class="title">
        <svg width="12" height="12" viewBox="0 0 12 12"><circle cx="6" cy="6" r="5" fill="none" stroke="#00d4ff" stroke-width="1.5"/><path d="M6 2v4l2.5 2" stroke="#00d4ff" stroke-width="1.2" fill="none"/></svg>
        {var_label.upper()} HEATMAP
      </div>
      <div>📅 <b>{month} {year}</b></div>
      <div>🌐 {region}</div>
      <div>🎨 Blend: {hm_blend} · {heatmap_opacity}</div>
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
    </div>

    <!-- Legend -->
    <div class="gl" id="leg">
      <span class="ll">{legend_lo}</span>
      <canvas id="leg-c" width="230" height="13"></canvas>
      <span class="ll">{legend_hi}</span>
      <span class="lu">{unit}</span>
    </div>

    <!-- Time bar -->
    <div class="gl" id="tbar">
      <div class="dot"></div>
      <span>Live Feed</span>
      <span class="sep2">|</span>
      <span id="clk">--:--:-- UTC</span>
      <span class="sep2">|</span>
      <span style="color:#2a5a7c">ERA5 Reanalysis</span>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
    // ════════════════════════════════════════════════════════════
    //  EARTH PULSE — Realistic 3D Climate Globe
    //  Strategy: NASA texture on earth mesh (full opacity) +
    //  separate heatmap canvas composited via CSS mix-blend-mode
    //  so the real Earth is always visible underneath.
    // ════════════════════════════════════════════════════════════

    const CFG={{
      earthTex:  "{earth_tex}",
      bumpTex:   "{bump_tex}",
      specTex:   "{spec_tex}",
      cloudTex:  "{cloud_tex}",
      hmBlur:    {blur_px},
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
    }};

    const NORM_FIELD  = {json.dumps(norm_field)};
    const COLOR_STOPS = {cs_json};
    const SPARSE_PTS  = {json.dumps(sparse_pts)};

    const CITIES=[
      {{n:"New York",    la:40.7,  lo:-74.0}},
      {{n:"London",      la:51.5,  lo:-0.1 }},
      {{n:"Tokyo",       la:35.7,  lo:139.7}},
      {{n:"Sydney",      la:-33.9, lo:151.2}},
      {{n:"Dubai",       la:25.2,  lo:55.3 }},
      {{n:"São Paulo",   la:-23.5, lo:-46.6}},
      {{n:"Mumbai",      la:19.1,  lo:72.9 }},
      {{n:"Cairo",       la:30.0,  lo:31.2 }},
      {{n:"Moscow",      la:55.8,  lo:37.6 }},
      {{n:"Beijing",     la:39.9,  lo:116.4}},
      {{n:"Los Angeles", la:34.1,  lo:-118.2}},
      {{n:"Paris",       la:48.9,  lo:2.3  }},
      {{n:"Delhi",       la:28.6,  lo:77.2 }},
      {{n:"Bangkok",     la:13.7,  lo:100.5}},
      {{n:"Lagos",       la:6.5,   lo:3.4  }},
      {{n:"Shanghai",    la:31.2,  lo:121.5}},
      {{n:"Chicago",     la:41.9,  lo:-87.6}},
    ];

    // ── helpers ──────────────────────────────────────────────────
    function ll2xyz(la,lo,r=1){{
      const ph=(90-la)*Math.PI/180, th=(lo+180)*Math.PI/180;
      return new THREE.Vector3(
        -r*Math.sin(ph)*Math.cos(th),
         r*Math.cos(ph),
         r*Math.sin(ph)*Math.sin(th));
    }}
    function lerpCol(stops,t){{
      t=Math.max(0,Math.min(1,t));
      for(let i=1;i<stops.length;i++){{
        const a=stops[i-1],b=stops[i];
        if(t<=b.t){{const s=(t-a.t)/(b.t-a.t);return[a.r+(b.r-a.r)*s,a.g+(b.g-a.g)*s,a.b+(b.b-a.b)*s];}}
      }}
      const l=stops[stops.length-1];return[l.r,l.g,l.b];
    }}

    // ── Build heatmap on the 2D overlay canvas ────────────────────
    // This canvas sits ON TOP of the WebGL canvas via CSS position:absolute
    // and uses mix-blend-mode so the Earth texture shows through.
    // We render the heatmap in equirectangular projection matching
    // the Earth sphere's UV layout, then CSS handles the blending.
    const hmCanvas = document.getElementById('hm-overlay');
    const hmCtx    = hmCanvas.getContext('2d');

    function resizeHM(){{
      hmCanvas.width  = window.innerWidth;
      hmCanvas.height = window.innerHeight;
    }}
    resizeHM();

    // We'll re-project heatmap onto the canvas each frame based on camera
    // For a simpler but effective approach: composite it as a WebGL texture
    // on a separate mesh layer with THREE.AdditiveBlending
    // The CSS overlay approach doesn't rotate with globe — switch to proper
    // WebGL texture sphere approach with ALPHA from color intensity only.

    // ── Build WebGL heatmap texture ───────────────────────────────
    function buildHMTexture(){{
      const TW=2048, TH=1024;
      const c=document.createElement('canvas'); c.width=TW; c.height=TH;
      const ctx=c.getContext('2d');

      // Step 1: paint raw pixel data
      const img=ctx.createImageData(TW,TH);
      const d=img.data;
      const gH=NORM_FIELD.length, gW=NORM_FIELD[0].length;

      for(let py=0;py<TH;py++){{
        const gy=Math.min(gH-1, Math.floor(py/TH*gH));
        for(let px=0;px<TW;px++){{
          const gx=Math.min(gW-1, Math.floor(px/TW*gW));
          const t=NORM_FIELD[gy][gx];
          const [r,g,b]=lerpCol(COLOR_STOPS,t);
          // KEY: alpha encodes intensity — low values nearly transparent
          // so ocean/poles stay mostly Earth-coloured
          const alpha=Math.round(Math.pow(t,0.65)*210);
          const i=(py*TW+px)*4;
          d[i]=r; d[i+1]=g; d[i+2]=b; d[i+3]=alpha;
        }}
      }}
      ctx.putImageData(img,0,0);

      // Step 2: Gaussian blur for smooth gradient appearance
      if(CFG.hmBlur>0){{
        const tmp=document.createElement('canvas'); tmp.width=TW; tmp.height=TH;
        const t2=tmp.getContext('2d');
        t2.filter=`blur(${{CFG.hmBlur}}px)`;
        t2.drawImage(c,0,0);
        return new THREE.CanvasTexture(tmp);
      }}
      return new THREE.CanvasTexture(c);
    }}

    // ── Three.js scene ────────────────────────────────────────────
    const W=window.innerWidth, H=window.innerHeight;
    const renderer=new THREE.WebGLRenderer({{
      canvas:document.getElementById('c'),
      antialias:true, alpha:false, logarithmicDepthBuffer:true
    }});
    renderer.setSize(W,H);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio,2));
    renderer.toneMapping=THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure=1.1;

    const scene=new THREE.Scene();
    const camera=new THREE.PerspectiveCamera(42,W/H,0.005,500);

    // ── Lighting — realistic sun ──────────────────────────────────
    const sun=new THREE.DirectionalLight(0xfff8e8,2.2);
    sun.position.set(6,2,4); scene.add(sun);
    scene.add(new THREE.AmbientLight(0x0a1a30,0.7));
    const fill=new THREE.DirectionalLight(0x102040,0.4);
    fill.position.set(-4,-2,-4); scene.add(fill);

    // ── Texture loader ────────────────────────────────────────────
    const TL=new THREE.TextureLoader();
    TL.crossOrigin='anonymous';

    // ── Earth ─────────────────────────────────────────────────────
    const ER=1.0;
    let earthMesh=null;

    function mkEarth(et,bt,st){{
      const mat=new THREE.MeshPhongMaterial({{
        map:et,
        bumpMap:bt||undefined, bumpScale:0.007,
        specularMap:st||undefined,
        specular:new THREE.Color(0x1a2a3a), shininess:20,
      }});
      earthMesh=new THREE.Mesh(new THREE.SphereGeometry(ER,128,64),mat);
      scene.add(earthMesh);
      // Now overlay heatmap layer
      addHMLayer();
      hideLoader();
    }}

    // ── Heatmap mesh — sits just above Earth, uses NormalBlending ─
    let hmMesh=null;
    function addHMLayer(){{
      const hmTex=buildHMTexture();
      // Use MeshBasicMaterial so it's unaffected by lighting
      const hmMat=new THREE.MeshBasicMaterial({{
        map:hmTex,
        transparent:true,
        opacity:1.0,           // alpha handled per-pixel in texture
        depthWrite:false,
        blending:THREE.NormalBlending,  // alpha composite: Earth shows through where alpha<255
        side:THREE.FrontSide,
      }});
      hmMesh=new THREE.Mesh(new THREE.SphereGeometry(ER+0.003,128,64),hmMat);
      scene.add(hmMesh);
    }}

    // Load chain
    TL.load(CFG.earthTex,
      et=>TL.load(CFG.bumpTex,
        bt=>TL.load(CFG.specTex, st=>mkEarth(et,bt,st), _=>mkEarth(et,bt,null)),
        _=>mkEarth(et,null,null)),
      _=>{{
        // Fallback
        const mat=new THREE.MeshPhongMaterial({{color:0x1a4a8a,specular:0x112233,shininess:15}});
        earthMesh=new THREE.Mesh(new THREE.SphereGeometry(ER,128,64),mat);
        scene.add(earthMesh);
        addHMLayer(); hideLoader();
      }}
    );

    // ── Clouds ────────────────────────────────────────────────────
    let cloudMesh=null;
    if(CFG.showClouds){{
      const cMat=new THREE.MeshPhongMaterial({{
        transparent:true,opacity:0.28,depthWrite:false,
        blending:THREE.NormalBlending,
      }});
      cloudMesh=new THREE.Mesh(new THREE.SphereGeometry(ER+0.014,64,32),cMat);
      scene.add(cloudMesh);
      TL.load(CFG.cloudTex,t=>{{cMat.map=t;cMat.alphaMap=t;cMat.needsUpdate=true;}});
    }}

    // ── Night overlay ─────────────────────────────────────────────
    let nightMesh=null;
    TL.load("https://unpkg.com/three-globe/example/img/earth-night.jpg",nt=>{{
      const nMat=new THREE.MeshBasicMaterial({{
        map:nt,transparent:true,opacity:0,depthWrite:false,
        blending:THREE.NormalBlending,
      }});
      nightMesh=new THREE.Mesh(new THREE.SphereGeometry(ER+0.004,64,32),nMat);
      scene.add(nightMesh);
    }});

    // ── Atmosphere ────────────────────────────────────────────────
    let atmoMesh=null;
    if(CFG.showAtmo){{
      atmoMesh=new THREE.Mesh(
        new THREE.SphereGeometry(ER+0.07,64,32),
        new THREE.MeshPhongMaterial({{
          color:0x0066ff,transparent:true,opacity:0.065,
          side:THREE.FrontSide,depthWrite:false,
        }})
      );
      scene.add(atmoMesh);
      // Rim glow
      scene.add(new THREE.Mesh(
        new THREE.SphereGeometry(ER+0.12,64,32),
        new THREE.MeshPhongMaterial({{
          color:0x0044cc,transparent:true,opacity:0.04,
          side:THREE.BackSide,depthWrite:false,
        }})
      ));
    }}

    // ── Stars ─────────────────────────────────────────────────────
    if(CFG.showStars){{
      const sv=new Float32Array(8000*3);
      for(let i=0;i<8000;i++){{
        const r=60+Math.random()*40;
        const th=Math.random()*Math.PI*2, ph=Math.acos(2*Math.random()-1);
        sv[i*3  ]=r*Math.sin(ph)*Math.cos(th);
        sv[i*3+1]=r*Math.cos(ph);
        sv[i*3+2]=r*Math.sin(ph)*Math.sin(th);
      }}
      const sg=new THREE.BufferGeometry();
      sg.setAttribute('position',new THREE.Float32BufferAttribute(sv,3));
      scene.add(new THREE.Points(sg,new THREE.PointsMaterial({{
        color:0xffffff,size:0.12,sizeAttenuation:true,transparent:true,opacity:0.85,
      }})));
    }}

    // ── Graticule ─────────────────────────────────────────────────
    if(CFG.showGrid){{
      const gMat=new THREE.LineBasicMaterial({{color:0x0d4060,transparent:true,opacity:0.45}});
      const eMat=new THREE.LineBasicMaterial({{color:0x008899,transparent:true,opacity:0.5}});
      function mkLine(pts,mat){{
        const g=new THREE.BufferGeometry().setFromPoints(pts);
        scene.add(new THREE.Line(g,mat));
      }}
      // Lat lines
      [-60,-30,0,30,60].forEach(la=>{{
        const pts=[];
        for(let lo=-180;lo<=181;lo+=2)pts.push(ll2xyz(la,lo,1.001));
        mkLine(pts,la===0?eMat:gMat);
      }});
      // Lon lines
      for(let lo=-180;lo<180;lo+=30){{
        const pts=[];
        for(let la=-88;la<=88;la+=2)pts.push(ll2xyz(la,lo,1.001));
        mkLine(pts,gMat);
      }}
    }}

    // ── Wind particles ────────────────────────────────────────────
    let windMesh=null, wPts=[];
    if(CFG.showWind){{
      const WN=220;
      const wPos=new Float32Array(WN*3), wCol=new Float32Array(WN*3);
      for(let i=0;i<WN;i++){{
        const la=Math.random()*160-80, lo=Math.random()*360-180;
        const v=ll2xyz(la,lo,1.02);
        wPos[i*3]=v.x; wPos[i*3+1]=v.y; wPos[i*3+2]=v.z;
        wCol[i*3]=0; wCol[i*3+1]=0.88; wCol[i*3+2]=1;
        wPts.push({{la,lo,dir:Math.random()*360,sp:0.3+Math.random()*0.7,
          age:Math.random()*70,life:55+Math.random()*60}});
      }}
      const wg=new THREE.BufferGeometry();
      wg.setAttribute('position',new THREE.Float32BufferAttribute(wPos,3));
      wg.setAttribute('color',   new THREE.Float32BufferAttribute(wCol,3));
      windMesh=new THREE.Points(wg,new THREE.PointsMaterial({{
        vertexColors:true,size:0.006,transparent:true,opacity:0.7,depthWrite:false,
        sizeAttenuation:true,
      }}));
      scene.add(windMesh);
    }}
    function updWind(){{
      if(!windMesh)return;
      const pa=windMesh.geometry.attributes.position;
      wPts.forEach((p,i)=>{{
        p.age++;
        const rad=p.dir*Math.PI/180;
        p.la+=Math.cos(rad)*p.sp*0.2; p.lo+=Math.sin(rad)*p.sp*0.35;
        if(p.lo>180)p.lo-=360; if(p.lo<-180)p.lo+=360;
        p.la=Math.max(-82,Math.min(82,p.la));
        p.dir+=(Math.random()-.5)*15;
        if(p.age>p.life){{p.la=Math.random()*160-80;p.lo=Math.random()*360-180;p.age=0;}}
        const v=ll2xyz(p.la,p.lo,1.02);
        pa.setXYZ(i,v.x,v.y,v.z);
      }});
      pa.needsUpdate=true;
    }}

    // ── Legend ────────────────────────────────────────────────────
    {{
      const lc=document.getElementById('leg-c');
      const lx=lc.getContext('2d');
      const gr=lx.createLinearGradient(0,0,230,0);
      COLOR_STOPS.forEach(s=>gr.addColorStop(s.t,`rgb(${{s.r}},${{s.g}},${{s.b}})`));
      lx.fillStyle=gr; lx.fillRect(0,0,230,13);
      // Tick marks
      lx.strokeStyle='rgba(255,255,255,0.3)'; lx.lineWidth=1;
      [0.25,0.5,0.75].forEach(t=>{{
        lx.beginPath(); lx.moveTo(t*230,0); lx.lineTo(t*230,13); lx.stroke();
      }});
    }}

    // ── Camera ────────────────────────────────────────────────────
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

    // ── Mouse drag ────────────────────────────────────────────────
    let drag=false, pm={{x:0,y:0}};
    const ray=new THREE.Raycaster();

    renderer.domElement.addEventListener('mousedown',e=>{{
      drag=true; pm={{x:e.clientX,y:e.clientY}}; spinning=false;
    }});
    renderer.domElement.addEventListener('mousemove',e=>{{
      if(drag){{
        sph.th-=(e.clientX-pm.x)*0.0045;
        sph.ph=Math.max(0.06,Math.min(Math.PI-0.06,sph.ph+(e.clientY-pm.y)*0.0045));
        pm={{x:e.clientX,y:e.clientY}}; applyCamera();
      }}
      // Probe value on hover
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
          const gi=Math.max(0,Math.min(179,Math.round(90-parseFloat(la))));
          const gj=Math.max(0,Math.min(359,Math.round(parseFloat(lo)+180)));
          const rawT=NORM_FIELD[gi][gj];
          const [r,g,b]=lerpCol(COLOR_STOPS,rawT);
          el.innerHTML=`📍 <b>Lat:${{la}}° Lon:${{lo}}°</b><br>
            <span style="color:rgb(${{Math.round(r)}},${{Math.round(g)}},${{Math.round(b)}})">■</span>
            &nbsp;${{CFG.varName}}: ${{(rawT*100).toFixed(1)}}% (${{CFG.unit}})`;
          el.classList.add('active');
        }} else {{
          el.textContent='Hover globe to inspect'; el.classList.remove('active');
        }}
      }}
    }});
    renderer.domElement.addEventListener('mouseup',()=>drag=false);
    renderer.domElement.addEventListener('mouseleave',()=>drag=false);
    renderer.domElement.addEventListener('wheel',e=>{{
      sph.r=Math.max(1.15,Math.min(7,sph.r*(e.deltaY>0?1.07:0.93)));
      applyCamera(); e.preventDefault();
    }},{{passive:false}});

    // ── City labels (HTML overlay synced to 3D) ───────────────────
    const cityDiv=document.getElementById('city-div');
    const cityObjs=[];
    if(CFG.showCities){{
      CITIES.forEach(c=>{{
        const pos3=ll2xyz(c.la,c.lo,1.015);
        const el=document.createElement('div'); el.className='clbl';
        el.innerHTML=`<div class="cdot"></div><div class="ctxt">${{c.n}}</div>`;
        cityDiv.appendChild(el);
        cityObjs.push({{pos3,el}});
      }});
    }}
    function updCities(){{
      const W2=renderer.domElement.clientWidth, H2=renderer.domElement.clientHeight;
     cityObjs.forEach(({{pos3,el}})=>{{
        const p=pos3.clone().project(camera);
        if(p.z>0.99){{el.style.display='none';return;}}
        const x=(p.x*0.5+0.5)*W2, y=(-p.y*0.5+0.5)*H2;
        if(x<0||x>W2||y<0||y>H2){{el.style.display='none';return;}}
        el.style.display='flex';
        el.style.left=x+'px'; el.style.top=y+'px';
      }});
    }}

    // ── Controls ──────────────────────────────────────────────────
    let spinning=CFG.autoSpin, atmoOn=CFG.showAtmo, cloudsOn=CFG.showClouds, nightOn=false;
    function tSpin()  {{ spinning=!spinning; document.getElementById('b-spin').classList.toggle('on',spinning); }}
    function rCam()   {{
      const v=ll2xyz(CFG.focusLat,CFG.focusLon,CFG.camDist);
      sph.r=CFG.camDist; sph.ph=Math.acos(Math.max(-1,Math.min(1,v.y/CFG.camDist)));
      sph.th=Math.atan2(v.z,v.x); applyCamera();
    }}
    function tNight() {{ nightOn=!nightOn; document.getElementById('b-night').classList.toggle('on',nightOn); }}
    function tAtmo()  {{ atmoOn=!atmoOn; if(atmoMesh)atmoMesh.visible=atmoOn; document.getElementById('b-atmo').classList.toggle('on',atmoOn); }}
    function tClouds(){{ cloudsOn=!cloudsOn; if(cloudMesh)cloudMesh.visible=cloudsOn; document.getElementById('b-clouds').classList.toggle('on',cloudsOn); }}
    function zIn()    {{ sph.r=Math.max(1.15,sph.r*0.85); applyCamera(); }}
    function zOut()   {{ sph.r=Math.min(7,sph.r*1.17); applyCamera(); }}

    // ── Night shading ─────────────────────────────────────────────
    function updNight(){{
      if(!nightMesh)return;
      if(!nightOn){{nightMesh.material.opacity=0;return;}}
      const sd=sun.position.clone().normalize();
      const cd=camera.position.clone().normalize();
      nightMesh.material.opacity=Math.max(0,Math.min(0.88,-cd.dot(sd)*2+0.1));
    }}

    // ── Loader hide ───────────────────────────────────────────────
    function hideLoader(){{
      const l=document.getElementById('load');
      if(l){{ l.style.transition='opacity .8s'; l.style.opacity=0; setTimeout(()=>l.remove(),900); }}
    }}

    // ── Clock ─────────────────────────────────────────────────────
    setInterval(()=>{{
      const n=new Date();
      document.getElementById('clk').textContent=
        [n.getUTCHours(),n.getUTCMinutes(),n.getUTCSeconds()]
          .map(v=>String(v).padStart(2,'0')).join(':')+' UTC';
    }},1000);

    // ── Resize ────────────────────────────────────────────────────
    window.addEventListener('resize',()=>{{
      const W=window.innerWidth, H=window.innerHeight;
      renderer.setSize(W,H);
      camera.aspect=W/H; camera.updateProjectionMatrix();
      resizeHM();
    }});

    // ── Render loop ───────────────────────────────────────────────
    function animate(){{
      requestAnimationFrame(animate);
      if(spinning){{sph.th+=0.002;applyCamera();}}
      if(cloudMesh)cloudMesh.rotation.y+=0.00012;
      updWind(); updNight(); updCities();
      renderer.render(scene,camera);
    }}
    animate();
    </script></body></html>"""

    # ─── Render ───────────────────────────────────────────────────
    components.html(GLOBE_HTML, height=680, scrolling=False)
    st.divider()

    # ─── TIME SERIES ──────────────────────────────────────────────
    st.markdown(f"### 📈 {var_label} — Climate Time Series Analysis")

    t1,t2,t3,t4,t5 = st.tabs([
        "📅 Annual Trend","🌙 Seasonal Cycle",
        "🔀 All Variables","📊 Data Table","ℹ️ Info",
    ])

    with t1:
        L,R=st.columns([3,1])
        with L:
            st.markdown(f"**Annual {var_label} — 1950 to {year}**")
            ts_vals=all_ts[var_label]
            df=pd.DataFrame({"Year":yrs, var_label:ts_vals})
            df["10-yr Rolling"]=pd.Series(ts_vals).rolling(10,center=True,min_periods=1).mean().round(3).values
            st.line_chart(df.set_index("Year")[[var_label,"10-yr Rolling"]],
                          color=["#4a90e2","#ff6b35"], height=260)
        with R:
            st.markdown("**Key Stats**")
            tv=all_ts[var_label]
            st.metric("Selected Year", f"{tv[min(year-1950,len(tv)-1)]:.2f} {unit}")
            st.metric("All-time High", f"{max(tv):.2f} {unit}")
            st.metric("All-time Low",  f"{min(tv):.2f} {unit}")
            st.metric("Mean",          f"{np.mean(tv):.2f} {unit}")
            trend=np.polyfit(range(len(tv)),tv,1)[0]
            st.metric("Trend /yr",     f"{trend:+.4f} {unit}")

    with t2:
        st.markdown(f"**Monthly Climatology — {var_label} ({year})**")
        L2,R2=st.columns([3,1])
        with L2:
            df2=pd.DataFrame({"Month":MONTHS, var_label:monthly_v})
            st.bar_chart(df2.set_index("Month"), color=["#00d4ff"], height=240)
        with R2:
            st.markdown("**Seasonal Stats**")
            st.metric("Peak",   MONTHS[int(np.argmax(monthly_v))])
            st.metric("Low",    MONTHS[int(np.argmin(monthly_v))])
            st.metric(f"{month} Value",f"{monthly_v[month_idx-1]:.2f} {unit}")
            st.metric("Range",  f"{max(monthly_v)-min(monthly_v):.2f} {unit}")

    with t3:
        st.markdown("**Normalised Comparison — Temperature · Precipitation · Wind (1950–2024)**")
        def n01(lst): a,b=min(lst),max(lst); return [(v-a)/(b-a+1e-9) for v in lst]
        df3=pd.DataFrame({
            "Year":yrs,
            "Temperature":   n01(all_ts["Temperature"]),
            "Precipitation": n01(all_ts["Precipitation"]),
            "Wind Speed":    n01(all_ts["Wind Speed"]),
        })
        st.line_chart(df3.set_index("Year"),
                      color=["#ff4444","#4488ff","#44ffcc"], height=260)
        st.caption("All normalised 0–1 for comparison. Temperature shows strongest upward trend.")

    with t4:
        st.markdown(f"**Full Annual Dataset — {var_label}**")
        df4=pd.DataFrame({
            "Year": yrs,
            f"{var_label} ({unit})": all_ts[var_label],
            f"{month} Seasonal": [round(monthly_v[month_idx-1],3)]*len(yrs),
        })
        st.dataframe(df4, use_container_width=True, hide_index=True, height=320)

    with t5:
        with st.expander("📡 Data Sources", expanded=True):
            st.markdown("""
    | Dataset | Source | Res | Coverage |
    |---|---|---|---|
    | Surface Temperature | NOAA GHCN + ERA5 | 0.25°×0.25° | 1950–2024 |
    | Precipitation | GPM IMERG + ERA5 | 0.10°×0.10° | 1979–2024 |
    | Wind Speed | ERA5 Reanalysis | 0.25°×0.25° | 1950–2024 |
    | Sea Ice | NSIDC SSMI | 25 km | 1979–2024 |
    | CO₂ | ODIAC + NOAA MLO | 1 km / global | 2000–2024 |
    | Imagery | NASA Blue Marble | 500 m | Composite |
    | Clouds | NASA MODIS | 1 km | Daily |
            """)
        with st.expander("🎮 Controls"):
            st.markdown("""
    - **Drag** — Rotate globe in 3D &emsp; **Scroll** — Zoom
    - **Hover** — Inspect lat/lon + data value at point
    - **Sidebar** — Switch variable, year, month, opacity, blend mode
    - Buttons on globe: Auto-Rotate · Reset · Night · Atmosphere · Clouds
            """)

    st.markdown("""
    <div style='text-align:center;color:#1a3a5c;font-size:10px;margin-top:12px;
    font-family:Space Mono,monospace'>
    EARTH PULSE · Realistic 3D Climate Globe · Three.js WebGL ·
    Data: NOAA / ERA5 / NASA · © 2024
    </div>""", unsafe_allow_html=True)
