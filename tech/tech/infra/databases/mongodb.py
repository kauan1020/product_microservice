import os
import certifi
import motor.motor_asyncio
from pymongo import MongoClient
from pymongo.collection import Collection

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://mongodb:mongodb@localhost:27017/products?authSource=admin")

# Versão simplificada das opções de conexão
ssl_options = {}
if "mongodb+srv" in MONGODB_URI:
    ssl_options = {
        "tlsCAFile": certifi.where(),
        "serverSelectionTimeoutMS": 30000
    }

mongo_client = MongoClient(MONGODB_URI, **ssl_options)
db = mongo_client.get_database()

async_client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI, **ssl_options)
async_db = async_client.get_database()

def get_collection(collection_name: str) -> Collection:
    """
    Obtém uma coleção do MongoDB para operações síncronas.

    Args:
        collection_name: Nome da coleção

    Returns:
        Collection: Coleção do MongoDB
    """
    return db[collection_name]

async def get_async_collection(collection_name: str):
    """
    Obtém uma coleção do MongoDB para operações assíncronas.

    Args:
        collection_name: Nome da coleção

    Returns:
        Collection: Coleção assíncrona do MongoDB
    """
    return async_db[collection_name]

def close_mongodb_connection():
    """
    Fecha a conexão com o MongoDB quando a aplicação é encerrada.
    """
    mongo_client.close()
    async_client.close()