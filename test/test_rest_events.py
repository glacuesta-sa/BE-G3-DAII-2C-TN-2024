import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
import boto3
from moto import mock_aws
from unittest.mock import patch

@pytest.fixture
def setup_dynamodb():

    with mock_aws():
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

        table = dynamodb.create_table(
            TableName='EventsHistory',
            KeySchema=[
                {'AttributeName': 'eventId', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'eventId', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        table.wait_until_exists()

        yield dynamodb

        table.delete()
        
from fastapi.testclient import TestClient
from api.rest import app

client = TestClient(app)

def test_get_operation_types():
        response = client.get("/v1/operations/types")
        assert response.status_code == 200
        # TODO pendiente de PO
        assert response.json() == {
            "ok": True,
            "message": "success",
            "data": {"operationTypes": ["venta", "reventa"]}
    }

def test_get_event_history_no_params(setup_dynamodb):
    with patch("api.rest.get_dynamodb_table") as mock_dynamodb_table:
        mock_dynamodb_table.return_value = setup_dynamodb.Table('EventsHistory')
        
        response = client.get("/v1/events/history")
        assert response.status_code == 200
        assert "events" in response.json()["data"]

def test_when_events_table_empty_len_zero_then_send_event_then_len_one(setup_dynamodb):
    with patch("api.rest.get_dynamodb_table") as mock_dynamodb_table:
        mock_dynamodb_table.return_value = setup_dynamodb.Table('EventsHistory')
        
        response = client.get("/v1/events/history")
        assert response.status_code == 200
        assert len(response.json()["data"]["events"]) == 0

        new_event = {
            "eventId": "1",
            "operation": "venta",
            "timestamp": "2024-10-14T12:34:56"
        }
        table = setup_dynamodb.Table('EventsHistory')
        table.put_item(Item=new_event)

        response = client.get("/v1/events/history")
        assert response.status_code == 200
        assert len(response.json()["data"]["events"]) == 1

        # Verificar el contenido del evento
        event = response.json()["data"]["events"][0]
        assert event["eventId"] == "1"
        assert event["operation"] == "venta"