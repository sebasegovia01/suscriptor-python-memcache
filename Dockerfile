FROM alpine:3.15

WORKDIR /app

# Instalar Python3, pip y otras dependencias necesarias
RUN apk add --no-cache python3 py3-pip \
    && pip install --upgrade pip

# Copiar el archivo de requisitos y luego instalar las dependencias
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el contenido del directorio actual a /app en el contenedor
COPY . .

# Comando para ejecutar tu aplicación FastAPI
CMD ["python3", "main.py"]
