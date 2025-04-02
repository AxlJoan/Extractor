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

    # Ejecutar el script Python
    python /data/data/com.termux/files/home/Extractor/eliminarDuplicados.py

    echo "Ejecutando el contador de integrantes en grupos..."
    # Ejecutar el script Python
    python /data/data/com.termux/files/home/Extractor/group_counter.py

    # Ejecutar el script Python
    python /data/data/com.termux/files/home/Extractor/eliminarRegistrosAntiguos.py

    echo "Proceso completado. Esperando 5 minutos antes de la siguiente ejecución..."

    # Esperar 5 minutos antes de la próxima ejecución
    sleep 300
done
