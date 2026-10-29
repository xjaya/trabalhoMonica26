
import importlib.util
import sys
from pathlib import Path


PASTA_CODIGO = Path(__file__).resolve().parent


def carregar_modulo(nome_arquivo, nome_modulo):
    caminho = PASTA_CODIGO / nome_arquivo

    if not caminho.exists():
        print(f"\nERRO: arquivo não encontrado: {caminho}")
        return None

    try:
        spec = importlib.util.spec_from_file_location(
            nome_modulo, caminho
        )

        if spec is None or spec.loader is None:
            print(f"\nERRO ao carregar {nome_arquivo}.")
            return None

        modulo = importlib.util.module_from_spec(spec)
        sys.modules[nome_modulo] = modulo
        spec.loader.exec_module(modulo)

        return modulo

    except Exception as erro:
        print(f"\nERRO ao importar {nome_arquivo}: {erro}")
        return None


def executar_etapa(nome_arquivo, nome_modulo):
 
    modulo = carregar_modulo(nome_arquivo, nome_modulo)

    if modulo is None:
        return False

    funcao_main = getattr(modulo, "main", None)

    if not callable(funcao_main):
        print(
            f"\nERRO: {nome_arquivo} precisa possuir "
            "uma função main()."
        )
        return False

    try:
        print("\n" + "=" * 60)
        print(f"EXECUTANDO: {nome_arquivo}")
        print("=" * 60)

        funcao_main()

        print(f"\nEtapa concluída: {nome_arquivo}")
        return True

    except Exception as erro:
        print(f"\nERRO durante {nome_arquivo}: {erro}")
        return False


def executar_todas():
   
    etapas = [
        ("01_banco_dados.py", "banco_dados"),
        ("02_gerar_medicoes.py", "gerar_medicoes"),
        ("03_agregacoes.py", "agregacoes"),
        ("04_redis.py", "redis_integracao"),
    ]

    for arquivo, modulo in etapas:
        sucesso = executar_etapa(arquivo, modulo)

        if not sucesso:
            print(
                "\nExecução interrompida. "
                "Corrija o erro antes de continuar."
            )
            return

    print("\n" + "=" * 60)
    print("PROJETO EXECUTADO COM SUCESSO!")
    print("Sensores, medições, agregações e Redis processados.")
    print("=" * 60)


def exibir_menu():
  
    while True:
        print("\n")
        print("=" * 60)
        print(" MONITORAMENTO DA QUALIDADE DO AR")
        print(" Integração MongoDB + Redis com Python")
        print("=" * 60)

        print("1 - Preparar banco de dados e sensores")
        print("2 - Gerar medições simuladas")
        print("3 - Calcular agregações horárias")
        print("4 - Armazenar e consultar resumos no Redis")
        print("5 - Executar todas as etapas")
        print("0 - Sair")

        opcao = input("\nEscolha uma opção: ").strip()

        if opcao == "1":
            executar_etapa(
                "01_banco_dados.py", "banco_dados"
            )

        elif opcao == "2":
            executar_etapa(
                "02_gerar_medicoes.py", "gerar_medicoes"
            )

        elif opcao == "3":
            executar_etapa(
                "03_agregacoes.py", "agregacoes"
            )

        elif opcao == "4":
            executar_etapa(
                "04_redis.py", "redis_integracao"
            )

        elif opcao == "5":
            executar_todas()

        elif opcao == "0":
            print("\nEncerrando o sistema...")
            break

        else:
            print("\nOpção inválida. Tente novamente.")


if __name__ == "__main__":
    try:
        exibir_menu()
    except KeyboardInterrupt:
        print("\n\nExecução interrompida pelo usuário.")
