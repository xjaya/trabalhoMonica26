import importlib.util
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent
sys.path.insert(0, str(PASTA))

ETAPAS = {
    "1": ("Preparar banco de dados e sensores", "01_banco_dados.py"),
    "2": ("Gerar medições simuladas", "02_gerar_medicoes.py"),
    "3": ("Calcular agregações horárias", "03_agregacoes.py"),
    "4": ("Armazenar e consultar resumos no Redis", "04_redis.py"),
    "5": ("Consultar medições por sensor e intervalo", "consultas.py"),
}


def executar_etapa(arquivo):
    print(f"\n{'=' * 60}\nEXECUTANDO: {arquivo}\n{'=' * 60}")

    try:
        caminho = PASTA / arquivo
        spec = importlib.util.spec_from_file_location(caminho.stem, caminho)
        modulo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modulo)
        modulo.main()

    except Exception as erro:
        print(f"\nERRO em {arquivo}: {erro}")
        return False

    print(f"\nEtapa concluída: {arquivo}")
    return True


def executar_todas():
    for chave in "1234":
        if not executar_etapa(ETAPAS[chave][1]):
            print("\nExecução interrompida. Corrija o erro antes de continuar.")
            return

    print("\nPROJETO EXECUTADO COM SUCESSO!")


def exibir_menu():
    while True:
        print(f"\n{'=' * 60}")
        print(" MONITORAMENTO DA QUALIDADE DO AR")
        print(" Integração MongoDB + Redis com Python")
        print("=" * 60)

        for chave, (titulo, _) in ETAPAS.items():
            print(f"{chave} - {titulo}")

        print("6 - Executar etapas 1 a 4")
        print("0 - Sair")

        opcao = input("\nEscolha uma opção: ").strip()

        if opcao in ETAPAS:
            executar_etapa(ETAPAS[opcao][1])
        elif opcao == "6":
            executar_todas()
        elif opcao == "0":
            break
        else:
            print("\nOpção inválida.")


if __name__ == "__main__":
    try:
        exibir_menu()
    except KeyboardInterrupt:
        print("\n\nExecução interrompida pelo usuário.")
