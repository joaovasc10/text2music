"""
GUIA DE USO - TextoMúsica

Este arquivo demonstra como usar o sistema TextoMúsica de forma programática,
além de via interface web.
"""

# ============================================================================
# EXEMPLO 1: Usar o sistema diretamente (sem servidor web)
# ============================================================================

def exemplo_uso_direto():
    """
    Demonstra como usar MusicSystem diretamente em um script Python.
    """
    from src.music_system import MusicSystem
    
    # Criar instância do sistema
    sistema = MusicSystem()
    
    # Configurar parâmetros
    sistema.configure(
        bpm=120,           # Batidas por minuto
        instrument=1,      # Piano (General MIDI #1)
        octave=4,          # Oitava base
        volume=64          # Volume (0-127)
    )
    
    # Texto a processar
    texto = "ABC"
    
    # Processar e tocar
    num_eventos = sistema.run(texto)
    print(f"Gerados {num_eventos} eventos musicais")
    
    # Aguardar fim da reprodução
    import time
    time.sleep(5)


# ============================================================================
# EXEMPLO 2: Usar o Interpreter diretamente
# ============================================================================

def exemplo_interpreter():
    """
    Demonstra como usar apenas o Interpreter para gerar eventos
    sem reproduzir áudio.
    """
    from src.interpreter import Interpreter
    
    # Criar interpretador
    interpreter = Interpreter()
    
    # Processar texto
    texto = "A B C"
    eventos = interpreter.interpret_text(texto)
    
    # Exibir eventos gerados
    print("Eventos gerados:")
    for i, evento in enumerate(eventos):
        print(f"  {i+1}. {evento}")


# ============================================================================
# EXEMPLO 3: Usar o CharacterMapper para entender as regras
# ============================================================================

def exemplo_character_mapper():
    """
    Demonstra como usar CharacterMapper para classificar caracteres.
    """
    from src.character_mapper import CharacterMapper
    
    mapper = CharacterMapper()
    
    caracteres = ['A', 'B', 'a', 'b', ' ', '!', '?', '1', '2']
    
    print("Classificação de caracteres:")
    for char in caracteres:
        print(f"\n  '{char}':")
        print(f"    É nota? {mapper.is_note(char)}")
        print(f"    É silêncio? {mapper.is_silence(char)}")
        print(f"    Dobra volume? {mapper.should_double_volume(char)}")
        print(f"    Sobe oitava? {mapper.should_raise_octave(char)}")
        print(f"    Muda instrumento? {mapper.get_instrument_change(char)}")
        print(f"    Dígito par? {mapper.get_even_digit_offset(char)}")
        print(f"    Dígito ímpar? {mapper.get_odd_digit_instrument(char)}")


# ============================================================================
# EXEMPLO 4: Entender o Context
# ============================================================================

def exemplo_context():
    """
    Demonstra como o Context mantém e atualiza o estado.
    """
    from src.context import Context
    from src.constants import DEFAULT_BPM, DEFAULT_VOLUME
    
    # Criar context
    context = Context()
    
    print("Estado inicial do Context:")
    print(f"  BPM: {context.get_bpm()}")
    print(f"  Volume: {context.get_volume()}")
    print(f"  Octava: {context.get_octave()}")
    print(f"  Instrumento: {context.get_instrument()}")
    print(f"  Última nota: {context.get_last_note()}")
    
    # Modificar
    context.set_bpm(140)
    context.set_volume(100)
    context.set_octave(5)
    context.set_last_note("La")
    
    print("\nEstado após modificações:")
    print(f"  BPM: {context.get_bpm()}")
    print(f"  Volume: {context.get_volume()}")
    print(f"  Octava: {context.get_octave()}")
    print(f"  Instrumento: {context.get_instrument()}")
    print(f"  Última nota: {context.get_last_note()}")
    
    # Calcular duração de nota
    duration_ms = context.note_duration_ms()
    print(f"\nDuração de nota em ms: {duration_ms}")
    
    # Reset
    context.reset()
    print("\nEstado após reset:")
    print(f"  BPM: {context.get_bpm()}")
    print(f"  Volume: {context.get_volume()}")


# ============================================================================
# EXEMPLO 5: Textos de teste interessantes
# ============================================================================

def exemplos_textos():
    """
    Alguns textos interessantes para testar o sistema.
    """
    
    textos_exemplo = {
        "Escala": "ABCDEFGH",
        
        "Com pausas": "A b C d E",
        
        "Com repetição": "JAK",
        
        "Com volume": "A AAA",
        
        "Com oitava": "A?A",
        
        "Com mudança de instrumento": "A!B!C",
        
        "Complexo": "ABC!DEF.GHA",
    }
    
    for nome, texto in textos_exemplo.items():
        print(f"{nome:25} -> {texto}")


# ============================================================================
# EXEMPLO 6: Testar regras de mapeamento
# ============================================================================

def teste_regras():
    """
    Testa todas as regras de mapeamento com textos simples.
    """
    from src.interpreter import Interpreter
    
    interpreter = Interpreter()
    
    regras = {
        "Nota Lá":           "A",
        "Nota Si":           "B",
        "Nota Dó":           "C",
        "Silêncio":          "a",
        "Dobrar volume":     " ",
        "Subir oitava":      "?",
        "Bandoneon":         "!",
        "Gaita de Foles":    "O",
        "Agogô":             ",",
        "Tubular Bells":     ";",
        "Dígito par":        "2",
        "Dígito ímpar":      "1",
    }
    
    print("Teste de regras de mapeamento:\n")
    
    for descricao, texto in regras.items():
        eventos = interpreter.interpret_text(texto)
        evento = eventos[0] if eventos else None
        print(f"{descricao:25} -> {evento}")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("GUIA DE USO - TextoMúsica")
    print("=" * 80)
    
    # Descomentar o exemplo que deseja executar
    
    print("\n1. EXEMPLOS DE TEXTOS:")
    print("-" * 80)
    exemplos_textos()
    
    print("\n\n2. TESTE DE REGRAS DE MAPEAMENTO:")
    print("-" * 80)
    teste_regras()
    
    print("\n\n3. EXEMPLO: USAR INTERPRETER:")
    print("-" * 80)
    exemplo_interpreter()
    
    print("\n\n4. EXEMPLO: USAR CHARACTER MAPPER:")
    print("-" * 80)
    exemplo_character_mapper()
    
    print("\n\n5. EXEMPLO: USAR CONTEXT:")
    print("-" * 80)
    exemplo_context()
    
    # Descomente para testar com reprodução de áudio
    # print("\n\n6. EXEMPLO: USO DIRETO COM REPRODUÇÃO:")
    # print("-" * 80)
    # exemplo_uso_direto()
    
    print("\n" + "=" * 80)
    print("Para usar via web, execute: python src/server.py")
    print("=" * 80)
