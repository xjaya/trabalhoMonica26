import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from consultas import obter_ultima_janela, resumo_por_cidade, resumo_por_sensor
from redis_cache import obter_redis, salvar_resumos


def main():
    janela = obter_ultima_janela()

    if janela is None:
        raise RuntimeError("Nenhuma medição encontrada. Execute a etapa 2 primeiro.")

    inicio, fim = janela

    redis = obter_redis()
    redis.ping()

    chaves = salvar_resumos(
        redis, resumo_por_sensor(inicio, fim), resumo_por_cidade(inicio, fim)
    )

    print(f"{len(chaves)} Hashes gravados no Redis (HSET).\n")

    for chave in chaves:
        print(f"HGETALL {chave}")

        for campo, valor in redis.hgetall(chave).items():
            print(f"  {campo}: {valor}")
