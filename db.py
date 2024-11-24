import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from datetime import datetime


# Cargar variables de entorno
load_dotenv()
POSTGRES_URL = os.getenv("POSTGRES_URL")

# Función para conectar a la base de datos
def get_connection():
    """Crea y devuelve una conexión a la base de datos PostgreSQL."""
    return psycopg2.connect(POSTGRES_URL, cursor_factory=RealDictCursor)

# Validar si un RUT existe en la base de datos
def validate_rut(rut):
    """Valida si un RUT existe en la base de datos."""
    query = "SELECT COUNT(*) FROM users WHERE rut = %s"  # Cambia `users` al nombre de tu tabla de usuarios
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (rut,))
            return cursor.fetchone()["count"] > 0

# Crear un nuevo ticket
def create_ticket(rut, descripcion, estado="En progreso", asignacion="Chatbot"):
    """Crea un ticket en la base de datos."""
    query = """
    INSERT INTO tickets (rut, descripcion_problema, estado_ticket, asignacion, fecha_creacion)
    VALUES (%s, %s, %s, %s, %s)
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (rut, descripcion, estado, asignacion, datetime.now()))
            conn.commit()

# Actualizar un ticket
def update_ticket(rut, estado, asignacion):
    """Actualiza un ticket existente."""
    query = """
    UPDATE tickets
    SET estado_ticket = %s, asignacion = %s
    WHERE rut = %s
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (estado, asignacion, rut))
            conn.commit()



# Función para conectar a la base de datos
def get_connection():
    """Crea y devuelve una conexión a la base de datos PostgreSQL."""
    try:
        conn = psycopg2.connect(POSTGRES_URL, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        print(f"Error al conectar con la base de datos: {e}")
        return None



# Función para comprobar la conexión
def check_database_connection():
    """Verifica si la base de datos está accesible."""
    try:
        conn = get_connection()
        if conn:
            print("Conexión exitosa a la base de datos.")
            conn.close()
            return True
        else:
            print("No se pudo conectar a la base de datos.")
            return False
    except Exception as e:
        print(f"Error al comprobar la conexión: {e}")
        return False

# Función para obtener un ticket por RUT
def get_tickets_by_rut(rut):
    """Devuelve todos los tickets asociados a un RUT."""
    query = "SELECT * FROM tickets WHERE rut = %s"
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (rut,))
                tickets = cursor.fetchall()
                return tickets
    except Exception as e:
        print(f"Error al consultar tickets por RUT: {e}")
        return []

# Función para obtener todos los tickets
def get_all_tickets():
    """Devuelve todos los tickets de la base de datos."""
    query = "SELECT * FROM Tickets"
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                tickets = cursor.fetchall()
                return tickets
    except Exception as e:
        print(f"Error al obtener todos los tickets: {e}")
        return []

# Función para eliminar un ticket por ID
def delete_ticket_by_id(ticket_id):
    """Elimina un ticket por su ID."""
    query = "DELETE FROM tickets WHERE id = %s"
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (ticket_id,))
                conn.commit()
                return cursor.rowcount > 0  # Devuelve True si se eliminó
    except Exception as e:
        print(f"Error al eliminar ticket con ID {ticket_id}: {e}")
        return False
def show_all_tables():
    """Muestra todas las tablas en la base de datos."""
    query = """
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public'
    """
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                tables = cursor.fetchall()
                if tables:
                    print("Tablas en la base de datos:")
                    for table in tables:
                        print(table[0])  # Nombre de la tabla
                else:
                    print("No se encontraron tablas en la base de datos.")
    except Exception as e:
        print(f"Error al obtener las tablas: {e}")

print("DB module loaded successfully.")
print (show_all_tables())