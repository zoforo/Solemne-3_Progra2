import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns # Usaremos seaborn para facilitar el diagrama de caja

# Configuración de página
st.set_page_config(page_title="Delivery Dashboard Pro", layout="wide")

# --- CARGA DE DATOS ---
@st.cache_data
def load_data():
    df = pd.read_csv("Food_Delivery_Route_Efficiency_Dataset.csv")
    return df

df = load_data()

st.title("🛵 Dashboard de Operaciones de Delivery")
st.markdown("Análisis avanzado de rutas, flota y tiempos de entrega.")

# --- SIDEBAR (FILTROS) ---
with st.sidebar:
    st.header("🎛️ Filtros Globales")
    
    # Filtro de Tráfico
    trafico_filter = st.multiselect(
        "Nivel de Tráfico:",
        options=["Low", "Medium", "High"],
        default=["Low", "Medium", "High"]
    )
    
    # Filtro de Distancia (CON CORRECCIÓN DE ERROR)
    min_dist, max_dist = int(df['distance_km'].min()), int(df['distance_km'].max())
    dist_range = st.slider(
        "Rango de Distancia (km):",
        min_value=min_dist,
        max_value=max_dist,
        value=(min_dist, max_dist)
    )
    
    # Validación para evitar error de rango 0-0
    if dist_range[0] == dist_range[1]:
        st.warning("⚠️ El inicio y fin del rango no pueden ser iguales.")
        st.stop()

    st.info("Estos filtros afectan a TODAS las pestañas.")

# Aplicar filtros
df_filtered = df[
    (df['traffic_level'].isin(trafico_filter)) &
    (df['distance_km'] >= dist_range[0]) &
    (df['distance_km'] <= dist_range[1])
]

# --- PESTAÑAS ---
tab1, tab2, tab3 = st.tabs(["📊 Visión General", "🚀 Flota y Vehículos", "📍 Zonas y Rutas"])

# === PESTAÑA 1: VISIÓN GENERAL Y CLIMA ===
with tab1:
    # Métricas
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Órdenes", len(df_filtered))
    c2.metric("Tiempo Promedio", f"{df_filtered['delivery_time_min'].mean():.1f} min")
    c3.metric("Distancia Promedio", f"{df_filtered['distance_km'].mean():.1f} km")
    
    st.divider()
    
    col_izq, col_der = st.columns(2)
    
    # IMPLEMENTACIÓN IDEA #4: Vehículos más populares (Gráfico de Torta)
    with col_izq:
        st.subheader("🚗 Popularidad de Vehículos")
        if not df_filtered.empty:
            vehiculos_counts = df_filtered['delivery_mode'].value_counts()
            fig1, ax1 = plt.subplots()
            ax1.pie(vehiculos_counts, labels=vehiculos_counts.index, autopct='%1.1f%%', startangle=140, colors=sns.color_palette("pastel"))
            st.pyplot(fig1)
        else:
            st.warning("Sin datos para mostrar.")

    # IMPLEMENTACIÓN IDEA #3: Relación Tiempo vs Clima (Gráfico de Barras)
    with col_der:
        st.subheader("⛈️ Tiempo Promedio por Clima")
        if not df_filtered.empty:
            df_weather = df_filtered.groupby('weather')['delivery_time_min'].mean().sort_values()
            fig2, ax2 = plt.subplots()
            # Usamos barh para barras horizontales, se leen mejor las etiquetas
            ax2.barh(df_weather.index, df_weather.values, color='teal')
            ax2.set_xlabel("Minutos Promedio")
            st.pyplot(fig2)

# === PESTAÑA 2: FLOTA (VEHÍCULOS) ===
with tab2:
    st.markdown("### Análisis de Rendimiento de la Flota")
    
    # IMPLEMENTACIÓN IDEA #5: Vehículos por Zona (Interactivo + Box Plot)
    # Nota: Un Box Plot es ideal para ver rangos de tiempos (mínimo, máximo, mediana)
    
    st.write("#### 📦 Distribución de Tiempos por Vehículo (Filtrado por Zona)")
    
    # Selector interactivo para la zona (restaurante)
    zonas_disponibles = df['restaurant_zone'].unique()
    zona_seleccionada = st.selectbox("Selecciona una Zona de Restaurante:", zones_disponibles)
    
    # Filtramos datos específicos para este gráfico
    df_zona = df_filtered[df_filtered['restaurant_zone'] == zona_seleccionada]
    
    if not df_zona.empty:
        fig3, ax3 = plt.subplots(figsize=(10, 5))
        # Boxplot: Eje X = Vehículo, Eje Y = Tiempo
        sns.boxplot(data=df_zona, x='delivery_mode', y='delivery_time_min', palette="Set2", ax=ax3)
        ax3.set_title(f"Variabilidad de Tiempos en Zona {zona_seleccionada}")
        ax3.set_ylabel("Tiempo de Entrega (min)")
        st.pyplot(fig3)
    else:
        st.info(f"No hay datos para la zona {zona_seleccionada} con los filtros actuales.")

# === PESTAÑA 3: RUTAS Y ZONAS ===
with tab3:
    
    # IMPLEMENTACIÓN IDEA #1: Scatter Plot Interactivo
    st.subheader("⏱️ Relación Distancia vs. Tiempo")
    
    # Botón interactivo (Radio) para elegir el color
    criterio_color = st.radio(
        "Colorear puntos por:",
        options=["Nivel de Tráfico", "Tipo de Vehículo"],
        horizontal=True
    )
    
    # Mapeo de la selección del usuario a la columna del dataframe
    columna_color = 'traffic_level' if criterio_color == "Nivel de Tráfico" else 'delivery_mode'
    
    if not df_filtered.empty:
        fig4, ax4 = plt.subplots(figsize=(10, 6))
        # Usamos seaborn scatterplot porque maneja los colores (hue) automáticamente muy bien
        sns.scatterplot(data=df_filtered, x='distance_km', y='delivery_time_min', hue=columna_color, style=columna_color, s=100, ax=ax4)
        ax4.set_title(f"Impacto de la Distancia en el Tiempo (según {criterio_color})")
        ax4.grid(True, linestyle='--', alpha=0.3)
        st.pyplot(fig4)
    
    st.divider()
    
    col_z1, col_z2 = st.columns(2)
    
    # IMPLEMENTACIÓN IDEA #2: Cantidad de entregas por Zona Cliente
    with col_z1:
        st.subheader("🏠 Pedidos por Zona (Cliente)")
        conteo_zonas = df_filtered['customer_zone'].value_counts()
        fig5, ax5 = plt.subplots()
        ax5.bar(conteo_zonas.index, conteo_zonas.values, color='salmon')
        ax5.set_ylabel("Cantidad de Pedidos")
        plt.xticks(rotation=45)
        st.pyplot(fig5)
        
    # IMPLEMENTACIÓN IDEA #6: Popularidad de Zonas de Restaurante
    with col_z2:
        st.subheader("🍔 Pedidos por Zona (Restaurante)")
        conteo_rest = df_filtered['restaurant_zone'].value_counts()
        fig6, ax6 = plt.subplots()
        ax6.bar(conteo_rest.index, conteo_rest.values, color='lightgreen')
        ax6.set_ylabel("Cantidad de Pedidos")
        plt.xticks(rotation=45)
        st.pyplot(fig6)
