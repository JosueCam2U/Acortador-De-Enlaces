# Acortador de enlaces

Aplicación con backend FastAPI, almacenamiento en DynamoDB y frontend estático.
El backend genera los códigos cortos; el navegador no accede directamente a AWS.

## Desarrollo local

Requisitos: Python 3.10 o posterior y credenciales de AWS configuradas localmente
(por ejemplo, mediante `aws configure` o variables de entorno).

En PowerShell, desde la carpeta `shortener`:

```powershell
python -m venv backend\venv
backend\venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
uvicorn main:app --app-dir backend --reload
```

El backend queda disponible en `http://localhost:8000`; la documentación
interactiva de la API está en `http://localhost:8000/docs`.

Sirve el frontend desde otra terminal, también desde `shortener`:

```powershell
python -m http.server 5500 --directory frontend
```

Abre `http://localhost:5500`. La URL del backend se configura al inicio de
`frontend/script.js` mediante `API_BASE`.

## DynamoDB y AWS

Crea la tabla `shortener-urls` en la región configurada, con clave de partición
`short_code` de tipo String. Los atributos `original_url` y `created_at` se
guardan en cada elemento y no necesitan definirse previamente en DynamoDB.

El usuario o rol IAM que ejecuta el backend necesita `dynamodb:PutItem` y
`dynamodb:GetItem` sobre esa tabla. En EC2, asigna los permisos a un rol de
instancia; no guardes claves de AWS en el código ni en el frontend.

## Configuración

`backend/.env` contiene la configuración local:

```dotenv
AWS_REGION=us-east-1
DYNAMODB_TABLE=shortener-urls
BASE_URL=http://localhost:8000
CORS_ORIGINS=*
```

Antes de desplegar, configura `BASE_URL` con la URL pública del backend y limita
`CORS_ORIGINS` al origen exacto del frontend. Actualiza también `API_BASE` en
`frontend/script.js` para que apunte al backend desplegado. Usa HTTPS en
producción.

El endpoint `/shorten` acepta URLs HTTP o HTTPS. `GET /{short_code}` redirige al
destino; `GET /urls/{short_code}` devuelve los datos almacenados.
