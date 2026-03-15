import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import time
import json as _json
import streamlit.components.v1 as components

EVENTS = [
    dict(id=0,year=1970,month="November",type="Cyclone",name="Bhola Cyclone",lat=22.0,lon=89.5,deaths=500000,affected_M=3.6,damage_B=1.0,temp_anom=0.02,description="The deadliest tropical cyclone in recorded history made landfall in East Pakistan (now Bangladesh). Storm surges of up to 10 metres swept over the low-lying Ganges delta, wiping out entire coastal villages.",region_name="Bay of Bengal / Bangladesh",highlight_lats=[20,24,24,20],highlight_lons=[88,88,92,92],color="#00b4d8",zoom_scale=3.5),
    dict(id=1,year=1976,month="July",type="Earthquake",name="Tangshan Earthquake",lat=39.6,lon=118.2,deaths=242000,affected_M=0.8,damage_B=10.0,temp_anom=0.05,description="A magnitude 7.6 earthquake struck the industrial city of Tangshan, China at 3:42 AM while residents slept. Within seconds, 85% of the city's buildings collapsed, killing an estimated 242,000 people.",region_name="Hebei Province, China",highlight_lats=[38,41,41,38],highlight_lons=[116,116,121,121],color="#ff6d00",zoom_scale=4.0),
    dict(id=2,year=1991,month="April",type="Cyclone",name="Bangladesh Cyclone 1991",lat=22.8,lon=91.8,deaths=138000,affected_M=10.0,damage_B=1.5,temp_anom=0.15,description="A powerful cyclone with 250 km/h winds struck the Chittagong coast of Bangladesh. Despite warnings, over 138,000 people perished in the storm surge. A landmark moment for disaster early-warning systems.",region_name="Chittagong, Bangladesh",highlight_lats=[21,24,24,21],highlight_lons=[90,90,93,93],color="#00b4d8",zoom_scale=3.5),
    dict(id=3,year=1995,month="July",type="Heatwave",name="Chicago Heatwave",lat=41.9,lon=-87.6,deaths=739,affected_M=2.5,damage_B=0.12,temp_anom=0.42,description="Five days of extreme heat transformed Chicago into a furnace. Temperatures reached 41°C with humidity making it feel like 52°C. 739 people, mostly elderly and isolated residents, died.",region_name="Chicago, Illinois, USA",highlight_lats=[40,43,43,40],highlight_lons=[-90,-90,-86,-86],color="#ff1744",zoom_scale=4.0),
    dict(id=4,year=2003,month="August",type="Heatwave",name="European Heatwave",lat=47.0,lon=2.0,deaths=70000,affected_M=0.52,damage_B=13.0,temp_anom=0.85,description="The deadliest heatwave in European history. Record temperatures scorched the continent for two weeks. France alone lost around 15,000 lives.",region_name="Western Europe",highlight_lats=[43,53,53,43],highlight_lons=[-5,-5,16,16],color="#ff1744",zoom_scale=2.5),
    dict(id=5,year=2004,month="December",type="Tsunami",name="Indian Ocean Tsunami",lat=3.3,lon=95.9,deaths=227898,affected_M=1.7,damage_B=10.0,temp_anom=0.48,description="A Mw 9.1 earthquake off northern Sumatra generated tsunamis up to 30 metres tall that struck 14 countries. The world's deadliest tsunami triggered the largest international aid response in history.",region_name="Indian Ocean — 14 Countries",highlight_lats=[-5,15,15,-5],highlight_lons=[80,80,100,100],color="#2979ff",zoom_scale=2.5),
    dict(id=6,year=2005,month="August",type="Cyclone",name="Hurricane Katrina",lat=29.9,lon=-90.1,deaths=1836,affected_M=0.4,damage_B=125.0,temp_anom=0.52,description="Katrina made landfall as a Category 4 hurricane and overwhelmed New Orleans' levee system. Floodwaters submerged 80% of the city.",region_name="Gulf Coast, USA",highlight_lats=[28,32,32,28],highlight_lons=[-93,-93,-87,-87],color="#00b4d8",zoom_scale=3.5),
    dict(id=7,year=2010,month="January",type="Earthquake",name="Haiti Earthquake",lat=18.5,lon=-72.3,deaths=316000,affected_M=3.0,damage_B=8.0,temp_anom=0.55,description="A magnitude 7.0 earthquake struck 25 km west of Port-au-Prince, devastating one of the world's poorest nations. Over 316,000 people died and 1.5 million were displaced.",region_name="Port-au-Prince, Haiti",highlight_lats=[17,20,20,17],highlight_lons=[-74,-74,-71,-71],color="#ff6d00",zoom_scale=4.5),
    dict(id=8,year=2011,month="March",type="Tsunami",name="Tōhoku Earthquake & Tsunami",lat=38.3,lon=142.4,deaths=15897,affected_M=0.45,damage_B=235.0,temp_anom=0.54,description="A Mw 9.1 earthquake triggered a 40-metre tsunami that devastated Japan's northeastern coast and caused the Fukushima Daiichi nuclear disaster.",region_name="Tōhoku Region, Japan",highlight_lats=[36,41,41,36],highlight_lons=[139,139,145,145],color="#2979ff",zoom_scale=3.5),
    dict(id=9,year=2013,month="November",type="Cyclone",name="Typhoon Haiyan",lat=11.2,lon=124.0,deaths=6340,affected_M=16.1,damage_B=2.98,temp_anom=0.68,description="One of the strongest tropical cyclones ever recorded, Typhoon Haiyan made landfall in the Philippines with 315 km/h winds.",region_name="Visayas, Philippines",highlight_lats=[9,14,14,9],highlight_lons=[121,121,127,127],color="#00b4d8",zoom_scale=3.5),
    dict(id=10,year=2019,month="September",type="Wildfire",name="Australian Black Summer",lat=-33.9,lon=151.2,deaths=34,affected_M=3.0,damage_B=103.0,temp_anom=1.2,description="Australia's catastrophic 'Black Summer' burned 18.6 million hectares. An estimated 3 billion animals were killed. Scientists confirmed climate change made the fires 30% more likely.",region_name="Eastern & Southern Australia",highlight_lats=[-40,-25,-25,-40],highlight_lons=[140,140,154,154],color="#ff9100",zoom_scale=2.0),
    dict(id=11,year=2021,month="June",type="Heatwave",name="Pacific NW Heat Dome",lat=49.3,lon=-123.1,deaths=1400,affected_M=2.0,damage_B=7.5,temp_anom=1.24,description="An extraordinary heat dome pushed temperatures to 49.6°C in Lytton, Canada. Scientists called it a 'once-in-a-thousand-year' event made 150 times more likely by climate change.",region_name="Pacific Northwest, Canada & USA",highlight_lats=[44,54,54,44],highlight_lons=[-130,-130,-118,-118],color="#ff1744",zoom_scale=2.5),
    dict(id=12,year=2022,month="June",type="Flood",name="Pakistan Mega-Floods",lat=30.0,lon=70.0,deaths=1730,affected_M=33.0,damage_B=30.0,temp_anom=1.15,description="A third of Pakistan disappeared underwater in its worst flooding in history. Monsoon rains five times above normal displaced 8 million people.",region_name="Sindh & Balochistan, Pakistan",highlight_lats=[23,37,37,23],highlight_lons=[60,60,78,78],color="#00e5ff",zoom_scale=2.5),
    dict(id=13,year=2023,month="February",type="Earthquake",name="Turkey–Syria Earthquake",lat=37.2,lon=37.0,deaths=59259,affected_M=1.5,damage_B=34.2,temp_anom=1.17,description="A pair of devastating earthquakes — Mw 7.8 and 7.5 — struck southeastern Turkey and northern Syria at dawn, killing over 59,000 people.",region_name="Gaziantep–Kahramanmaraş, Turkey",highlight_lats=[35,40,40,35],highlight_lons=[33,33,42,42],color="#ff6d00",zoom_scale=3.5),
    dict(id=14,year=2023,month="September",type="Flood",name="Libya Derna Floods",lat=32.9,lon=21.8,deaths=11300,affected_M=0.35,damage_B=1.8,temp_anom=1.19,description="Storm Daniel caused catastrophic flooding in Libya. Two dams upstream of Derna collapsed simultaneously, releasing a 7-metre wall of water that swept entire city quarters into the sea.",region_name="Derna, Libya",highlight_lats=[31,34,34,31],highlight_lons=[19,19,24,24],color="#00e5ff",zoom_scale=4.0),
]

TYPE_COLORS = {
    "Cyclone":    ("#00b4d8","rgba(0,180,216,.12)","rgba(0,180,216,.35)"),
    "Earthquake": ("#ff6d00","rgba(255,109,0,.12)","rgba(255,109,0,.35)"),
    "Heatwave":   ("#ff1744","rgba(255,23,68,.12)","rgba(255,23,68,.35)"),
    "Flood":      ("#00e5ff","rgba(0,229,255,.12)","rgba(0,229,255,.35)"),
    "Wildfire":   ("#ff9100","rgba(255,145,0,.12)","rgba(255,145,0,.35)"),
    "Tsunami":    ("#2979ff","rgba(41,121,255,.12)","rgba(41,121,255,.35)"),
}
TYPE_EMOJI = {"Cyclone":"🌀","Earthquake":"⚡","Heatwave":"🔥","Flood":"🌊","Wildfire":"🔥","Tsunami":"🌊"}

def fmt(n):
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
    if n >= 1_000:     return f"{n/1_000:.1f}K"
    return str(int(n))

def build_globe(event, lon_center, lat_center, zoomed=False):
    fig = go.Figure()
    lons_full = np.linspace(-180,180,361).tolist()
    lats_full = np.linspace(-90,90,181).tolist()
    for lat_v in range(-60,90,30):
        fig.add_trace(go.Scattergeo(lon=lons_full,lat=[lat_v]*361,mode="lines",line=dict(width=.4,color="rgba(56,189,248,0.07)"),hoverinfo="skip",showlegend=False))
    for lon_v in range(-180,181,30):
        fig.add_trace(go.Scattergeo(lon=[lon_v]*181,lat=lats_full,mode="lines",line=dict(width=.4,color="rgba(56,189,248,0.07)"),hoverinfo="skip",showlegend=False))
    fig.add_trace(go.Scattergeo(lon=lons_full,lat=[0]*361,mode="lines",line=dict(width=.8,color="rgba(56,189,248,0.14)",dash="dot"),hoverinfo="skip",showlegend=False))
    for e in EVENTS:
        if e["id"]==event["id"]: continue
        c,_,_=TYPE_COLORS.get(e["type"],("#aaa","",""))
        sz=float(np.clip(np.log1p(e["deaths"])*2.8,6,22))*(0.5 if zoomed else 1)
        fig.add_trace(go.Scattergeo(lon=[e["lon"]],lat=[e["lat"]],mode="markers",marker=dict(size=sz,color=c,opacity=.2 if zoomed else .3,line=dict(width=.8,color=c)),text=[e["name"]],hovertemplate="<b>%{text}</b><br>"+str(e["year"])+"<extra></extra>",showlegend=False))
    _hc=event["color"].lstrip("#"); _r,_g,_b=int(_hc[0:2],16),int(_hc[2:4],16),int(_hc[4:6],16)
    fig.add_trace(go.Scattergeo(lon=event["highlight_lons"]+[event["highlight_lons"][0]],lat=event["highlight_lats"]+[event["highlight_lats"][0]],mode="lines",line=dict(width=2.5 if zoomed else 1.5,color=event["color"]),fill="toself",fillcolor=f"rgba({_r},{_g},{_b},{0.35 if zoomed else 0.18})",hoverinfo="skip",showlegend=False))
    base=float(np.clip(np.log1p(event["deaths"])*3.2,14,42))
    for sz,op in ([(base*.9,.1),(base*.65,.18),(base*.45,.3)] if zoomed else [(base*2.6,.07),(base*1.9,.12),(base*1.4,.2)]):
        fig.add_trace(go.Scattergeo(lon=[event["lon"]],lat=[event["lat"]],mode="markers",marker=dict(size=sz,color=event["color"],opacity=op,line=dict(width=1,color=event["color"])),hoverinfo="skip",showlegend=False))
    fig.add_trace(go.Scattergeo(lon=[event["lon"]],lat=[event["lat"]],mode="markers+text",marker=dict(size=base*(0.55 if zoomed else 1),color=event["color"],opacity=1,line=dict(width=2,color="#ffffff")),text=[f"  {event['name']}"],textposition="middle right",textfont=dict(size=11 if zoomed else 10,color="#ffffff",family="DM Mono"),hovertemplate=f"<b>{event['name']}</b><br>{event['year']}<br>Deaths: {fmt(event['deaths'])}<extra></extra>",showlegend=False))
    proj_scale=event.get("zoom_scale",3.0) if zoomed else 1.0
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",margin=dict(l=0,r=0,t=0,b=0),height=480,geo=dict(projection_type="orthographic",projection_rotation=dict(lon=lon_center,lat=lat_center,roll=0),projection_scale=proj_scale,showland=True,landcolor="#0f1e32",showocean=True,oceancolor="#060e1a",showcountries=True,countrycolor="rgba(56,100,140,0.22)",countrywidth=.5,showcoastlines=True,coastlinecolor="rgba(56,140,180,0.28)",coastlinewidth=.7,showframe=False,bgcolor="rgba(0,0,0,0)",showlakes=True,lakecolor="#060e1a"),dragmode="pan")
    return fig


def story_mode_page():
    # ── CSS ──
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&family=DM+Sans:wght@300;400;500&display=swap');
    .story-header { display:flex;align-items:center;justify-content:space-between;padding:.65rem 1.2rem;background:linear-gradient(90deg,#0d1520,#111827,#0d1520);border:1px solid #1e2d45;border-radius:10px;margin-bottom:1rem;position:relative;overflow:hidden; }
    .story-header::after { content:'';position:absolute;bottom:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,#38bdf8,#f59e0b,transparent);opacity:.6; }
    .story-logo { font-family:'Syne',sans-serif;font-size:1.05rem;font-weight:800;letter-spacing:.12em;color:#38bdf8;text-transform:uppercase; }
    .story-logo span { color:#f59e0b; }
    .story-tag { font-family:'DM Mono',monospace;font-size:.58rem;color:#405570;letter-spacing:.2em;text-transform:uppercase; }
    .spill { display:flex;gap:.5rem; }
    .spill-pill { font-family:'DM Mono',monospace;font-size:.52rem;letter-spacing:.1em;padding:.22rem .55rem;border-radius:20px;text-transform:uppercase; }
    .pill-g { background:rgba(52,211,153,.1);border:1px solid rgba(52,211,153,.3);color:#34d399; }
    .pill-b { background:rgba(56,189,248,.1);border:1px solid rgba(56,189,248,.3);color:#38bdf8; }
    .pill-o { background:rgba(245,158,11,.1);border:1px solid rgba(245,158,11,.3);color:#f59e0b; }
    .panel-lbl { font-family:'DM Mono',monospace;font-size:.5rem;letter-spacing:.25em;text-transform:uppercase;color:#405570;padding:.5rem .8rem .4rem;border-bottom:1px solid #1e2d45;display:flex;align-items:center;gap:5px; }
    .panel-lbl::before { content:'';width:5px;height:1px;background:#38bdf8; }
    .detail-hero { background:linear-gradient(135deg,#0d1e30,#132030);border:1px solid #1e2d45;border-radius:8px;padding:1rem;margin-bottom:.8rem; }
    .d-year { font-family:'DM Mono',monospace;font-size:1.8rem;font-weight:500;line-height:1;margin-bottom:.25rem;color:#f59e0b;letter-spacing:-.02em; }
    .d-name { font-family:'Syne',sans-serif;font-size:1rem;font-weight:700;color:#f0f6ff;margin-bottom:.4rem;line-height:1.25; }
    .d-desc { font-size:.78rem;color:#8baabf;line-height:1.65; }
    .d-badge { display:inline-block;padding:.1rem .4rem;border-radius:3px;font-family:'DM Mono',monospace;font-size:.5rem;letter-spacing:.08em;text-transform:uppercase;font-weight:500;margin-bottom:.5rem; }
    .stat-grid { display:grid;grid-template-columns:1fr 1fr;gap:.45rem;margin-bottom:.8rem; }
    .stat-card { background:#1a2235;border:1px solid #1e2d45;border-radius:6px;padding:.55rem .7rem; }
    .stat-val { font-family:'Syne',sans-serif;font-size:1.05rem;font-weight:700;margin-bottom:.12rem;display:block; }
    .stat-lbl { font-family:'DM Mono',monospace;font-size:.48rem;color:#405570;letter-spacing:.1em;text-transform:uppercase; }
    .coord-row { display:flex;gap:.4rem;margin-bottom:.7rem;flex-wrap:wrap; }
    .coord-chip { font-family:'DM Mono',monospace;font-size:.58rem;color:#38bdf8;background:rgba(56,189,248,.1);border:1px solid rgba(56,189,248,.2);border-radius:4px;padding:.22rem .5rem; }
    .imp-wrap { margin-bottom:.45rem; }
    .imp-lbl { display:flex;justify-content:space-between;font-family:'DM Mono',monospace;font-size:.55rem;color:#8baabf;margin-bottom:.18rem; }
    .imp-track { height:4px;background:#1e2d45;border-radius:2px;overflow:hidden; }
    .imp-fill { height:100%;border-radius:2px; }
    .sec-title { font-family:'DM Mono',monospace;font-size:.52rem;color:#405570;letter-spacing:.2em;text-transform:uppercase;margin-bottom:.45rem;padding-bottom:.28rem;border-bottom:1px solid #1e2d45; }
    .restart-btn button { background:linear-gradient(135deg,#1a1000,#2a1a00)!important;border:1px solid #f59e0b!important;color:#f59e0b!important; }
    </style>
    """, unsafe_allow_html=True)

    # ── Session state ──
    for k,v in [("s_idx",0),("s_playing",False),("s_finished",False),("s_zoomed",False)]:
        if k not in st.session_state: st.session_state[k]=v

    # Handle timeline click via query param
    qp = st.query_params
    if "tl_click" in qp:
        try:
            ci = int(qp["tl_click"])
            if 0 <= ci < len(EVENTS):
                if st.session_state.s_idx == ci:
                    st.session_state.s_zoomed = not st.session_state.s_zoomed
                else:
                    st.session_state.s_idx    = ci
                    st.session_state.s_zoomed = True
                    st.session_state.s_playing  = False
                    st.session_state.s_finished = False
        except: pass
        st.query_params.clear()

    ev = EVENTS[st.session_state.s_idx]

    # ── Three columns ──
    col_tl, col_globe, col_detail = st.columns([1, 1.7, 1.1], gap="small")

    # ── LEFT: Timeline HTML component ──
    with col_tl:
        st.markdown('<div class="panel-lbl">⬡ Timeline — 1970 to Present</div>', unsafe_allow_html=True)
        js_events = _json.dumps([{"id":e["id"],"year":e["year"],"month":e["month"],"type":e["type"],"name":e["name"],"desc":e["description"][:110]+"…","color":TYPE_COLORS.get(e["type"],("#aaa","",""))[0],"bg":TYPE_COLORS.get(e["type"],("#aaa","rgba(170,170,170,.1)",""))[1],"bd":TYPE_COLORS.get(e["type"],("#aaa","","rgba(170,170,170,.3)"))[2],"emoji":TYPE_EMOJI.get(e["type"],"●")} for e in EVENTS])
        active_idx = st.session_state.s_idx
        zoomed_flag = "true" if st.session_state.s_zoomed else "false"
        tl_html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@600;700&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400&display=swap');
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{background:#0b0f19;color:#f0f6ff;font-family:'DM Sans',sans-serif;height:100%;overflow:hidden}}
#scroll{{height:calc(100vh - 28px);overflow-y:auto;padding:.45rem .4rem .45rem .28rem;scrollbar-width:thin;scrollbar-color:#1e2d45 #0b0f19}}
#scroll::-webkit-scrollbar{{width:3px}}#scroll::-webkit-scrollbar-track{{background:#0b0f19}}#scroll::-webkit-scrollbar-thumb{{background:#1e2d45;border-radius:2px}}
.row{{display:flex;cursor:pointer;margin-bottom:.08rem}}
.spine{{display:flex;flex-direction:column;align-items:center;width:20px;flex-shrink:0}}
.dot{{width:8px;height:8px;border-radius:50%;border:2px solid #1e2d45;background:#0b0f19;margin-top:5px;flex-shrink:0;z-index:2;transition:all .2s}}
.vl{{width:1px;flex:1;min-height:24px;background:linear-gradient(#1e2d45,transparent)}}
.card{{flex:1;background:#1a2235;border:1px solid #1e2d45;border-left:2px solid #1e2d45;border-radius:6px;padding:.44rem .58rem;margin-bottom:.28rem;transition:all .18s;user-select:none}}
.card:hover{{background:#1d2a40;border-color:rgba(56,189,248,.45);border-left-color:#38bdf8;transform:translateX(3px);box-shadow:-3px 0 10px rgba(56,189,248,.12)}}
.card.active{{background:#1a2d42;border-color:rgba(56,189,248,.5)}}
.card.flash{{background:rgba(56,189,248,.15)!important;transform:translateX(3px) scale(1.004)!important}}
.badge{{display:inline-block;padding:.08rem .35rem;border-radius:3px;font-family:'DM Mono',monospace;font-size:.46rem;letter-spacing:.08em;text-transform:uppercase;font-weight:500;margin-bottom:.15rem}}
.zt{{display:inline-block;margin-left:4px;padding:.08rem .32rem;border-radius:3px;font-family:'DM Mono',monospace;font-size:.43rem;letter-spacing:.1em;text-transform:uppercase;background:rgba(52,211,153,.1);border:1px solid rgba(52,211,153,.28);color:#34d399;animation:zp 1.6s ease-in-out infinite}}
@keyframes zp{{0%,100%{{opacity:.7}}50%{{opacity:1}}}}
.yr{{font-family:'DM Mono',monospace;font-size:.58rem;letter-spacing:.1em;margin-bottom:.12rem}}
.nm{{font-family:'Syne',sans-serif;font-size:.74rem;font-weight:600;color:#f0f6ff;line-height:1.2;margin-bottom:.12rem}}
.ds{{font-size:.64rem;color:#8baabf;line-height:1.4;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}}
.hint{{padding:.3rem .5rem;border-top:1px solid #1e2d45;font-family:'DM Mono',monospace;font-size:.46rem;color:#405570;letter-spacing:.15em;text-transform:uppercase;text-align:center}}
</style></head><body>
<div id="scroll"></div><div class="hint">click to zoom · click again to unzoom</div>
<script>
const EV={js_events},ACTIVE={active_idx},ZOOMED={zoomed_flag};
const sc=document.getElementById('scroll');
EV.forEach((e,i)=>{{
  const isA=(i===ACTIVE);
  const row=document.createElement('div');row.className='row';
  const spine=document.createElement('div');spine.className='spine';
  const dot=document.createElement('div');dot.className='dot';
  if(isA){{dot.style.background=e.color;dot.style.borderColor=e.color;dot.style.boxShadow=`0 0 6px ${{e.color}}`;}}
  const vl=document.createElement('div');vl.className='vl';
  spine.appendChild(dot);spine.appendChild(vl);
  const card=document.createElement('div');
  card.className='card'+(isA?' active':'');
  card.style.borderLeftColor=isA?e.color:'#1e2d45';
  const bw=document.createElement('div');bw.style.cssText='display:flex;align-items:center;margin-bottom:.15rem';
  const b=document.createElement('span');b.className='badge';
  b.style.cssText=`background:${{e.bg}};border:1px solid ${{e.bd}};color:${{e.color}}`;
  b.textContent=e.emoji+' '+e.type;bw.appendChild(b);
  if(isA&&ZOOMED){{const zt=document.createElement('span');zt.className='zt';zt.textContent='⊕ Zoomed';bw.appendChild(zt);}}
  const yr=document.createElement('div');yr.className='yr';yr.style.color=e.color;yr.textContent=e.year+' · '+e.month;
  const nm=document.createElement('div');nm.className='nm';nm.textContent=e.name;
  const ds=document.createElement('div');ds.className='ds';ds.textContent=e.desc;
  card.appendChild(bw);card.appendChild(yr);card.appendChild(nm);card.appendChild(ds);
  row.appendChild(spine);row.appendChild(card);sc.appendChild(row);
  row.addEventListener('mouseenter',()=>{{if(i!==ACTIVE){{dot.style.background=e.color+'55';dot.style.borderColor=e.color;dot.style.boxShadow=`0 0 5px ${{e.color}}88`;card.style.borderLeftColor=e.color;}}}} );
  row.addEventListener('mouseleave',()=>{{if(i!==ACTIVE){{dot.style.background='';dot.style.borderColor='';dot.style.boxShadow='';card.style.borderLeftColor='#1e2d45';}}}} );
  row.addEventListener('click',()=>{{card.classList.add('flash');setTimeout(()=>{{const u=new URL(window.parent.location.href);u.searchParams.set('tl_click',String(i));window.parent.location.href=u.toString();}},120);}});
}});
setTimeout(()=>{{const rows=sc.querySelectorAll('.row');if(rows[ACTIVE])rows[ACTIVE].scrollIntoView({{behavior:'smooth',block:'center'}});}},80);
</script></body></html>"""
        components.html(tl_html, height=680, scrolling=False)

    # ── MIDDLE: Globe ──
    with col_globe:
        st.markdown(f'<div class="panel-lbl">⬡ Interactive 3D Globe · {"🔍 ZOOMED" if st.session_state.s_zoomed else "🌐 Globe View"} &nbsp;·&nbsp; <span style="color:#405570">{ev["year"]} · {ev["region_name"]}</span></div>', unsafe_allow_html=True)

        lon_c = float(ev["lon"])
        lat_c = max(-60.0, min(60.0, float(ev["lat"])))

        fig_globe = build_globe(ev, lon_c, lat_c, zoomed=st.session_state.s_zoomed)
        clicked = st.plotly_chart(fig_globe, use_container_width=True,
            config={"displayModeBar":True,"modeBarButtonsToRemove":["select2d","lasso2d","resetScale2d"],"displaylogo":False,"scrollZoom":True},
            key=f"globe_{st.session_state.s_idx}_{st.session_state.s_zoomed}",
            on_select="rerun", selection_mode="points")

        if clicked and hasattr(clicked,"selection") and clicked.selection:
            pts = clicked.selection.get("points",[])
            if pts:
                pt=pts[0]; clat=pt.get("lat"); clon=pt.get("lon")
                if clat is not None and clon is not None:
                    for e in EVENTS:
                        if abs(e["lat"]-clat)<0.5 and abs(e["lon"]-clon)<0.5:
                            if st.session_state.s_idx==e["id"]:
                                st.session_state.s_zoomed = not st.session_state.s_zoomed
                            else:
                                st.session_state.s_idx=e["id"]; st.session_state.s_zoomed=True
                                st.session_state.s_playing=False; st.session_state.s_finished=False
                            st.rerun(); break

        pct = int(st.session_state.s_idx/(len(EVENTS)-1)*100)
        st.markdown(f"""<div style="padding:.1rem 0 0"><div style="display:flex;justify-content:space-between;font-family:'DM Mono',monospace;font-size:.52rem;color:#405570;margin-bottom:4px"><span>1970</span><span style="color:#f59e0b">Event {st.session_state.s_idx+1} / {len(EVENTS)}</span><span>2023</span></div><div style="height:3px;background:#1e2d45;border-radius:2px;overflow:hidden"><div style="width:{pct}%;height:100%;background:linear-gradient(90deg,#38bdf8,#f59e0b);border-radius:2px;transition:width .4s ease"></div></div></div>""", unsafe_allow_html=True)
        st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

        if st.session_state.s_finished:
            st.markdown('<div style="text-align:center;padding:.3rem 0;font-family:DM Mono,monospace;font-size:.58rem;color:#f59e0b;letter-spacing:.15em">✓ TIMELINE COMPLETE</div>', unsafe_allow_html=True)
            rf1,rf2,rf3 = st.columns([1,2,1])
            with rf1:
                if st.button("⏮", key="fin_first"):
                    st.session_state.s_idx=0; st.session_state.s_finished=False; st.session_state.s_zoomed=False; st.rerun()
            with rf2:
                if st.button("↺  Restart", key="btn_restart", use_container_width=True):
                    st.session_state.s_idx=0; st.session_state.s_playing=True; st.session_state.s_finished=False; st.session_state.s_zoomed=False; st.rerun()
            with rf3:
                if st.button("◀", key="fin_prev"):
                    st.session_state.s_idx=max(0,st.session_state.s_idx-1); st.session_state.s_finished=False; st.rerun()
        else:
            pc1,pc2,pc3,pc4,pc5 = st.columns([1,1,2,1,1],gap="small")
            with pc1:
                if st.button("⏮",key="btn_first"): st.session_state.s_idx=0;st.session_state.s_playing=False;st.session_state.s_finished=False;st.session_state.s_zoomed=False;st.rerun()
            with pc2:
                if st.button("◀",key="btn_prev"): st.session_state.s_idx=max(0,st.session_state.s_idx-1);st.session_state.s_playing=False;st.session_state.s_finished=False;st.rerun()
            with pc3:
                if st.session_state.s_playing:
                    if st.button("⏸  Pause",key="btn_pause",use_container_width=True): st.session_state.s_playing=False;st.rerun()
                else:
                    if st.button("▶  Play",key="btn_play",use_container_width=True): st.session_state.s_playing=True;st.session_state.s_finished=False;st.session_state.s_zoomed=False;st.rerun()
            with pc4:
                if st.button("▶",key="btn_next"): st.session_state.s_idx=min(len(EVENTS)-1,st.session_state.s_idx+1);st.session_state.s_playing=False;st.session_state.s_finished=False;st.rerun()
            with pc5:
                if st.button("⏭",key="btn_last"): st.session_state.s_idx=len(EVENTS)-1;st.session_state.s_playing=False;st.session_state.s_finished=False;st.rerun()

    # ── RIGHT: Details ──
    with col_detail:
        st.markdown('<div class="panel-lbl">⬡ Event Details</div>', unsafe_allow_html=True)
        c_hex,c_bg,c_bd = TYPE_COLORS.get(ev["type"],("#aaa","rgba(170,170,170,.1)","rgba(170,170,170,.3)"))
        em = TYPE_EMOJI.get(ev["type"],"●")
        st.markdown(f"""<div class="detail-hero"><div class="d-badge" style="background:{c_bg};border:1px solid {c_bd};color:{c_hex}">{em}&nbsp;{ev['type']}</div><div class="d-year">{ev['year']}</div><div class="d-name">{ev['name']}</div><div style="font-family:'DM Mono',monospace;font-size:.58rem;color:#405570;margin-bottom:.55rem;letter-spacing:.08em">📍 {ev['region_name']}</div><div class="d-desc">{ev['description']}</div></div>""", unsafe_allow_html=True)
        max_d=max(e["deaths"] for e in EVENTS); max_a=max(e["affected_M"] for e in EVENTS); max_dm=max(e["damage_B"] for e in EVENTS)
        st.markdown(f"""<div class="stat-grid"><div class="stat-card"><span class="stat-val" style="color:{c_hex}">{fmt(ev['deaths'])}</span><span class="stat-lbl">Deaths</span></div><div class="stat-card"><span class="stat-val" style="color:#f59e0b">${ev['damage_B']:.0f}B</span><span class="stat-lbl">Economic Damage</span></div><div class="stat-card"><span class="stat-val" style="color:#34d399">{ev['affected_M']:.1f}M</span><span class="stat-lbl">People Affected</span></div><div class="stat-card"><span class="stat-val" style="color:#f87171">+{ev['temp_anom']:.2f}°C</span><span class="stat-lbl">Temp Anomaly</span></div></div>""", unsafe_allow_html=True)
        zoom_status="🔍 ZOOMED" if st.session_state.s_zoomed else "🌐 Globe"
        st.markdown(f"""<div class="coord-row"><div class="coord-chip">LAT {ev['lat']:+.1f}°</div><div class="coord-chip">LON {ev['lon']:+.1f}°</div><div class="coord-chip">{ev['month']}</div><div class="coord-chip" style="color:{'#34d399' if st.session_state.s_zoomed else '#405570'}">{zoom_status}</div></div>""", unsafe_allow_html=True)
        st.markdown('<div class="sec-title">Relative Impact Scale</div>', unsafe_allow_html=True)
        bars_html=""
        for label,frac,col in [("Human Toll",ev["deaths"]/max_d,c_hex),("People Affected",ev["affected_M"]/max_a,"#34d399"),("Economic Loss",ev["damage_B"]/max_dm,"#f59e0b"),("Climate Signal",min(ev["temp_anom"]/1.5,1),"#f87171")]:
            pct2=max(4,int(frac*100))
            bars_html+=f'<div class="imp-wrap"><div class="imp-lbl"><span>{label}</span><span style="color:{col}">{pct2}%</span></div><div class="imp-track"><div class="imp-fill" style="width:{pct2}%;background:linear-gradient(90deg,{col},{col}88)"></div></div></div>'
        st.markdown(bars_html, unsafe_allow_html=True)

    # ── Auto-play ──
    if st.session_state.s_playing:
        if st.session_state.s_idx < len(EVENTS)-1:
            time.sleep(2.2)
            st.session_state.s_idx += 1
            st.rerun()
        else:
            st.session_state.s_playing=False; st.session_state.s_finished=True; st.rerun()
