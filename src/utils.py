import re

def higienizar_input(texto: str) -> str:
    """
    Analisa a mensagem do usuário aplicando regras rígidas de segurança.
    Bloqueia ataques de Prompt Injection e mascara informações sensíveis (PII).
    """
    if not texto:
        return ""

    # 1. Bloqueio de injeções de prompt comuns (burlar regras/alterar persona)
    padroes_burlar = [
        r"esqueça.*regras", 
        r"ignore.*instruções", 
        r"nova.*personalidade", 
        r"substitua.*diretrizes", 
        r"act as", 
        r"você agora trabalha",
        r"mude.*diretrizes"
    ]
    
    for padrao in padroes_burlar:
        if re.search(padrao, texto, re.IGNORECASE):
            return "PROMPT_INJECTION_DETECTED"
            
    # 2. Mascaramento automático de dados sensíveis (PII leakage)
    # Mascara CPFs digitados por engano no formato 000.000.000-00
    texto_limpo = re.sub(r'\d{3}\.\d{3}\.\d{3}-\d{2}', '[CPF_MASCARADO]', texto)
    
    # Mascara padrões textuais de vazamento de senhas
    texto_limpo = re.sub(r'senha:\s*\S+', 'senha: [PROTEGIDA]', texto_limpo, flags=re.IGNORECASE)
    
    return texto_limpo