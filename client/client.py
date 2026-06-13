import socket
import threading
import sys

HOST = "127.0.0.1"
PORT = 12345

# Variable global para coordinar el fin del cliente
client_running = True

def recibir_mensajes(sock):
    """Hilo secundario dedicado EXCLUSIVAMENTE a escuchar al servidor."""
    global client_running
    while client_running:
        try:
            data = sock.recv(1024).decode('utf-8')
            if not data:
                if client_running:
                    print("\n[SISTEMA] El servidor cerró la conexión.")
                break
            
            # Borrar la línea actual para evitar el prompt duplicado "Tú: "
            sys.stdout.write("\r" + " " * 6 + "\r")
            sys.stdout.write(data + "\n")
            sys.stdout.write("Tú: ")
            sys.stdout.flush()
        except Exception:
            break
    client_running = False
    try:
        sock.close()
    except:
        pass
    print("\n[SISTEMA] Conexión cerrada. Presiona Enter para salir.")
    sys.exit(0)

def enviar_mensajes(sock):
    """Hilo dedicado EXCLUSIVAMENTE a enviar mensajes desde la consola al servidor."""
    global client_running
    try:
        while client_running:
            mensaje = input("Tú: ")
            if not client_running:
                break
            
            if mensaje == '/help':
                print("\n--- COMANDOS DISPONIBLES ---")
                print("  /register <usuario> <password> : Registrar un nuevo usuario y loguearse automáticamente.")
                print("  /login <usuario> <password>    : Iniciar sesión con un usuario existente.")
                print("  /logout                        : Cerrar sesión sin cerrar la conexión.")
                print("  /all <mensaje>                 : Enviar un mensaje a todos los usuarios del chat.")
                print("  /exit                         : Desconectarse del servidor y cerrar el programa.")
                print("  /help                          : Mostrar este menú de ayuda.")
                print("----------------------------\n")
                continue

            if mensaje == '/exit':
                sock.sendall(mensaje.encode('utf-8'))
                print("Desconectando...")
                client_running = False
                break
                
            if mensaje:
                sock.sendall(mensaje.encode('utf-8'))
    except (EOFError, KeyboardInterrupt):
        client_running = False
    except Exception as e:
        print(f"\n[ERROR] Error al enviar: {e}")
    finally:
        client_running = False
        try:
            sock.close()
        except:
            pass

def iniciar_cliente():
    global client_running
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((HOST, PORT))
    except ConnectionRefusedError:
        print("[ERROR] El servidor no está activo.")
        return

    print("Conectado al servidor.")

    # --- FASE DE CHAT Y AUTENTICACION (Asíncrona multihilo) ---
    # Lanzamos el hilo de recepción y el hilo de envío
    hilo_escucha = threading.Thread(target=recibir_mensajes, args=(s,), daemon=True)
    hilo_envio = threading.Thread(target=enviar_mensajes, args=(s,), daemon=True)
    
    hilo_escucha.start()
    hilo_envio.start()

    # Mantener el hilo principal vivo mientras sigan corriendo los hilos de comunicación
    try:
        while client_running:
            hilo_envio.join(timeout=0.5)
            hilo_escucha.join(timeout=0.5)
    except KeyboardInterrupt:
        client_running = False
        print("\nCerrando cliente...")
    finally:
        s.close()

if __name__ == "__main__":
    iniciar_cliente()