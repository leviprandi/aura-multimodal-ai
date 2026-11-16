import json
import os
import unittest
from unittest.mock import patch

from perguntas_respostas.respostas_generativas import obter_resposta_ollama


class OllamaTest(unittest.TestCase):
    def setUp(self):
        servidor = self.enterContext(patch("perguntas_respostas.respostas_generativas.HTTPConnection"))
        self.servidor = servidor
        self.conexao = servidor.return_value
        self.resposta = self.conexao.getresponse.return_value.__enter__.return_value
        self.resposta.status = 200
        self.resposta.read.return_value = b'{"response": "  Oi  "}'

    def test_envia_pergunta_ao_modelo_padrao_sem_streaming(self):
        with patch.dict(os.environ, {"AURA_OLLAMA_MODEL": ""}):
            self.assertEqual(obter_resposta_ollama("Olá"), "Oi")
        self.servidor.assert_called_once_with("127.0.0.1", 11434, timeout=60)
        args, kwargs = self.conexao.request.call_args
        self.assertEqual(args, ("POST", "/api/generate"))
        self.assertEqual(json.loads(kwargs["body"]), {
            "model": "qwen3.5:9b", "prompt": "Olá", "stream": False, "think": False,
        })
        self.conexao.close.assert_called_once()

    def test_modelo_configuravel_e_indisponivel(self):
        self.resposta.status = 404
        with patch.dict(os.environ, {"AURA_OLLAMA_MODEL": "outro:1b"}):
            self.assertIn("modelo configurado não está disponível", obter_resposta_ollama("teste"))
        self.assertEqual(json.loads(self.conexao.request.call_args.kwargs["body"])["model"], "outro:1b")

    def test_timeout_e_conexao_recusada(self):
        for erro, mensagem in [(TimeoutError, "demorou demais"), (ConnectionRefusedError, "conectar")]:
            with self.subTest(erro=erro):
                self.conexao.request.side_effect = erro
                self.assertIn(mensagem, obter_resposta_ollama("teste"))

    def test_resposta_invalida(self):
        for corpo in (b"sem JSON", b"[]", b'{"response": 7}', b'{"response": "   "}'):
            with self.subTest(corpo=corpo):
                self.resposta.read.return_value = corpo
                self.assertIn("resposta inválida", obter_resposta_ollama("teste"))

    def test_erro_do_servidor(self):
        self.resposta.status = 500
        self.assertIn("não conseguiu gerar", obter_resposta_ollama("teste"))
        self.resposta.read.assert_not_called()
