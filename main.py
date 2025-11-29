import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Delivery Dashboard", layout="wide")

# --- CARGA DE DATOS ---
@st.cache_data
def load_data():
    # Asegúrate que el CSV está en la misma carpeta
    df = pd.read_csv("Food_Delivery_Route_Efficiency_Dataset.csv")
    return df

df = load_data()

st.title("🛵 Dashboard de Operaciones de Delivery")
st.markdown("Análisis de tiempos, rutas y flota utilizando **Matplotlib** puro.")

# --- SIDEBAR: FILTROS GLOBALES ---
with st.sidebar:
    st.header("🎛️ Filtros Globales")
    
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
        st.warning("⚠️ El inicio y fin del rango no pueden ser iguales.")
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
tab1, tab2, tab3 = st.tabs(["📊 Visión General", "🚀 Flota y Vehículos", "📍 Zonas y Rutas"])

# === PESTAÑA 1: VISIÓN GENERAL ===
with tab1:
    # 4. Columns y 5. Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Órdenes", len(df_filtered))
    c2.metric("Tiempo Promedio", f"{df_filtered['delivery_time_min'].mean():.1f} min")
    c3.metric("Distancia Promedio", f"{df_filtered['distance_km'].mean():.1f} km")
    
    st.divider()
    
    col_izq, col_der = st.columns(2)
    
    # --- GRÁFICO 1: PIE CHART (Vehículos Populares) ---
    with col_izq:
        st.subheader("🚗 Popularidad de Vehículos")
        if not df_filtered.empty:
            counts = df_filtered['delivery_mode'].value_counts()
            
            fig1, ax1 = plt.subplots()
            # Gráfico de torta simple
            ax1.pie(counts, labels=counts.index, autopct='%1.1f%%', startangle=90, 
                    colors=['#ff9999','#66b3ff','#99ff99','#ffcc99'])
            st.pyplot(fig1)
        else:
            st.info("No hay datos disponibles.")

    # --- GRÁFICO 2: BAR CHART HORIZONTAL (Tiempo vs Clima) ---
    with col_der:
        st.subheader("⛈️ Tiempo Promedio por Clima")
        if not df_filtered.empty:
            # Agrupamos por clima y sacamos promedio de tiempo
            df_weather = df_filtered.groupby('weather')['delivery_time_min'].mean().sort_values()
            
            fig2, ax2 = plt.subplots()
            ax2.barh(df_weather.index, df_weather.values, color='teal')
            ax2.set_xlabel("Minutos Promedio")
            st.pyplot(fig2)

# === PESTAÑA 2: FLOTA (Diagrama de Caja Interactivo) ===
with tab2:
    st.markdown("### Rendimiento por Vehículo en Zonas Específicas")
    
    # 6. Selectbox (Interacción para elegir Zona)
    zonas = df['restaurant_zone'].unique()
    zona_sel = st.selectbox("Selecciona Zona de Restaurante:", zones)
    
    # Filtramos datos SOLO para esa zona
    df_zona = df_filtered[df_filtered['restaurant_zone'] == zona_sel]
    
    # --- GRÁFICO 3: BOX PLOT (Matplotlib Puro) ---
    if not df_zona.empty:
        # Preparamos los datos: Matplotlib necesita una lista de arrays, uno por cada vehículo
        vehiculos_en_zona = df_zona['delivery_mode'].unique()
        datos_para_box = []
        labels_box = []
        
        for v in vehiculos_en_zona:
            # Extraemos los tiempos solo para ese vehículo en esa zona
            tiempos = df_zona[df_zona['delivery_mode'] == v]['delivery_time_min']
            datos_para_box.append(tiempos)
            labels_box.append(v)
            
        fig3, ax3 = plt.subplots(figsize=(8, 5))
        # Creamos el boxplot
        ax3.boxplot(datos_para_box, labels=labels_box, patch_artist=True)
        
        ax3.set_title(f"Variabilidad de Tiempos en {zona_sel}")
        ax3.set_ylabel("Tiempo (min)")
        ax3.set_xlabel("Tipo de Vehículo")
        ax3.grid(True, linestyle='--', alpha=0.3)
        
        st.pyplot(fig3)
        st.caption("La línea naranja dentro de la caja indica el tiempo mediano.")
    else:
        st.warning(f"No hay envíos en la zona {zona_sel} con los filtros actuales.")

# === PESTAÑA 3: RUTAS (Scatter Interactivo) ===
with tab3:
    st.subheader("⏱️ Relación Distancia vs. Tiempo")
    
    # 7. Radio (Interacción para elegir color)
    criterio = st.radio(
        "Colorear puntos por:",
        ["Nivel de Tráfico", "Tipo de Vehículo"],
        horizontal=True
    )
    
    # Mapeamos la opción del usuario al nombre real de la columna
    col_map = {"Nivel de Tráfico": "traffic_level", "Tipo de Vehículo": "delivery_mode"}
    columna_elegida = col_map[criterio]
    
    # --- GRÁFICO 4: SCATTER PLOT (Con loop para colores) ---
    if not df_filtered.empty:
        fig4, ax4 = plt.subplots(figsize=(9, 6))
        
        # Para colorear por grupos en matplotlib puro, iteramos sobre los grupos
        # Esto reemplaza el 'hue' de seaborn
        grupos = df_filtered.groupby(columna_elegida)
        
        for nombre, grupo in grupos:
            ax4.scatter(grupo['distance_km'], grupo['delivery_time_min'], label=nombre, alpha=0.7)
            
        ax4.set_xlabel("Distancia (km)")
        ax4.set_ylabel("Tiempo de Entrega (min)")
        ax4.legend(title=criterio) # Muestra la leyenda automática
        ax4.grid(True, alpha=0.3)
        
        st.pyplot(fig4)
    
    st.divider()
    
    col_z1, col_z2 = st.columns(2)
    
    # --- GRÁFICO 5: BAR PLOT (Pedidos por Zona Cliente) ---
    with col_z1:
        st.subheader("🏠 Pedidos por Zona (Cliente)")
        # Contamos cuántos pedidos hay por zona
        conteo_clientes = df_filtered['customer_zone'].value_counts()
        
        fig5, ax5 = plt.subplots()
        ax5.bar(conteo_clientes.index, conteo_clientes.values, color='salmon')
        ax5.set_ylabel("Cantidad")
        # Rotamos las etiquetas si son muy largas
        plt.setp(ax5.get_xticklabels(), rotation=45)
        st.pyplot(fig5)
        
    # --- GRÁFICO 6: BAR PLOT (Pedidos por Zona Restaurante) ---
    with col_z2:
        st.subheader("🍔 Pedidos por Zona (Restaurante)")
        conteo_rest = df_filtered['restaurant_zone'].value_counts()
        
        fig6, ax6 = plt.subplots()
        ax6.bar(conteo_rest.index, conteo_rest.values, color='lightgreen')
        ax6.set_ylabel("Cantidad")
        plt.setp(ax6.get_xticklabels(), rotation=45)
        st.pyplot(fig6)
