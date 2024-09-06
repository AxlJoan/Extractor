#!/data/data/com.termux/files/usr/bin/bash

# Copiar archivos desde la ubicación correcta de la instancia LDPlayer
echo "Copiando archivos desde com.whatsapp..."
su -c 'cp /data/data/com.whatsapp/databases/msgstore.db /sdcard/msgstore.db'
su -c 'cp /data/data/com.whatsapp/databases/wa.db /sdcard/wa.db'

echo "Archivos copiados exitosamente."
