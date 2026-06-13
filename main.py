import os
import sys

# Agregar el directorio raíz al path de Python para evitar errores de importación
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db import init_db
from server.server import iniciar_servidor

def main():
    print("[MAIN] Iniciando aplicación de chat...")
    # Inicializa la base de datos (con fallback a diccionario local)
    init_db()
    # Arranca el servidor de sockets
    iniciar_servidor()

if __name__ == "__main__":
    main()
