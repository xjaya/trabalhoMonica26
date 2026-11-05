import os
import unicodedata

from redis import Redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
PREFIXO = "qualidadear"
FORMATO_DATA = "%Y-%m-%dT%H:%M:%SZ"


def obter_redis():
    return Redis.from_url(REDIS_URL, decode_responses=True)


def normalizar(texto):
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore")
    return sem_acento.decode().strip().lower()


def chave_cidade(resumo):
    return f"{PREFIXO}:cidade:{resumo['uf']}:{normalizar(resumo['cidade'])}"


def chave_sensor(resumo):
    return f"{PREFIXO}:sensor:{resumo['sensor_id']}"


def para_hash(resumo):
    campos = {
        k: v for k, v in resumo.items()
        if k not in ("sensor_id", "cidade", "uf")
    }

    for campo in ("inicio_periodo", "fim_periodo"):
        campos[campo] = campos[campo].strftime(FORMATO_DATA)

    return campos


def salvar_resumos(redis, resumos_sensor, resumos_cidade):
    """Grava um Hash por sensor e por cidade e retorna as chaves usadas."""
    pares = (
        [(chave_sensor(r), r) for r in resumos_sensor]
        + [(chave_cidade(r), r) for r in resumos_cidade]
    )

    pipe = redis.pipeline()

    for chave, resumo in pares:
        pipe.hset(chave, mapping=para_hash(resumo))

    pipe.execute()

    return [chave for chave, _ in pares]
