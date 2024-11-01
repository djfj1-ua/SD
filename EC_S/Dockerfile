FROM python:3.9-alpine

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar requirements.txt al directorio de trabajo
COPY requirements.txt ./

# Instalar dependencias y screen
RUN apk add --no-cache screen && pip install -r requirements.txt

# Copiar el resto de los archivos al directorio de trabajo
COPY EC_S.py main.py ./

# Cambiar los permisos del fichero
RUN chmod +x main.py

# Ejecutar el script principal
CMD python main.py \
    --engine-ip $ENGINE_IP \
    --engine-port $ENGINE_PORT
