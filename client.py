import socket
import threading
import sys

HOST = "127.0.0.1"
PORT = 12345

def recibir_mensajes(sock):
    """Hilo secundario dedicado EXCLUSIVAMENTE a escuchar al servidor."""
    while True:
        try:
            data = sock.recv(1024).decode('utf-8')
            if not data:
                print("\n[SISTEMA] El servidor cerró la conexión.")
                sock.close()
                sys.exit(0) # Forzamos el cierre del programa
            
            # Truco visual para que el mensaje no pise el prompt de "Tú: "
            print(f"\n{data}\nTú: ", end="", flush=True)
        except Exception:
            # Si el socket se cierra desde el hilo principal, esto saltará
            break

def iniciar_cliente():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((HOST, PORT))
    except ConnectionRefusedError:
        print("[ERROR] El servidor no está activo.")
        return

    print("Conectado al servidor.")

    # --- FASE DE CHAT Y AUTENTICACION (Asíncrona multihilo) ---
    # Lanzamos el hilo de recepción en modo daemon (muere si se cierra el programa)
    hilo_escucha = threading.Thread(target=recibir_mensajes, args=(s,), daemon=True)
    hilo_escucha.start()

    # El hilo principal se queda acá esperando que el usuario escriba
    try:
        while True:
            mensaje = input("Tú: ")
            
            if mensaje == '/salir':
                s.sendall(mensaje.encode('utf-8'))
                print("Desconectando...")
                break
                
            # Si tocamos enter sin escribir nada, no mandamos paquete vacío
            if mensaje:
                s.sendall(mensaje.encode('utf-8'))
                
    except KeyboardInterrupt:
        pass # Captura si el usuario aprieta Ctrl+C
    finally:
        s.close()

if __name__ == "__main__":
    iniciar_cliente()