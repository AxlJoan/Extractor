# Instalación y Extracción para WhatsApp desde dispositivos moviles

Para hacer funcionar esta herramienta, utilizaremos Termux.

## Requisitos para la primera vez que se realiza el proceso

1. [Descarga Termux desde F-Droid](https://f-droid.org/es/packages/com.termux/).
2. Verificar que la instancia en la que se está realizando el proceso está rooteada

### Configuración del Emulador

Sigue estos pasos para configurar el emulador y hacer que el código funcione automáticamente:

#### Actualización de Paquetes

Abre Termux y ejecuta los siguientes comandos para actualizar los paquetes:

```sh
pkg update -y
pkg upgrade -y
pkg install git -y
pkg install tur-repo -y
pkg install python-pandas -y
pip install mysql-connector-python -y
pip install emoji -y
```
#### Clonar el Repositorio
Clona el repositorio necesario ejecutando el siguiente comando:

```sh
git clone https://github.com/AxlJoan/Extractor.git
```
#### Entrar a la carpeta del repositorio y darle permisos a Termux
```
cd Extractor

# Esto dará permisos a termux para acceder a los archivos
termux-setup-storage
```

#### Permisos para los Scripts
Otorga permisos de ejecución a los scripts necesarios:

```sh
chmod +x sacarCombinado.sh
chmod +x main.sh
```
#### Ejecución Automática del Código
Para ejecutar el código de manera automática, ejecuta el script principal:
```sh
./main.sh
```
**IMPORTANTE:** Al ser la primera vez que se ejecuta el proceso nos pedirá ingresar el nombre del cliente, estado y municipio, asegurarse de tener estas variables anotadas en algún lado ya que son las que se utilizarán para crear al usuario en la base de datos.
## Proceso ya con usuario de extracción creado:
1. Abrir Termux
2. Ingresar a la carpeta del repositorio
```
cd Extractor
```
3. Ejecutar el archivo main que realizará el proceso automáticamente
```sh
./main.sh
```

# Opcional no es necesario esto:
## Ejecución manual del código
## Cambiar formato de archivo para poder ejecutar correctamente el código
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
Damos permisos de ejecución al script de python y ejecutamos el script extractor2.py
```
chmod +x extractor2.py
python extractor2.py
```

Se está trabajando en la automatización del proceso todavía.

### Instalacion de termux-api
Para ejecutar el código:
```sh
pkg update
pkg upgrade
pkg install termux-api
```


