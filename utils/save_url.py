import boto3
import os

# Inicializar clientes de AWS
cf_client = boto3.client('cloudformation')
ssm_client = boto3.client('ssm')

def lambda_handler(event, context):
    stack_name = "eventify-eda-be-dev"
    parameter_name = "/eventify-eda-be/websocket-url"

    try:
        print(f"Obteniendo la WebSocket URL desde el stack: {stack_name}")

        # Obtener la salida del stack de CloudFormation
        response = cf_client.describe_stacks(StackName=stack_name)
        outputs = response['Stacks'][0]['Outputs']

        # Buscar el valor de la WebSocket URL
        websocket_url = None
        for output in outputs:
            if output['OutputKey'] == 'ServiceEndpointWebsocket':
                websocket_url = output['OutputValue']
                break
        
        if websocket_url:
            print(f"WebSocket URL encontrada: {websocket_url}")

            # Guardar la WebSocket URL en SSM
            ssm_client.put_parameter(
                Name=parameter_name,
                Value=websocket_url,
                Type='String',  #  'SecureString' para cifrar
                Overwrite=True
            )

            print(f"WebSocket URL guardada en SSM Parameter Store: {parameter_name}")

        else:
            print("No se encontró la WebSocket URL en la salida del stack.")
            return {
                'statusCode': 500,
                'body': 'No se encontró la WebSocket URL en la salida del stack.'
            }

        return {
            'statusCode': 200,
            'body': f'WebSocket URL guardada en SSM: {websocket_url}'
        }

    except Exception as e:
        print(f"Error al procesar el evento: {str(e)}")
        return {
            'statusCode': 500,
            'body': f"Error: {str(e)}"
        }
