import boto3
import json
import os

# Configurar credenciales usando variables de entorno
os.environ['AWS_ACCESS_KEY_ID'] = 'AS*******ZCP'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'iA7****************2v/3Ubnv'
os.environ['AWS_SESSION_TOKEN'] = 'IQoJ********************/Z7jrIaA6Be3w6F10L8NtLZlTrIA=='
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1' #obligatorio

sns_client = boto3.client('sns', region_name='us-east-1')

TOPIC_ARN = "arn:aws:sns:us-east-1:442042507897:artist-topic"
#TOPIC_ARN = "arn:aws:sns:us-east-1:442042507897:recital-topic"

def subscribe_to_topic(email_address):
    try:
        response = sns_client.subscribe(
            TopicArn=TOPIC_ARN,
            Protocol="email",
            Endpoint=email_address
        )
        subscription_arn = response['SubscriptionArn']
        print(f"Suscrito al topico! Subscription ARN: {subscription_arn}")

    except Exception as e:
        print(f"Error al suscribirse: {e}")

if __name__ == "__main__":

    email_address = "glacuesta@uade.edu.ar"
    subscribe_to_topic(email_address)
