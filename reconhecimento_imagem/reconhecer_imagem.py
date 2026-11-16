from pathlib import Path
from pickle import UnpicklingError

import torch
from PIL import Image
from torchvision import transforms

if __package__:
    from .modelo import Net
else:
    from modelo import Net


CLASSES = ("garrafas", "gatos")
CHECKPOINT = Path(__file__).resolve().parents[1] / "reconhecedor_objetos_pytorch.pth"
PREPROCESSAMENTO = transforms.Compose([
    transforms.Resize((32, 32)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])


def carregar_modelo() -> Net:
    modelo = Net(num_classes=len(CLASSES))
    modelo.load_state_dict(torch.load(CHECKPOINT, map_location="cpu", weights_only=True))
    modelo.eval()
    return modelo


@torch.inference_mode()
def classificar_imagem(modelo: Net, imagem_rgb: Image.Image) -> str:
    entrada = PREPROCESSAMENTO(imagem_rgb).unsqueeze(0)
    indice = int(modelo(entrada).argmax(dim=1).item())
    return CLASSES[indice]


def iniciar_reconhecimento_objetos() -> None:
    try:
        import cv2
    except ImportError:
        print("O reconhecimento pela webcam requer opencv-contrib-python.")
        return

    try:
        modelo = carregar_modelo()
    except (OSError, RuntimeError, UnpicklingError, EOFError):
        print("Não foi possível carregar o checkpoint da CNN.")
        return

    camera = cv2.VideoCapture(0)
    try:
        while True:
            status, frame = camera.read()
            if not status:
                break

            rgb = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            classe = classificar_imagem(modelo, rgb)
            cv2.putText(frame, classe, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.imshow("Reconhecimento de Imagem", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    except cv2.error:
        print("Não foi possível usar a webcam para o reconhecimento de objetos.")
    finally:
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    iniciar_reconhecimento_objetos()
