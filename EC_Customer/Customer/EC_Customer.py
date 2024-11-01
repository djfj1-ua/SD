import time
import kafka
import threading
import json

FORMAT='utf-8'

def leer_locations():
    with open("EC_locations.json", "r") as f:
        data = json.load(f)
    locations = {loc["Id"]: list(map(int, loc["POS"].split(','))) for loc in data["locations"]}
    return locations

def leer_requests():
    with open("EC_Requests.json", "r") as f:
        data = json.load(f)
    requests = [req["Id"] for req in data["Requests"]]
    return requests

def obtener_posicion(id_busqueda):
    locations = leer_locations()
    return locations.get(id_busqueda, "ID no encontrado")

#Función para esperar a que termine la ejecución de la instrucción que se le pasa a la central
def finRecorrido(customer):
    consumer = kafka.KafkaConsumer(bootstrap_servers=ADDR)#,auto_offset_reset='earliest')
    topic_partition = kafka.TopicPartition('cliente',1)
    consumer.assign([topic_partition])
    for texto in consumer:
        if int(texto.key.decode(FORMAT)) == int(customer._id_):
            print(f'El cliente {customer._id_} recibe de la central -> {texto.value.decode(FORMAT)}')
            if texto.value.decode(FORMAT) == 'FIN':
                return True
            elif texto.value.decode(FORMAT) == 'WAIT':
                return False
    else:
        consumer.close()
        return

def poscliente(customer):
    poscli = kafka.KafkaConsumer(bootstrap_servers=ADDR, auto_offset_reset='latest',enable_auto_commit=True)
    topic_partition = kafka.TopicPartition('movements_cliente',1)
    poscli.assign([topic_partition])
    for posc in poscli:
        if int(customer._id_) == int(posc.key.decode(FORMAT)):
            print(f'Posicion actual del cliente -> {posc.value.decode(FORMAT)}')
            partes = posc.value.decode(FORMAT).split(':')
            if f'{partes[0]}' == 'FIN':
                poscli.close()
                return
            else:
                customer._pos_[0] = int(partes[0])
                customer._pos_[1] = int(partes[1])
    else:
        poscli.close()
        return

def enviarCentral(instruccion,customer,pos):

    print(f'Enviando instrucción a la central...')
    producer = kafka.KafkaProducer(bootstrap_servers=ADDR) #Cambiar la ip por la de la maquina de despliegue
    instruccion = f'{instruccion}:{customer._id_}:{pos}'
    print(f'Envio -> {instruccion}')
    producer.send('cliente',partition=0,value=instruccion.encode(FORMAT), key=f'{customer._id_}'.encode(FORMAT))
    producer.flush()

    threadc = threading.Thread(target=poscliente, args=(customer,))
    threadc.start()
    if finRecorrido(customer):
        return True
    else:
        return False

def handShake(mensaje,customer):
    time.sleep(1)
    consumer = kafka.KafkaConsumer(bootstrap_servers=ADDR,consumer_timeout_ms=2000)
    topic_partition = kafka.TopicPartition('cliente',1)
    consumer.assign([topic_partition])
    producer = kafka.KafkaProducer(bootstrap_servers=ADDR) #Cambiar la ip por la de la maquina de despliegue
    instruccion = f'{mensaje}:{customer._id_}'
    producer.send('cliente',partition=0,value=instruccion.encode(FORMAT), key=f'{customer._id_}'.encode(FORMAT))
    producer.flush()
    for verificacion in consumer:
        if int(verificacion.key.decode(FORMAT)) == int(customer._id_):
            consumer.close()
            return verificacion.value.decode(FORMAT)
    else:
        consumer.close()
        return False
    

class Customer:

    def __init__(self, args):
        global SERVE, PORT, ADDR, POS
        
        #Instanciar los argumentos para conectarnos al kafka
        SERVE = args.broker_ip
        PORT = args.broker_port
        ADDR = f'{SERVE}:{PORT}'
        
        #Instanciar variables de clase
        self._id_ = args.customer_id
        self._pos_ = [1,18]
    
    def serve(self):
        
        #Leer fichero de las instrucciones del cliente
        instrucciones = leer_requests()

        stop = False
        no_taxi = False

        while stop == False:
            conn = handShake('INIT',self)
            #Mensaje de que el cliente va a empezar a mandar mensajes con las instrucciones
            if conn == 'True':
                stop = True
                print(f'Comprobado que la central esta activa')
                #Bucle para enviar los servicios a la central
                for instruccion in instrucciones:
                    print(f'Instruccion -> {instruccion}')
                    pos = obtener_posicion(instruccion)
                    while True:
                        no_taxi = enviarCentral(f'{pos[0]},{pos[1]}',self,self._pos_)
                        #Mensaje de que el cliente ha terminado de enviar una instruccion
                        handShake(f'NEXT',self) 
                        if no_taxi:
                            break
                        time.sleep(4)
                print(f'No quedan más instrucciones')
                
                #Crear una funcion para añadir destinos a mano
            elif conn == 'WAIT':
                print(f'No hay taxis disponibles.')#Hacer que se quede en espera a que se conecte la central.
                stop = False
            print(f'Cliente en espera.')