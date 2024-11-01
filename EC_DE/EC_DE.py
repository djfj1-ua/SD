#Digital Engine
import socket
import threading
import kafka
import time

import kafka.producer

HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
AUTH = 'KO'

CENTRAL_IP = CENTRAL_PORT = BROKER_IP = BROKER_PORT = ID = None

def handle_client(conn, addr):
    print(f"[NUEVA CONEXION] {addr} connected.")

    connected = True
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            if msg == 'OK':
                print(f" He recibido del cliente [{addr}] el mensaje: {msg}")
            elif msg == 'KO':
                print('Parar taxi, error en el sensor')
                #Enviar mensaje a la central, para que pare el taxi
            elif msg == 'OFF':
                print('Cerrando conexion')
                conn.close()     
                connected = False

def send(msg, client):
    message = f'{msg}'.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)

def start(server):
    server.listen()
    print(f"[LISTENING] Servidor a la escucha en {SERVER}")
    while True:
        try:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
        except Exception as e:
            print(e)

def servidor(self):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    print("[STARTING] Servidor inicializándose...")
    start(server)

#El topic movements_taxi tiene dos particiones, 
#La particion 0 se usa para consumir los mensajes que envia la central
#La particion 1 se usa para enviar los mensajes a la central
def movements(self):
    print(f'Funcion para realizar los movimientos del taxi.')
    consumer = kafka.KafkaConsumer(bootstrap_servers=ADDR, auto_offset_reset='latest',enable_auto_commit=True)
    topic_partition = kafka.TopicPartition('movements_taxi',0)
    consumer.assign([topic_partition])

    for direccion in consumer:
        if direccion.key.decode(FORMAT) == self._taxi_id_:
            #Taxi pasa a estar ocupado
            self._estado_ = 1
            print(f'Mensaje -> {direccion.value.decode(FORMAT)}')
            #Partes[0] -> Destino
            #Partes[1] -> cliente
            #Partes[2] -> Posicion cliente
            #partes = direccion.value.decode(FORMAT).split(':')
            #producer = kafka.KafkaProducer(bootstrap_servers=ADDR, acks='all')




            
        
def client(self):#Envia id del taxi para autenticacion
        global AUTH
        print(f'Proceso de autenticado.')
        ADDR = (CENTRAL_IP, CENTRAL_PORT)

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Bucle de reintento hasta que se logre la conexión
        while True:
            try:
                print(f'Intentando autenticar en {ADDR}...')
                client.connect(ADDR)  # Intentar conectar
                print(f"Conexión establecida en [{ADDR}]")
                break  # Salir del bucle si la conexión es exitosa
            except (socket.error, ConnectionRefusedError) as e:
                print(f"Error al conectar con la central: {e}. Reintentando la conexión...")
                time.sleep(3)

        # Enviar id el taxi
        send(self._taxi_id, client)
        AUTH = client.recv(2048).decode(FORMAT)
        print("Recibo del Servidor: ", AUTH)#Recibo el resultado de la autenticacion
        client.close()

        if AUTH == 'OK':
            print(f'Se ha autenticado con exito.')
        else:
            print(f'El taxi no se ha podido autenticar')

class Engine:
    def __init__(self, args):
        global CENTRAL_IP, CENTRAL_PORT, BROKER_IP, BROKER_PORT
        self._taxi_id_ = args.taxi_id
        self._pos_ = [1,1]
        self._estado_ = 0
        
        #Instanciar los argumentos para conectarnos al Broker
        CENTRAL_IP = args.central_ip
        CENTRAL_PORT = args.central_port
        BROKER_IP = args.broker_ip
        BROKER_PORT = args.broker_port

        ADDR = f'{BROKER_IP}:{BROKER_PORT}'

    def serve(self):#Inicializacion del servidor
        threadClient = threading.Thread(client(self))
        threadClient.start()
        threadClient.join()#Espero a que termine la autenticacion
        if AUTH == 'OK':
            threadServe = threading.Thread(servidor(self))#Hacer que cuando reciba KO de un sensor pare el taxi
            threadMovement = threading.Thread(movements(self))
            threadServe.start()
            threadMovement.start()
            #Hay que hacer que el taxi cambie de posicion para ir acercandose al cliente, y que se mueva a su destino