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
    
    def characters(self):
        """
        Gerador que faz yield de um caractere por vez.
        
        Newline (\n) é entregue como 'NL' para facilitar o mapeamento
        em Constants.
        
        Yields:
            str: Caractere individual ou 'NL' para newline
        """
        for char in self.raw_text:
            if char == '\n':
                # Entregar newline como 'NL' para facilitar mapeamento
                yield 'NL'
            else:
                yield char
