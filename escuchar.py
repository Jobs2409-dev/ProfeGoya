# escuchar.py
import sys
import websocket

proyecto, token = sys.argv[1], sys.argv[2]
url = f"ws://127.0.0.1:8000/ws/projects/{proyecto}/?token={token}"

# Se agrega un timeout de 60 segundos para evitar cierres por inactividad en Windows
ws = websocket.create_connection(url, timeout=60)
print("Conectado. Esperando mensajes (Ctrl+C para salir)...")

while True:
    try:
        mensaje = ws.recv()
        if mensaje:
            print(mensaje)
    except websocket.WebSocketTimeoutException:
        # Si transcurren 60 segundos sin mensajes, el bucle continúa activo
        continue
    except (websocket.WebSocketConnectionClosedException, ConnectionResetError):
        print("\nConexión cerrada por el servidor.")
        break
    except KeyboardInterrupt:
        print("\nDesconectado manualmente.")
        ws.close()
        break
