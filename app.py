import streamlit as st
import pandas as pd
import numpy as np
import requests
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import joblib
import os

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Lille Metro Intelligence",
    page_icon="🚇",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;700&display=swap');

:root {
    --bg: #0a0e1a;
    --surface: #111827;
    --surface2: #1a2235;
    --accent: #00d4ff;
    --accent2: #ff6b35;
    --accent3: #7c3aed;
    --text: #e2e8f0;
    --muted: #64748b;
    --success: #10b981;
    --warning: #f59e0b;
    --danger: #ef4444;
    --border: rgba(0,212,255,0.15);
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

.stApp { background-color: var(--bg) !important; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}

/* Header */
.metro-header {
    background: linear-gradient(135deg, #0a0e1a 0%, #111827 50%, #0d1b2e 100%);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 2rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.metro-header::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(0,212,255,0.08) 0%, transparent 70%);
    pointer-events: none;
}
.metro-header h1 {
    font-family: 'Space Mono', monospace !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
    color: var(--accent) !important;
    margin: 0 !important;
    letter-spacing: -1px;
}
.metro-header p {
    color: var(--muted);
    margin: 0.5rem 0 0 0;
    font-size: 0.9rem;
}

/* KPI Cards */
.kpi-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
}
.kpi-card::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0;
    width: 100%; height: 3px;
}
.kpi-card.blue::after  { background: var(--accent); }
.kpi-card.orange::after { background: var(--accent2); }
.kpi-card.purple::after { background: var(--accent3); }
.kpi-card.green::after  { background: var(--success); }

.kpi-label {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: var(--muted);
    margin-bottom: 0.5rem;
}
.kpi-value {
    font-family: 'Space Mono', monospace;
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--text);
    line-height: 1;
}
.kpi-sub {
    font-size: 0.8rem;
    color: var(--muted);
    margin-top: 0.4rem;
}

/* Section titles */
.section-title {
    font-family: 'Space Mono', monospace;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: var(--accent);
    border-left: 3px solid var(--accent);
    padding-left: 0.75rem;
    margin: 1.5rem 0 1rem 0;
}

/* Prediction card */
.pred-card {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
}
.pred-value {
    font-family: 'Space Mono', monospace;
    font-size: 3.5rem;
    font-weight: 700;
    line-height: 1;
}
.pred-label {
    font-size: 0.85rem;
    color: var(--muted);
    margin-top: 0.5rem;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* Level badges */
.level-badge {
    display: inline-block;
    padding: 0.35rem 1rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 0.75rem;
}
.level-low    { background: rgba(16,185,129,0.15); color: #10b981; border: 1px solid rgba(16,185,129,0.3); }
.level-medium { background: rgba(245,158,11,0.15); color: #f59e0b; border: 1px solid rgba(245,158,11,0.3); }
.level-high   { background: rgba(239,68,68,0.15);  color: #ef4444; border: 1px solid rgba(239,68,68,0.3); }

/* Selectbox & inputs */
[data-testid="stSelectbox"] > div > div,
[data-testid="stDateInput"] > div > div,
[data-testid="stSlider"] {
    background: var(--surface2) !important;
    border-color: var(--border) !important;
    color: var(--text) !important;
}

/* Plotly dark bg override */
.js-plotly-plot { border-radius: 12px; overflow: hidden; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }

/* Hide Streamlit branding */
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── Data loading ───────────────────────────────────────────────────────────────
@st.cache_data(ttl=120, show_spinner=False)
def load_vlille():
    url = "https://data.lillemetropole.fr/geoserver/ogc/features/v1/collections/dsp_ilevia:vlille_temps_reel/items"
    try:
        r = requests.get(url, timeout=15)
        data = r.json()
        df = pd.json_normalize([f['properties'] for f in data['features']])
        df = df[df['etat'] == 'EN SERVICE'].copy()
        return df
    except:
        return pd.DataFrame()

@st.cache_data(ttl=300, show_spinner=False)
def load_metro():
    url = "https://data.lillemetropole.fr/geoserver/ogc/features/v1/collections/dsp_ilevia:entree_sortie_metro/items"
    try:
        r = requests.get(url, timeout=15)
        data = r.json()
        df = pd.json_normalize([f['properties'] for f in data['features']])
        return df
    except:
        return pd.DataFrame()

@st.cache_data(ttl=3600, show_spinner=False)
def load_metro_stops():
    url = "https://data.lillemetropole.fr/geoserver/ogc/features/v1/collections/dsp_ilevia:arrets_metro/items?limit=200"
    try:
        r = requests.get(url, timeout=15)
        data = r.json()
        records = []
        for f in data['features']:
            props = f.get('properties', {})
            coords = f.get('geometry', {}).get('coordinates', [None, None])
            records.append({
                'nom': props.get('libelle_station') or props.get('nom') or props.get('name'),
                'lon': coords[0],
                'lat': coords[1],
            })
        return pd.DataFrame(records).dropna()
    except:
        return pd.DataFrame()

# ── Model loading ─────────────────────────────────────────────────────────────
@st.cache_resource
def load_model():
    model_path   = "models/final_xgboost_model.pkl"
    feature_path = "models/feature_columns.pkl"
    if os.path.exists(model_path) and os.path.exists(feature_path):
        model    = joblib.load(model_path)
        features = joblib.load(feature_path)
        return model, features
    return None, None

ml_model, ml_features = load_model()
MODEL_AVAILABLE = ml_model is not None

def predict_with_model(station, hour, day_of_week, is_holiday=0, temp=10.0, precip=0.0, df_metro_ref=None):
    """Predict using the trained XGBoost model."""
    # Build station_id from category codes
    station_id = 0
    if df_metro_ref is not None and not df_metro_ref.empty and 'libelle_station' in df_metro_ref.columns:
        cat = df_metro_ref['libelle_station'].astype('category')
        mapping = dict(zip(cat.cat.categories, cat.cat.codes))
        station_id = int(mapping.get(station, 0))

    row = pd.DataFrame([{col: 0 for col in ml_features}])
    row['station_id']    = station_id
    row['hour']          = hour
    row['day_of_week']   = day_of_week
    row['is_holiday']    = is_holiday
    row['temp_mean']     = temp
    row['precipitation'] = precip
    row['is_weekend']    = 1 if day_of_week >= 5 else 0
    row['month']         = pd.Timestamp.now().month
    row['hour_sin']      = np.sin(2 * np.pi * hour / 24)
    row['hour_cos']      = np.cos(2 * np.pi * hour / 24)
    row['dow_sin']       = np.sin(2 * np.pi * day_of_week / 7)
    row['dow_cos']       = np.cos(2 * np.pi * day_of_week / 7)
    row['is_peak_hour']  = 1 if hour in [7, 8, 9, 16, 17, 18] else 0
    row['hour_holiday']  = hour * is_holiday
    row['temp_precip']   = temp * precip
    row['temp_holiday']  = temp * is_holiday
    row['peak_holiday']  = row['is_peak_hour'].values[0] * is_holiday
    row['peak_school']   = 0

    pred_log = ml_model.predict(row[ml_features])[0]
    return max(0, int(np.expm1(pred_log)))

def get_congestion_level(score):
    if score < 33:   return "Faible",   "low",    "🟢"
    elif score < 66: return "Modéré",   "medium", "🟡"
    else:            return "Élevé",    "high",   "🔴"

def get_time_category(h):
    if 7 <= h <= 9:    return 'Matin Peak', '#ff6b35'
    elif 16 <= h <= 19: return 'Soir Peak',  '#ff6b35'
    elif 10 <= h <= 15: return 'Milieu Journée', '#00d4ff'
    else:               return 'Nuit/Creux',  '#64748b'

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 1rem 0 1.5rem;'>
        <div style='font-family: Space Mono, monospace; font-size: 1.2rem; color: #00d4ff; font-weight:700;'>🚇 METRO LILLE</div>
        <div style='font-size: 0.75rem; color: #64748b; margin-top: 0.25rem;'>Intelligence Transport</div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        ["📊 Tableau de Bord", "🗺️ Carte Interactive", "🔮 Prévision Affluence", "📈 Analyse Temporelle"],
        label_visibility="collapsed"
    )

    st.markdown("<hr style='border-color: rgba(0,212,255,0.15); margin: 1rem 0;'>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.75rem; color:#64748b; text-transform:uppercase; letter-spacing:1px; margin-bottom:0.5rem;'>Données en temps réel</div>", unsafe_allow_html=True)

    if st.button("🔄 Actualiser", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    now = datetime.now()
    st.markdown(f"<div style='font-size:0.75rem; color:#64748b; margin-top:0.5rem;'>Mis à jour: {now.strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)


# ── Load data ──────────────────────────────────────────────────────────────────
with st.spinner("Chargement des données..."):
    df_vlille = load_vlille()
    df_metro  = load_metro()
    df_stops  = load_metro_stops()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — TABLEAU DE BORD
# ══════════════════════════════════════════════════════════════════════════════
if page == "📊 Tableau de Bord":

    st.markdown("""
    <div class='metro-header'>
        <h1>🚇 Lille Metro Intelligence</h1>
        <p>Analyse en temps réel du réseau de transport métropolitain</p>
    </div>
    """, unsafe_allow_html=True)

    # KPIs
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        n_stations = len(df_vlille) if not df_vlille.empty else "—"
        st.markdown(f"""
        <div class='kpi-card blue'>
            <div class='kpi-label'>Stations V'Lille actives</div>
            <div class='kpi-value'>{n_stations}</div>
            <div class='kpi-sub'>EN SERVICE</div>
        </div>""", unsafe_allow_html=True)

    with col2:
        total_bikes = int(df_vlille['nb_velos_dispo'].sum()) if not df_vlille.empty and 'nb_velos_dispo' in df_vlille.columns else "—"
        st.markdown(f"""
        <div class='kpi-card orange'>
            <div class='kpi-label'>Vélos disponibles</div>
            <div class='kpi-value'>{total_bikes:,}</div>
            <div class='kpi-sub'>Réseau complet</div>
        </div>""", unsafe_allow_html=True)

    with col3:
        total_docks = int(df_vlille['nb_places_dispo'].sum()) if not df_vlille.empty and 'nb_places_dispo' in df_vlille.columns else "—"
        st.markdown(f"""
        <div class='kpi-card purple'>
            <div class='kpi-label'>Places libres</div>
            <div class='kpi-value'>{total_docks:,}</div>
            <div class='kpi-sub'>Pour retourner un vélo</div>
        </div>""", unsafe_allow_html=True)

    with col4:
        hour_now = now.hour
        period, _ = get_time_category(hour_now)[:2], None
        period = get_time_category(hour_now)[0]
        st.markdown(f"""
        <div class='kpi-card green'>
            <div class='kpi-label'>Période actuelle</div>
            <div class='kpi-value' style='font-size:1.2rem; padding-top:0.3rem;'>{period}</div>
            <div class='kpi-sub'>{now.strftime('%H:%M')} — {now.strftime('%A')}</div>
        </div>""", unsafe_allow_html=True)

    # Charts row
    if not df_vlille.empty and 'nb_velos_dispo' in df_vlille.columns:
        st.markdown("<div class='section-title'>Distribution des vélos par station</div>", unsafe_allow_html=True)

        col_a, col_b = st.columns([3, 2])

        with col_a:
            df_top = df_vlille.nlargest(15, 'nb_velos_dispo')[['nom', 'nb_velos_dispo']].copy()
            fig = px.bar(
                df_top, x='nb_velos_dispo', y='nom', orientation='h',
                color='nb_velos_dispo',
                color_continuous_scale=[[0,'#1a2235'],[0.5,'#0077aa'],[1,'#00d4ff']],
                labels={'nb_velos_dispo': 'Vélos dispo', 'nom': ''}
            )
            fig.update_layout(
                plot_bgcolor='#111827', paper_bgcolor='#111827',
                font_color='#e2e8f0', height=380,
                coloraxis_showscale=False,
                margin=dict(l=10, r=10, t=10, b=10),
                yaxis=dict(tickfont=dict(size=11)),
                xaxis=dict(gridcolor='rgba(255,255,255,0.05)')
            )
            fig.update_traces(marker_line_width=0)
            st.plotly_chart(fig, use_container_width=True)

        with col_b:
            bins = [0, 5, 15, 30, 100]
            labels_bin = ['Vide (0-5)', 'Faible (6-15)', 'Moyen (16-30)', 'Plein (31+)']
            df_vlille['cat'] = pd.cut(df_vlille['nb_velos_dispo'], bins=bins, labels=labels_bin)
            cat_counts = df_vlille['cat'].value_counts()

            fig2 = go.Figure(go.Pie(
                labels=cat_counts.index,
                values=cat_counts.values,
                hole=0.6,
                marker_colors=['#ef4444','#f59e0b','#00d4ff','#10b981'],
                textfont_size=12,
            ))
            fig2.update_layout(
                plot_bgcolor='#111827', paper_bgcolor='#111827',
                font_color='#e2e8f0', height=380,
                showlegend=True,
                legend=dict(font=dict(size=11), bgcolor='rgba(0,0,0,0)'),
                margin=dict(l=10, r=10, t=30, b=10),
                annotations=[dict(text='Stations', x=0.5, y=0.5,
                                  font=dict(size=13, color='#64748b'), showarrow=False)]
            )
            st.plotly_chart(fig2, use_container_width=True)

    # Metro traffic if available
    if not df_metro.empty and 'nombre_entree_heure' in df_metro.columns:
        st.markdown("<div class='section-title'>Trafic Metro par station (Top 10)</div>", unsafe_allow_html=True)
        df_metro['nombre_entree_heure'] = pd.to_numeric(df_metro['nombre_entree_heure'], errors='coerce')
        df_top_metro = df_metro.groupby('libelle_station')['nombre_entree_heure'].mean().nlargest(10).reset_index()
        fig3 = px.bar(
            df_top_metro, x='libelle_station', y='nombre_entree_heure',
            color='nombre_entree_heure',
            color_continuous_scale=[[0,'#1a2235'],[0.5,'#7c3aed'],[1,'#a855f7']],
            labels={'libelle_station': '', 'nombre_entree_heure': 'Entrées/heure (moy.)'}
        )
        fig3.update_layout(
            plot_bgcolor='#111827', paper_bgcolor='#111827',
            font_color='#e2e8f0', height=320,
            coloraxis_showscale=False,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(tickangle=-30, tickfont=dict(size=11)),
            yaxis=dict(gridcolor='rgba(255,255,255,0.05)')
        )
        fig3.update_traces(marker_line_width=0)
        st.plotly_chart(fig3, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — CARTE INTERACTIVE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🗺️ Carte Interactive":

    st.markdown("<div class='section-title'>Carte du Réseau — Lille Métropole</div>", unsafe_allow_html=True)

    map_type = st.radio("Afficher", ["🚲 Stations V'Lille", "🚇 Arrêts Métro", "🗺️ Les deux"], horizontal=True)

    m = folium.Map(location=[50.629, 3.057], zoom_start=13,
                   tiles='CartoDB dark_matter')

    if map_type in ["🚲 Stations V'Lille", "🗺️ Les deux"] and not df_vlille.empty:
        for _, row in df_vlille.iterrows():
            try:
                lat, lon = float(row['y']), float(row['x'])
                bikes = int(row.get('nb_velos_dispo', 0))
                docks = int(row.get('nb_places_dispo', 0))
                color = '#10b981' if bikes > 5 else '#f59e0b' if bikes > 0 else '#ef4444'
                folium.CircleMarker(
                    location=[lat, lon], radius=6,
                    color=color, fill=True, fill_color=color, fill_opacity=0.8,
                    popup=folium.Popup(
                        f"<b>{row.get('nom','?')}</b><br>🚲 Vélos: {bikes}<br>🅿️ Places: {docks}",
                        max_width=200
                    )
                ).add_to(m)
            except: pass

    if map_type in ["🚇 Arrêts Métro", "🗺️ Les deux"] and not df_stops.empty:
        for _, row in df_stops.iterrows():
            try:
                folium.Marker(
                    location=[float(row['lat']), float(row['lon'])],
                    popup=folium.Popup(f"<b>🚇 {row['nom']}</b>", max_width=200),
                    icon=folium.Icon(color='blue', icon='subway', prefix='fa')
                ).add_to(m)
            except: pass

    st_folium(m, width=None, height=520)

    if not df_vlille.empty:
        col1, col2, col3 = st.columns(3)
        col1.markdown("<span style='color:#10b981'>●</span> Disponible (>5 vélos)", unsafe_allow_html=True)
        col2.markdown("<span style='color:#f59e0b'>●</span> Limité (1-5 vélos)", unsafe_allow_html=True)
        col3.markdown("<span style='color:#ef4444'>●</span> Vide (0 vélo)", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — PRÉVISION AFFLUENCE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔮 Prévision Affluence":

    st.markdown("<div class='section-title'>Prévision d'affluence — Simulateur</div>", unsafe_allow_html=True)

    # Get station list
    stations = []
    if not df_metro.empty and 'libelle_station' in df_metro.columns:
        stations = sorted(df_metro['libelle_station'].dropna().unique().tolist())
    if not stations:
        stations = ["Gare Lille-Flandres", "République Beaux-Arts", "Rihour",
                    "Grand Palais", "Euralille", "Gare Lille-Europe",
                    "Mairie de Lille", "Saint-Philibert", "4 Cantons"]

    # Model status banner
    if MODEL_AVAILABLE:
        st.markdown("<div style='background:rgba(16,185,129,0.1); border:1px solid rgba(16,185,129,0.3); border-radius:8px; padding:0.5rem 1rem; margin-bottom:1rem; font-size:0.85rem; color:#10b981;'>✅ Modèle XGBoost chargé — R² = 0.8916</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='background:rgba(245,158,11,0.1); border:1px solid rgba(245,158,11,0.3); border-radius:8px; padding:0.5rem 1rem; margin-bottom:1rem; font-size:0.85rem; color:#f59e0b;'>⚠️ Modèle non trouvé — simulation de secours activée</div>", unsafe_allow_html=True)

    col_in1, col_in2 = st.columns(2)
    with col_in1:
        station      = st.selectbox("🚇 Station", stations)
        selected_date = st.date_input("📅 Date", value=date.today())

    with col_in2:
        hour         = st.slider("🕐 Heure", 0, 23, datetime.now().hour, format="%dh00")
        day_names    = ['Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi','Dimanche']
        day_of_week  = selected_date.weekday()
        st.markdown(f"<div style='background:var(--surface2); border:1px solid var(--border); border-radius:8px; padding:0.75rem 1rem; margin-top:0.5rem;'>📆 Jour: <b>{day_names[day_of_week]}</b></div>", unsafe_allow_html=True)

    # Extra inputs (collapsible)
    with st.expander("⚙️ Paramètres avancés"):
        col_a, col_b, col_c = st.columns(3)
        temp       = col_a.number_input("🌡️ Température (°C)", -5.0, 35.0, 10.0, 0.5)
        precip     = col_b.number_input("🌧️ Précipitations (mm)", 0.0, 50.0, 0.0, 0.5)
        is_holiday = int(col_c.checkbox("🎉 Jour férié"))

    period_label, period_color = get_time_category(hour)[:2]

    # ── Prediction ────────────────────────────────────────────────────────────
    if MODEL_AVAILABLE:
        predicted = predict_with_model(
            station, hour, day_of_week, is_holiday, temp, precip, df_metro
        )
    else:
        base_traffic = {
            0:30,1:15,2:10,3:8,4:20,5:80,6:180,
            7:450,8:520,9:380,10:280,11:260,12:300,
            13:290,14:260,15:290,16:410,17:490,18:460,
            19:320,20:240,21:180,22:130,23:70
        }
        weekend_factor = 0.55 if day_of_week >= 5 else 1.0
        station_factor = (hash(station) % 100) / 100 * 0.8 + 0.6
        predicted = int(base_traffic.get(hour, 200) * weekend_factor * station_factor)

    congestion_score = min(100, int((predicted / 550) * 100))
    level_label, level_class, level_emoji = get_congestion_level(congestion_score)

    # ── Display results ───────────────────────────────────────────────────────
    st.markdown("<div class='section-title'>Résultat de la prévision</div>", unsafe_allow_html=True)

    col_r1, col_r2, col_r3 = st.columns([2, 2, 3])

    with col_r1:
        st.markdown(f"""
        <div class='pred-card'>
            <div class='pred-value' style='color:{period_color}'>{predicted}</div>
            <div class='pred-label'>Entrées / heure</div>
            <div class='level-badge level-{level_class}'>{level_emoji} {level_label}</div>
        </div>""", unsafe_allow_html=True)

    with col_r2:
        st.markdown(f"""
        <div class='pred-card'>
            <div class='pred-value' style='color:var(--accent); font-size:2.5rem'>{congestion_score}%</div>
            <div class='pred-label'>Score d'affluence</div>
            <div class='kpi-sub' style='margin-top:0.5rem'>{period_label}</div>
        </div>""", unsafe_allow_html=True)

    with col_r3:
        # 24h forecast curve — use model if available
        hours_range = list(range(24))
        if MODEL_AVAILABLE:
            forecast = [
                predict_with_model(station, h, day_of_week, is_holiday, temp, precip, df_metro)
                for h in hours_range
            ]
        else:
            wf = 0.55 if day_of_week >= 5 else 1.0
            sf = (hash(station) % 100) / 100 * 0.8 + 0.6
            base = {0:30,1:15,2:10,3:8,4:20,5:80,6:180,7:450,8:520,9:380,10:280,11:260,
                    12:300,13:290,14:260,15:290,16:410,17:490,18:460,19:320,20:240,21:180,22:130,23:70}
            forecast = [int(base.get(h, 200) * wf * sf) for h in hours_range]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hours_range, y=forecast, fill='tozeroy',
            fillcolor='rgba(0,212,255,0.08)',
            line=dict(color='#00d4ff', width=2), name='Prévision'
        ))
        fig.add_vline(x=hour, line_dash="dash", line_color="#ff6b35", line_width=2)
        fig.add_annotation(x=hour, y=max(forecast)*0.95 if max(forecast)>0 else 1,
                           text=f"{hour}h", showarrow=False,
                           font=dict(color='#ff6b35', size=11))
        fig.update_layout(
            plot_bgcolor='#111827', paper_bgcolor='#1a2235',
            font_color='#e2e8f0', height=200,
            margin=dict(l=10, r=10, t=10, b=10), showlegend=False,
            xaxis=dict(tickvals=list(range(0,24,3)),
                       ticktext=[f"{h}h" for h in range(0,24,3)],
                       gridcolor='rgba(255,255,255,0.05)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.05)')
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── Recommendations ───────────────────────────────────────────────────────
    st.markdown("<div class='section-title'>Recommandations</div>", unsafe_allow_html=True)
    if congestion_score < 33:
        st.success(f"✅ Affluence faible à {hour}h — Voyage confortable recommandé")
    elif congestion_score < 66:
        st.warning(f"⚠️ Affluence modérée — Prévoyez quelques minutes supplémentaires")
    else:
        st.error(f"🔴 Forte affluence — Envisagez de décaler votre trajet de 30-60 min")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — ANALYSE TEMPORELLE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📈 Analyse Temporelle":

    st.markdown("<div class='section-title'>Patterns temporels du trafic</div>", unsafe_allow_html=True)

    if not df_metro.empty and 'nombre_entree_heure' in df_metro.columns and 'heure_debut' in df_metro.columns:
        df_temp = df_metro.copy()
        df_temp['nombre_entree_heure'] = pd.to_numeric(df_temp['nombre_entree_heure'], errors='coerce')

        _h = df_temp['heure_debut'].astype(str).str.replace('Z','',regex=False)
        h1 = pd.to_datetime(_h, format='%H:%M:%S', errors='coerce').dt.hour
        h2 = pd.to_datetime(_h, errors='coerce').dt.hour
        df_temp['hour'] = h1.fillna(h2).fillna(0).astype(int)

        # By hour
        hourly = df_temp.groupby('hour')['nombre_entree_heure'].mean().reset_index()
        hourly.columns = ['hour', 'mean_entries']

        fig_h = go.Figure()
        colors = ['#ff6b35' if (7<=h<=9 or 16<=h<=19) else '#00d4ff' if 10<=h<=15 else '#64748b'
                  for h in hourly['hour']]
        fig_h.add_trace(go.Bar(
            x=hourly['hour'], y=hourly['mean_entries'],
            marker_color=colors, name='Entrées moy.'
        ))
        fig_h.update_layout(
            title=dict(text="Trafic moyen par heure", font=dict(color='#e2e8f0', size=14)),
            plot_bgcolor='#111827', paper_bgcolor='#111827',
            font_color='#e2e8f0', height=320,
            margin=dict(l=10, r=10, t=40, b=10),
            xaxis=dict(tickvals=list(range(0,24,2)),
                       ticktext=[f"{h}h" for h in range(0,24,2)],
                       gridcolor='rgba(255,255,255,0.05)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.05)')
        )
        st.plotly_chart(fig_h, use_container_width=True)

        # By period
        def cat(h):
            if 7<=h<=9:    return 'Matin Peak'
            elif 16<=h<=19: return 'Soir Peak'
            elif 10<=h<=15: return 'Milieu Journée'
            else:           return 'Nuit/Creux'

        df_temp['period'] = df_temp['hour'].apply(cat)
        period_stats = df_temp.groupby('period')['nombre_entree_heure'].sum().reset_index()
        order = ['Matin Peak', 'Milieu Journée', 'Soir Peak', 'Nuit/Creux']
        period_stats['period'] = pd.Categorical(period_stats['period'], categories=order, ordered=True)
        period_stats = period_stats.sort_values('period')

        col1, col2 = st.columns(2)

        with col1:
            fig_p = px.bar(
                period_stats, x='period', y='nombre_entree_heure',
                color='period',
                color_discrete_map={
                    'Matin Peak':'#ff6b35','Soir Peak':'#ff6b35',
                    'Milieu Journée':'#00d4ff','Nuit/Creux':'#64748b'
                },
                labels={'period':'Période','nombre_entree_heure':'Total entrées'}
            )
            fig_p.update_layout(
                title=dict(text="Total par période", font=dict(color='#e2e8f0', size=14)),
                plot_bgcolor='#111827', paper_bgcolor='#111827',
                font_color='#e2e8f0', height=300, showlegend=False,
                margin=dict(l=10, r=10, t=40, b=10),
                xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.05)')
            )
            st.plotly_chart(fig_p, use_container_width=True)

        with col2:
            if 'libelle_station' in df_temp.columns:
                top_stations = df_temp.groupby('libelle_station')['nombre_entree_heure'].mean().nlargest(8).reset_index()
                fig_s = px.bar(
                    top_stations, x='nombre_entree_heure', y='libelle_station',
                    orientation='h',
                    color='nombre_entree_heure',
                    color_continuous_scale=[[0,'#1a2235'],[1,'#7c3aed']],
                    labels={'libelle_station':'', 'nombre_entree_heure':'Moy. entrées/h'}
                )
                fig_s.update_layout(
                    title=dict(text="Top stations (affluence moy.)", font=dict(color='#e2e8f0', size=14)),
                    plot_bgcolor='#111827', paper_bgcolor='#111827',
                    font_color='#e2e8f0', height=300, coloraxis_showscale=False,
                    margin=dict(l=10, r=10, t=40, b=10),
                    xaxis=dict(gridcolor='rgba(255,255,255,0.05)')
                )
                st.plotly_chart(fig_s, use_container_width=True)
    else:
        st.info("Les données temporelles du métro ne sont pas disponibles pour le moment.")

    # Legend
    st.markdown("""
    <div style='display:flex; gap:1.5rem; margin-top:0.5rem;'>
        <span><span style='color:#ff6b35'>■</span> Heures de pointe</span>
        <span><span style='color:#00d4ff'>■</span> Milieu de journée</span>
        <span><span style='color:#64748b'>■</span> Heures creuses</span>
    </div>
    """, unsafe_allow_html=True)
