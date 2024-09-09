#!/bin/sh

# Mantener el dispositivo despierto
termux-wake-lock

# Actualizar los repositorios y instalar dos2unix
pkg update -y
pkg install -y dos2unix

# Convertir el archivo de formato DOS a formato UNIX
dos2unix /data/data/com.termux/files/home/Extractor/sacarCombinado.sh

# Esperar un minuto
sleep 60

# Ejecutar el script combinado
bash /data/data/com.termux/files/home/Extractor/sacarCombinado.sh

# Ejecutar el script Python
python /data/data/com.termux/files/home/Extractor/extractor2.py

# Liberar el bloqueo de la pantalla
termux-wake-unlock

# Iniciar el servicio de cron (Descomentar si es necesario y si el servicio está disponible en Termux)
# crond start
