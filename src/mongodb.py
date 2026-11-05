import os

from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
NOME_BANCO = "QualidadeAr"
COLECAO_SENSORES = "Sensores"
COLECAO_MEDICOES = "Medicoes"

_cliente = None


def obter_banco():
    global _cliente

    if _cliente is None:
        _cliente = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)

    return _cliente[NOME_BANCO]


def obter_sensores():
    return obter_banco()[COLECAO_SENSORES]


def obter_medicoes():
    return obter_banco()[COLECAO_MEDICOES]
