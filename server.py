import socket
import select
import threading
import db

# Diccionario para guardar los clientes autenticados: {socket_del_cliente: "nombre_de_usuario"}
clientes_activos = {}
# Lista de todos los sockets de clientes conectados (autenticados o no)
sockets_conectados = []

def broadcast(mensaje, remitente_socket=None):
    """Envía un mensaje a todos los clientes AUTENTICADOS, excepto al remitente."""
    for cliente_sock in list(clientes_activos.keys()):
        if cliente_sock != remitente_socket:
            try:
                cliente_sock.sendall(mensaje.encode('utf-8'))
            except Exception:
                desconectar_cliente(cliente_sock)

def desconectar_cliente(sock):
    """Maneja la desconexión de un cliente de forma segura."""
    if sock in sockets_conectados:
        sockets_conectados.remove(sock)
    if sock in clientes_activos:
        usuario = clientes_activos[sock]
        del clientes_activos[sock]
        broadcast(f"[SISTEMA] {usuario} ha abandonado el chat.")
        print(f"[DESCONEXIÓN] {usuario} se ha ido.")
    try:
        sock.close()
    except:
        pass

def comandos_servidor():
    """Hilo dedicado a escuchar los comandos que tipeamos en la consola del servidor."""
    while True:
        try:
            comando = input()
            if comando == '/all-users':
                print("\n--- BASE DE DATOS DE USUARIOS ---")
                usuarios = db.get_all_users()
                if usuarios:
                    for user in usuarios:
                        print(f"- {user}")
                else:
                    print("No hay usuarios registrados o error de DB.")
                print("---------------------------------\n")
        except EOFError:
            break

def manejar_datos_cliente(sock):
    """Procesa los datos recibidos de un socket."""
    try:
        data = sock.recv(1024)
        if not data:
            desconectar_cliente(sock)
            return

        mensaje = data.decode('utf-8').strip()
        if not mensaje:
            return

        # Si el usuario ya está autenticado
        if sock in clientes_activos:
            usuario = clientes_activos[sock]
            if mensaje == '/salir':
                desconectar_cliente(sock)
            elif mensaje.startswith("/all "):
                contenido = mensaje[5:]
                mensaje_formateado = f"[{usuario} a todos]: {contenido}"
                print(f"[BROADCAST] {mensaje_formateado}")
                broadcast(mensaje_formateado, remitente_socket=sock)
            else:
                sock.sendall(f"Server recibió en privado: {mensaje}".encode('utf-8'))
        else:
            # Cliente NO autenticado, esperar /login o /register
            if mensaje.startswith("/register "):
                partes = mensaje.split(" ")
                if len(partes) >= 3:
                    u = partes[1]
                    p = " ".join(partes[2:])
                    success, msg = db.register_user(u, p)
                    sock.sendall(f"REGISTER_RES: {msg}".encode('utf-8'))
                else:
                    sock.sendall(b"ERROR: Formato incorrecto. Uso: /register <usuario> <password>")
            elif mensaje.startswith("/login "):
                partes = mensaje.split(" ")
                if len(partes) >= 3:
                    u = partes[1]
                    p = " ".join(partes[2:])
                    success, msg = db.authenticate_user(u, p)
                    if success:
                        sock.sendall(b"AUTH_SUCCESS: Autenticacion exitosa. Ya puedes chatear con /all <mensaje>.")
                        clientes_activos[sock] = u
                        print(f"[AUTH OK] {u} ha entrado al chat.")
                        broadcast(f"[SISTEMA] {u} se ha unido al chat.")
                    else:
                        sock.sendall(f"AUTH_FAIL: {msg}".encode('utf-8'))
                else:
                    sock.sendall(b"ERROR: Formato incorrecto. Uso: /login <usuario> <password>")
            elif mensaje == '/salir':
                desconectar_cliente(sock)
            else:
                sock.sendall(b"AUTH_REQ: Debes autenticarte. Uso: /login <user> <pass> o /register <user> <pass>")

    except ConnectionResetError:
        desconectar_cliente(sock)
    except Exception as e:
        print(f"[ERROR MANEJANDO CLIENTE] {e}")
        desconectar_cliente(sock)

def iniciar_servidor():
    HOST = "127.0.0.1"
    PORT = 12345

    # Inicializar la base de datos si es necesario
    db.init_db()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f'[ESCUCHANDO] Servidor activo en {HOST}:{PORT}')

    # Arrancamos el hilo para tipear comandos desde el server
    hilo_comandos = threading.Thread(target=comandos_servidor, daemon=True)
    hilo_comandos.start()

    sockets_conectados.append(server_socket)

    try:
        while True:
            # select.select toma (listas_de_lectura, listas_de_escritura, listas_de_errores)
            # Retorna los sockets que están listos para ser procesados
            leer_sockets, _, errores_sockets = select.select(sockets_conectados, [], sockets_conectados)

            for sock in leer_sockets:
                # Si el socket listo es el servidor, significa que hay una nueva conexión
                if sock == server_socket:
                    client_socket, addr = server_socket.accept()
                    print(f"[NUEVA CONEXIÓN] {addr} conectando...")
                    sockets_conectados.append(client_socket)
                    # Enviar mensaje automático de autenticación obligatorio al conectar
                    client_socket.sendall(b"AUTH_REQ: Bienvenido. Por favor ingresa /login <user> <pass> o /register <user> <pass>")
                else:
                    # Es un socket de cliente enviando datos
                    manejar_datos_cliente(sock)

            for sock in errores_sockets:
                desconectar_cliente(sock)

    except KeyboardInterrupt:
        print("\n[APAGANDO] Servidor cerrándose...")
    finally:
        for s in sockets_conectados:
            s.close()
        server_socket.close()

if __name__ == "__main__":
    iniciar_servidor()