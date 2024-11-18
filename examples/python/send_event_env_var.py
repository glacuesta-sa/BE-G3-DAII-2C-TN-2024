import boto3
import json
import os

# Configurar credenciales usando variables de entorno
os.environ['AWS_ACCESS_KEY_ID'] = 'TU_ACCESS_KEY_ID'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'TU_ACCESS_KEY_SECRET'
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1' #obligatorio

client = boto3.client('events')

def send_test_event():
    response = client.put_events(
        Entries=[
            {
                'EventBusName': 'arn:aws:events:us-east-1:442042507897:event-bus/default', # obligatorio
                'Source': 'artist-module', # obligatorio
                'DetailType': 'recital', # obligatorio
                'Detail': json.dumps({
                    "operation": "creation", # obligatorio
                    "artista": "Monolink",
                    "lugar": "Platea A",
                    "estadio": "Monumental",
                    "fecha_presentacion": "2024-09-29",
                    "fecha_creacion": "2024-09-29",
                    "fecha_actualizacion": "2024-09-29"
                }),
            }
        ]
    )

    print(f"Evento enviado: {response}")

if __name__ == "__main__":
    send_test_event()
