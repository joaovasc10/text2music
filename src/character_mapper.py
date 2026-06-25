"""
Classe CharacterMapper - TextoMúsica

Encapsula todas as regras de mapeamento de caracteres para ações musicais.

Não tem estado — apenas recebe um caractere e responde perguntas sobre ele
consultando Constants. Este isolamento intencional garante que quando o
professor alterar as regras, somente esta classe muda (princípio Aberto/Fechado).
"""

from constants import (
    NOTE_MAP,
    SILENCE_CHARS,
    INSTRUMENT_MAP,
)


class CharacterMapper:
    """
    Responsável por classificar um caractere e determinar qual ação
    musical deve ser executada.
    
    Todos os métodos são públicos e sem estado.
    Consulta Constants para obter regras e mapeamentos.
    """
    
    @staticmethod
    def is_note(char):
        """
        Retorna True se o caractere é uma das letras A-H maiúsculas (notas musicais).
        
        Args:
            char (str): Caractere a classificar
            
        Returns:
            bool: True se é nota
        """
        return char in NOTE_MAP
    
    @staticmethod
    def get_note(char):
        """
        Retorna o nome da nota (ex: 'La' para 'A') ou None se não for nota.
        
        Args:
            char (str): Caractere a verificar
            
        Returns:
            str | None: Nome da nota ou None
        """
        return NOTE_MAP.get(char)
    
    @staticmethod
    def is_silence(char):
        """
        Retorna True se o caractere é uma letra minúscula a-h (silêncio/pausa).
        
        Args:
            char (str): Caractere a classificar
            
        Returns:
            bool: True se é silêncio
        """
        return char in SILENCE_CHARS
    
    @staticmethod
    def is_repeat_condition(char):
        """
        Retorna True se o caractere é uma consoante não-nota ou caractere
        não mapeado — indica repetição ou silêncio.
        
        Exemplos: 'J', 'K', 'L', 'Z' (consoantes que não são notas),
                  '@', '#', etc. (caracteres não mapeados)
        
        Args:
            char (str): Caractere a classificar
            
        Returns:
            bool: True se deve repetir última nota ou fazer silêncio
        """
        # Se é nota ou silêncio, não é repetição
        if CharacterMapper.is_note(char) or CharacterMapper.is_silence(char):
            return False
        
        # Se é um caractere mapeado (instrumento), não é repetição
        if char in INSTRUMENT_MAP:
            return False
        
        # Se é espaço ou dígito, não é repetição (têm regras próprias)
        if char == ' ' or char.isdigit():
            return False
        
        # Se é '?' ou '.', não é repetição (sobe oitava)
        if char in ('?', '.'):
            return False

        # Fase 2: 'V', '>' e '<' têm regras próprias
        if char in ('V', '>', '<'):
            return False

        # Tudo mais é repetição ou silêncio
        return True
    
    @staticmethod
    def get_instrument_change(char):
        """
        Retorna o número MIDI do novo instrumento se o caractere exige troca,
        ou None.
        
        Caracteres que trigam mudança: '!', vogais, ';', ',', 'NL'
        
        Args:
            char (str): Caractere a verificar
            
        Returns:
            int | None: Número MIDI do instrumento ou None
        """
        return INSTRUMENT_MAP.get(char)
    
    @staticmethod
    def should_double_volume(char):
        """
        Retorna True se o caractere é espaço (dobra o volume).
        
        Args:
            char (str): Caractere a verificar
            
        Returns:
            bool: True se deve dobrar volume
        """
        return char == ' '
    
    @staticmethod
    def should_raise_octave(char):
        """
        Retorna True se o caractere é '?' ou '.' (sobe uma oitava).
        
        Args:
            char (str): Caractere a verificar
            
        Returns:
            bool: True se deve subir oitava
        """
        return char in ('?', '.')
    
    @staticmethod
    def get_even_digit_offset(char):
        """
        Se o caractere for um dígito par, retorna seu valor inteiro
        para somar ao instrumento atual. Caso contrário, retorna None.
        
        Dígitos pares: 0, 2, 4, 6, 8
        
        Args:
            char (str): Caractere a verificar
            
        Returns:
            int | None: Valor do dígito par ou None
        """
        if not char.isdigit():
            return None
        
        digit = int(char)
        if digit % 2 == 0:  # É par
            return digit
        
        return None
    
    @staticmethod
    def should_lower_octave(char):
        return char == 'V'

    @staticmethod
    def should_accelerate(char):
        return char == '>'

    @staticmethod
    def should_decelerate(char):
        return char == '<'

    @staticmethod
    def get_odd_digit_instrument(char):
        """
        Se o caractere for um dígito ímpar, retorna o instrumento
        Tubular Bells (15). Caso contrário, retorna None.
        
        Dígitos ímpares: 1, 3, 5, 7, 9
        
        Args:
            char (str): Caractere a verificar
            
        Returns:
            int | None: 15 (Tubular Bells) ou None
        """
        if not char.isdigit():
            return None
        
        digit = int(char)
        if digit % 2 == 1:  # É ímpar
            return 15  # Tubular Bells
        
        return None
