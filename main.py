from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pymysql
import os

app = FastAPI(title="CloudDash Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "defaultdb")

def init_db():
    """Función automática para crear la tabla de métricas si no existe"""
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        with connection.cursor() as cursor:
            # Crear la tabla requerida por el flujo del informe
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    cpu_usage FLOAT NOT NULL,
                    ram_usage FLOAT NOT NULL,
                    disk_usage FLOAT NOT NULL,
                    network_in FLOAT NOT NULL,
                    network_out FLOAT NOT NULL
                )
            """)
            # Insertar un dato de prueba inicial si la tabla está vacía
            cursor.execute("SELECT COUNT(*) FROM metrics")
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO metrics (cpu_usage, ram_usage, disk_usage, network_in, network_out) 
                    VALUES (24.5, 61.2, 42.8, 150.4, 89.2)
                """)
        connection.commit()
        connection.close()
        print("Base de datos inicializada correctamente.")
    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}")

# Llamamos a la inicialización al arrancar la API
init_db()

def get_db_connection():
    try:
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
    return {"status": "online", "message": "Backend de CloudDash Operativo y conectado a MySQL"}

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