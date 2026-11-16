import argparse
from pathlib import Path
from pickle import UnpicklingError


def main() -> None:
    parser = argparse.ArgumentParser(description="Classifique uma imagem com a CNN da AURA.")
    parser.add_argument("--image", type=Path, required=True, help="Caminho da imagem")
    args = parser.parse_args()

    try:
        from PIL import Image
        from reconhecimento_imagem.reconhecer_imagem import carregar_modelo, classificar_imagem
    except ImportError:
        parser.exit(1, "Erro: instale as dependências de requirements.txt.\n")

    try:
        with Image.open(args.image) as imagem:
            rgb = imagem.convert("RGB")
    except FileNotFoundError:
        parser.exit(1, "Erro: arquivo de imagem inexistente.\n")
    except (OSError, ValueError, Image.DecompressionBombError):
        parser.exit(1, "Erro: imagem inválida, corrompida ou incompatível.\n")

    try:
        modelo = carregar_modelo()
    except FileNotFoundError:
        parser.exit(1, "Erro: checkpoint da CNN ausente. Consulte o README.md para usar uma cópia autorizada.\n")
    except (OSError, RuntimeError, UnpicklingError, EOFError):
        parser.exit(1, "Erro: não foi possível carregar o checkpoint da CNN.\n")

    print(classificar_imagem(modelo, rgb))


if __name__ == "__main__":
    main()
