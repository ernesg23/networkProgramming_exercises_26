import socket
import threading

# 1. Base de datos prefabricada de usuarios
DB_USUARIOS = {
    "ernesto": "1234",
    "fede": "pass1",
    "edu": "pass2",
    "admin": "admin"
}

# Diccionario para guardar los clientes autenticados: {socket_del_cliente: "nombre_de_usuario"}
clientes_activos = {}
lock_clientes = threading.Lock() # Evita errores si dos clientes se conectan a la vez

def broadcast(mensaje, remitente_socket=None):
    """Envía un mensaje a todos los clientes conectados, excepto al remitente."""
    with lock_clientes:
        for cliente_sock in clientes_activos:
            if cliente_sock != remitente_socket:
                try:
                    cliente_sock.sendall(mensaje.encode('utf-8'))
                except Exception:
                    pass # El cliente se desconectó repentinamente

def manejar_cliente(client_socket, addr):
    """Maneja la autenticación y la recepción de mensajes de un cliente."""
    print(f"[NUEVA CONEXIÓN] {addr} conectando...")
    
    # --- FASE DE AUTENTICACIÓN ---
    try:
        client_socket.sendall(b"AUTH_REQ: Bienvenido. Por favor, ingresa tu usuario:")
        usuario_ingresado = client_socket.recv(1024).decode('utf-8').strip()
        
        if usuario_ingresado in DB_USUARIOS:
            client_socket.sendall(b"AUTH_SUCCESS: Autenticacion exitosa. Ya puedes chatear.")
            with lock_clientes:
                clientes_activos[client_socket] = usuario_ingresado
            
            print(f"[AUTH OK] {usuario_ingresado} ({addr}) ha entrado al chat.")
            broadcast(f"[SISTEMA] {usuario_ingresado} se ha unido al chat.")
        else:
            client_socket.sendall(b"AUTH_FAIL: Usuario no registrado. Desconectando...")
            print(f"[AUTH FALLIDA] {addr} intento entrar como '{usuario_ingresado}'.")
            client_socket.close()
            return # Terminamos el hilo para este cliente
            
    except Exception as e:
        client_socket.close()
        return

    # --- FASE DE CHAT ---
    try:
        while True:
            mensaje = client_socket.recv(1024).decode('utf-8')
            
            if not mensaje or mensaje == '/salir':
                break
                
            # Verificar si es el comando /all
            if mensaje.startswith("/all "):
                # Extraemos el contenido quitando los primeros 5 caracteres ("/all ")
                contenido = mensaje[5:]
                mensaje_formateado = f"[{usuario_ingresado} a todos]: {contenido}"
                print(f"[BROADCAST] {mensaje_formateado}")
                broadcast(mensaje_formateado, remitente_socket=client_socket)
            else:
                # Comportamiento por defecto (mensaje privado al server)
                client_socket.sendall(f"Server recibió en privado: {mensaje}".encode('utf-8'))

    except ConnectionResetError:
        pass
    finally:
        with lock_clientes:
            if client_socket in clientes_activos:
                usuario = clientes_activos[client_socket]
                del clientes_activos[client_socket]
                broadcast(f"[SISTEMA] {usuario} ha abandonado el chat.")
                print(f"[DESCONEXIÓN] {usuario} ({addr}) se ha ido.")
        client_socket.close()

def comandos_servidor():
    """Hilo dedicado a escuchar los comandos que tipeamos en la consola del servidor."""
    while True:
        comando = input()
        if comando == '/all-users':
            print("\n--- BASE DE DATOS DE USUARIOS ---")
            for user in DB_USUARIOS.keys():
                print(f"- {user}")
            print("---------------------------------\n")

def iniciar_servidor():
    HOST = "127.0.0.1"
    PORT = 12345

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f'[ESCUCHANDO] Servidor activo en {HOST}:{PORT}')

    # Arrancamos el hilo para tipear comandos desde el server
    hilo_comandos = threading.Thread(target=comandos_servidor, daemon=True)
    hilo_comandos.start()

    while True:
        conn, addr = server_socket.accept()
        thread = threading.Thread(target=manejar_cliente, args=(conn, addr))
        thread.start()

if __name__ == "__main__":
    iniciar_servidor()