import pg8000.dbapi
# Configuración por defecto de la base de datos (ajustar si es necesario)
DB_CONFIG = {
    'database': 'chatdb',
    'user': 'postgres',
    'password': '1234',
    'host': 'localhost',
    'port': '5432'
}

def get_connection():
    try:
        conn = pg8000.dbapi.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"[DB ERROR] No se pudo conectar a la base de datos: {e}")
        return None

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
            print("[DB] Base de datos inicializada correctamente.")
        except Exception as e:
            print(f"[DB ERROR] Error inicializando la BD: {e}")
        finally:
            conn.close()

def register_user(username, password):
    conn = get_connection()
    if not conn:
        return False, "Error de conexion a la base de datos."
    
    try:
        cur = conn.cursor()
        try:
            # Check if user exists
            cur.execute("SELECT id FROM usuarios WHERE username = %s", (username,))
            if cur.fetchone():
                return False, "El usuario ya existe."
            
            # Insert new user
            cur.execute("INSERT INTO usuarios (username, password) VALUES (%s, %s)", (username, password))
            conn.commit()
            return True, "Usuario registrado exitosamente."
        finally:
            cur.close()
    except Exception as e:
        return False, f"Error al registrar: {e}"
    finally:
        conn.close()

def authenticate_user(username, password):
    conn = get_connection()
    if not conn:
        return False, "Error de conexion a la base de datos."
    
    try:
        cur = conn.cursor()
        try:
            cur.execute("SELECT password FROM usuarios WHERE username = %s", (username,))
            result = cur.fetchone()
            if result and result[0] == password:
                return True, "Autenticacion exitosa."
            return False, "Usuario o contrasena incorrectos."
        finally:
            cur.close()
    except Exception as e:
        return False, f"Error de autenticacion: {e}"
    finally:
        conn.close()

def get_all_users():
    conn = get_connection()
    if not conn:
        return []
    
    try:
        cur = conn.cursor()
        try:
            cur.execute("SELECT username FROM usuarios")
            users = [row[0] for row in cur.fetchall()]
            return users
        finally:
            cur.close()
    except Exception as e:
        print(f"[DB ERROR] Error obteniendo usuarios: {e}")
        return []
    finally:
        conn.close()

# Si se ejecuta este script directamente, inicializa la DB
if __name__ == "__main__":
    init_db()
