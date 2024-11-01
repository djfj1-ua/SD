import socket
import sys
import time
import threading

HEADER = 64
FORMAT = 'utf-8'
MSG = 'OK'
running = True

PORT = SERVER = None

def send_messages(client):  # Ahora recibe el cliente
    global MSG, running
    while running:
        try:
            send(MSG, client)  # Pasar el cliente a send
            time.sleep(1)
        except (BrokenPipeError, ConnectionResetError):
            print("Error: La conexión se ha perdido con el servidor.")
            running = False  # Detener el bucle si hay un error en la conexión

def send(msg, client):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)

def input_commands():
    global MSG, running
    while running:
        command = input().strip()
        if command == 'p':
            MSG = 'KO'
        elif command == 't':
            MSG = 'OK'
        elif command == 'q':
            MSG = 'OFF'
            running = False  # Para detener ambos bucles

class Sensor:
    def __init__(self, args):
        global SERVER, PORT
        
        # Instanciar los argumentos para conectarnos al engine
        SERVER = args.engine_ip
        PORT = args.engine_port

    def serve(self):

        print("****** Código del sensor del taxi ****\n\nPara provocar un error: p\nPara volver a OK: t\nPara apagar el sensor: q")
        
        ADDR = (SERVER, PORT)

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        while True:
            try:
                print(f"Intentando conectar al engine en {ADDR}...")
                client.connect(ADDR)  # Intentar conectar
                print(f"Conexión establecida en [{ADDR}]")
                break  # Salir del bucle cuando la conexión sea exitosa
            except (socket.error, ConnectionRefusedError) as e:
                print(f"Error al conectar a {ADDR}: {e}. Reintentando en 5 segundos...")
                time.sleep(5)  # Pausa de 5 segundos antes de intentar de nuevo

        # Crear hilo para enviar mensajes cada segundo
        thread_send = threading.Thread(target=send_messages, args=(client,))  # Pasar el cliente al hilo
        thread_send.start()

        # Manejar los comandos de usuario en el hilo principal
        input_commands()

        # Esperar a que el hilo de envío termine
        thread_send.join()

        # Enviar el mensaje de cierre
        send(MSG, client)
        client.close()
        print("Conexión cerrada.")
