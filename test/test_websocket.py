import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
import pytest
from unittest.mock import patch
from api.websocket import connect, disconnect, default
from moto import mock_aws
import boto3


@pytest.fixture
def setup_dynamodb():

    with mock_aws():
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

        table = dynamodb.create_table(
            TableName='ConnectionsTable',
            KeySchema=[
                {'AttributeName': 'connectionId', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'connectionId', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        table.wait_until_exists()

        yield dynamodb

        table.delete()
        
@pytest.fixture
def mock_apigateway():
    with patch("boto3.client") as mock_apigateway:
        mock_client = mock_apigateway.return_value
        yield mock_client


def test_connect(setup_dynamodb):
    # Simular el evento de conexión
    event = {
        'requestContext': {
            'connectionId': 'test-connection-id'
        }
    }

    response = connect(event, None)

    # Obtener la tabla mockeada de DynamoDB
    table = setup_dynamodb.Table('ConnectionsTable')

    # Verificar que se llama a put_item en DynamoDB
    item = table.get_item(Key={'connectionId': 'test-connection-id'})
    assert 'Item' in item

    # Verificar la respuesta
    assert response['statusCode'] == 200
    assert json.loads(response['body']) == 'Conectado'


def test_disconnect(setup_dynamodb):
    # Simular el evento de desconexión
    event = {
        'requestContext': {
            'connectionId': 'test-connection-id'
        }
    }

    # Insertar un elemento en la tabla
    table = setup_dynamodb.Table('ConnectionsTable')
    table.put_item(Item={'connectionId': 'test-connection-id'})

    response = disconnect(event, None)

    # Verificar que el item fue eliminado de DynamoDB
    item = table.get_item(Key={'connectionId': 'test-connection-id'})
    assert 'Item' not in item

    # Verificar la respuesta
    assert response['statusCode'] == 200
    assert json.loads(response['body']) == 'Desconectado'


def test_default(setup_dynamodb, mock_apigateway):
    # Simular el evento de mensaje
    event = {
        'requestContext': {
            'connectionId': 'test-connection-id',
            'domainName': 'example.com',
            'stage': 'dev'
        },
        'body': json.dumps({
            'message': 'Hello, WebSocket!'
        })
    }

    response = default(event, None)

    # Verificar que se llama a post_to_connection en el cliente de API Gateway
    mock_apigateway.post_to_connection.assert_called_once_with(
        ConnectionId='test-connection-id',
        Data=json.dumps({
            'message': 'Se recibio el mensaje Hello, WebSocket!',
            'connectionId': 'test-connection-id'
        })
    )

    # Verificar la respuesta
    assert response['statusCode'] == 200
    assert json.loads(response['body']) == {
        'message': 'Se recibio el mensaje Hello, WebSocket!'
    }