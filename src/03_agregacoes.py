import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from consultas import (
    formatar_numero, obter_ultima_janela, resumo_por_cidade, resumo_por_sensor
)

COLUNAS = [
    ("qt_medicoes", "Qtd", 0), ("pm25_media", "PM2.5", 1),
    ("pm10_media", "PM10", 1), ("co2_media", "CO2", 0),
    ("temperatura_media", "Temp", 1), ("umidade_media", "Umid", 1),
    ("pm25_max", "PM2.5max", 1), ("pm10_max", "PM10max", 1),
]


def imprimir(titulo, resumos, rotulo):
    print(f"\n{titulo}")

    cabecalho = " " * 16 + "".join(f"{nome:>9}" for _, nome, _ in COLUNAS)

    print(cabecalho)
    print("-" * len(cabecalho))

    for r in resumos:
        valores = "".join(
            f"{formatar_numero(r[campo], casas):>9}" for campo, _, casas in COLUNAS
        )
        print(f"{rotulo(r):<16}{valores}")


def main():
    janela = obter_ultima_janela()

    if janela is None:
        raise RuntimeError("Nenhuma medição encontrada. Execute a etapa 2 primeiro.")

    inicio, fim = janela

    print(f"Janela horária: {inicio:%Y-%m-%d %H:%M} a {fim:%H:%M} UTC")

    imprimir("RESUMO POR SENSOR", resumo_por_sensor(inicio, fim),
             lambda r: r["sensor_id"])
    imprimir("RESUMO POR CIDADE", resumo_por_cidade(inicio, fim),
             lambda r: f"{r['cidade']}/{r['uf']}")
