import pg8000.dbapi

# Configuración por defecto de la base de datos
DB_CONFIG = {
    'database': 'chatdb',
    'user': 'postgres',
    'password': '1234',
    'host': 'localhost',
    'port': '5432'
}

# Diccionario prefabricado como base de datos en memoria
USERS_DICT = {}

def get_connection():
    return pg8000.dbapi.connect(**DB_CONFIG)

def init_db():
    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor()
            try:
                cur.execute('''
                    CREATE TABLE IF NOT EXISTS usuarios (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        password VARCHAR(255) NOT NULL
                    )
                ''')
            finally:
                cur.close()
            conn.commit()
            print("[DB] Base de datos Postgres inicializada correctamente.")
            
            # Cargar usuarios existentes de Postgres al diccionario en memoria
            try:
                cur = conn.cursor()
                cur.execute("SELECT username, password FROM usuarios")
                for row in cur.fetchall():
                    USERS_DICT[row[0]] = row[1]
                cur.close()
            except Exception:
                pass
        except Exception as e:
            print(f"[DB WARN] Error inicializando Postgres: {e}. Usando base de datos en memoria (diccionario).")
        finally:
            conn.close()
    else:
        print("[DB] Usando base de datos prefabricada en memoria (diccionario de Python, nada de SQL).")

def register_user(username, password):
    # Validar en base de datos en memoria
    if username in USERS_DICT:
        return False, "El usuario ya existe."
    
    # Intentar comprobar y persistir en Postgres si está disponible
    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor()
            try:
                # Comprobar si existe en Postgres
                cur.execute("SELECT id FROM usuarios WHERE username = %s", (username,))
                if cur.fetchone():
                    return False, "El usuario ya existe."
                
                # Insertar en Postgres
                cur.execute("INSERT INTO usuarios (username, password) VALUES (%s, %s)", (username, password))
                conn.commit()
            finally:
                cur.close()
        except Exception as e:
            print(f"[DB WARN] No se pudo guardar en Postgres: {e}. Guardado en memoria.")
        finally:
            conn.close()
            
    # Guardar en memoria
    USERS_DICT[username] = password
    return True, "Usuario registrado exitosamente."


def authenticate_user(username, password):
    # Validar con base de datos en memoria primero
    if username in USERS_DICT:
        if USERS_DICT[username] == password:
            return True, "Autenticacion exitosa."
        return False, "Usuario o contrasena incorrectos."
        
    # Intentar con Postgres por si hay desincronización
    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor()
            try:
                cur.execute("SELECT password FROM usuarios WHERE username = %s", (username,))
                result = cur.fetchone()
                if result:
                    USERS_DICT[username] = result[0]  # Sincronizar en memoria
                    if result[0] == password:
                        return True, "Autenticacion exitosa."
            finally:
                cur.close()
        except Exception:
            pass
        finally:
            conn.close()
            
    return False, "Usuario o contrasena incorrectos."

def get_all_users():
    # Intentar sincronizar desde Postgres si se puede conectar
    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor()
            try:
                cur.execute("SELECT username, password FROM usuarios")
                for row in cur.fetchall():
                    USERS_DICT[row[0]] = row[1]
            finally:
                cur.close()
            conn.close()
        except Exception:
            pass
            
    # Retornar los usuarios del diccionario en memoria
    return list(USERS_DICT.keys())

# Si se ejecuta este script directamente, inicializa la DB
if __name__ == "__main__":
    init_db()

