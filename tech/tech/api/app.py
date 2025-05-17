from http import HTTPStatus

from fastapi import FastAPI
from tech.interfaces.schemas.message_schema import (
    Message,
)

from tech.api import  products_router

app = FastAPI()
app.include_router(
    products_router.router, prefix='/products', tags=['products']
)

@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Tech Challenge FIAP - Kauan Silva!      Products Microservice'}

@app.get("/health")
async def health_check():
    """
    Endpoint de verificação de saúde da aplicação.
    Utilizado pelo Kubernetes para readiness e liveness probes.
    """
    try:
        # Não vamos verificar a conexão com o MongoDB aqui
        # para evitar que a health check falhe por problemas de banco
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}