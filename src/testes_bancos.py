
import json
import os
import unittest
import uuid
from datetime import datetime

from pymongo import MongoClient
from redis import Redis

from src.dados_teste import MEDICOES_TESTE


class TestesBancos(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mongo = MongoClient(
            os.getenv("MONGO_URI", "mongodb://localhost:27017/"),
            serverSelectionTimeoutMS=3000
        )

        cls.redis = Redis.from_url(
            os.getenv("REDIS_URL", "redis://localhost:6379/0"),
            decode_responses=True
        )

        cls.mongo.admin.command("ping")
        cls.redis.ping()

        cls.db_name = "qualidade_ar_teste_" + uuid.uuid4().hex[:12]
        cls.col = cls.mongo[cls.db_name]["medicoes"]
        cls.prefixo = "teste_ar:" + uuid.uuid4().hex + ":"

    @classmethod
    def tearDownClass(cls):
        try:
            cls.mongo.drop_database(cls.db_name)

            chaves = list(cls.redis.scan_iter(
                match=cls.prefixo + "*"
            ))

            if chaves:
                cls.redis.delete(*chaves)
        finally:
            cls.mongo.close()
            cls.redis.close()

    def setUp(self):
        self.col.delete_many({})

        chaves = list(self.redis.scan_iter(
            match=self.prefixo + "*"
        ))

        if chaves:
            self.redis.delete(*chaves)

    def test_01_inserir_medicoes(self):
        resultado = self.col.insert_many(
            [dict(dado) for dado in MEDICOES_TESTE]
        )

        self.assertEqual(len(resultado.inserted_ids), 3)
        self.assertEqual(self.col.count_documents({}), 3)

    def test_02_consultar_medicao(self):
        self.col.insert_many(
            [dict(dado) for dado in MEDICOES_TESTE]
        )

        resultado = self.col.find_one({
            "cidade": "Cidade Teste Beta",
            "poluente": "PM10"
        })

        self.assertIsNotNone(resultado)
        self.assertEqual(resultado["valor"], 48.0)

    def test_03_atualizar_medicao(self):
        self.col.insert_one(dict(MEDICOES_TESTE[0]))

        resultado = self.col.update_one(
            {"cidade": "Cidade Teste Alfa"},
            {"$set": {"valor": 16.2}}
        )

        self.assertEqual(resultado.modified_count, 1)

        medicao = self.col.find_one({
            "cidade": "Cidade Teste Alfa"
        })

        self.assertEqual(medicao["valor"], 16.2)

    def test_04_excluir_medicao(self):
        self.col.insert_one(dict(MEDICOES_TESTE[0]))

        resultado = self.col.delete_one({
            "cidade": "Cidade Teste Alfa"
        })

        self.assertEqual(resultado.deleted_count, 1)
        self.assertEqual(self.col.count_documents({}), 0)

    def test_05_armazenamento_redis(self):
        chave = self.prefixo + "medicao:alfa"

        dados = {
            "cidade": "Cidade Teste Alfa",
            "poluente": "PM2.5",
            "valor": 12.5
        }

        self.redis.set(
            chave,
            json.dumps(dados),
            ex=60
        )

        resultado = json.loads(self.redis.get(chave))

        self.assertEqual(resultado, dados)
        self.assertGreater(self.redis.ttl(chave), 0)

    def test_06_integracao_mongodb_redis(self):
        self.col.insert_one(dict(MEDICOES_TESTE[2]))

        chave = self.prefixo + "consulta:gama"

        self.assertIsNone(self.redis.get(chave))

        documento = self.col.find_one(
            {"cidade": "Cidade Teste Gama"},
            {"_id": 0}
        )

        self.assertIsNotNone(documento)

        if isinstance(documento["data_hora"], datetime):
            documento["data_hora"] = documento["data_hora"].isoformat()

        self.redis.set(
            chave,
            json.dumps(documento, ensure_ascii=False),
            ex=60
        )

        resultado = json.loads(self.redis.get(chave))

        self.assertEqual(resultado["cidade"], "Cidade Teste Gama")
        self.assertEqual(resultado["valor"], 31.8)


if __name__ == "__main__":
    unittest.main(verbosity=2)
