FROM python:3.10-slim

# Evitar que Python escriba archivos .pyc y forzar salida stdout/stderr sin buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copiar e instalar dependencias
COPY src/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente y las plantillas
COPY src/ /app/

# Copiar el modelo al path esperado por la inferencia en Docker (/entrenamiento)
COPY entrenamiento/seadd_morfologia_savedmodel/ /entrenamiento/seadd_morfologia_savedmodel/

# Exponer el puerto 8000 (donde escucha FastAPI)
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["python", "main.py"]
