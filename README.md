# 🚇 Smart Urban Mobility Predictor — Lille Metro & V'Lille Integration

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red)
![XGBoost](https://img.shields.io/badge/XGBoost-R²%3D0.89-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

> Analyse en temps réel et prévision d'affluence du réseau de transport métropolitain de Lille — métro + vélos partagés V'Lille.

---

## 🌐 Liens

| | Lien |
|--|--|
| 🚀 **Dashboard Live** | [Ouvrir le Dashboard](https://YOUR_APP.streamlit.app) |
| 📓 **Notebook Colab** | [Ouvrir dans Google Colab](https://colab.research.google.com/drive/YOUR_COLAB_ID) |
| 📊 **Données source** | [data.lillemetropole.fr](https://data.lillemetropole.fr) |

---

## 📌 Description du projet

Ce projet combine deux sources de données ouvertes de la Métropole Européenne de Lille :

- **Réseau Métro** — flux de passagers par station et par heure
- **V'Lille** — disponibilité en temps réel des vélos et des bornes

L'objectif est de répondre à trois questions clés :
1. **Où** sont les lacunes de connectivité entre métro et vélos ?
2. **Quand** la demande est-elle la plus élevée ?
3. **Comment** anticiper l'affluence pour mieux planifier les déplacements ?

---

## 🔮 Modèle de prévision

| Paramètre | Valeur |
|-----------|--------|
| Algorithme | XGBoost Regressor |
| Optimisation | Optuna (60 trials) |
| Validation | TimeSeriesSplit (k=5) |
| **R² final** | **0.8916** |
| Features | 22 (heure, station, météo, jours fériés, lag...) |

### Features utilisées
- Temporelles : `hour`, `day_of_week`, `month`, `is_weekend`
- Cycliques : `hour_sin`, `hour_cos`, `dow_sin`, `dow_cos`
- Contextuelles : `is_holiday`, `is_school_holiday`, `is_peak_hour`
- Météo : `temp_mean`, `precipitation`
- Lag : `lag_1h`, `lag_24h`, `rolling_3h`
- Interactions : `peak_holiday`, `temp_precip`, `hour_holiday`

---

## 📊 Dashboard — Pages

| Page | Contenu |
|------|---------|
| 📊 Tableau de Bord | KPIs temps réel + graphiques réseau |
| 🗺️ Carte Interactive | Carte Folium — stations V'Lille + arrêts métro |
| 🔮 Prévision Affluence | Simulateur basé sur le modèle XGBoost |
| 📈 Analyse Temporelle | Patterns horaires et périodiques |

---

## 🛠️ Installation locale

```bash
# 1. Cloner le repository
git clone https://github.com/dagher-h/Smart-Urban-Mobility-Predictor-Lille-Metro-V-Lille-Integration.git
cd Smart-Urban-Mobility-Predictor-Lille-Metro-V-Lille-Integration

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Lancer le dashboard
streamlit run app.py
```

Ouvrir dans le navigateur : `http://localhost:8501`

---

## 📁 Structure du projet

```
├── app.py                        # Dashboard Streamlit
├── requirements.txt              # Dépendances Python
├── models/
│   ├── final_xgboost_model.pkl   # Modèle entraîné (XGBoost)
│   └── feature_columns.pkl       # Liste des features
└── v_lille_metro_clean.ipynb     # Notebook d'analyse complet
```

---

## 📡 Sources de données

| Source | Description | Mise à jour |
|--------|-------------|-------------|
| `dsp_ilevia:vlille_temps_reel` | Disponibilité V'Lille | Toutes les 2 min |
| `dsp_ilevia:entree_sortie_metro` | Flux passagers métro | Historique |
| `dsp_ilevia:arrets_metro` | Coordonnées arrêts | Statique |
| Open-Meteo Archive API | Données météo historiques | Quotidien |

---

## 🧰 Stack technique

| Catégorie | Bibliothèques |
|-----------|--------------|
| Machine Learning | XGBoost, LightGBM, Optuna, Scikit-learn |
| Data | Pandas, NumPy, GeoPandas |
| Visualisation | Plotly, Folium, Seaborn, Matplotlib |
| Dashboard | Streamlit, Streamlit-Folium |
| API | Requests, Open-Meteo |

---

## 👤 Auteur

**dagher-h** — [GitHub](https://github.com/dagher-h)

---

## 📄 Licence

Ce projet est sous licence MIT — données sources sous [Licence Ouverte v2.0](https://data.lillemetropole.fr).
