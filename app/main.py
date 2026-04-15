import streamlit as st
from streamlit_folium import st_folium
import folium
import httpx
import pandas as pd
from datetime import datetime
import json


st.set_page_config(
    page_title="SAFE - Alertas y Reportes Urbanos",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded",
)


API_URL = "http://localhost:8000"


def get_api_client():
    return httpx.Client(base_url=API_URL, timeout=10.0)


def check_api_health():
    try:
        with get_api_client() as client:
            response = client.get("/api/v1/health")
            return response.status_code == 200
    except Exception:
        return False


def get_incidents(filters=None):
    try:
        with get_api_client() as client:
            response = client.get("/api/v1/incidents", params=filters or {})
            if response.status_code == 200:
                data = response.json()
                return data.get("data", {}).get("incidents", [])
    except Exception:
        pass
    return []


def create_incident(incident_data):
    try:
        with get_api_client() as client:
            response = client.post("/api/v1/incidents", json=incident_data)
            return response.status_code in [200, 201]
    except Exception:
        return False


def get_categories():
    return ["hurto", "violencia", "convivencia", "otro"]


def get_tipo_reporte():
    return ["rapido", "convivencia", "delito"]


SAMPLE_INCIDENTS = [
    {
        "id": "1",
        "title": "Hurto de celular en bus",
        "description": "Me robaron el celular en el bus de la ruta 257",
        "category": "hurto",
        "tipo_reporte": "delito",
        "severity": 3,
        "location": {
            "latitude": 4.7110,
            "longitude": -74.0721,
            "address": "Av. Caracas",
        },
        "status": "recibido",
        "timestamp": "2024-01-15T10:30:00",
    },
    {
        "id": "2",
        "title": "Ruido excesivo",
        "description": "Los vecinos tienen música muy alta",
        "category": "convivencia",
        "tipo_reporte": "convivencia",
        "severity": 1,
        "location": {"latitude": 4.7150, "longitude": -74.0740, "address": "Calle 45"},
        "status": "en_proceso",
        "timestamp": "2024-01-14T15:20:00",
    },
    {
        "id": "3",
        "title": "Agresión verbal",
        "description": "Vecino me insultó sin motivo",
        "category": "violencia",
        "tipo_reporte": "delito",
        "severity": 2,
        "location": {
            "latitude": 4.7090,
            "longitude": -74.0700,
            "address": "Carrera 10",
        },
        "status": "resuelto",
        "timestamp": "2024-01-13T09:00:00",
    },
    {
        "id": "4",
        "title": "Intento de hurto",
        "description": "Unidad de carga fue forcejeada",
        "category": "hurto",
        "tipo_reporte": "delito",
        "severity": 4,
        "location": {
            "latitude": 4.7130,
            "longitude": -74.0750,
            "address": "Terminal de transporte",
        },
        "status": "recibido",
        "timestamp": "2024-01-15T08:00:00",
    },
    {
        "id": "5",
        "title": "Pelea en la calle",
        "description": "Dos personas pelearon frente al parque",
        "category": "violencia",
        "tipo_reporte": "convivencia",
        "severity": 3,
        "location": {
            "latitude": 4.7080,
            "longitude": -74.0690,
            "address": "Parque Central",
        },
        "status": "cerrado",
        "timestamp": "2024-01-12T18:30:00",
    },
]


def render_report_form():
    st.header("📝 Reportar Incidente")
    st.markdown("Ayuda a mejorar tu ciudad reportando incidentes.")

    with st.form("incident_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            title = st.text_input(
                "Título del incidente *",
                placeholder="Ej: Hurto en el bus de la mañana",
                help="Título breve que describa el incidente",
            )
            category = st.selectbox(
                "Categoría *",
                get_categories(),
                help="Tipo de incidente que estás reportando",
            )
            tipo_reporte = st.selectbox(
                "Tipo de reporte *", get_tipo_reporte(), help="Naturaleza del reporte"
            )
            severity = st.slider(
                "Nivel de gravedad",
                min_value=1,
                max_value=5,
                value=1,
                help="1=Ninguno, 5=Crítico",
            )

        with col2:
            lat = st.number_input(
                "Latitud *",
                value=4.7110,
                min_value=-90.0,
                max_value=90.0,
                format="%.6f",
                help="Coordenada geográfica",
            )
            lng = st.number_input(
                "Longitud *",
                value=-74.0721,
                min_value=-180.0,
                max_value=180.0,
                format="%.6f",
                help="Coordenada geográfica",
            )
            address = st.text_input(
                "Dirección", placeholder="Dirección o lugar aproximado (opcional)"
            )

        description = st.text_area(
            "Descripción detallada",
            placeholder="Describe los hechos con el mayor detalle posible...",
            height=100,
        )

        col3, col4 = st.columns(2)
        with col3:
            reporter_name = st.text_input("Tu nombre", placeholder="Nombre o seudónimo")
        with col4:
            reporter_contact = st.text_input("Contacto", placeholder="Teléfono o email")

        es_anonimo = st.checkbox("Reportar de forma anónima")

        st.markdown("---")
        submitted = st.form_submit_button(
            "📨 Enviar Reporte", type="primary", use_container_width=True
        )

        if submitted:
            if not title:
                st.error("⚠️ El título es obligatorio")
            else:
                incident_data = {
                    "title": title,
                    "description": description,
                    "category": category,
                    "tipo_reporte": tipo_reporte,
                    "ley": "599/2000" if tipo_reporte == "delito" else "1801/2016",
                    "severity": severity,
                    "fuente": "ciudadano",
                    "location": {
                        "latitude": lat,
                        "longitude": lng,
                        "address": address if address else None,
                    },
                    "reporter_name": None
                    if es_anonimo
                    else (reporter_name or "Ciudadano"),
                    "reporter_contact": reporter_contact if not es_anonimo else None,
                    "reporter_type": "Anonimo"
                    if es_anonimo
                    else ("Nombre" if reporter_name else "Telefono"),
                    "es_anonimo": es_anonimo,
                }

                success = create_incident(incident_data)
                if success:
                    st.success("✅ Reporte enviado exitosamente!")
                    st.balloons()
                else:
                    st.error("Error al conectar con la API. Intente más tarde.")


def render_map():
    st.header("🗺️ Mapa de Incidentes")

    api_online = check_api_health()

    if not api_online:
        st.warning("⚠️ API no disponible. Mostrando datos de ejemplo.")
        incidents = SAMPLE_INCIDENTS
    else:
        incidents = get_incidents()

    col1, col2 = st.columns([3, 1])
    with col1:
        category_filter = st.selectbox(
            "Filtrar por categoría", ["todos"] + get_categories()
        )
    with col2:
        auto_refresh = st.checkbox("Auto-refresh", value=False)

    if category_filter != "todos":
        incidents = [i for i in incidents if i.get("category") == category_filter]

    if not incidents:
        st.info("No hay incidentes para mostrar.")
        return

    center_lat = sum(i["location"]["latitude"] for i in incidents) / len(incidents)
    center_lng = sum(i["location"]["longitude"] for i in incidents) / len(incidents)

    m = folium.Map(
        location=[center_lat, center_lng], zoom_start=13, tiles="cartodbpositron"
    )

    for incident in incidents:
        lat = incident.get("location", {}).get("latitude")
        lng = incident.get("location", {}).get("longitude")

        if lat and lng:
            color_map = {
                "hurto": "red",
                "violencia": "darkred",
                "convivencia": "orange",
                "otro": "blue",
            }
            color = color_map.get(incident.get("category"), "blue")

            status_icon = {
                "recibido": "📨",
                "en_proceso": "⏳",
                "resuelto": "✅",
                "cerrado": "❎",
            }.get(incident.get("status"), "❓")

            popup_html = f"""
            <div style='font-family: Arial; min-width: 200px;'>
                <h4>{incident.get("title")}</h4>
                <p><b>Categoría:</b> {incident.get("category")}</p>
                <p><b>Tipo:</b> {incident.get("tipo_reporte")}</p>
                <p><b>Severidad:</b> {"⭐" * incident.get("severity", 1)}</p>
                <p><b>Estado:</b> {status_icon} {incident.get("status")}</p>
                <p><b>Dirección:</b> {incident.get("location", {}).get("address", "N/A")}</p>
                <p><b>Fecha:</b> {incident.get("timestamp", "")}</p>
            </div>
            """

            folium.CircleMarker(
                location=[lat, lng],
                radius=8 + incident.get("severity", 1) * 2,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.7,
                popup=folium.Popup(popup_html, max_width=300),
            ).add_to(m)

    folium.LayerControl().add_to(m)

    st_folium(m, width=800, height=550, returned_objects=[])


def render_dashboard():
    st.header("📊 Dashboard Analítico")

    api_online = check_api_health()

    if not api_online:
        st.warning("⚠️ API no disponible. Mostrando datos de ejemplo.")
        incidents = SAMPLE_INCIDENTS
    else:
        incidents = get_incidents()

    total = len(incidents)
    hurto = sum(1 for i in incidents if i.get("category") == "hurto")
    violencia = sum(1 for i in incidents if i.get("category") == "violencia")
    convivencia = sum(1 for i in incidents if i.get("category") == "convivencia")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Reportes", total, delta=None)
    with col2:
        st.metric("Hurtos 🏴", hurto)
    with col3:
        st.metric("Violencia 🔴", violencia)
    with col4:
        st.metric("Convivencia 🟠", convivencia)

    if incidents:
        df = pd.DataFrame(incidents)

        st.markdown("### Distribución por Categoría")
        if "category" in df.columns:
            cat_counts = df["category"].value_counts()
            st.bar_chart(cat_counts, color="#FF4B4B")

        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("### Incidentes por Estado")
            if "status" in df.columns:
                status_counts = df["status"].value_counts()
                st.bar_chart(status_counts, color="#4B8BFF")

        with col_b:
            st.markdown("### Severidad")
            if "severity" in df.columns:
                severity_counts = df["severity"].value_counts().sort_index()
                st.bar_chart(severity_counts, color="#FFD700")

        col_c, col_d = st.columns(2)

        with col_c:
            st.markdown("### Tabla de Incidentess")
            display_cols = ["title", "category", "severity", "status"]
            available_cols = [c for c in display_cols if c in df.columns]
            st.dataframe(df[available_cols], use_container_width=True)

        with col_d:
            st.markdown("### Datos crudos")
            st.json(incidents[:3] if len(incidents) > 3 else incidents)
    else:
        st.info("No hay datos para mostrar.")


def render_settings():
    st.header("⚙️ Configuración")

    st.info("Configuración global de SAFE")

    col1, col2 = st.columns(2)

    with col1:
        st.text_input("API URL", value=API_URL, disabled=True)
        st.text_input("Resolución H3", value="8", disabled=True)

    with col2:
        zona = st.selectbox(
            "Zona horaria", ["UTC-5 (Colombia)", "UTC", "UTC-5"], disabled=True
        )
        st.selectbox("Nivel de registro", ["DEBUG", "INFO", "WARNING"], disabled=True)

    st.markdown("---")
    st.markdown("### Estado de la API")

    if check_api_health():
        st.success("🟢 API - En línea")
    else:
        st.error("🔴 API - Sin conexión")

    with st.expander("Ver datos de ejemplo disponibles"):
        st.json(SAMPLE_INCIDENTS, expanded=False)


def main():
    st.title("🚨 SAFE - Sistema de Alertas y Reportes Urbanos")
    st.markdown("---")

    menu = st.sidebar.radio(
        "Navegación", ["📝 Reportar", "🗺️ Mapa", "📊 Dashboard", "⚙️ Configuración"]
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Acerca de")
    st.sidebar.info(
        "SAFE v1.0.0\n\n"
        "Sistema de Alertas y Reportes Urbanos\n\n"
        "Tecnología H3 para geoespaciado"
    )

    pages = {
        "📝 Reportar": render_report_form,
        "🗺️ Mapa": render_map,
        "📊 Dashboard": render_dashboard,
        "⚙️ Configuración": render_settings,
    }

    render_func = pages.get(menu, render_report_form)
    render_func()


if __name__ == "__main__":
    main()
