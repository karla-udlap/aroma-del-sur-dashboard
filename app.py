import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Aroma del Sur Dashboard",
    page_icon="☕",
    layout="wide"
)

TU_NOMBRE = "Dafne, Zaira y Karla"
TU_ID     = "184344, 183800, 184047"


TU_INSIGHT = """
Descubrimos que las sucursales con más empleados tienen ventas 
casi perfectamente correlacionadas (0.98), mientras que La Paz 
con el menor número de empleados genera solo 423,000 vs 1.6M 
de Angelópolis. Recomiendo contratar más personal en La Paz y 
Cholula para incrementar sus ventas al menos un 30%.
"""

@st.cache_data
def cargar_datos():
    ventas    = pd.read_csv("ventas_limpio.csv")
    clientes  = pd.read_csv("clientes_limpio-2.csv")
    productos = pd.read_csv("productos_limpio-2.csv")
    sucursales = pd.read_csv("sucursales_limpio-2.csv")

    ventas["total"]    = pd.to_numeric(ventas["total"], errors="coerce")
    ventas["fecha"]    = pd.to_datetime(ventas["fecha"], errors="coerce")
    ventas["Year"]     = ventas["fecha"].dt.year
    ventas["Month"]    = ventas["fecha"].dt.to_period("M").astype(str)
    ventas["hora_sola"] = ventas["hora"].astype(str).str[:2]
    clientes["total_gastado"] = pd.to_numeric(clientes["total_gastado"], errors="coerce")

    df = ventas.merge(sucursales, on="sucursal_id", how="left")
    df = df.merge(productos, on="producto_id", how="left")
    return df, clientes, productos, sucursales

df, clientes, productos, sucursales = cargar_datos()

# ── TITULO ──
st.title("☕ Aroma del Sur — Dashboard Ejecutivo")
st.caption(f"Por **{TU_NOMBRE}** · ID {TU_ID} · LAD3012 · UDLAP Verano I 2026")
st.markdown("---")

# ── FILTROS ──
st.sidebar.header("🔎 Filtros")

sucursales_lista = sorted(df["nombre_x"].dropna().unique())
filtro_sucursal = st.sidebar.multiselect(
    "Sucursal",
    options=sucursales_lista,
    default=sucursales_lista
)

categorias_lista = sorted(df["categoria"].dropna().unique())
filtro_categoria = st.sidebar.multiselect(
    "Categoría de producto",
    options=categorias_lista,
    default=categorias_lista
)

anios_lista = sorted(df["Year"].dropna().unique())
filtro_anio = st.sidebar.multiselect(
    "Año",
    options=anios_lista,
    default=anios_lista
)

# Aplicar filtros
df_f = df[
    df["nombre_x"].isin(filtro_sucursal) &
    df["categoria"].isin(filtro_categoria) &
    df["Year"].isin(filtro_anio)
]

if len(df_f) == 0:
    st.warning("No hay datos con esos filtros. Selecciona al menos una opción en cada filtro.")
    st.stop()

# ══════════════════════════════════════
# VISTA 1 — KPIs GENERALES
# ══════════════════════════════════════
st.header("📊 KPIs Generales")
st.markdown("---")

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Ingresos Totales", f"${df_f['total'].sum():,.0f}")
col2.metric("🧾 Transacciones", f"{len(df_f):,}")
col3.metric("📦 Productos Vendidos", f"{df_f['cantidad'].sum():,.0f}")
col4.metric("🎯 Ticket Promedio", f"${df_f['total'].mean():,.2f}")

st.markdown("---")

g1, g2 = st.columns(2)

with g1:
    st.subheader("Ventas por Sucursal")
    ventas_suc = df_f.groupby("nombre_x")["total"].sum().reset_index().sort_values("total", ascending=False)
    fig1 = px.bar(ventas_suc, x="nombre_x", y="total",
                  labels={"nombre_x": "Sucursal", "total": "Ventas ($)"},
                  color="nombre_x")
    fig1.update_layout(showlegend=False, height=380)
    st.plotly_chart(fig1, use_container_width=True)

with g2:
    st.subheader("Ventas por Hora del Día")
    ventas_hora = df_f.groupby("hora_sola")["venta_id"].count().reset_index()
    ventas_hora.columns = ["Hora", "Ventas"]
    fig2 = px.bar(ventas_hora.sort_values("Hora"), x="Hora", y="Ventas",
                  color="Ventas", color_continuous_scale="teal")
    fig2.update_layout(height=380)
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ══════════════════════════════════════
# VISTA 2 — ANÁLISIS DE PRODUCTOS
# ══════════════════════════════════════
st.header("📦 Análisis de Productos")
st.markdown("---")

g3, g4 = st.columns(2)

with g3:
    st.subheader("Ingresos por Categoría")
    rent_cat = df_f.groupby("categoria")["total"].sum().reset_index().sort_values("total", ascending=False)
    fig3 = px.bar(rent_cat, x="categoria", y="total",
                  labels={"categoria": "Categoría", "total": "Ingresos ($)"},
                  color="categoria")
    fig3.update_layout(showlegend=False, height=380)
    st.plotly_chart(fig3, use_container_width=True)

with g4:
    st.subheader("Top 10 Productos Más Vendidos")
    top_prod = df_f.groupby("nombre_y")["cantidad"].sum().reset_index().sort_values("cantidad", ascending=False).head(10)
    fig4 = px.bar(top_prod, x="cantidad", y="nombre_y", orientation="h",
                  labels={"nombre_y": "Producto", "cantidad": "Cantidad"},
                  color="cantidad", color_continuous_scale="teal")
    fig4.update_layout(height=380)
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# ══════════════════════════════════════
# VISTA 3 — ANÁLISIS DE CLIENTES
# ══════════════════════════════════════
st.header("👥 Análisis de Clientes")
st.markdown("---")

col1, col2, col3 = st.columns(3)
col1.metric("👤 Total Clientes", f"{len(clientes):,}")
col2.metric("💳 Gasto Promedio", f"${clientes['total_gastado'].mean():,.2f}")
col3.metric("🎂 Edad Promedio", f"{clientes['edad'].mean():.0f} años")

st.markdown("---")

g5, g6 = st.columns(2)

with g5:
    st.subheader("Distribución de Edades")
    fig5 = px.histogram(clientes, x="edad", nbins=20,
                        labels={"edad": "Edad"},
                        color_discrete_sequence=["teal"])
    fig5.update_layout(height=380)
    st.plotly_chart(fig5, use_container_width=True)

with g6:
    st.subheader("Gasto Promedio por Género")
    gasto_genero = clientes.groupby("genero")["total_gastado"].mean().reset_index()
    fig6 = px.bar(gasto_genero, x="genero", y="total_gastado",
                  labels={"genero": "Género", "total_gastado": "Gasto Promedio ($)"},
                  color="genero",
                  color_discrete_sequence=["teal", "purple"])
    fig6.update_layout(showlegend=False, height=380)
    st.plotly_chart(fig6, use_container_width=True)

st.markdown("---")

st.subheader("Segmentación de Clientes (K-Means)")
from sklearn.cluster import KMeans
X = clientes[["edad", "total_gastado"]].dropna()
kmeans = KMeans(n_clusters=3, random_state=42, n_init="auto").fit(X)
clientes_clean = clientes.loc[X.index].copy()
clientes_clean["Segmento"] = kmeans.labels_.astype(str)
clientes_clean["Segmento"] = clientes_clean["Segmento"].replace({
    "0": "Ocasionales ($1,179)",
    "1": "VIP ($13,065)",
    "2": "Regulares ($7,204)"
})
fig7 = px.scatter(clientes_clean, x="edad", y="total_gastado",
                  color="Segmento",
                  labels={"edad": "Edad", "total_gastado": "Total Gastado ($)"},
                  color_discrete_sequence=["purple", "gold", "teal"])
fig7.update_layout(height=450)
st.plotly_chart(fig7, use_container_width=True)

st.markdown("---")

# ── PREGUNTAS GUIA ──
with st.expander("🔍 Preguntas guía para encontrar tu insight"):
    st.markdown("""
**Juega con los filtros del sidebar mientras te haces estas preguntas:**

1. ¿Cuál sucursal tiene los ingresos más bajos? ¿Por qué crees que sea?
2. ¿Qué categoría de producto genera más dinero? ¿Y cuál menos?
3. ¿A qué hora del día se vende más? ¿Qué implicaría eso para el personal?
4. ¿Hay diferencia en el gasto entre hombres y mujeres?
5. ¿Qué tienen en común los clientes VIP?
    """)

# ── INSIGHT ──
st.subheader("💡 Insight de negocio")
st.info(TU_INSIGHT)

st.markdown("---")
st.caption("Dashboard desarrollado con pandas + plotly + Streamlit · LAD3012 · Aroma del Sur ☕")
