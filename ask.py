import argparse

from perguntas_respostas.respostas_generativas import obter_resposta_ollama


def main() -> None:
    parser = argparse.ArgumentParser(description="Envie uma pergunta ao Ollama local.")
    parser.add_argument("pergunta", help="Pergunta entre aspas")
    pergunta = parser.parse_args().pergunta.strip()
    if not pergunta:
        parser.error("a pergunta deve conter texto")
    print(obter_resposta_ollama(pergunta))


if __name__ == "__main__":
    main()
