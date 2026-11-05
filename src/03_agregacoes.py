
from pprint import pprint


def criar_pipeline_por_sensor():
    pipeline = [
        {
            "$match": {
                "timestamp": {"$type": "date"},
                "sensor_id": {"$exists": True}
            }
        },
        {
            "$group": {
                "_id": {
                    "sensor_id": "$sensor_id",
                    "hora": {
                        "$dateTrunc": {
                            "date": "$timestamp",
                            "unit": "hour"
                        }
                    }
                },
                "qt_medicoes": {"$sum": 1},
                "pm25_media": {"$avg": "$pm25"},
                "pm10_media": {"$avg": "$pm10"},
                "co2_media": {"$avg": "$co2"},
                "temperatura_media": {"$avg": "$temperatura"},
                "umidade_media": {"$avg": "$umidade"},
                "pm25_max": {"$max": "$pm25"},
                "pm10_max": {"$max": "$pm10"}
            }
        },
        {
            "$project": {
                "_id": 0,
                "sensor_id": "$_id.sensor_id",
                "inicio_periodo": "$_id.hora",
                "fim_periodo": {
                    "$dateAdd": {
                        "startDate": "$_id.hora",
                        "unit": "hour",
                        "amount": 1
                    }
                },
                "qt_medicoes": 1,
                "pm25_media": 1,
                "pm10_media": 1,
                "co2_media": 1,
                "temperatura_media": 1,
                "umidade_media": 1,
                "pm25_max": 1,
                "pm10_max": 1
            }
        },
        {
            "$sort": {
                "sensor_id": 1,
                "inicio_periodo": 1
            }
        }
    ]

    return pipeline


def criar_pipeline_por_cidade():
    pipeline = [
        {
            "$match": {
                "timestamp": {"$type": "date"},
                "sensor_id": {"$exists": True}
            }
        },
        {
            "$lookup": {
                "from": "Sensores",
                "localField": "sensor_id",
                "foreignField": "_id",
                "as": "sensor"
            }
        },
        {
            "$unwind": "$sensor"
        },
        {
            "$group": {
                "_id": {
                    "cidade": "$sensor.localizacao.cidade",
                    "uf": "$sensor.localizacao.uf",
                    "hora": {
                        "$dateTrunc": {
                            "date": "$timestamp",
                            "unit": "hour"
                        }
                    }
                },
                "qt_medicoes": {"$sum": 1},
                "pm25_media": {"$avg": "$pm25"},
                "pm10_media": {"$avg": "$pm10"},
                "co2_media": {"$avg": "$co2"},
                "temperatura_media": {"$avg": "$temperatura"},
                "umidade_media": {"$avg": "$umidade"},
                "pm25_max": {"$max": "$pm25"},
                "pm10_max": {"$max": "$pm10"}
            }
        },
        {
            "$project": {
                "_id": 0,
                "cidade": "$_id.cidade",
                "uf": "$_id.uf",
                "inicio_periodo": "$_id.hora",
                "fim_periodo": {
                    "$dateAdd": {
                        "startDate": "$_id.hora",
                        "unit": "hour",
                        "amount": 1
                    }
                },
                "qt_medicoes": 1,
                "pm25_media": 1,
                "pm10_media": 1,
                "co2_media": 1,
                "temperatura_media": 1,
                "umidade_media": 1,
                "pm25_max": 1,
                "pm10_max": 1
            }
        },
        {
            "$sort": {
                "cidade": 1,
                "inicio_periodo": 1
            }
        }
    ]

    return pipeline

def executar_agregacao_por_sensor(db):
    """
    Executa a agregação por sensor e retorna os resultados.
    """
    pipeline = criar_pipeline_por_sensor()

    resultados = list(
        db["Medicoes"].aggregate(pipeline)
    )

    return resultados

def executar_agregacao_por_cidade(db):
    """
    Executa a agregação por cidade e retorna os resultados.
    """
    pipeline = criar_pipeline_por_cidade()

    resultados = list(
        db["Medicoes"].aggregate(pipeline)
    )

    return resultados

def obter_resumos(db):
    """
    Retorna os resumos por sensor e por cidade.
    """

    resumos = {
        "por_sensor": executar_agregacao_por_sensor(db),
        "por_cidade": executar_agregacao_por_cidade(db)
    }

    return resumos

def main():
    print("========================================")
    print(" AGREGACOES - QUALIDADE DO AR")
    print("========================================")

    pipeline_sensor = criar_pipeline_por_sensor()
    pipeline_cidade = criar_pipeline_por_cidade()

    print("\n========== PIPELINE POR SENSOR ==========")
    pprint(pipeline_sensor, sort_dicts=False)

    print("\n========== PIPELINE POR CIDADE ==========")
    pprint(pipeline_cidade, sort_dicts=False)


if __name__ == "__main__":
    main()
