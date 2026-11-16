import datetime
from collections.abc import Callable

from agenda_sistema.agenda import Agenda
from habilidades_extras.habilidades import abrir_sites_e_programas, calcular, contar_piada
from perguntas_respostas.respostas_generativas import obter_resposta_ollama


NOME_ASSISTENTE = "assistente"


def informar_data_hora(falar: Callable[[str], None]) -> None:
    """Informa a data e a hora atuais."""
    agora = datetime.datetime.now()
    data_formatada = agora.strftime("Hoje é %d de %B de %Y")
    hora_formatada = agora.strftime("e agora são %H horas e %M minutos")
    falar(f"{data_formatada}, {hora_formatada}.")

def gerenciar_novo_evento(
    falar: Callable[[str], None], escutar_comando: Callable[[], str | None], agenda: Agenda
) -> None:
    """Orquestra a conversa de múltiplos passos para cadastrar um novo evento."""
    falar("Qual o dia do evento?")
    dia = escutar_comando()
    if not dia:
        falar("Não entendi o dia. Operação cancelada.")
        return

    falar("Que horas?")
    horas = escutar_comando()
    if not horas:
        falar("Não entendi a hora. Operação cancelada.")
        return

    falar("Qual a duração?")
    duracao = escutar_comando()
    if not duracao:
        falar("Não entendi a duração. Operação cancelada.")
        return

    falar("Por último, qual o nome do evento?")
    nome = escutar_comando()
    if not nome:
        falar("Não entendi o nome. Operação cancelada.")
        return

    evento_completo = f"Evento: {nome}, no dia {dia} às {horas}, com duração de {duracao}."
    confirmacao = agenda.adicionar_evento(evento_completo)
    falar(confirmacao)


def executar_comando(
    comando: str,
    falar: Callable[[str], None],
    escutar_comando: Callable[[], str | None],
    agenda: Agenda,
) -> bool:
    """Executa um comando e informa se o assistente deve continuar escutando."""
    if "reconhecimento facial" in comando:
        try:
            from reconhecimento_facial.reconhecimento import iniciar_reconhecimento_facial
        except ImportError:
            falar("Este comando requer OpenCV contrib.")
            return True
        falar("Ok, iniciando o reconhecimento facial.")
        iniciar_reconhecimento_facial()
        falar("Módulo de reconhecimento facial finalizado.")

    elif "reconhecer imagem" in comando or "reconhecer objeto" in comando:
        try:
            from reconhecimento_imagem.reconhecer_imagem import iniciar_reconhecimento_objetos
        except ImportError:
            falar("Este comando requer as dependências de visão.")
            return True
        falar("Ok, iniciando o reconhecimento de objetos.")
        iniciar_reconhecimento_objetos()
        falar("Módulo de reconhecimento de objetos finalizado.")

    elif "texto" in comando and any(acao in comando for acao in ("reconhecer", "ler", "reconheça")):
        try:
            from reconhecimento_texto.reconhecimento_texto import iniciar_reconhecimento_texto
        except ImportError:
            falar("Este comando requer OpenCV e EasyOCR.")
            return True
        falar("Certo, iniciando o reconhecimento de texto pela câmera.")
        iniciar_reconhecimento_texto()
        falar("Módulo de reconhecimento de texto finalizado.")

    elif any(frase in comando for frase in ("que dia é hoje", "qual a data", "que horas são")):
        informar_data_hora(falar)

    elif "marcar evento" in comando or "cadastrar evento" in comando:
        gerenciar_novo_evento(falar, escutar_comando, agenda)

    elif "ler agenda" in comando:
        resposta_agenda = agenda.ler_eventos()
        falar(resposta_agenda)

    elif "limpar agenda" in comando:
        resposta_agenda = agenda.limpar_agenda()
        falar(resposta_agenda)

    elif "abrir" in comando:
        abrir_sites_e_programas(comando, falar)

    elif "piada" in comando:
        contar_piada(falar)

    elif "quanto é" in comando or "calcule" in comando:
        calcular(comando, falar)

    elif "encerrar" in comando or "desligar" in comando:
        falar("Encerrando. Até a próxima!")
        return False

    else:
        resposta_da_ia = obter_resposta_ollama(comando)
        falar(resposta_da_ia)
    return True


def main() -> None:
    try:
        import pyttsx3
        import speech_recognition as sr

        sr.Microphone.get_pyaudio()
    except (ImportError, AttributeError):
        raise SystemExit("O modo de voz requer SpeechRecognition, PyAudio (PortAudio) e pyttsx3.") from None

    reconhecedor = sr.Recognizer()
    sintetizador = pyttsx3.init()
    sintetizador.setProperty("rate", 180)
    sintetizador.setProperty("volume", 1.0)
    agenda = Agenda()

    def falar(texto: str) -> None:
        """Função central para a assistente falar."""
        if texto:
            print(f"AURA: {texto}")
            sintetizador.say(texto)
            sintetizador.runAndWait()

    def escutar_comando() -> str | None:
        """Escuta o microfone e retorna o texto reconhecido."""
        try:
            with sr.Microphone() as mic:
                reconhecedor.adjust_for_ambient_noise(mic, duration=1)
                print("Aguardando comando...")
                audio = reconhecedor.listen(mic, timeout=5, phrase_time_limit=20)
                print("Reconhecendo...")
                texto_comando = reconhecedor.recognize_google(audio, language='pt-BR')
                return texto_comando.lower()
        except sr.WaitTimeoutError:
            print("Tempo de escuta esgotado.")
            return None
        except sr.UnknownValueError:
            print("Não consegui entender o áudio.")
            return None
        except (OSError, sr.RequestError):
            print("Não foi possível obter ou transcrever o áudio.")
            return None

    falar(f"AURA iniciada. Diga '{NOME_ASSISTENTE}' para me ativar.")

    while True:
        print(f"\nOuvindo para a palavra de ativação '{NOME_ASSISTENTE}'...")
        comando_inicial = escutar_comando()

        if comando_inicial and NOME_ASSISTENTE in comando_inicial:
            falar("Sim? Estou ouvindo o seu comando.")
            comando_final = escutar_comando()

            if not comando_final:
                falar("Não ouvi seu comando. Por favor, tente novamente.")
                continue

            if not executar_comando(comando_final, falar, escutar_comando, agenda):
                break


if __name__ == "__main__":
    main()
