# Instalación y Extracción para WhatsApp desde instancias de dispositivos móviles con Termux
Para hacer funcionar esta herramienta, utilizaremos Termux.

## Requisitos
1. Descarga Termux desde F-Droid
2. Tener una instancia con WhatsApp con root habilitado

## Configuración del Emulador
Sigue estos pasos para configurar el emulador y hacer que el código funcione automáticamente

### Actualización de paquetes
Abre Termux y ejecuta los siguientes comandos para actualizar los paquetes:

```
pkg update
pkg upgrade
pkg install git
pkg install tur-repo -y
pkg install python-pandas -y
pip install mysql-connector-python
pip install emoji
termux-setup-storage
```

### Clonar el Repositorio
```
git clone https://github.com/
```

### Moverse a la carpeta del repositorio
```
cd 
```

### Permisos para el script
Otorga permisos de ejecución a los scripts necesarios:
```
chmod +x sacar.sh
chmod +x main.sh
```

### Ejecución automática del código
Para ejecutar el código de manera automática, ejecuta el script principal:
```
./main.sh
```
