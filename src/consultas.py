import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


PASTA_CODIGO = Path(__file__).resolve().parent

if str(PASTA_CODIGO) not in sys.path:
    sys.path.insert(0, str(PASTA_CODIGO))

from mongodb import COLECAO_SENSORES, obter_medicoes, obter_sensores


LIMITE_EXIBICAO = 30

# Uma medição só é válida se todas as grandezas forem numéricas e plausíveis
FILTRO_VALIDAS = {
    "pm25": {"$type": "number", "$gte": 0},
    "pm10": {"$type": "number", "$gte": 0},
    "co2": {"$type": "number", "$gte": 0},
    "temperatura": {"$type": "number"},
    "umidade": {"$type": "number", "$gte": 0, "$lte": 100}
}

# Estatísticas calculadas sobre as MEDIÇÕES (não sobre médias de sensores),
# por isso a média da cidade já considera quantidades diferentes de registros
ESTATISTICAS = {
    "qt_medicoes": {"$sum": 1},
    "pm25_media": {"$avg": "$pm25"},
    "pm10_media": {"$avg": "$pm10"},
    "co2_media": {"$avg": "$co2"},
    "temperatura_media": {"$avg": "$temperatura"},
    "umidade_media": {"$avg": "$umidade"},
    "pm25_max": {"$max": "$pm25"},
    "pm10_max": {"$max": "$pm10"}
}


def formatar_numero(valor, casas=1):

    if valor is None:
        return "-"

    return f"{valor:.{casas}f}"


def listar_sensores():
    return list(obter_sensores().find({}).sort("_id", 1))


def consultar_medicoes_sensor(sensor_id, inicio, fim):

    filtro = {
        "sensor_id": sensor_id,
        "timestamp": {"$gte": inicio, "$lt": fim}
    }

    cursor = obter_medicoes().find(filtro, {"_id": 0}).sort("timestamp", 1)

    return list(cursor)


def obter_ultima_janela():

    ultima = obter_medicoes().find_one(
        {},
        {"_id": 0, "timestamp": 1},
        sort=[("timestamp", -1)]
    )

    if ultima is None:
        return None

    inicio = ultima["timestamp"].replace(
        minute=0, second=0, microsecond=0
    )

    return inicio, inicio + timedelta(hours=1)


def filtro_janela(inicio, fim):

    filtro = {"timestamp": {"$gte": inicio, "$lt": fim}}
    filtro.update(FILTRO_VALIDAS)

    return filtro


def montar_projecao(inicio, fim, identificadores):

    return {
        "_id": 0,
        **identificadores,
        "inicio_periodo": {"$literal": inicio},
        "fim_periodo": {"$literal": fim},
        "qt_medicoes": 1,
        "pm25_media": {"$round": ["$pm25_media", 1]},
        "pm10_media": {"$round": ["$pm10_media", 1]},
        "co2_media": {"$round": ["$co2_media", 1]},
        "temperatura_media": {"$round": ["$temperatura_media", 1]},
        "umidade_media": {"$round": ["$umidade_media", 1]},
        "pm25_max": 1,
        "pm10_max": 1
    }


def resumo_por_sensor(inicio, fim):

    pipeline = [
        {"$match": filtro_janela(inicio, fim)},
        {"$group": {"_id": "$sensor_id", **ESTATISTICAS}},
        {"$project": montar_projecao(
            inicio, fim, {"sensor_id": "$_id"}
        )},
        {"$sort": {"sensor_id": 1}}
    ]

    return list(obter_medicoes().aggregate(pipeline))


def resumo_por_cidade(inicio, fim):

    pipeline = [
        {"$match": filtro_janela(inicio, fim)},
        {"$lookup": {
            "from": COLECAO_SENSORES,
            "localField": "sensor_id",
            "foreignField": "_id",
            "as": "sensor"
        }},
        {"$unwind": "$sensor"},
        {"$group": {
            "_id": {
                "uf": "$sensor.localizacao.uf",
                "cidade": "$sensor.localizacao.cidade"
            },
            **ESTATISTICAS
        }},
        {"$project": montar_projecao(
            inicio, fim, {"uf": "$_id.uf", "cidade": "$_id.cidade"}
        )},
        {"$sort": {"uf": 1, "cidade": 1}}
    ]

    return list(obter_medicoes().aggregate(pipeline))


def ler_data(rotulo, padrao):

    while True:
        texto = input(f"{rotulo} [{padrao:%Y-%m-%d %H:%M}]: ").strip()

        if not texto:
            return padrao

        try:
            return datetime.strptime(
                texto, "%Y-%m-%d %H:%M"
            ).replace(tzinfo=timezone.utc)

        except ValueError:
            print("Formato inválido. Use AAAA-MM-DD HH:MM.")


def main():

    sensores = listar_sensores()

    if not sensores:
        raise RuntimeError(
            "Nenhum sensor cadastrado. Execute a etapa 1 primeiro."
        )

    janela = obter_ultima_janela()

    if janela is None:
        raise RuntimeError(
            "Nenhuma medição encontrada. Execute a etapa 2 primeiro."
        )

    print("Sensores cadastrados:")

    for sensor in sensores:
        local = sensor["localizacao"]

        print(
            f"  {sensor['_id']} - {local['cidade']}/{local['uf']} - "
            f"{sensor['descricao']}"
        )

    padrao_sensor = sensores[0]["_id"]
    inicio_padrao, fim_padrao = janela

    print("\nConsulta por sensor e intervalo (horários em UTC).")
    print("Pressione Enter para usar o valor entre colchetes.\n")

    sensor_id = input(f"Sensor [{padrao_sensor}]: ").strip().upper()
    sensor_id = sensor_id or padrao_sensor

    inicio = ler_data("Início", inicio_padrao)
    fim = ler_data("Fim   ", fim_padrao)

    if fim <= inicio:
        print("\nERRO: o fim do intervalo deve ser maior que o início.")
        return

    medicoes = consultar_medicoes_sensor(sensor_id, inicio, fim)

    print(
        f"\nSensor {sensor_id}: {len(medicoes)} medições entre "
        f"{inicio:%Y-%m-%d %H:%M} e {fim:%Y-%m-%d %H:%M}"
    )

    if not medicoes:
        return

    cabecalho = (
        f"{'Data/hora (UTC)':<18}{'PM2.5':>8}{'PM10':>8}"
        f"{'CO2':>8}{'Temp':>8}{'Umid':>8}"
    )

    print("\n" + cabecalho)
    print("-" * len(cabecalho))

    for medicao in medicoes[:LIMITE_EXIBICAO]:
        print(
            f"{medicao['timestamp']:%Y-%m-%d %H:%M}  "
            f"{formatar_numero(medicao.get('pm25')):>8}"
            f"{formatar_numero(medicao.get('pm10')):>8}"
            f"{formatar_numero(medicao.get('co2'), 0):>8}"
            f"{formatar_numero(medicao.get('temperatura')):>8}"
            f"{formatar_numero(medicao.get('umidade'), 0):>8}"
        )

    restantes = len(medicoes) - LIMITE_EXIBICAO

    if restantes > 0:
        print(f"... e mais {restantes} medições.")


if __name__ == "__main__":
    main()