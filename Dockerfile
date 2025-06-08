# -------------------------
# Etapa 1: Build (Builder)
# -------------------------
FROM python:3.10-slim AS builder

# Definimos el directorio de trabajo
WORKDIR /app

# Evitamos que Python escriba archivos .pyc y forzamos logs sin buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copiamos solo las dependencias primero (aprovecha cache de Docker)
COPY requirements.txt .

# Construimos las ruedas (wheels) para instalar luego sin internet
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# -------------------------
# Etapa 2: Imagen final
# -------------------------
FROM python:3.10-slim

# Creamos un usuario no-root para mayor seguridad
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Copiamos las ruedas y las instalamos
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache-dir /wheels/* \
    && rm -rf /wheels

# Copiamos el código del proyecto
COPY . .

# Creamos directorio para la base de datos SQLite y archivos estáticos
RUN mkdir -p /app/db /app/staticfiles \
    && chown -R appuser:appuser /app

# Cambiamos al usuario no-root
USER appuser

# Colectamos archivos estáticos
RUN python manage.py collectstatic --noinput

# Exponemos el puerto por donde se accede a la app
EXPOSE 8000

# Script de inicio que ejecuta migraciones y luego inicia el servidor
# Para SQLite es seguro ejecutar migrate en cada inicio
CMD ["sh", "-c", "python manage.py migrate && gunicorn --bind 0.0.0.0:8000 --workers 2 eventhub.wsgi"]