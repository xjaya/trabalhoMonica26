import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mongodb import obter_medicoes, obter_sensores

HORAS = 24
INTERVALO_MIN = 5
PROB_INVALIDA = 0.01  # simula falhas de leitura (valor nulo)


def gerar_base():
    return {
        "pm25": random.uniform(15, 35),
        "pm10": random.uniform(30, 60),
        "co2": random.uniform(450, 600),
        "temperatura": random.uniform(22, 26),
        "umidade": random.uniform(60, 70),
    }


def main():
    sensores = list(obter_sensores().find({"ativo": True}))

    if not sensores:
        raise RuntimeError("Nenhum sensor cadastrado. Execute a etapa 1 primeiro.")

    fim = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    inicio = fim - timedelta(hours=HORAS)
    total = HORAS * 60 // INTERVALO_MIN

    documentos = []

    for sensor in sensores:
        base = gerar_base()

        for i in range(total):
            doc = {
                "sensor_id": sensor["_id"],
                "timestamp": inicio + timedelta(minutes=INTERVALO_MIN * i),
                **{k: round(v * random.uniform(0.85, 1.15), 1) for k, v in base.items()},
            }

            if random.random() < PROB_INVALIDA:
                doc["pm25"] = None

            documentos.append(doc)

    colecao = obter_medicoes()
    colecao.delete_many({})
    colecao.insert_many(documentos)

    print(f"{len(documentos)} medições inseridas ({total} por sensor).")
    print(f"Período: {inicio:%Y-%m-%d %H:%M} a {fim:%Y-%m-%d %H:%M} UTC")
