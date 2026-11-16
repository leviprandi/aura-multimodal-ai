import io
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import torch
from PIL import Image

import predict
from reconhecimento_imagem import reconhecer_imagem
from reconhecimento_imagem.modelo import Net


class PredictTest(unittest.TestCase):
    def setUp(self):
        self.pasta = Path(self.enterContext(TemporaryDirectory()))
        self.imagem = self.pasta / "entrada teste.png"

    def test_classifica_rgb_e_preserva_os_dois_rotulos(self):
        Image.new("RGB", (65, 48), (50, 150, 200)).save(self.imagem)
        checkpoint = self.pasta / "pesos sinteticos.pth"
        modelo = Net()
        with torch.no_grad():
            for parametro in modelo.parameters():
                parametro.zero_()
        args = ["predict.py", "--image", str(self.imagem)]
        for indice, rotulo in enumerate(("garrafas", "gatos")):
            with self.subTest(rotulo=rotulo):
                with torch.no_grad():
                    modelo.fc2.bias.zero_()
                    modelo.fc2.bias[indice] = 1.0
                torch.save(modelo.state_dict(), checkpoint)
                with patch.object(reconhecer_imagem, "CHECKPOINT", checkpoint), patch("sys.argv", args):
                    with redirect_stdout(io.StringIO()) as saida:
                        predict.main()
                self.assertEqual(saida.getvalue().strip(), rotulo)

    def test_informa_checkpoint_ausente_com_imagem_valida(self):
        Image.new("RGB", (32, 32)).save(self.imagem)
        args = ["predict.py", "--image", str(self.imagem)]
        with patch.object(reconhecer_imagem, "CHECKPOINT", self.pasta / "ausente.pth"), patch("sys.argv", args):
            with redirect_stderr(io.StringIO()) as saida, self.assertRaises(SystemExit) as erro:
                predict.main()
        self.assertEqual(erro.exception.code, 1)
        self.assertIn("checkpoint da CNN ausente", saida.getvalue())

    def test_rejeita_arquivo_inexistente_corrompido_ou_diretorio(self):
        corrompida = self.pasta / "imagem corrompida.png"
        corrompida.write_bytes(b"arquivo de teste")
        for entrada, mensagem in ((self.imagem, "inexistente"), (corrompida, "corrompida"), (self.pasta, "incompatível")):
            with self.subTest(entrada=entrada), patch("sys.argv", ["predict.py", "--image", str(entrada)]):
                with redirect_stderr(io.StringIO()) as saida, self.assertRaises(SystemExit) as erro:
                    predict.main()
                self.assertEqual(erro.exception.code, 1)
                self.assertIn(mensagem, saida.getvalue())
