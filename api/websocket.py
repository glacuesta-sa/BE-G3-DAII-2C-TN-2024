
import json
import boto3

def get_conn_table():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
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
        table = get_conn_table()

        connection_id = event['requestContext']['connectionId']

        print(f'Mensaje recibido de cliente id ({connection_id}): ')
        print(body)

        ws_client = boto3.client('apigatewaymanagementapi',
            endpoint_url=f"https://{event['requestContext']['domainName']}/{event['requestContext']['stage']}"
        )

        # enviar respuesta al cliente WebSocket
        try: 
            ws_client.post_to_connection(
            ConnectionId=connection_id,
            Data=json.dumps({
                'body': body,
                'connectionId': connection_id
            })
        )
        except ws_client.exceptions.GoneException:
            print(f"Connection ID {connection_id} no es valida. Eliminando...")
            table.delete_item(
                Key={'connectionId': connection_id}
            )
        except Exception as e:
            print(f"Error enviando mensaje a {connection_id}: {str(e)}")

        return {
            'statusCode': 200,
            'message': "se recibio mensaje en websocket",
            'body': json.dumps(body)
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
