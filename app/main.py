import streamlit as st
from streamlit_folium import st_folium
import folium
import httpx
import pandas as pd
from datetime import datetime, timedelta
import h3
import geopandas as gpd
from shapely.geometry import Polygon
import json


st.set_page_config(
    page_title="SAFE - Sistema de Alertas y Reportes", page_icon="🚨", layout="wide"
)


API_URL = "http://localhost:8000"


def get_incidents(filters=None):
    try:
        params = filters or {}
        response = httpx.get(f"{API_URL}/api/v1/incidents", params=params, timeout=10.0)
        if response.status_code == 200:
            data = response.json()
            return data.get("data", {}).get("incidents", [])
    except Exception:
        pass
    return []


def create_incident(incident_data):
    try:
        response = httpx.post(
            f"{API_URL}/api/v1/incidents", json=incident_data, timeout=10.0
        )
        return response.status_code == 201
    except Exception:
        return False


def get_h3_density(h3_index, k=1):
    try:
        response = httpx.get(
            f"{API_URL}/api/v1/h3/{h3_index}/density", params={"k": k}, timeout=10.0
        )
        if response.status_code == 200:
            return response.json().get("data", {}).get("density", [])
    except Exception:
        pass
    return []


st.title("🚨 SAFE - Sistema de Alertas y Reportes Urbanos")


menu = st.sidebar.selectbox("Menú", ["Reportar", "Mapa", "Dashboard", "Configuración"])


if menu == "Reportar":
    st.header("📝 Reportar Incidente")

    with st.form("incident_form"):
        col1, col2 = st.columns(2)

        with col1:
            title = st.text_input("Título *", placeholder="Título breve del incidente")
            category = st.selectbox(
                "Categoría *", ["hurto", "violencia", "convivencia"]
            )
            tipo_reporte = st.selectbox(
                "Tipo de reporte *", ["rapido", "convivencia", "delito"]
            )
            severity = st.slider("Nivel de gravedad", 1, 5, 1)

        with col2:
            lat = st.number_input("Latitud *", value=4.7110, format="%.6f")
            lng = st.number_input("Longitud *", value=-74.0721, format="%.6f")
            address = st.text_input("Dirección", placeholder="Dirección opcional")

        description = st.text_area("Descripción detallada")

        es_anonimo = st.checkbox("-reportar de forma anónima")

        submitted = st.form_submit_button("Enviar Reporte", type="primary")

        if submitted and title and lat and lng:
            incident_data = {
                "title": title,
                "description": description,
                "category": category,
                "tipo_reporte": tipo_reporte,
                "ley": "599/2000" if tipo_reporte == "delito" else "1801/2016",
                "severity": severity,
                "fuente": "ciudadano",
                "location": {"latitude": lat, "longitude": lng, "address": address},
                "reporter_name": None if es_anonimo else "Ciudadano",
                "reporter_type": "Anonimo" if es_anonimo else "Nombre",
                "es_anonimo": es_anonimo,
            }

            if create_incident(incident_data):
                st.success("✅ Reporte enviado exitosamente!")
            else:
                st.error("Error al enviar el reporte. Intente más tarde.")


elif menu == "Mapa":
    st.header("🗺️ Mapa de Incidentes")

    col1, col2, col3 = st.columns(3)
    with col1:
        category_filter = st.selectbox(
            "Categoría", ["todos", "hurto", "violencia", "convivencia"]
        )
    with col2:
        k_value = st.slider("Radio de vecindad (k-ring)", 1, 5, 1)
    with col3:
        show_density = st.checkbox("Mostrar densidad", value=True)

    incidents = get_incidents()

    if category_filter != "todos":
        incidents = [i for i in incidents if i.get("category") == category_filter]

    if incidents:
        center_lat = sum(i["location"]["latitude"] for i in incidents) / len(incidents)
        center_lng = sum(i["location"]["longitude"] for i in incidents) / len(incidents)
    else:
        center_lat, center_lng = 4.7110, -74.0721

    m = folium.Map(location=[center_lat, center_lng], zoom_start=13)

    for incident in incidents:
        lat = incident.get("location", {}).get("latitude")
        lng = incident.get("location", {}).get("longitude")

        if lat and lng:
            color = {
                "hurto": "red",
                "violencia": "darkred",
                "convivencia": "orange",
            }.get(incident.get("category"), "blue")

            folium.CircleMarker(
                location=[lat, lng],
                radius=6 + incident.get("severity", 1) * 2,
                color=color,
                fill=True,
                popup=f"<b>{incident.get('title')}</b><br>{incident.get('category')}<br>Severidad: {incident.get('severity')}",
            ).add_to(m)

    if show_density and incidents:
        h3_cells = {}
        for incident in incidents:
            lat = incident.get("location", {}).get("latitude")
            lng = incident.get("location", {}).get("longitude")
            if lat and lng:
                idx = h3.latlng_to_cell(lat, lng, 8)
                h3_cells[idx] = h3_cells.get(idx, 0) + 1

        for idx, count in h3_cells.items():
            boundary = h3.cell_to_boundary(idx)
            coords = [[c[1], c[0]] for c in boundary]
            coords.append(coords[0])

            folium.Polygon(
                locations=coords,
                color="purple",
                weight=2,
                fill=True,
                fill_opacity=min(0.3 + count * 0.1, 0.7),
                popup=f"H3: {idx}<br>Incidentes: {count}",
            ).add_to(m)

    st_folium(m, width=800, height=500)


elif menu == "Dashboard":
    st.header("📊 Dashboard Analítico")

    incidents = get_incidents()

    col1, col2, col3, col4 = st.columns(4)

    total = len(incidents)
    hurto = sum(1 for i in incidents if i.get("category") == "hurto")
    violencia = sum(1 for i in incidents if i.get("category") == "violencia")
    convivencia = sum(1 for i in incidents if i.get("category") == "convivencia")

    col1.metric("Total Reportes", total)
    col2.metric("Hurtos", hurto)
    col3.metric("Violencia", violencia)
    col4.metric("Convivencia", convivencia)

    if incidents:
        df = pd.DataFrame(incidents)

        st.subheader("Distribución por Categoría")
        category_counts = df["category"].value_counts()
        st.bar_chart(category_counts)

        st.subheader("Distribución por Severidad")
        severity_counts = df["severity"].value_counts().sort_index()
        st.bar_chart(severity_counts)

        with st.expander("Ver datos crudos"):
            st.json(incidents)


elif menu == "Configuración":
    st.header("⚙️ Configuración")

    st.info("Configuración de la aplicación SAFE")

    st.text_input("API URL", value=API_URL, disabled=True)
    st.text_input("Resolución H3", value="8", disabled=True)
    st.text_input("Zona Horaria", value="UTC-5", disabled=True)


if __name__ == "__main__":
    st.run()
