# SAFE - Sistema de Alertas y Reportes Urbanos

Aplicación web completa para reporte y análisis de incidentes urbanos con geoespaciado H3.

## Estructura del Proyecto

```
h3/
├── app/                  # Frontend Streamlit
│   ├── pages/            # Páginas adicionales
│   ├── components/       # Componentes reutilizables
│   └── main.py           # Aplicación principal
├── api/                 # Backend FastAPI
│   ├── routers/          # Endpoints
│   ├── models/          # Schemas Pydantic
│   └── main.py          # Servidor API
├── core/                # Configuración y utilitarios
│   ├── config.py        # Settings
│   ├── h3_utils.py     # Funciones H3
│   └── security.py      # Autenticación
├── db/                  # Modelos de base de datos
├── docker/              # Dockerfiles y compose
├── requirements.txt      # Dependencias
├── .env.example        # Variables de entorno
└── README.md
```

## Requisitos

- Python 3.11+
- PostgreSQL 14+ con PostGIS
- Docker (opcional)

## Instalación

1. Clonar y entrar al directorio:
```bash
cd h3
```

2. Crear entorno virtual e instalar dependencias:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate    # Windows
pip install -r requirements.txt
```

3. Copiar y configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

4. Iniciar PostgreSQL con PostGIS o usar Docker:
```bash
docker run -d \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=incidentes_db \
  -p 5432:5432 \
  postgis/postgis:14-3.2
```

## Ejecución

### API (FastAPI)
```bash
uvicorn api.main:app --reload --port 8000
```

### Frontend (Streamlit)
```bash
streamlit run app/main.py
```

### Docker Compose
```bash
cd docker
docker-compose up -d
```

## Uso

1. Acceder a `http://localhost:8501` para la UI Streamlit
2. Acceder a `http://localhost:8000/docs` para la documentación API

### Endpoints Principales

| Método | Ruta | Descripción |
|--------|------|------------|
| POST | /api/v1/incidents | Crear reporte |
| GET | /api/v1/incidents | Listar reportes |
| GET | /api/v1/incidents/{id} | Ver detalle |
| PUT | /api/v1/incidents/{id} | Actualizar |
| GET | /api/v1/h3/{index}/density | Densidad H3 |
| POST | /api/v1/auth/register | Registrarse |
| POST | /api/v1/auth/login | Login |

### Ejemplo: Crear Incident

```bash
curl -X POST http://localhost:8000/api/v1/incidents \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Hurto en bus",
    "description": "Me robaron el celular",
    "category": "hurto",
    "tipo_reporte": "delito",
    "ley": "599/2000",
    "severity": 3,
    "location": {
      "latitude": 4.7110,
      "longitude": -74.0721
    },
    "es_anonimo": false
  }'
```

## Configuración H3

La resolución H3 se configura en `.env`:
- Resolución 7: barrios/manzanas
- Resolución 8: cuadras (recomendado)
- Resolución 9: intersecciones

## Docker

```bash
# Build y ejecución
cd docker
docker-compose up --build

# Accesos
- API: http://localhost:8000
- Streamlit: http://localhost:8501
- PostgreSQL: localhost:5432
```

## Tests

```bash
pytest tests/
```

## Licencia

MIT