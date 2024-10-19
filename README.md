# IntApp-EDA

# Requerimientos
- Docker (https://www.docker.com/)
- Serverless (https://serverless.com/ -> Registrarse / Crear Cuenta)
- Node JS y NPM (v22.10.0+)
- Python 3.10+

- Modificar numero de cuenta de sandbox en serverless.yaml, actualizar todos los lugares donde diga "637423304975" por el numero de tu cuenta de AWS del sandbox: 
![alt text](.doc/image.png)

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

# Ejecutar
```bash 
serverless deploy
```