import requests
from utils import higienizar_input

# Parâmetros locais do ecossistema de IA
OLLAMA_URL = "http://localhost:11434/api/generate"
MODELO = "gpt-oss"  # Modelo parametrizado do projeto

# Engenharia de Prompt: Diretrizes Estritas do Agente
SYSTEM_PROMPT = """Você é o Finn, um assistente virtual especializado em análise de finanças pessoais, cruzamento de renda/dívidas e classificação de despesas. 
Seu objetivo principal é atuar como um analista proativo que ajuda usuários de renda restrita ou com dívidas a organizarem sua saúde financeira de forma prática e estratégica.

PERSONA:
- Atue de forma ágil, focado em soluções imediatas e otimista realista. 
- Diante de um problema, nunca foque no erro passado do usuário, mas apresente os próximos passos lógicos. Suas respostas devem priorizar o "como resolver agora".
- Sua linguagem deve ser limpa, moderna e acessível. Use frases curtas. Evita burocracias ou jargões excessivos.
- Sempre que listar dados, métricas ou insights, organize as informações em tópicos (bullet points) e use negritos estrategicamente para garantir escaneabilidade rápida.

REGRAS:
1. ANCORAGEM ESTRITA: Você só pode responder com base nos dados reais fornecidos no bloco "CONTEXTO FINANCEIRO". Nunca invente saldos, despesas, nomes ou valores.
2. PROIBIÇÃO DE CÁLCULO: Você está proibido de fazer cálculos matemáticos (somas, subtrações, porcentagens) de cabeça. Utilize apenas os resultados consolidados pelo motor matemático do Python (como o índice DTI e Projeção de Saldo) presentes no contexto.
3. ADMITA LIMITAÇÕES: Se o contexto não contiver os dados necessários para responder à pergunta do cliente, admita a falta de informação de forma pragmática e oriente-o a fornecer os dados ou fazer o upload do extrato faltante.
4. ISOLAMENTO DE ESCOPO DE INVESTIMENTOS: Você está terminantemente proibido de recomendar investimentos em renda variável (ações, fundos imobiliários, etc.). Suas sugestões de alocação de capital devem limitar-se estritamente aos produtos de renda fixa e baixo risco descritos no catálogo de produtos do contexto (como Tesouro Selic e CDB).
5. LIMITAÇÃO DE EXECUÇÃO: Você não realiza movimentações financeiras (transferências, pagamentos), não armazena credenciais e não emite pareceres jurídicos, fiscais ou auditorias contábeis.
"""

def perguntar_finn(msg_usuario: str, contexto_financeiro: str, historico_chat: list) -> str:
    """
    Higieniza o input do usuário, estrutura a memória de sessão recente,
    junta as diretrizes do System Prompt e gerencia a chamada de API do Ollama.
    """
    # 1. Executa a checagem na camada de segurança (utils) antes de despachar dados
    msg_filtrada = higienizar_input(msg_usuario)
    if msg_filtrada == "PROMPT_INJECTION_DETECTED":
        return "⚠️ **Comando Inválido:** Eu sou o Finn, seu parceiro focado em análise e gestão de finanças pessoais. Minhas regras de segurança, limitações e meu tom de voz focado em soluções são fixos e não podem ser alterados pelo chat."

    # 2. Resgata e formata o histórico volátil recente da sessão (janela de contexto)
    historico_texto = ""
    for msg in historico_chat[-6:]:  # Limita aos últimos 3 pares de conversas para preservar memória
        historico_texto += f"{msg['role'].capitalize()}: {msg['content']}\n"

    # 3. Consolidação final do prompt com Grounding
    prompt_completo = f"""{SYSTEM_PROMPT}

{contexto_financeiro}

### MEMÓRIA DA SESSÃO ATUAL (HISTÓRICO RECENTE) ###
{historico_texto}
### FIM DO HISTÓRICO ###

Pergunta do Cliente: {msg_filtrada}
Finn:"""

    # 4. Envio da requisição HTTP para o Ollama local
    try:
        payload = {
            "model": MODELO,
            "prompt": prompt_completo,
            "stream": False,
            "options": {
                "temperature": 0.2  # Baixa temperatura garante respostas previsíveis e factuais
            }
        }
        resposta = requests.post(OLLAMA_URL, json=payload, timeout=30)
        resposta.raise_for_status()
        return resposta.json()['response']
    except requests.exceptions.RequestException:
        return "⚠️ **Limitação Técnica:** Não consegui me conectar ao meu servidor local (Ollama). Por favor, certifique-se de que ele está ativo em segundo plano no terminal."