import logging
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

import boto3
from botocore.exceptions import BotoCoreError
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl

load_dotenv(Path(__file__).with_name(".env"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
TABLE_NAME = os.getenv("DYNAMODB_TABLE", "shortener-urls")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000").rstrip("/")
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "*").split(",")
    if origin.strip()
]

app = FastAPI(title="Acortador de enlaces")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
table = dynamodb.Table(TABLE_NAME)


class URLCreate(BaseModel):
    original_url: HttpUrl


def get_url_item(short_code: str) -> dict:
    try:
        response = table.get_item(Key={"short_code": short_code})
    except BotoCoreError as error:
        logger.exception("No se pudo consultar DynamoDB")
        raise HTTPException(
            status_code=503,
            detail="El servicio de almacenamiento no está disponible",
        ) from error

    item = response.get("Item")
    if not item:
        raise HTTPException(status_code=404, detail="Enlace corto no encontrado")
    return item


@app.post("/shorten")
def shorten_url(payload: URLCreate) -> dict[str, str]:
    original_url = str(payload.original_url)
    short_code = str(uuid.uuid4())
    item = {
        "short_code": short_code,
        "original_url": original_url,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    try:
        table.put_item(Item=item)
    except BotoCoreError as error:
        logger.exception("No se pudo guardar el enlace en DynamoDB")
        raise HTTPException(
            status_code=503,
            detail="El servicio de almacenamiento no está disponible",
        ) from error

    return {
        "short_code": short_code,
        "original_url": original_url,
        "short_url": f"{BASE_URL}/{short_code}",
    }


@app.get("/{short_code}")
def redirect_to_original(short_code: str) -> RedirectResponse:
    item = get_url_item(short_code)
    return RedirectResponse(url=item["original_url"], status_code=307)


@app.get("/urls/{short_code}")
def get_url_info(short_code: str) -> dict:
    return get_url_item(short_code)
