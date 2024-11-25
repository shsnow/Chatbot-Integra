import os
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from datetime import datetime

# Cargar variables de entorno
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

# Crear el pool de conexiones
connection_pool = pool.SimpleConnectionPool(
    1,  # Número mínimo de conexiones en el pool
    10,  # Número máximo de conexiones en el pool
    DATABASE_URL
)

if connection_pool:
    print("Pool de conexiones creado exitosamente.")

# Obtener una conexión del pool
def get_connection():
    try:
        return connection_pool.getconn()
    except Exception as e:
        print(f"Error al obtener la conexión: {e}")
        return None

# Liberar la conexión al pool
def release_connection(conn):
    if conn:
        connection_pool.putconn(conn)

def validate_rut(rut):
    """Valida si un RUT existe en la base de datos."""
    table_name = 'Clients'  # Cambia esto si la tabla tiene otro nombre
    conn = None
    try:
        conn = get_connection()

        # Verificar si la tabla existe en el esquema public
        with conn.cursor() as cursor:
            cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = 'public' AND LOWER(table_name) = LOWER(%s)
            """, (table_name,))
            table_exists = cursor.fetchone()[0] > 0

            if not table_exists:
                print(f"Error: La tabla '{table_name}' no existe en la base de datos.")
                return False

        # Ajustar el nombre de la tabla para evitar problemas de mayúsculas
        formatted_table_name = f'"{table_name}"' if not table_name.islower() else table_name

        # Validar el RUT en la tabla
        with conn.cursor() as cursor:
            query = f"SELECT COUNT(*) FROM {formatted_table_name} WHERE rut = %s"
            cursor.execute(query, (rut,))
            result = cursor.fetchone()
            exists = result[0] > 0

            if exists:
                print(f"El RUT '{rut}' existe en la tabla '{table_name}'.")
            else:
                print(f"El RUT '{rut}' no existe en la tabla '{table_name}'.")
            return exists
    except Exception as e:
        print(f"Error al validar el RUT: {e}")
        return False
    finally:
        release_connection(conn)




#funcion que muestra a los usuarios los tickets que tienen
def show_tickets(rut):
    """Muestra los tickets asociados a un RUT."""
    tickets = get_tickets_by_rut(rut)
    if tickets:
        print(f"Tickets asociados al RUT {rut}:")
        for ticket in tickets:
            print(f" - {ticket}")
    else:
        print(f"No se encontraron tickets asociados al RUT {rut}.")
# Crear un ticket
def create_ticket(rut, title, description, category_id, state_id, sla_id, asignacion="Chatbot"):
    """Crea un nuevo ticket en la base de datos usando el clientId asociado al RUT."""
    # Obtener el clientId correspondiente al RUT
    query_client_id = "SELECT id FROM \"Clients\" WHERE rut = %s"
    conn = None
    try:
        conn = get_connection()
        if conn:
            with conn.cursor() as cursor:
                # Obtener el clientId basado en el RUT
                cursor.execute(query_client_id, (rut,))
                client = cursor.fetchone()
                
                if not client:
                    print(f"No se encontró el RUT {rut} en la base de datos.")
                    return
                
                client_id = client[0]  # Obtener el clientId
                
                # Crear el ticket utilizando el clientId
                query_create_ticket = """
                INSERT INTO "Tickets" (title, description, estado_ticket, asignacion, clientId, categoryId, stateId, slaId, createdAt, updatedAt)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query_create_ticket, (title, description, "En progreso", asignacion, client_id, category_id, state_id, sla_id, datetime.now(), datetime.now()))
                conn.commit()
                print("Ticket creado exitosamente.")
    except Exception as e:
        print(f"Error al crear el ticket: {e}")
    finally:
        release_connection(conn)


def update_ticket(rut, estado, asignacion, category_id, state_id, sla_id):
    """Actualiza un ticket existente basado en el RUT, usando el clientId en lugar del RUT."""
    # Obtener el clientId correspondiente al RUT
    query_client_id = "SELECT id FROM \"Clients\" WHERE rut = %s"
    query_update_ticket = """
    UPDATE "Tickets"
    SET estado_ticket = %s, asignacion = %s, categoryId = %s, stateId = %s, slaId = %s, updatedAt = %s
    WHERE clientId = %s
    """
    conn = None
    try:
        conn = get_connection()
        if conn:
            with conn.cursor() as cursor:
                # Obtener el clientId basado en el RUT
                cursor.execute(query_client_id, (rut,))
                client = cursor.fetchone()
                
                if not client:
                    print(f"No se encontró el RUT {rut} en la base de datos.")
                    return
                
                client_id = client[0]  # Obtener el clientId
                
                # Actualizar el ticket usando el clientId
                cursor.execute(query_update_ticket, (estado, asignacion, category_id, state_id, sla_id, datetime.now(), client_id))
                conn.commit()
                print(f"Ticket de cliente {rut} actualizado exitosamente.")
    except Exception as e:
        print(f"Error al actualizar el ticket: {e}")
    finally:
        release_connection(conn)


def get_tickets_by_rut(rut):
    """Devuelve todos los tickets asociados a un RUT desde la tabla 'Tickets'."""
    query = """
    SELECT t.* 
    FROM "Tickets" t
    JOIN "Clients" c ON t."clientId" = c.id  -- Unimos las tablas por clientId
    WHERE c.rut = %s  -- Filtramos por el RUT del cliente
    """
    conn = None
    try:
        conn = get_connection()
        if conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, (rut,))
                tickets = cursor.fetchall()
                if tickets:
                    return tickets  # Devuelve los tickets encontrados para el RUT
                else:
                    print(f"No se encontraron tickets asociados al RUT {rut}.")
                    return []  # Si no hay tickets, devolver una lista vacía
    except Exception as e:
        print(f"Error al obtener tickets por RUT: {e}")
        return []
    finally:
        release_connection(conn)


def show_first_5_records_per_table():
    """Muestra los nombres de las columnas y los primeros 5 registros de cada tabla en el esquema 'public'."""
    query_tables = """
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public'
    """
    conn = None
    try:
        conn = get_connection()
        if conn:
            with conn.cursor() as cursor:
                # Obtener todas las tablas en el esquema 'public'
                cursor.execute(query_tables)
                tables = cursor.fetchall()

                if not tables:
                    print("No se encontraron tablas en el esquema 'public'.")
                    return

                print("Columnas y primeros 5 registros de cada tabla:")
                for table in tables:
                    table_name = table[0]

                    # Asegurar que el nombre de la tabla esté entre comillas si contiene mayúsculas
                    formatted_table_name = f'"{table_name}"' if not table_name.islower() else table_name

                    # Obtener las columnas de la tabla
                    try:
                        cursor.execute("""
                        SELECT column_name
                        FROM information_schema.columns
                        WHERE table_schema = 'public' AND table_name = %s
                        """, (table_name,))
                        columns = cursor.fetchall()
                        print(f"\nTabla: {table_name}")
                        if columns:
                            print("Columnas:")
                            for column in columns:
                                print(f" - {column[0]}")
                        else:
                            print(" - Sin columnas.")

                        # Obtener los primeros 5 registros de la tabla actual
                        query_data = f"SELECT * FROM {formatted_table_name} LIMIT 5"
                        cursor.execute(query_data)
                        records = cursor.fetchall()

                        #if records:
                        #    print("Primeros 5 registros:")
                        #    for record in records:
                        #        print(record)
                        #else:
                        #    print(" - Sin registros.")
                    except Exception as e:
                        print(f"Error al obtener datos de la tabla '{table_name}': {e}")
                        conn.rollback()  # Reiniciar la transacción después de un error
    except Exception as e:
        print(f"Error al obtener las tablas: {e}")
    finally:
        release_connection(conn)



# Obtener todas las tablas
def show_all_tables():
    """Muestra todas las tablas en la base de datos."""
    query = """
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public'
    """
    conn = None
    try:
        conn = get_connection()
        if conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                tables = cursor.fetchall()
                if tables:
                    print("Tablas en la base de datos:")
                    for table in tables:
                        print(f" - {table[0]}")
                else:
                    print("No se encontraron tablas en el esquema 'public'.")
    except Exception as e:
        print(f"Error al listar las tablas: {e}")
    finally:
        release_connection(conn)

# Función principal para probar la conexión y mostrar las tablas
def main():
    conn = None
    try:
        # Obtener conexión para probar la conexión
        conn = get_connection()
        if conn:
            print("Conexión exitosa a la base de datos.")
            # Probar consulta
            with conn.cursor() as cursor:
                cursor.execute("SELECT NOW();")
                current_time = cursor.fetchone()[0]
                print(f"Hora actual en la base de datos: {current_time}")
        else:
            print("No se pudo establecer conexión con la base de datos.")
    except Exception as e:
        print(f"Error al conectar con la base de datos: {e}")
    finally:
        release_connection(conn)

    # Mostrar tablas
    #show_all_tables()
    #show_first_5_records_per_table()
    #validate_rut("20.404.282-9")
    show_tickets("20.404.282-9")
# Ejecutar el script
if __name__ == "__main__":
    main()
