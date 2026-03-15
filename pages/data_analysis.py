import streamlit as st
import xarray as xr
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import os

# ── Plotly dark template ───────────────────────────────────────────────────────
PLOTLY_TEMPLATE = dict(
    layout=dict(
        paper_bgcolor="#0d1117",
        plot_bgcolor="#161b22",
        font=dict(family="DM Sans", color="#e6edf3", size=13),
        xaxis=dict(gridcolor="#21262d", linecolor="#30363d", zerolinecolor="#21262d"),
        yaxis=dict(gridcolor="#21262d", linecolor="#30363d", zerolinecolor="#21262d"),
        margin=dict(l=50, r=30, t=50, b=50),
        coloraxis_colorbar=dict(
            bgcolor="#161b22", tickcolor="#8b949e", tickfont=dict(color="#8b949e")
        ),
    )
)

VAR_META = {
    "t2m": {
        "label": "2m Temperature",
        "unit": "°C",
        "colorscale": "RdBu_r",
        "color": "#ff7b72",
        "convert": lambda x: x - 273.15,   # Kelvin → Celsius
    },
    "tp": {
        "label": "Total Precipitation",
        "unit": "mm",
        "colorscale": "Blues",
        "color": "#58a6ff",
        "convert": lambda x: x * 1000,     # metres → mm
    },
}

# ── Data loading ───────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading NetCDF4 datasets…")
def load_data():
    """Load and merge both ERA5 NetCDF4 files."""
    instant_path = "data/data_stream-oper_stepType-instant.nc"
    accum_path   = "data/data_stream-oper_stepType-accum.nc"

    datasets = {}
    errors   = []

    for path, label in [(instant_path, "instant"), (accum_path, "accum")]:
        if os.path.exists(path):
            try:
                ds = xr.open_dataset(path, engine="netcdf4")
                datasets[label] = ds
            except Exception as e:
                errors.append(f"Could not open `{path}`: {e}")
        else:
            errors.append(f"File not found: `{path}`")

    return datasets, errors


def get_available_vars(datasets):
    """Return list of variable keys present across both datasets."""
    found = []
    for key in ["t2m", "tp"]:
        for ds in datasets.values():
            if key in ds.data_vars:
                found.append(key)
                break
    return found


def get_var_da(datasets, var_key):
    """Retrieve a DataArray for a given variable key."""
    for ds in datasets.values():
        if var_key in ds.data_vars:
            return ds[var_key]
    return None


def get_time_dim(da):
    """Return the name of the time dimension (handles 'time', 'valid_time', etc.)."""
    for candidate in ("time", "valid_time"):
        if candidate in da.dims:
            return candidate
    # Fallback: first dimension whose coordinate values are datetime-like
    for dim in da.dims:
        if dim in da.coords:
            try:
                pd.to_datetime(da[dim].values)
                return dim
            except Exception:
                pass
    raise ValueError(f"Cannot find a time dimension in DataArray with dims: {da.dims}")


def get_time_values(da):
    """Return time coordinate values as a pandas DatetimeIndex."""
    time_dim = get_time_dim(da)
    return pd.to_datetime(da[time_dim].values)


def daily_global_mean(da, meta):
    """Compute daily (00:00) global-mean time series, unit-converted."""
    time_dim = get_time_dim(da)
    # Spatial mean over all non-time dims
    da_mean = da.mean(dim=[d for d in da.dims if d != time_dim])
    df = da_mean.to_series().reset_index()
    df.columns = [time_dim, "value"]
    df["value"] = meta["convert"](df["value"])
    df["date"] = pd.to_datetime(df[time_dim]).dt.date
    return df.sort_values("date").reset_index(drop=True)


    # ── Main page entry point ──────────────────────────────────────────────────────
def analysis_page():
    # ── Custom CSS ─────────────────────────────────────────────────────────────
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0d1117;
    color: #f0f6fc;
}
.stApp { background-color: #0d1117; }

h1, h2, h3 {
    font-family: 'Space Mono', monospace;
    color: #58a6ff;
    letter-spacing: -0.5px;
}
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #161b22;
    border-right: 1px solid #30363d;
}
section[data-testid="stSidebar"] h2 { font-size: 0.85rem; color: #c9d1d9; text-transform: uppercase; letter-spacing: 1px; }

/* Metrics */
[data-testid="metric-container"] {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 12px 16px;
}
[data-testid="metric-container"] label { color: #c9d1d9 !important; font-size: 0.75rem !important; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { color: #58a6ff !important; font-family: 'Space Mono', monospace; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap: 8px; background: transparent; border-bottom: 1px solid #30363d; }
.stTabs [data-baseweb="tab"] {
    background: #161b22; border: 1px solid #30363d; border-radius: 6px 6px 0 0;
    color: #8b949e; font-family: 'Space Mono', monospace; font-size: 0.8rem;
}
.stTabs [aria-selected="true"] { background: #1f2937 !important; color: #58a6ff !important; border-color: #58a6ff !important; }

/* Selectbox / multiselect */
.stSelectbox label, .stMultiSelect label, .stDateInput label, .stSlider label { color: #c9d1d9; font-size: 0.8rem; }
div[data-baseweb="select"] > div { background-color: #161b22 !important; border-color: #30363d !important; color: #f0f6fc !important; }

/* Divider */
hr { border-color: #30363d; }

/* Info/warning boxes */
.stAlert { border-radius: 8px; }

.badge {
    display: inline-block; background: #1f3a5f; color: #58a6ff;
    border: 1px solid #30363d; border-radius: 20px;
    padding: 2px 10px; font-size: 0.72rem; font-family: 'Space Mono', monospace;
    margin: 2px 4px;
}
</style>
""", unsafe_allow_html=True)

    # ── App Header ─────────────────────────────────────────────────────────────
    col_title, col_badge = st.columns([5, 1])
    with col_title:
        st.markdown("# 🌍 ERA5 Climate Explorer")
        st.markdown("<p style='color:#c9d1d9;margin-top:-12px;font-size:0.9rem;'>Reanalysis · Jan–Mar 2026 · Daily 00:00 UTC snapshots</p>", unsafe_allow_html=True)
    with col_badge:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<span class="badge">ERA5</span> <span class="badge">NetCDF4</span>', unsafe_allow_html=True)

    st.markdown("---")

    # ── Load data ──────────────────────────────────────────────────────────────
    datasets, load_errors = load_data()

    if load_errors:
        for err in load_errors:
            st.error(f"⚠️ {err}")
        if not datasets:
            st.warning("Place your `.nc` files in the same directory as this script and restart.")
            st.stop()

    available_vars = get_available_vars(datasets)
    if not available_vars:
        st.error("No recognised variables (t2m, tp) found in the loaded files.")
        st.stop()

    # Collect date range from the first available var
    _sample_da = get_var_da(datasets, available_vars[0])
    all_times   = get_time_values(_sample_da)
    all_dates   = sorted(set(all_times.date))
    min_date    = all_dates[0]
    max_date    = all_dates[-1]

    # ── Quick stats ────────────────────────────────────────────────────────────
    stat_cols = st.columns(len(available_vars) * 2)
    col_i = 0
    for vk in available_vars:
        meta = VAR_META[vk]
        da   = get_var_da(datasets, vk)
        vals = meta["convert"](da.values.flatten())
        vals = vals[~np.isnan(vals)]
        stat_cols[col_i].metric(f"{meta['label']} — Min", f"{vals.min():.2f} {meta['unit']}")
        stat_cols[col_i + 1].metric(f"{meta['label']} — Max", f"{vals.max():.2f} {meta['unit']}")
        col_i += 2

    st.markdown("---")

    # ── Tabs ───────────────────────────────────────────────────────────────────
    tab_ts, tab_spatial, tab_temporal = st.tabs(["📈 Time Series", "🗺️ Spatial Heatmap", "⏱️ Temporal (Point)"])


    # ════════════════════════════════════════════════════════════════════════════
    # TAB 1 – TIME SERIES
    # ════════════════════════════════════════════════════════════════════════════
    with tab_ts:
        st.markdown("### Time Series")

        # ── Mode toggle ────────────────────────────────────────────────────────
        ts_mode = st.radio(
            "View mode",
            options=["🌐 Global Mean", "📍 Point Location"],
            horizontal=True,
            key="ts_mode",
        )
        use_point = ts_mode == "📍 Point Location"

        if use_point:
            st.markdown("<p style='color:#c9d1d9;font-size:0.85rem;'>Values at a chosen grid point · 00:00 UTC per day</p>", unsafe_allow_html=True)
        else:
            st.markdown("<p style='color:#c9d1d9;font-size:0.85rem;'>Spatial average over all grid points · 00:00 UTC per day</p>", unsafe_allow_html=True)

        # ── Controls ───────────────────────────────────────────────────────────
        if use_point:
            ctrl_ts1, ctrl_ts2, ctrl_ts3, ctrl_ts4 = st.columns([2, 2, 2, 3])
        else:
            ctrl_ts1, ctrl_ts4 = st.columns([2, 3])

        with ctrl_ts1:
            st.markdown("**Date Range**")
            ts_start = st.date_input(
                "Start date",
                value=min_date,
                min_value=min_date,
                max_value=max_date,
                key="ts_start_main",
            )
            ts_end = st.date_input(
                "End date",
                value=max_date,
                min_value=min_date,
                max_value=max_date,
                key="ts_end_main",
            )
            if ts_start > ts_end:
                st.warning("Start date must be ≤ end date.")
                ts_start, ts_end = min_date, max_date

        if use_point:
            with ctrl_ts2:
                st.markdown("**Location**")
                ts_lat = st.number_input("Latitude  (-90 to 90)",  value=25.3, step=0.5, key="ts_lat")
            with ctrl_ts3:
                st.markdown("&nbsp;", unsafe_allow_html=True)
                ts_lon = st.number_input("Longitude (-180 to 180)", value=82.0, step=0.5, key="ts_lon")

        with ctrl_ts4:
            st.markdown("**Variables**")
            var_labels = {k: VAR_META[k]["label"] for k in available_vars}
            selected_vars_ts = st.multiselect(
                "Time-series variables",
                options=available_vars,
                default=available_vars,
                format_func=lambda k: var_labels[k],
                key="ts_vars_main",
            )

        if not selected_vars_ts:
            st.info("Select at least one variable.")
        else:
            # Build figure — dual y-axis if both vars selected
            dual = len(selected_vars_ts) == 2
            if dual:
                fig = make_subplots(specs=[[{"secondary_y": True}]])
            else:
                fig = go.Figure()

            ts_actual_coords = {}
            for i, vk in enumerate(selected_vars_ts):
                meta = VAR_META[vk]
                da   = get_var_da(datasets, vk)

                if use_point:
                    lat_name = next((d for d in da.dims if "lat" in d.lower()), None)
                    lon_name = next((d for d in da.dims if "lon" in d.lower()), None)
                    if lat_name is None or lon_name is None:
                        st.error(f"Cannot identify lat/lon dimensions for {meta['label']}.")
                        continue
                    da_point = da.sel({lat_name: ts_lat, lon_name: ts_lon}, method="nearest")
                    ts_actual_coords[vk] = (float(da_point[lat_name].values), float(da_point[lon_name].values))
                    time_dim_ts = get_time_dim(da_point)
                    df = da_point.to_series().reset_index()
                    if time_dim_ts in df.columns:
                        df = df.rename(columns={time_dim_ts: "time"})
                    df = df[["time", df.columns[-1]]].copy()
                    df.columns = ["time", "value"]
                    df["value"] = meta["convert"](df["value"])
                    df["date"]  = pd.to_datetime(df["time"]).dt.date
                    df = df[(df["date"] >= ts_start) & (df["date"] <= ts_end)].sort_values("date")
                else:
                    df   = daily_global_mean(da, meta)
                    mask = (df["date"] >= ts_start) & (df["date"] <= ts_end)
                    df   = df[mask]

                trace = go.Scatter(
                    x=df["date"],
                    y=df["value"].round(4),
                    mode="lines+markers",
                    name=f"{meta['label']} ({meta['unit']})",
                    line=dict(color=meta["color"], width=2.5),
                    marker=dict(size=5, color=meta["color"]),
                    hovertemplate=f"<b>{meta['label']}</b><br>Date: %{{x}}<br>Value: %{{y:.3f}} {meta['unit']}<extra></extra>",
                )
                if dual:
                    fig.add_trace(trace, secondary_y=(i == 1))
                else:
                    fig.add_trace(trace)

            # Axes labels
            if dual:
                fig.update_yaxes(title_text=f"{VAR_META[selected_vars_ts[0]]['label']} ({VAR_META[selected_vars_ts[0]]['unit']})", secondary_y=False, gridcolor="#21262d", color=VAR_META[selected_vars_ts[0]]["color"])
                fig.update_yaxes(title_text=f"{VAR_META[selected_vars_ts[1]]['label']} ({VAR_META[selected_vars_ts[1]]['unit']})", secondary_y=True,  gridcolor="#21262d", color=VAR_META[selected_vars_ts[1]]["color"])
            else:
                vk = selected_vars_ts[0]
                fig.update_yaxes(title_text=f"{VAR_META[vk]['label']} ({VAR_META[vk]['unit']})", gridcolor="#21262d")

            fig.update_layout(
                **PLOTLY_TEMPLATE["layout"],
                xaxis_title="Date",
                hovermode="x unified",
                height=450,
                legend=dict(bgcolor="#161b22", bordercolor="#30363d", borderwidth=1, orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            )
            st.plotly_chart(fig, use_container_width=True)

            # Show snapped coordinates in point mode
            if use_point:
                for vk in selected_vars_ts:
                    if vk in ts_actual_coords:
                        meta = VAR_META[vk]
                        alat, alon = ts_actual_coords[vk]
                        st.caption(f"**{meta['label']}** — nearest grid point: {alat:.2f}°N, {alon:.2f}°E")


    # ════════════════════════════════════════════════════════════════════════════
    # TAB 2 – SPATIAL HEATMAP (time fixed, space varies)
    # ════════════════════════════════════════════════════════════════════════════
    with tab_spatial:
        st.markdown("### Spatial Distribution")
        st.markdown("<p style='color:#c9d1d9;font-size:0.85rem;'>Time is fixed — see how a variable varies across the globe on a single day.</p>", unsafe_allow_html=True)

        ctrl_col1, ctrl_col2 = st.columns([2, 3])
        with ctrl_col1:
            heatmap_var = st.selectbox(
                "Variable",
                options=available_vars,
                format_func=lambda k: VAR_META[k]["label"],
                key="hm_var",
            )
        with ctrl_col2:
            selected_heatmap_date = st.date_input(
                "Select date",
                value=min_date,
                min_value=min_date,
                max_value=max_date,
                key="hm_date",
            )

        da   = get_var_da(datasets, heatmap_var)
        meta = VAR_META[heatmap_var]

        # Select time slice
        time_dim   = get_time_dim(da)
        time_match = get_time_values(da)
        idx = np.where(time_match.date == selected_heatmap_date)[0]
        if len(idx) == 0:
            st.warning(f"No data for {selected_heatmap_date}.")
        else:
            da_slice = da.isel({time_dim: idx[0]})
            data_2d  = meta["convert"](da_slice.values)

            # Detect lat/lon dim names
            lat_name = next((d for d in da_slice.dims if "lat" in d.lower()), da_slice.dims[0])
            lon_name = next((d for d in da_slice.dims if "lon" in d.lower()), da_slice.dims[1])

            lats = da_slice[lat_name].values
            lons = da_slice[lon_name].values

            # Ensure 2-D shape (lat x lon)
            if da_slice.dims[0] == lon_name:
                data_2d = data_2d.T

            fig_map = go.Figure(go.Heatmap(
                z=data_2d,
                x=lons,
                y=lats,
                colorscale=meta["colorscale"],
                colorbar=dict(title=meta["unit"], tickfont=dict(color="#8b949e")),
                hovertemplate="Lat: %{y:.2f}°<br>Lon: %{x:.2f}°<br>Value: %{z:.3f} " + meta["unit"] + "<extra></extra>",
            ))
            fig_map.update_layout(
                **PLOTLY_TEMPLATE["layout"],
                title=f"{meta['label']} — {selected_heatmap_date}",
                xaxis_title="Longitude (°E)",
                yaxis_title="Latitude (°N)",
                height=520,
            )
            st.plotly_chart(fig_map, use_container_width=True)

            # Summary stats for this day
            flat = data_2d[~np.isnan(data_2d)]
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Min",  f"{flat.min():.3f} {meta['unit']}")
            c2.metric("Max",  f"{flat.max():.3f} {meta['unit']}")
            c3.metric("Mean", f"{flat.mean():.3f} {meta['unit']}")
            c4.metric("Std",  f"{flat.std():.3f} {meta['unit']}")


    # ════════════════════════════════════════════════════════════════════════════
    # TAB 3 – TEMPORAL (space fixed, time varies)
    # ════════════════════════════════════════════════════════════════════════════
    with tab_temporal:
        st.markdown("### Point Time Series")
        st.markdown("<p style='color:#c9d1d9;font-size:0.85rem;'>Space is fixed — see how one or more variables vary over time at a chosen location.</p>", unsafe_allow_html=True)

        pt_ctrl1, pt_ctrl2, pt_ctrl3 = st.columns([3, 2, 2])
        with pt_ctrl1:
            selected_vars_pt = st.multiselect(
                "Variables",
                options=available_vars,
                default=available_vars,
                format_func=lambda k: VAR_META[k]["label"],
                key="pt_vars",
            )
        with pt_ctrl2:
            lat_val = st.number_input("Latitude  (-90 to 90)",  value=25.3, step=0.5, key="pt_lat")
        with pt_ctrl3:
            lon_val = st.number_input("Longitude (-180 to 180)", value=82.0, step=0.5, key="pt_lon")

        if not selected_vars_pt:
            st.info("Select at least one variable above.")
        else:
            dual_pt = len(selected_vars_pt) == 2
            if dual_pt:
                fig_pt = make_subplots(specs=[[{"secondary_y": True}]])
            else:
                fig_pt = go.Figure()

            actual_coords = {}
            for i, vk in enumerate(selected_vars_pt):
                meta = VAR_META[vk]
                da   = get_var_da(datasets, vk)

                lat_name = next((d for d in da.dims if "lat" in d.lower()), None)
                lon_name = next((d for d in da.dims if "lon" in d.lower()), None)

                if lat_name is None or lon_name is None:
                    st.error(f"Cannot identify lat/lon dimensions for {meta['label']}.")
                    continue

                da_point   = da.sel({lat_name: lat_val, lon_name: lon_val}, method="nearest")
                actual_coords[vk] = (float(da_point[lat_name].values), float(da_point[lon_name].values))

                time_dim_pt = get_time_dim(da_point)
                df_pt = da_point.to_series().reset_index()
                if time_dim_pt in df_pt.columns:
                    df_pt = df_pt.rename(columns={time_dim_pt: "time"})
                df_pt = df_pt[["time", df_pt.columns[-1]]].copy()
                df_pt.columns = ["time", "value"]
                df_pt["value"] = meta["convert"](df_pt["value"])
                df_pt["date"]  = pd.to_datetime(df_pt["time"]).dt.date
                df_pt = df_pt[(df_pt["date"] >= ts_start) & (df_pt["date"] <= ts_end)].sort_values("date")

                df_pt["rolling7"] = df_pt["value"].rolling(7, min_periods=1).mean()

                bar_trace = go.Bar(
                    x=df_pt["date"],
                    y=df_pt["value"].round(4),
                    name=f"{meta['label']} ({meta['unit']})",
                    marker_color=meta["color"],
                    opacity=0.5,
                    hovertemplate=f"Date: %{{x}}<br>{meta['label']}: %{{y:.4f}} {meta['unit']}<extra></extra>",
                )
                line_trace = go.Scatter(
                    x=df_pt["date"],
                    y=df_pt["rolling7"].round(4),
                    name=f"{meta['label']} 7-day mean",
                    mode="lines",
                    line=dict(color=meta["color"], width=2.5, dash="dot"),
                    hovertemplate=f"Date: %{{x}}<br>7-day mean: %{{y:.4f}} {meta['unit']}<extra></extra>",
                )

                if dual_pt:
                    sec = (i == 1)
                    fig_pt.add_trace(bar_trace,  secondary_y=sec)
                    fig_pt.add_trace(line_trace, secondary_y=sec)
                else:
                    fig_pt.add_trace(bar_trace)
                    fig_pt.add_trace(line_trace)

            if dual_pt:
                fig_pt.update_yaxes(title_text=f"{VAR_META[selected_vars_pt[0]]['label']} ({VAR_META[selected_vars_pt[0]]['unit']})", secondary_y=False, gridcolor="#21262d", color=VAR_META[selected_vars_pt[0]]["color"])
                fig_pt.update_yaxes(title_text=f"{VAR_META[selected_vars_pt[1]]['label']} ({VAR_META[selected_vars_pt[1]]['unit']})", secondary_y=True,  gridcolor="#21262d", color=VAR_META[selected_vars_pt[1]]["color"])
            elif selected_vars_pt:
                vk = selected_vars_pt[0]
                fig_pt.update_yaxes(title_text=f"{VAR_META[vk]['label']} ({VAR_META[vk]['unit']})", gridcolor="#21262d")

            fig_pt.update_layout(
                **PLOTLY_TEMPLATE["layout"],
                xaxis_title="Date",
                height=470,
                barmode="overlay",
                hovermode="x unified",
                legend=dict(bgcolor="#161b22", bordercolor="#30363d", borderwidth=1, orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            )
            st.plotly_chart(fig_pt, use_container_width=True)

            # Show snapped coordinates and stats
            for vk in selected_vars_pt:
                if vk in actual_coords:
                    meta = VAR_META[vk]
                    alat, alon = actual_coords[vk]
                    st.caption(f"**{meta['label']}** — nearest grid point: {alat:.2f}°N, {alon:.2f}°E")