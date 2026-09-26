import os
import json
import pandas as pd

# Define caminhos dinâmicos relativos para a pasta de dados local
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), "data")

def processar_motor_financeiro() -> str:
    """
    Consome os arquivos locais e executa a esteira matemática de dados.
    Retorna o bloco de contexto estruturado em Markdown com as citações e grounding.
    """
    # 1. Carregamento seguro dos arquivos locais (Base de Conhecimento Mockada)
    caminho_perfil = os.path.join(DATA_DIR, 'perfil_investidor.json')
    caminho_transacoes = os.path.join(DATA_DIR, 'transacoes.csv')
    caminho_historico = os.path.join(DATA_DIR, 'historico_atendimento.csv')
    caminho_produtos = os.path.join(DATA_DIR, 'produtos_financeiros.json')

    # Validação inicial de integridade do diretório
    if not (os.path.exists(caminho_perfil) and os.path.exists(caminho_transacoes)):
        raise FileNotFoundError("Arquivos essenciais de perfil ou transações ausentes na pasta /data.")

    perfil = json.load(open(caminho_perfil, encoding='utf-8'))
    transacoes = pd.read_csv(caminho_transacoes)
    historico = pd.read_csv(caminho_historico)
    produtos = json.load(open(caminho_produtos, encoding='utf-8'))
    
    # 2. Execução Determinística: Cálculo de Comprometimento de Renda (DTI)
    renda_liquida = perfil.get("renda_mensal_liquida", perfil.get("renda_mensal", 0.0))
    dividas = perfil.get("dividas_ativas", [])
    total_dividas_mes = sum(d["valor_mensal"] for d in dividas)
    
    dti = (total_dividas_mes / renda_liquida) * 100 if renda_liquida > 0 else 0.0
    
    # Definição técnica dos limites de risco (Métricas de Saúde do Agente)
    if dti > 50.0:
        status_risco = "Alto Risco de Inadimplência"
    elif dti >= 30.0:
        status_risco = "Alerta Limite"
    else:
        status_risco = "Saudável / Controlado"

    # 3. Execução Preditiva: Ritmo de Caixa (Burn Rate)
    # Filtra apenas saídas do mês que não estejam pré-vinculadas a parcelas fixas/contratos
    saidas_variaveis = transacoes[
        (transacoes['tipo'] == 'saida') & 
        (transacoes['id_vinculo'].isna() | (transacoes['id_vinculo'] == 'N/A'))
    ]
    total_variavel = saidas_variaveis['valor'].sum()
    
    # Projeção de balanço
    saldo_restante_estimado = renda_liquida - total_dividas_mes - total_variavel
    if saldo_restante_estimado < 0:
        projecao_caixa = f"Risco iminente de saldo negativo (Déficit estimado de -R$ {abs(saldo_restante_estimado):.2f}). Recomenda-se corte emergencial em gastos variáveis supérfluos."
    else:
        projecao_caixa = f"Conta em equilíbrio. Saldo remanescente previsto para o fim do mês: R$ {saldo_restante_estimado:.2f}."

    # 4. Formatação de Grounding (Montagem do Bloco de Contexto Estrito para a LLM)
    contexto_markdown = f"""
### CONTEXTO FINANCEIRO REAL DO CLIENTE (NÃO ALUCINE) ###
- Cliente Atual: {perfil['nome']} [2]
- Idade / Profissão: {perfil['idade']} anos, {perfil.get('profissao', 'Não Informada')} [2]
- Renda Mensal Líquida: R$ {renda_liquida:.2f} [2]
- Patrimônio Total: R$ {perfil['patrimonio_total']:.2f} (Reserva Atual: R$ {perfil['reserva_emergencia_atual']:.2f}) [2]

### ANÁLISE DE COMPROMETIMENTO DE RENDA (MOTOR MATEMÁTICO PYTHON) ###
- Total de Dívidas Fixas no Mês: R$ {total_dividas_mes:.2f} [2, 4]
"""
    for d in dividas:
        contexto_markdown += f"  * [{d.get('id_contrato', 'DIV-000')}] {d['tipo']}: R$ {d['valor_mensal']:.2f} (Vence dia {d.get('vencimento_dia', 'N/A')}) [2]\n"
        
    contexto_markdown += f"""- Índice de Comprometimento Atual (DTI): {dti:.1f}% -> Status de Risco: {status_risco}
- Projeção de Saldo para Fim do Mês: {projecao_caixa}

### HISTÓRICO RECENTE DE TRANSAÇÕES (MÊS ATUAL) ###
{transacoes.to_string(index=False)} [4]

### ATENDIMENTOS ANTERIORES E MEMÓRIA DE LONGO PRAZO ###
{historico.to_string(index=False)} [1]

### CATÁLOGO DE PRODUTOS PERMITIDOS PARA SUGESTÃO (RENDA FIXA) ###
{json.dumps(produtos, indent=2, ensure_ascii=False)} [3]
--------------------------------------------------------------------------------------------------------------------------------------
"""
    return contexto_markdown