import sys
import unittest
from unittest.mock import Mock, patch

import assistente_voz
from agenda_sistema.agenda import Agenda


class RoteadorTest(unittest.TestCase):
    def setUp(self):
        self.falar = Mock()
        self.escutar = Mock()
        self.agenda = Mock(spec=Agenda)
        self.qwen = self.enterContext(patch("assistente_voz.obter_resposta_ollama", return_value="Resposta local"))

    def executar(self, comando):
        return assistente_voz.executar_comando(comando, self.falar, self.escutar, self.agenda)

    def test_pergunta_aberta_usa_qwen(self):
        self.assertTrue(self.executar("explique o ciclo da água"))
        self.qwen.assert_called_once_with("explique o ciclo da água")
        self.falar.assert_called_once_with("Resposta local")

    def test_calculo_agenda_e_encerramento_preservam_roteamento(self):
        self.assertTrue(self.executar("quanto é 2 mais 3 vezes 4?"))
        self.falar.assert_called_with("O resultado é 14")
        self.agenda.ler_eventos.return_value = "Evento fictício"
        self.assertTrue(self.executar("ler agenda"))
        self.agenda.ler_eventos.assert_called_once()
        self.falar.assert_called_with("Evento fictício")
        self.assertFalse(self.executar("encerrar"))
        self.qwen.assert_not_called()

    def test_calculo_rejeita_expoente_excessivo(self):
        self.assertTrue(self.executar("calcule 9**99999"))
        self.falar.assert_called_with("Desculpe, não consegui calcular isso.")
        self.qwen.assert_not_called()

    def test_comandos_de_visao_e_dependencia_opcional(self):
        visao = [
            ("reconhecimento facial", "reconhecimento_facial.reconhecimento", "iniciar_reconhecimento_facial"),
            ("reconhecer imagem", "reconhecimento_imagem.reconhecer_imagem", "iniciar_reconhecimento_objetos"),
            ("ler texto", "reconhecimento_texto.reconhecimento_texto", "iniciar_reconhecimento_texto"),
        ]
        for comando, modulo, nome in visao:
            with self.subTest(comando=comando):
                iniciar = Mock()
                with patch.dict(sys.modules, {modulo: Mock(**{nome: iniciar})}):
                    self.assertTrue(self.executar(comando))
                iniciar.assert_called_once()
        with patch.dict(sys.modules, {"reconhecimento_texto.reconhecimento_texto": None}):
            self.assertTrue(self.executar("ler texto"))
        self.falar.assert_called_with("Este comando requer OpenCV e EasyOCR.")
        self.qwen.assert_not_called()
