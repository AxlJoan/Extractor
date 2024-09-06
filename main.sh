#!/bin/sh

# Mantener el dispositivo despierto
termux-wake-lock

# Esperar un minuto
sleep 60

# Ejecutar el script combinado
sh /data/data/com.termux/files/home/extractor/sacarCombinado.sh

# Ejecutar el script Python
python /data/data/com.termux/files/home/extractor/extractor2.py

# Liberar el bloqueo de la pantalla
termux-wake-unlock

# Iniciar el servicio de cron
crond start
