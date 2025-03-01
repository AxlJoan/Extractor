#!/bin/sh

# Mantener el dispositivo despierto permanentemente
termux-wake-lock

while true; do
    echo "Iniciando proceso de extracción..."

    # Actualizar los repositorios y asegurar que dos2unix está instalado
    pkg update -y
    pkg install -y dos2unix

    # Convertir el archivo de formato DOS a formato UNIX
    dos2unix /data/data/com.termux/files/home/Extractor/sacarCombinado.sh

    # Ejecutar el script combinado
    bash /data/data/com.termux/files/home/Extractor/sacarCombinado.sh

    # Ejecutar el script Python
    python /data/data/com.termux/files/home/Extractor/extractor2.py

    echo "Proceso completado. Esperando 1 día antes de la siguiente ejecución..."

    # Esperar 10 minutos antes de la próxima ejecución
    sleep 18600
done
