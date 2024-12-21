FROM python:3.10-slim-bullseye

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

# No need to create a sockets directory
# RUN mkdir -p /app/sockets && chmod -R 777 /app/sockets

# Remove the VOLUME directive as it's not needed for TCP/IP communication
# VOLUME ["/app/sockets"]

EXPOSE 8000 

# Bind Gunicorn to TCP port 8000 instead of a Unix socket
CMD ["gunicorn", "--workers", "3", "--bind", "0.0.0.0:8000", "catalog_service.wsgi:application"]
