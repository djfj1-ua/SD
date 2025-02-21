from sys import argv
import socket
import kafka
from json import dumps
import threading
import time

#CENTRAL tiene que tener varios hilos para
#autenticación, escuchar taxis, envío de... etc
#"como 6 o 8 módulos distintos y cada uno funciona"

#Lo que hay que tener básicamente en el "main":
#thread1.thread = handleclient = autenticacion taxi
#thread2.thread = handleclient = producer taxi (lo que sea eso)
#thread3.thread = handleclient = consumer taxi
#gestión de tráfico
#...

#Vale, reflexión mía
#1: hilo_aut_taxi ya es un hilo para escuchar la autenticación de los taxis
#2: Central necesita KafkaConsumir un topic de movimientos N,NE,E,SE... de taxis
#3: Central es el que produce el mapa, KafkaProduce el topic mapa
    #Y el mapa es una variable global, ya que el profe dijo que eso haría falta
#4: Enviar órdenes asíncronas a los taxis debería ser otro módulo que KafkaProduzca
    #y los taxis escuchen
#5: Deberá KafkaConsumir los servicios de los clientes
#6: Y deberá KafkaProducir contestaciones a los clientes sobre el estado del taxi y viaje
#Vale, podemos hacerlo

HEADER = 64
SERVER = socket.gethostbyname(socket.gethostname())
FORMAT = 'utf-8'

# Inicializa el mapa y las localizaciones configuradas en mapa.txt
def configurarMapa():
    mapa = list()
    for i in range(20):
        fila = list()
        for j in range(20):
            fila.append(' ')
        mapa.append(fila)
    
    localizaciones = open('mapa.txt')
    for linea in localizaciones:
        loc = linea.strip('<>\n').split('><')

        loc_ID = loc[0]
        loc_coord_x = int(loc[1]) #Equivale a la columna
        loc_coord_y = int(loc[2]) #Equivale a la fila
        mapa[loc_coord_y-1][loc_coord_x-1] = loc_ID

    return mapa

# Evalúa si un taxi (según ID) está en el fichero de taxis disponibles taxis.txt y si ya existe en el programa
def disponible(IDTaxi, disponible):#Modificar esto para json
    taxis = open('taxis.txt')
    for taxi in taxis:
        taxi = taxi.strip('\n')
        if taxi == IDTaxi:
            for disp in disponible:
                if disp[1] == int(taxi):
                    return False
            return True
    return False

#def modulo_mapa():
#    print("Soy el módulo mapa")
#    mapa_producer = KafkaProducer(
#        bootstrap_servers=[f"{BROKER_IP}:{BROKER_PORT}"],
#        value_serializer=lambda x:dumps(x).encode(FORMAT),
#        api_version="3.8.0" #Necesario para que detecte el broker, por algún motivo
#    )

#    mapa_producer.send('mapa', value=3)

def vaciarTaxi(id,disponible,self):
    for taxi in disponible:
        if int(taxi[0]) == int(id):
            with self.disponible_lock:
                taxi[0] = 0

def comprobarTaxi(disponible,self):
    with self.disponible_lock:
        for taxi in disponible:
            if taxi[0] == 0:
                return taxi[1]
        return -1

def ocuparTaxi(id_taxi, id_cliente,disponible,self):
    for taxi in disponible:
        if taxi[1] == id_taxi:
            with self.disponible_lock:
                taxi[0] = id_cliente

def movtaxi(taxi):

    postaxi = kafka.KafkaConsumer(bootstrap_servers=ADDRK, auto_offset_reset='latest',enable_auto_commit=True)
    topic_partition = kafka.TopicPartition('movements_taxi',1)
    postaxi.assign([topic_partition])

    for post in postaxi:
        if int(post.key.decode(FORMAT)) == int(taxi):
            print(f'Coordenadas donde esta el taxi -> {post.value.decode(FORMAT)}')#Esto es para el mapa
            if f'{post.value.decode(FORMAT)}' == f'FIN':
                postaxi.close()
                break
    postaxi.close()

def movcliente(cliente, destino):

    partes = destino.split(',')
    dest = f'{partes[0]}:{partes[1]}'

    producercli = kafka.KafkaProducer(bootstrap_servers=ADDRK, acks='all')

    poscliente = kafka.KafkaConsumer(bootstrap_servers=ADDRK, auto_offset_reset='latest',enable_auto_commit=True)
    topic_partition = kafka.TopicPartition('movements_cliente',0)
    poscliente.assign([topic_partition])

    for posc in poscliente:
        if int(posc.key.decode(FORMAT)) == int(cliente):
            print(f'Coordenadas donde esta el cliente -> {posc.value.decode(FORMAT)}')
            producercli.send('movements_cliente',partition=1,value=f'{posc.value.decode(FORMAT)}'.encode(FORMAT),key=f'{cliente}'.encode(FORMAT))
            producercli.flush()
            if f'{dest}' == f'{posc.value.decode(FORMAT)}':
                break
    poscliente.close()
    
#Partes[0] -> Destino
#Partes[1] -> cliente
#Partes[2] -> Posicion cliente
#Partes[3] -> id_taxi
def movimiento(destino, cliente, pos, taxi):
    print(f'{destino}')
    producer = kafka.KafkaProducer(bootstrap_servers=ADDRK, acks='all')
    producer.send('movements_taxi',partition=0,value=f'{destino}:{cliente}:{pos}'.encode(FORMAT),key=f'{taxi}'.encode(FORMAT))
    producer.flush()

    #Hilos para controlar los movimientos del taxi y del cliente
    threadt = threading.Thread(target=movtaxi, args=(taxi,))
    threadc = threading.Thread(target=movcliente, args=(cliente,destino))
    threadt.start()
    threadc.start()

    threadc.join()
    threadt.join()

def recv_instrucciones(cliente, instruccion, taxis, producer,self):
    partes = instruccion.value.decode(FORMAT).split(':')
    if partes[0] == 'NEXT':
        if instruccion.key.decode(FORMAT) == f'{cliente}':
                vaciarTaxi(cliente,taxis,self)
    else:#Cuando envia una instruccion para llamar a un taxi
        if instruccion.key.decode(FORMAT) == f'{cliente}':
                print(f'Instruccion -> {instruccion.value.decode(FORMAT)}')
                time.sleep(0.5)
                id_taxi = comprobarTaxi(taxis,self)#Comprobar si hay un taxi libre
                if id_taxi != -1:#Si hay taxi libre
                    producer.send('cliente',partition=1,value=f'El taxi con el id {id_taxi} va de camino.'.encode(FORMAT), key=f'{cliente}'.encode(FORMAT))
                    producer.flush()
                    ocuparTaxi(id_taxi, int(cliente),taxis,self)#Funcion para cambiar el estado de un taxi de libre a ocupado
                    #Hacer que el taxi vaya a por el cliente -> Instruccion:ID:posicionCliente
                    print(f'Instruccion -> {instruccion.value.decode(FORMAT)}')
                    threadmov = threading.Thread(target=movimiento, args=(partes[0],partes[1],partes[2],id_taxi))
                    threadmov.start()
                    threadmov.join()
                else:#Si no hay ningun taxi libre
                    producer.send('cliente',partition=1,value=f'WAIT'.encode(FORMAT), key=f'{cliente}'.encode(FORMAT))
                    producer.flush()
                time.sleep(1)
                producer.send('cliente',partition=1,value=f'FIN'.encode(FORMAT), key=f'{cliente}'.encode(FORMAT))
                producer.flush()

#El topic cliente tiene dos particiones, 
#La particion 0 se usa para consumir los mensajes que envia el cliente
#La particion 1 se usa para enviar los mensajes al cliente
def handle_customer(taxis,self):
    partes = []
    instruccion = ''

    #Creo un consumidor y le asigno una particion del topic cliente
    consumerInstrucciones = kafka.KafkaConsumer(bootstrap_servers=ADDRK, auto_offset_reset='latest',enable_auto_commit=True)
    topic_partition = kafka.TopicPartition('cliente',0)
    consumerInstrucciones.assign([topic_partition])

    #Creo un productor
    producer = kafka.KafkaProducer(bootstrap_servers=ADDRK, acks='all')

    print(f'Mensajes enviados del cliente a la central por kafka:\n')
    for instruccion in consumerInstrucciones:
        print(f'{instruccion.value.decode(FORMAT)}')

        #Separo el mensaje con delimitadores, 
        #La primera parte es el mensaje, la segunda el id del cliente y la tercera la posicion del cliente
        partes = instruccion.value.decode(FORMAT).split(':')

        #Mensaje para iniciar la comunicacion con el cliente
        if partes[0] == 'INIT':
            time.sleep(0.5)
            print(f'Empiezan los mensajes del cliente -> {partes[1]}')
            if comprobarTaxi(taxis,self) == -1:
                producer.send('cliente',partition=1,value=f'WAIT'.encode(FORMAT), key=f'{partes[1]}'.encode(FORMAT))
            else:
                producer.send('cliente',partition=1,value=f'True'.encode(FORMAT), key=f'{partes[1]}'.encode(FORMAT))
            producer.flush()
        
        else:
            recv_instrucciones(partes[1],instruccion,taxis,producer,self)
    else:
        consumerInstrucciones.close()

def handle_taxi(conn, addr, taxi_disponible,self):
    print(f"[NUEVA CONEXION] {addr} connected.")
    aut = False
    connected = True
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            aut = disponible(msg, taxi_disponible)
            if aut == True:
                conn.send(f'OK'.encode(FORMAT))
                print(f'Taxi autenticado con exito.')
                with self.disponible_lock:
                    taxi_disponible.append([0,int(msg)])
                    for taxi in taxi_disponible:
                        print(f'Taxis en el array -> {taxi}')
            else:
                conn.send(f'KO'.encode(FORMAT))
                print(f'Error al autenticar taxi.')
    conn.close()

def handle_auth(taxis,self):
    auth_taxi = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    auth_taxi.bind(ADDR)
    auth_taxi.listen()

    print(f'Esperando taxi para autenticar.')
    while True:
        conn, addr = auth_taxi.accept()
        thread = threading.Thread(target=handle_taxi, args=(conn, addr, taxis,self))
        thread.start()

class Central:
    def __init__(self, args):
        global PORT, BROKER_IP, BROKER_PORT, ADDR, ADDRK
        
        #Instanciar los argumentos para conectarnos al Broker
        PORT = args.port
        BROKER_IP = args.broker_ip
        BROKER_PORT = args.broker_port

        #IP y puerto para los sockets
        ADDR = (SERVER, int(PORT))

        #IP y puerto para kafka
        ADDRK = f'{BROKER_IP}:{BROKER_PORT}'

        # Inicializar bloqueos
        self.disponible_lock = threading.Lock()

    def serve(self):
        #Array donde almaceno los taxis disponibles, tiene dos valores cada elemento
        #El primer valor es el ID del cliente, si no tiene cliente será -1
        #El segundo valor sera el ID del taxi
        disponible = []

        #Hilo para autenticar los taxis
        auth_thread = threading.Thread(target=handle_auth,args=(disponible,self))
        auth_thread.start()
        
        #Hilo para leer las instrucciones de los clientes
        read_customer = threading.Thread(target=handle_customer, args=(disponible,self))
        read_customer.start()

        #Falta hilo para la comunicación del mapa y las posiciones con los taxis con kafka