# Eventify-EDA
El modulo del EDA es la capa de transporte de Eventify, provee los canales necesarios para soportar los casos de uso de negocio del proyecto: Eventos, Colas, Mensajes, Websocket y una API REST.

# Compile & Build
Este repositorio esta integrado y deployado continuamente utilizando Github Actions
[![GitHub Actions](https://github.com/glacuesta-sa/BE-G3-DAII-2C-TN-2024/actions/workflows/main.yml/badge.svg?branch=main)](https://github.com/glacuesta-sa/BE-G3-DAII-2C-TN-2024/actions/workflows/main.yml)

Utilizamos Serverless Framework para automatizar el deployent al sandbox de AWS utilizando Cloudformation. A continuación se detallan los requerimientos necesitarios para deployar este modulo.

# Requerimientos
- Docker (https://www.docker.com/) - Es necesario temporalmente para crear las capas de dependencia para las lambdas, se migrará a Layers (TBD).
- Serverless Framework: es el marco de trabajo elegido para desplegar la arquitectura serverless en AWS. Permite crear arquitecturas serverless a través de definiciones en formato YAML, agilizando el desarrollo y a la vez proveyendo 
    -  Registrarse / Crear Cuenta en serverless.com
- Node JS y NPM (v21.1.0+ https://nodejs.org/en/download/package-manager)
- Python 3.10+ (https://www.python.org/downloads/)

- Modificar numero de cuenta de sandbox en serverless.yaml, actualizar todos los lugares donde diga "637423304975" por el numero de tu cuenta de AWS del sandbox: 
![alt text](docs/image.png)

Instalar:
```bash 
npm install serverless
```
```bash 
npm install serverless-python-requirements
```
```bash 
npm install serverless-scriptable-plugin
```

# Configurar CLI
Se necesita actualizar el Sandbox API Key, API Secret, API Access Token set. Crear un perfil "aws-academy" en .aws/config:
```bash 
[profile aws-academy]
region = us-east-1
output = json
```
Copiar credenciales del sandbox y pegar en .aws/credentials:
```bash 
[aws-academy]
aws_access_key_id=ASIA24FA4IFROT4LWUOH
aws_secret_access_key=dGwxWWFVgESV*******zT2M5ZJDuhxLo6vq9
aws_session_token=IQoJb3JpZ2lL8JN/li/G0zC0uZ*******361zZ2XuQjJtdKxzXJtYFTW02M+izA==
```

Tambien es necesario setear el SERVERLESS_ACCESS_KEY como variable de entorno (Obtener de Serverless Dashboard)
```bash 
export SERVERLESS_ACCESS_KEY=fkAOkwWkkVGwgESV*******************vtVh1UsKGezT2M5ZJ6vq9
```

# Ejecutar
```bash 
serverless deploy --stage dev
```