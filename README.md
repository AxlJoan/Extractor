# Instalación y Extracción para WhatsApp desde dispositivos moviles

Para hacer funcionar esta herramienta, utilizaremos Termux. Además, para la automatización, agregaremos Tasker y Termux:Tasker.

## Requisitos

1. [Descarga Termux desde F-Droid](https://f-droid.org/es/packages/com.termux/).
2. Instala Tasker y Termux:Tasker para la automatización.

## Configuración del Emulador

Sigue estos pasos para configurar el emulador y hacer que el código funcione automáticamente:

### Actualización de Paquetes

Abre Termux y ejecuta los siguientes comandos para actualizar los paquetes:

```sh
pkg update
pkg upgrade
pkg install git
pkg install tur-repo -y
pkg install python-pandas -y
pip install mysql-connector-python
pip install emoji
```
### Clonar el Repositorio
Clona el repositorio necesario ejecutando el siguiente comando:

```sh
git clone https://github.com/AxlJoan/Extractor.git
```
### Entrar a la carpeta del repositorio y darle permisos a Termux
```
cd Extractor
termux-setup-storage
```

### Permisos para los Scripts
Otorga permisos de ejecución a los scripts necesarios:

```sh
chmod +x sacarCombinado
chmod +x main.sh
chmod +x extractor2.py
```
### Ejecución manual del código
Primero ocupamos usar dos2unix para convertir sacarCombinado.sh de formato DOS a formanto Unix
```
pkg install dos2unix
```
Luego convierte el archivo:
```
dos2unix sacarCombinado.sh
```
Lo ejecutamos con bash
```
bash sacarCombinado.sh
```
Y ejecutamos el script en python extractor2.py
```
python extractor2.py
```

### Ejecución Automática del Código (En producción)
Para ejecutar el código de manera automática, ejecuta el script principal:
```sh
./main.sh
```
**Este es solo para funcionar con Termux para usar con Tasker mover el main.sh**

### Instalacion de termux-api
Para ejecutar el código:
```sh
pkg update
pkg upgrade
pkg install termux-api
```


