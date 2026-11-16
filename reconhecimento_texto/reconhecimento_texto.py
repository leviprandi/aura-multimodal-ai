import cv2
import easyocr

def iniciar_reconhecimento_texto():
    print("Iniciando reconhecimento de texto... Pressione 'q' na janela para voltar ao menu.")
    try:
        # gpu=False é mais seguro se você não tiver certeza sobre a configuração da sua GPU
        reader = easyocr.Reader(['pt', 'en'], gpu=False, download_enabled=False)
        camera = cv2.VideoCapture(0)
        frame_contador = 0

        while True:
            status, frame = camera.read()
            if not status: break

            frame_contador += 1
            if frame_contador % 10 == 0:
                results = reader.readtext(frame)
                if results:
                    print("\n--- Texto Detectado ---")
                    for (bbox, texto, conf) in results:
                        print(f"{texto} (Conf: {conf:.2f})")
                        top_left = tuple(map(int, bbox[0]))
                        bottom_right = tuple(map(int, bbox[2]))
                        cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)

            cv2.imshow("Reconhecimento de Texto", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except Exception as e:
        print(f"Ocorreu um erro no OCR: {e}")
    finally:
        if 'camera' in locals():
            camera.release()
            cv2.destroyAllWindows()

if __name__ == '__main__':
    iniciar_reconhecimento_texto()
