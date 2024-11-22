from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime
from mangum import Mangum
from typing import Optional
import boto3

from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html

app = FastAPI()

sns_client = boto3.client("sns", region_name="us-east-1")

# TODO security: mejorar politicas de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todas las fuentes
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Permitir todos los encabezados
)


def get_dynamodb_table():
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    return dynamodb.Table("EventsHistory")


@app.get("/v1/health")
def health_check():
    """
    Health check endpoint to verify if the service is running.
    """

    # Obtener topicos de la cuenta
    response = sns_client.list_topics()
    topics = response.get("Topics", [])
    topic_arns = [topic["TopicArn"] for topic in topics]

    return JSONResponse(
        content={
            "ok": True,
            "message": "Service is healthy",
            "resources": {"topics": topics},
        },
        headers={
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
        },
    )


@app.get("/v1/events/history")
def get_event_history(
    detail_type: Optional[str] = Query(
        None, alias="detail-type",  description="Filtrar eventos por operación (ej: artist.registration, recital.created)"
    ),
    source: Optional[str] = Query(
        None,  description="Filtrar eventos por fuente (ej: artist-module, tickets-module)"
    ),
    sort_by: Optional[str] = Query(
        default="timestamp",
        description="Campo por el que ordenar los eventos (ej: timestamp)",
    ),
    sort_order: Optional[str] = Query(
        default="desc", description="Orden de los eventos (asc o desc)"
    ),
    start_date: Optional[str] = Query(
        None, description="Fecha de inicio en formato YYYY-MM-DD"
    ),
    end_date: Optional[str] = Query(
        None, description="Fecha de fin en formato YYYY-MM-DD"
    ),
    page: Optional[int] = Query(
        default=1, ge=1, description="Número de página (1 para la primera página)"
    ),
    page_size: Optional[int] = Query(
        default=50, ge=1, le=100, description="Cantidad de eventos por página"
    ),
):
    try:
        # Filtrar por fechas si se proveen
        filter_expression = None

        # Validar parámetros de página
        if page < 1:
            raise HTTPException(
                status_code=400,
                detail="El número de página debe ser mayor o igual a 1",
            )

        # Filtrar por operación si se proporciona
        if detail_type:
            filter_expression = Attr("detail-type").eq(detail_type)

        # Filtrar por source
        if source:
            filter_expression = Attr("source").eq(source)

        if start_date or end_date:
            date_format = "%Y-%m-%d"
            if start_date:
                try:
                    start_datetime = datetime.strptime(start_date, date_format)
                    filter_expression = Key("timestamp").gte(start_datetime.isoformat())
                except ValueError:
                    raise HTTPException(
                        status_code=400,
                        detail="Formato de fecha inválido para start_date",
                    )

            if end_date:
                try:
                    end_datetime = datetime.strptime(end_date, date_format)
                    if filter_expression:
                        filter_expression = filter_expression & Key("timestamp").lte(
                            end_datetime.isoformat()
                        )
                    else:
                        filter_expression = Key("timestamp").lte(
                            end_datetime.isoformat()
                        )
                except ValueError:
                    raise HTTPException(
                        status_code=400,
                        detail="Formato de fecha inválido para end_date",
                    )

        history_table = get_dynamodb_table()

        # Escanear la tabla con los filtros
        scan_kwargs = {}
        if filter_expression:
            scan_kwargs["FilterExpression"] = filter_expression

        response = history_table.scan(**scan_kwargs)
        items = response.get("Items", [])

        # Ordenar los resultados si se solicita
        if sort_by:
            reverse_order = True if sort_order == "desc" else False
            items = sorted(
                items, key=lambda x: x.get(sort_by, ""), reverse=reverse_order
            )

        # paginado
        total_items = len(items)
        total_pages = (total_items + page_size - 1) // page_size  # redondeo hacia arriba
        start_index = (page - 1) * page_size
        end_index = start_index + page_size

        if start_index >= total_items:
            items = []

        paginated_items = items[start_index:end_index]

        return JSONResponse(
            content={
                "ok": True,
                "message": "success",
                "data": {
                    "events": paginated_items,
                    "pagination": {
                        "current_page": page,
                        "total_pages": total_pages,
                        "page_size": page_size,
                        "total_items": total_items,
                    },
                },
            },
            headers={
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
            },
        )

    except Exception as e:
        print(f"Error al obtener el historico de eventos: {e}")
        raise HTTPException(
            status_code=500, detail="Error al obtener el historico de eventos."
        )


@app.get("/v1/detail-types")
def get_detail_types():
    # TODO: pendiente de definicion de PO
    return JSONResponse(
        content={
            "ok": True,
            "message": "success",
            "data": {
                "detailTypes": [
                    "artist.registration",
                    "artist.profile.created",
                    "recital.created",
                    "recital.updated",
                    "recital.deleted",
                ],
                "sources": [
                    "artist-module",
                    "wallet-module",
                    "tickets-module",
                    "analytics-module",
                    "blockchain-module",
                    "ldap-module",
                ],
            },
        },
        headers={
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
        },
    )


# Docs
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Eventify - EDA API Rest",
        version="1.0.0",
        description="EDA API REST",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


@app.get("/openapi.json", include_in_schema=False)
def get_open_api_endpoint():
    return custom_openapi()


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/dev/openapi.json",
        title="Swagger UI",
    )


# adaptar la rest API a Lambda
handler = Mangum(app)
