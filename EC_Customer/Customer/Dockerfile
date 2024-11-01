FROM python:3.9-alpine

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar requirements.txt al directorio de trabajo
COPY requirements.txt ./

# Instalar dependencias y screen
RUN apk add --no-cache screen && pip install -r requirements.txt

# Copiar el resto de los archivos al directorio de trabajo
COPY EC_Customer.py main.py EC_locations.json EC_Requests.json ./

# Cambiar los permisos del fichero
RUN chmod +x main.py

# Ejecutar el script principal
CMD python main.py \
    --broker-ip $BROKER_IP \
    --broker-port $BROKER_PORT \
    --customer-id $CUSTOMER_ID