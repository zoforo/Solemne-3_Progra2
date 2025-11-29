import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Delivery Dashboard", layout="wide")

# --- CARGA DE DATOS ---
@st.cache_data
def load_data():
    # Asegúrate de que el CSV está en la misma carpeta
    df = pd.read_csv("Food_Delivery_Route_Efficiency_Dataset.csv")
    return df

df = load_data()

# --- TÍTULO PRINCIPAL ---
st.title("Dashboard de Operaciones de Delivery")
st.markdown("Análisis de tiempos, rutas y flota utilizando **Matplotlib** puro.")

# --- SIDEBAR: FILTROS GLOBALES ---
with st.sidebar:
    st.header("Filtros Globales")
    
    # 1. Multiselect (Filtro Tráfico)
    trafico_filter = st.multiselect(
        "Nivel de Tráfico:",
        options=["Low", "Medium", "High"],
        default=["Low", "Medium", "High"]
    )
    
    # 2. Slider (Filtro Distancia)
    min_dist, max_dist = int(df['distance_km'].min()), int(df['distance_km'].max())
    dist_range = st.slider(
        "Rango de Distancia (km):",
        min_value=min_dist,
        max_value=max_dist,
        value=(min_dist, max_dist)
    )
    
    # Validación del Slider (Solución al error 0-0)
    if dist_range[0] == dist_range[1]:
        st.warning("El inicio y fin del rango no pueden ser iguales.")
        st.stop()

    st.info("Filtra los datos para actualizar todos los gráficos.")

# Aplicar filtros al DataFrame
df_filtered = df[
    (df['traffic_level'].isin(trafico_filter)) &
    (df['distance_km'] >= dist_range[0]) &
    (df['distance_km'] <= dist_range[1])
]

# --- PESTAÑAS PRINCIPALES ---
# 3. Tabs
tab1, tab2, tab3 = st.tabs(["Visión General", "Flota y Vehículos", "Zonas y Rutas"])

# === PESTAÑA 1: VISIÓN GENERAL ===
with tab1:
    # 4. Columns y 5. Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Órdenes", len(df_filtered))
    c2.metric("Tiempo Promedio", f"{df_filtered['delivery_time_min'].mean():.1f} min")
    c3.metric("Distancia Promedio", f"{df_filtered['distance_km'].mean():.1f
