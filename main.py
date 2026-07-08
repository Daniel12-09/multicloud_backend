from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pymysql
import os

app = FastAPI(title="CloudDash Backend API")

# Configuración de CORS para que tu frontend en Vercel pueda comunicarse con la API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción lo limitaremos a tu dominio clouddashdaniel.studio
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Variables de entorno para la base de datos (se configurarán en el servidor)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "clouddash_db")

def get_db_connection():
    try:
        # Conexión a MySQL a través del Proxy Inverso (según requerimiento del informe)
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error de conexión a la Base de Datos: {str(e)}")

@app.get("/")
def read_root():
    return {"status": "online", "message": "Backend de CloudDash Operativo"}

# Endpoint para obtener las métricas (Cumple con el flujo de datos del sistema)
@app.get("/api/metrics")
def get_metrics():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM metrics ORDER BY timestamp DESC LIMIT 10")
            result = cursor.fetchall()
            return {"server_status": "OK", "metrics": result}
    finally:
        connection.close()