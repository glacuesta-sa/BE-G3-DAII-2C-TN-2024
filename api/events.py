import json
import boto3
from datetime import datetime
import uuid

ssm = boto3.client('ssm')

def get_websocket_url():
    response = ssm.get_parameter(Name='/eventify-eda-be/websocket-url', WithDecryption=True)
    return response['Parameter']['Value']

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ConnectionsTable')
history_table = dynamodb.Table('EventsHistory')

def lambda_handler(event, context):
    
    print(f"Received event: {json.dumps(event)}")

    # Obtener la WebSocket URL
    websocket_url = get_websocket_url()
    print(f"La WebSocket URL es: {websocket_url}")

    url_https = websocket_url.replace("wss://", "https://")

    ws_client = boto3.client('apigatewaymanagementapi',
            endpoint_url=url_https
        )

    try:
        if 'detail' not in event:
            raise KeyError("no se recibio detail en el evento")
        
        #TODO  Validar esquema
        detail = event['detail']
        
        operation = detail.get('operation', 'desconocida')
        
        # Guardar evento en DynamoDB como historial
        event_id = str(uuid.uuid4())
        history_table.put_item(
            Item={
                'eventId': event_id,
                'timestamp': datetime.utcnow().isoformat(),
                'operation': operation,
                'detail': detail
            }
        )

        # Obtener los ConnectionIds almacenados en DynamoDB
        response = table.scan()
        connections = response.get('Items', [])

        for connection in connections:
            connection_id = connection['connectionId']
            print(f"Connection ID: {connection_id}")
            
            # Enviar un mensaje a cada cliente WebSocket usando el API Gateway Management API
            ws_client.post_to_connection(
                ConnectionId=connection_id,
                Data=json.dumps(detail)
            )
    except Exception as e:
        err = f"Error procesando el evento: {str(e)}"
        print(err)
        return {
            'statusCode': 500,
            'body': json.dumps(err)
        }

    return {
        'statusCode': 200,
        'body': json.dumps('Evento processado satisfactoriamente.')
    }
