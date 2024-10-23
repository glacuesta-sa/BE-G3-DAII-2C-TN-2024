
import json
import boto3

def get_conn_table():
    dynamodb = boto3.resource('dynamodb')
    return dynamodb.Table('ConnectionsTable')

def connect(event, context):

    connection_id = event['requestContext']['connectionId']
    print(f"Conectado client id: {connection_id}")

    # Guardar el ConnectionId en DynamoDB
    table = get_conn_table()
    table.put_item(
        Item={
            'connectionId': connection_id
        }
    )

    return {
        'statusCode': 200,
        'body': json.dumps('Conectado')
    }

def disconnect(event, context):

    connection_id = event['requestContext']['connectionId']
    print(f"Desconectado client id: {connection_id}")

    # Eliminar el ConnectionId de DynamoDB cuando el cliente se desconecta
    table = get_conn_table()
    table.delete_item(
        Key={
            'connectionId': connection_id
        }
    )
 
    return {
        'statusCode': 200,
        'body': json.dumps('Desconectado')
    }

def default(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        message = body.get('message', 'No message found')

        connection_id = event['requestContext']['connectionId']

        print(f'Mensaje recibido de cliente id ({connection_id}): {message}')

        ws_client = boto3.client('apigatewaymanagementapi',
            endpoint_url=f"https://{event['requestContext']['domainName']}/{event['requestContext']['stage']}"
        )

        # enviar respuesta al cliente WebSocket
        ws_client.post_to_connection(
            ConnectionId=connection_id,
            Data=json.dumps({
                'message': f"Se recibio el mensaje {message}",
                'connectionId': connection_id
            })
        )

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f"Se recibio el mensaje {message}"
            })
        }

    except Exception as e:

        print('error al procesar peticion' + str(e))

        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Internal server error',
                'error': str(e)
            })
        }
