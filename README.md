# Chat Multiusuario Asíncrono en Red

Esta aplicación implementa una comunicación asíncrona cliente-servidor a través de sockets TCP en Python, con soporte para hilos concurrentes del lado del cliente e integración con Postgres (y fallback transparente a un diccionario en memoria).

---

Un chat ligero y robusto diseñado para la consola de comandos:
- **Asíncrono**: Recibe y envía mensajes simultáneamente.
- **Seguro**: Autenticación obligatoria antes de chatear.
- **Persistente**: Soporta bases de datos relacionales Postgres, con fallback a memoria local de Python.
- **Multitarea**: Control del servidor por consola local interactiva y soporte para múltiples clientes en paralelo.

---

## Comandos del Servidor

El servidor cuenta con una consola interactiva local que admite los siguientes comandos:

*   `**` (Consola del Servidor)*
    *   `/all-users`: Lista todos los usuarios registrados en el sistema (leyendo del diccionario en memoria sincronizado con la base de datos).
    *   `Ctrl + C` / `KeyboardInterrupt`: Apaga el servidor de forma segura cerrando todos los sockets activos.

---

## Comandos del Cliente

Una vez conectado, cada cliente puede interactuar mediante los siguientes comandos en su consola:

*   `/help`
    *   Muestra un menú de ayuda local detallando todos los comandos disponibles.
*   `/register <usuario> <password>`
    *   Registra una nueva cuenta de usuario. Si tiene éxito, realiza un **inicio de sesión automático** inmediato.
*   `/login <usuario> <password>`
    *   Inicia sesión con credenciales previamente registradas.
*   `/all <mensaje>`
    *   Envía un mensaje de broadcast a todos los usuarios conectados y autenticados en el servidor.
*   `/logout`
    *   Cierra la sesión actual del usuario en el servidor pero mantiene abierta la conexión de red, volviendo a solicitar autenticación (/login o /register).
*   `/exit`
    *   Cierra la sesión actual, se desconecta del servidor de sockets y finaliza el programa del cliente.

---

## Estructura del Proyecto

El proyecto está organizado de la siguiente manera:

```text
networkProgramming_exercises_26/
├── database/
│   └── db.py            # Módulo de base de datos (Postgres y fallback local)
├── server/
│   └── server.py        # Código del Servidor (multiplexación selectiva y comandos de administración)
├── client/
│   └── client.py        # Código del Cliente (hilos duales de envío/recepción y comandos de usuario)
├── main.py              # Punto de entrada unificado para base de datos y servidor
├── requirements.txt     # Dependencias de Python requeridas para Postgres
└── README.md            # Documentación del proyecto (este archivo)
```

### Explicación por Archivo

1.  **[main.py](file:///c:/Users/alumno.ET26/Downloads/networkProgramming_exercises_26/main.py)**
    El punto de entrada principal del lado del servidor. Llama secuencialmente a la inicialización de la base de datos y arranca el bucle de escucha del servidor TCP.
2.  **[database/db.py](file:///c:/Users/alumno.ET26/Downloads/networkProgramming_exercises_26/database/db.py)**
    Maneja las operaciones de almacenamiento de datos. Define un diccionario `USERS_DICT` en memoria que se utiliza como base de datos por defecto. Intenta conectarse a Postgres (`pg8000`) si el servicio está activo, permitiendo registrar y buscar usuarios de forma persistente.
3.  **[server/server.py](file:///c:/Users/alumno.ET26/Downloads/networkProgramming_exercises_26/server/server.py)**
    Implementa el servidor mediante multiplexación no bloqueante con la librería `select`. Maneja el estado de inicio de sesión de los clientes y expone la función `auth` de ejecución automática que obliga a los nuevos sockets a autenticarse.
4.  **[client/client.py](file:///c:/Users/alumno.ET26/Downloads/networkProgramming_exercises_26/client/client.py)**
    Implementa el cliente de chat. Crea dos hilos (`recibir_mensajes` y `enviar_mensajes`) para posibilitar la comunicación asíncrona bidireccional continua sin bloqueos y evita el parpadeo o duplicación del prompt en consola.

### Librerías utilizadas

*   `asn1crypto==1.5.1`: Librería de análisis y serialización rápida de estructuras ASN.1, comúnmente utilizada para verificar certificados y claves criptográficas en protocolos de seguridad.
*   `pg8000==1.31.5`: Conector nativo de Python para bases de datos PostgreSQL (pure-Python), lo que facilita conexiones SQL eficientes sin requerir compiladores ni librerías del sistema.
*   `six==1.17.0`: Biblioteca de compatibilidad que provee funciones de utilidad para suavizar diferencias de sintaxis entre distintas versiones de Python (especialmente Python 2 y 3).
*   `psycopg2-binary==2.9.12`: Adaptador de base de datos PostgreSQL de alto rendimiento para Python, precompilado con dependencias de C para un despliegue rápido y directo.
*   `python-dateutil==2.9.0.post0`: Extensión del módulo estándar `datetime` que facilita el parseo de fechas en múltiples formatos, cálculo de zonas horarias y aritmética de fechas complejas.
*   `scramp==1.4.8`: Implementación del mecanismo de autenticación SCRAM (Salted Challenge Response Authentication Mechanism) necesaria para conectarse de forma segura a servidores modernos de PostgreSQL.
