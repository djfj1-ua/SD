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
            #if msg == 'OK':
                #print(f" He recibido del cliente [{addr}] el mensaje: {msg}")
            if msg == 'KO':
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

def camino(xc, yc, pos,producer,op,cliente,self):
    pos[0] = int(pos[0])
    pos[1] = int(pos[1])
    
    while (xc,yc) != (pos[0],pos[1]):

        auxx = auxy = 0
        dist_abajo = dist_arriba = dist_derecha = dist_izquierda = 0
        #Calculo si esta mas cerca el cliente por la derecha o por la izquierda
        if xc != pos[0]:
            dist_derecha = (xc - pos[0]) % 20
            dist_izquierda = (pos[0] - xc) % 20

            #Voy por el camino mas corto
            if dist_derecha < dist_izquierda:
                auxx = 1
            else:
                auxx = -1

            #Actualizo la posicion
            #El mas y menos 1 es para ajustar que el mapa sea de [0,19] para el % y luego vuelve a ponerlo a [1,20]
            pos[0] = (pos[0] + auxx - 1) % 20 + 1

        #Calculo si esta mas cerca por arriba o por abajo
        if yc != pos[1]:
            dist_abajo = (yc - pos[1]) % 20
            dist_arriba = (pos[1] - yc) % 20

            #Si el cliente esta a la derecha
            if dist_abajo < dist_arriba:
                auxy = 1
            else:#Si el cliente esta a la izquierda
                auxy = -1

            #Actualizo la posicion
            #El mas y menos 1 es para ajustar que el mapa sea de [0,19] para el % y luego vuelve a ponerlo a [1,20]
            pos[1] = (pos[1] + auxy - 1) % 20 + 1 

        print(f'Posicion: {pos[0]}:{pos[1]}')

        if op == 0:
            #Envio la posicion del taxi a la central
            producer.send('movements_taxi',partition=1,value=f'{pos[0]}:{pos[1]}'.encode(FORMAT),key=f'{self._taxi_id_}'.encode(FORMAT))
            producer.flush()
        else:
            producer.send('movements_taxi',partition=1,value=f'{pos[0]}:{pos[1]}'.encode(FORMAT),key=f'{self._taxi_id_}'.encode(FORMAT))
            producer.send('movements_cliente',partition=0,value=f'{pos[0]}:{pos[1]}'.encode(FORMAT),key=f'{cliente}'.encode(FORMAT))
            producer.flush()
        time.sleep(1)
    self._pos_ = pos

#El topic movements_taxi tiene dos particiones, 
#La particion 0 se usa para consumir los mensajes que envia la central
#La particion 1 se usa para enviar los mensajes a la central
def movements(self):
    consumer = kafka.KafkaConsumer(bootstrap_servers=ADDRK, auto_offset_reset='latest',enable_auto_commit=True)
    topic_partition = kafka.TopicPartition('movements_taxi',0)
    consumer.assign([topic_partition])

    producer = kafka.KafkaProducer(bootstrap_servers=ADDRK, acks='all')

    for direccion in consumer:

        if int(direccion.key.decode(FORMAT)) == int(self._taxi_id_):
            #Taxi pasa a estar ocupado
            self._estado_ = 'RUN'
            #Partes[0] -> Destino
            #Partes[1] -> cliente
            #Partes[2] -> Posicion cliente
            partes = direccion.value.decode(FORMAT).split(':')

            #Coordenadas cliente
            coord = partes[2].strip('[]').split(', ')
            dest = partes[0].split(',')
            xc, yc = map(int, coord)
            postaxi = [self._pos_[0],self._pos_[1]]
            print(f'PosTaxi -> {postaxi}')

            camino(xc,yc,postaxi,producer,0,partes[1],self)
            print(f'El taxi ha llegado donde esta el cliente.')
            postaxi = [self._pos_[0],self._pos_[1]]
            print(f'PosTaxi -> {postaxi}')
            camino(int(dest[0]),int(dest[1]),postaxi,producer,1,partes[1],self)
            print(f'El cliente ha llegado a su destino')
            #Enviar mensaje de trayecto finalizado
            producer.send('movements_taxi',partition=1,value=f'FIN'.encode(FORMAT),key=f'{self._taxi_id_}'.encode(FORMAT))
            producer.send('movements_cliente',partition=1,value=f'FIN'.encode(FORMAT),key=f'{partes[1]}'.encode(FORMAT))
            producer.flush()
    consumer.close()


            


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
        send(self._taxi_id_, client)
        AUTH = client.recv(2048).decode(FORMAT)
        print("Recibo del Servidor: ", AUTH)#Recibo el resultado de la autenticacion
        client.close()

        if AUTH == 'OK':
            print(f'Se ha autenticado con exito.')
        else:
            print(f'El taxi no se ha podido autenticar')

class Engine:
    def __init__(self, args):
        global CENTRAL_IP, CENTRAL_PORT, BROKER_IP, BROKER_PORT, ADDRK
        self._taxi_id_ = args.taxi_id
        self._pos_ = [1,1]
        self._estado_ = 'END'
        
        #Instanciar los argumentos para conectarnos al Broker
        CENTRAL_IP = args.central_ip
        CENTRAL_PORT = args.central_port
        BROKER_IP = args.broker_ip
        BROKER_PORT = args.broker_port

        ADDRK = f'{BROKER_IP}:{BROKER_PORT}'

    def serve(self):#Inicializacion del servidor
        threadClient = threading.Thread(target=client, args=(self,))
        threadClient.start()
        threadClient.join()#Espero a que termine la autenticacion
        if AUTH == 'OK':
            threadServe = threading.Thread(target=servidor, args=(self,))#Hacer que cuando reciba KO de un sensor pare el taxi
            threadMovement = threading.Thread(target=movements, args=(self,))
            threadServe.start()
            threadMovement.start()
            #Hay que hacer que el taxi cambie de posicion para ir acercandose al cliente, y que se mueva a su destino