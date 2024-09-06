#!/data/data/com.termux/files/usr/bin/bash

# Función para copiar archivos
copiar_archivos() {
  local ruta=$1
  local destino=$2

  su -c "cp $ruta/msgstore.db $destino/msgstore.db"
  su -c "cp $ruta/wa.db $destino/wa.db"

  echo "Archivos copiados desde $ruta a $destino."
}

# Primera ruta de copia
ruta1="/data/data/com.whatsapp.w4b/databases"
destino="/sdcard"

# Segunda ruta de copia
ruta2="/data/data/com.whatsapp/databases"

# Verificar si la primera ruta existe
if [ -d "$ruta1" ]; then
  copiar_archivos "$ruta1" "$destino"
else
  # Si la primera ruta no existe, intenta con la segunda
  if [ -d "$ruta2" ]; then
    copiar_archivos "$ruta2" "$destino"
  else
    echo "Ninguna de las rutas de datos existe."
  fi
fi
