from contextlib import redirect_stderr, redirect_stdout
import io
import unittest
from unittest.mock import patch

import ask


class AskTest(unittest.TestCase):
    def test_imprime_resposta_da_integracao(self):
        with patch("ask.obter_resposta_ollama", return_value="Resposta local") as ollama:
            with patch("sys.argv", ["ask.py", " Explique o que é uma CNN "]), redirect_stdout(io.StringIO()) as saida:
                ask.main()
        ollama.assert_called_once_with("Explique o que é uma CNN")
        self.assertEqual(saida.getvalue().strip(), "Resposta local")

    def test_rejeita_pergunta_vazia_ou_ausente(self):
        for argumentos in ([], ["   "]):
            with self.subTest(argumentos=argumentos), patch("sys.argv", ["ask.py", *argumentos]):
                with patch("ask.obter_resposta_ollama") as ollama, redirect_stderr(io.StringIO()) as saida:
                    with self.assertRaises(SystemExit) as erro:
                        ask.main()
                self.assertEqual(erro.exception.code, 2)
                self.assertIn("pergunta", saida.getvalue())
                ollama.assert_not_called()
