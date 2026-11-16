from contextlib import closing
from http.client import HTTPConnection, HTTPException
import json
import os


MODELO_PADRAO = "qwen3.5:9b"
TIMEOUT_SEGUNDOS = 60


def obter_resposta_ollama(pergunta: str) -> str:
    modelo = os.getenv("AURA_OLLAMA_MODEL", "").strip() or MODELO_PADRAO
    corpo = json.dumps({
        "model": modelo,
        "prompt": pergunta,
        "stream": False,
        "think": False,
    }).encode("utf-8")

    try:
        with closing(HTTPConnection("127.0.0.1", 11434, timeout=TIMEOUT_SEGUNDOS)) as conexao:
            conexao.request("POST", "/api/generate", body=corpo, headers={"Content-Type": "application/json"})
            with conexao.getresponse() as resposta:
                if resposta.status == 404:
                    return "O modelo configurado não está disponível no Ollama local."
                if resposta.status != 200:
                    return "O Ollama não conseguiu gerar uma resposta."
                dados = json.loads(resposta.read())
    except TimeoutError:
        return "O Ollama demorou demais para responder. Tente novamente."
    except OSError:
        return "Não foi possível conectar ao Ollama local. Verifique se ele está em execução."
    except (HTTPException, ValueError):
        return "O Ollama retornou uma resposta inválida."

    texto = dados.get("response") if isinstance(dados, dict) else None
    if not isinstance(texto, str) or not texto.strip():
        return "O Ollama retornou uma resposta inválida."
    return texto.strip()
