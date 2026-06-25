"""
Classe TextReader - TextoMúsica

Responsabilidade única: carregar o texto e fornecer um caractere por vez
ao Interpreter.

Usar um gerador Python (yield) garante consumo sob demanda.
Se o texto vier de um arquivo no futuro, somente esta classe muda.
"""


class TextReader:
    """
    Encapsula a leitura do texto de entrada.
    
    Atributos:
        raw_text (str): Texto carregado via load()
    """
    
    def __init__(self):
        """Inicializa o TextReader."""
        self.raw_text = ""
    
    def load(self, text):
        """
        Armazena o texto recebido da interface gráfica ou servidor.

        Args:
            text (str): Texto a processar
        """
        self.raw_text = text

    def load_from_file(self, path):
        """
        Lê um arquivo .txt e armazena o conteúdo como raw_text.

        Args:
            path (str): Caminho para o arquivo de texto
        """
        with open(path, 'r', encoding='utf-8') as f:
            self.raw_text = f.read()

    def characters(self):
        """
        Gerador que faz yield de um token por vez.

        Tokens especiais emitidos:
        - 'NL'     → newline (\\n)
        - 'Mb'     → dígrafo Mi Bemol (M seguido de b)
        - '[n]'    → atraso de n batidas (ex: '[3]' para 3 batidas)

        Yields:
            str: Token individual
        """
        text = self.raw_text
        i = 0
        while i < len(text):
            char = text[i]

            if char == '\n':
                yield 'NL'
                i += 1

            elif char == 'M' and i + 1 < len(text) and text[i + 1] == 'b':
                # Dígrafo Mi Bemol
                yield 'Mb'
                i += 2

            elif char == '[':
                # Tenta ler token de atraso [n]
                j = i + 1
                digits = ''
                while j < len(text) and text[j].isdigit():
                    digits += text[j]
                    j += 1
                if digits and j < len(text) and text[j] == ']':
                    yield f'[{digits}]'
                    i = j + 1
                else:
                    yield char
                    i += 1

            else:
                yield char
                i += 1
