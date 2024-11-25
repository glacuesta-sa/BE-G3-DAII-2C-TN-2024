import boto3
import json
from datetime import date

client = boto3.client('events')

session = boto3.Session(
    profile_name='aws-academy', ## existe un perfil llamado aws-academy con las credenciales en ~/.aws/credentials
    region_name='us-east-1' 
)

# Initialize EventBridge client
client = session.client('events')

def send_test_event():
    response = client.put_events(
        Entries=[
            {
                'EventBusName': 'arn:aws:events:us-east-1:442042507897:event-bus/default', # obligatorio (no tocar)
                'Source': 'artist-module', # obligatorio; el valor es un ejempl onomas
                'DetailType': 'recital', # obligatorio; el valor es un ejempl onomas
                'Detail': json.dumps({ # detail es un payload dinamico, puede venir cualquier cosa
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
