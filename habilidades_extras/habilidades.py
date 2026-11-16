# habilidades_extras/habilidades.py
import ast
import operator
import random
import webbrowser
import os
import re

def contar_piada(falar_func):
    """Seleciona uma piada e usa a função 'falar' fornecida para comunicá-la."""
    piadas = [
        "O que o pato falou para a pata? Vem quá!",
        "Por que a velhinha não usa relógio? Porque ela é uma senhora.",
        "Você conhece a piada do pônei? Pô nei eu...",
        "O que um cromossomo disse para o outro? Cromossomos felizes!"
    ]
    piada_escolhida = random.choice(piadas)
    falar_func(piada_escolhida)

def abrir_sites_e_programas(comando, falar_func):
    """Abre YouTube ou Calculadora e usa a função 'falar' para confirmar."""
    if "youtube" in comando:
        falar_func("Abrindo o YouTube.")
        webbrowser.open("https://www.youtube.com")
    elif "calculadora" in comando:
        falar_func("Abrindo a calculadora.")
        os.system("start calc") # Comando para Windows
    else:
        falar_func("Desculpe, não sei como abrir isso.")

OPERACOES = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Pow: operator.pow,
}


def avaliar_expressao(no: ast.AST) -> int | float:
    if isinstance(no, ast.Constant) and type(no.value) in (int, float):
        return no.value
    if isinstance(no, ast.UnaryOp) and isinstance(no.op, (ast.UAdd, ast.USub)):
        valor = avaliar_expressao(no.operand)
        return -valor if isinstance(no.op, ast.USub) else valor
    if isinstance(no, ast.BinOp) and type(no.op) in OPERACOES:
        esquerda = avaliar_expressao(no.left)
        direita = avaliar_expressao(no.right)
        if isinstance(no.op, ast.Pow) and abs(direita) > 100:
            raise ValueError("Expoente fora do limite.")
        resultado = OPERACOES[type(no.op)](esquerda, direita)
        if type(resultado) not in (int, float) or isinstance(resultado, int) and resultado.bit_length() > 4096:
            raise ValueError("Resultado fora do limite.")
        return resultado
    raise ValueError("Expressão não suportada.")


def calcular(comando, falar_func):
    """Resolve uma expressão matemática simples e usa a função 'falar' para dar o resultado."""
    comando = comando.replace("mais", "+").replace("menos", "-").replace("vezes", "*").replace("dividido por", "/")
    match = re.search(r'(\d[\s\d\.\+\-\*\/]+)', comando)
    if not match:
        falar_func("Não encontrei uma expressão matemática clara no seu comando.")
        return

    try:
        expressao = match.group(0).strip()
        if len(expressao) > 128:
            raise ValueError("Expressão longa demais.")
        resultado = avaliar_expressao(ast.parse(expressao, mode="eval").body)
    except (ArithmeticError, SyntaxError, ValueError):
        falar_func("Desculpe, não consegui calcular isso.")
        return
    falar_func(f"O resultado é {resultado}")
