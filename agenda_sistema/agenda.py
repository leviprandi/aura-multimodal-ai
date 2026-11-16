# agenda_sistema/agenda.py

class Agenda:
    def __init__(self, arquivo="agenda.txt"):
        """Inicializa a agenda, definindo o nome do arquivo e garantindo que ele exista."""
        self.arquivo = arquivo
        # Garante que o arquivo exista ao criar o objeto
        with open(self.arquivo, 'a'):
            pass

    def adicionar_evento(self, evento_completo):
        """Adiciona um evento formatado ao final do arquivo."""
        with open(self.arquivo, 'a', encoding='utf-8') as f:
            f.write(evento_completo + "\n")
        return f"Ok, evento '{evento_completo}' cadastrado com sucesso!"

    def ler_eventos(self):
        """Lê todos os eventos do arquivo e retorna como uma única string."""
        try:
            with open(self.arquivo, 'r', encoding='utf-8') as f:
                eventos = f.readlines()
            if not eventos:
                return "Sua agenda está vazia."
            else:
                # Junta todos os eventos em um único texto para ser falado
                eventos_formatados = "Aqui estão seus eventos: " + ". ".join([e.strip() for e in eventos])
                return eventos_formatados
        except FileNotFoundError:
            return "Arquivo da agenda não encontrado."

    def limpar_agenda(self):
        """Apaga todo o conteúdo do arquivo da agenda sem excluir o arquivo."""
        with open(self.arquivo, 'w'):
            pass
        return "Agenda limpa com sucesso!"