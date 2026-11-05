import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dados import SENSORES
from mongodb import obter_medicoes, obter_sensores


def main():
    sensores = obter_sensores()

    for sensor in SENSORES:
        sensores.replace_one({"_id": sensor["_id"]}, sensor, upsert=True)

    obter_medicoes().create_index([("sensor_id", 1), ("timestamp", -1)])

    cidades = {s["localizacao"]["cidade"] for s in SENSORES}

    print(f"{len(SENSORES)} sensores cadastrados em {len(cidades)} cidades.")
    print("Índice {sensor_id: 1, timestamp: -1} criado em Medicoes.")
