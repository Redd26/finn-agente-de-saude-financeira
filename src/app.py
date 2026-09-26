import streamlit as st
from analisador import processar_motor_financeiro
from conexao import perguntar_finn

# ==============================================================================
# CONFIGURAÇÃO DE LAYOUT DA INTERFACE (STREAMLIT)
# ==============================================================================
st.set_page_config(
    page_title="Finn - Analista de Saúde Financeira", 
    page_icon="📊", 
    layout="centered"
)

st.title("📊 Finn — Analista Financeiro")
st.caption("Seu parceiro pragmático e proativo para controle de caixa e mitigação de endividamento.")

# ==============================================================================
# INICIALIZAÇÃO DE ESTADOS DA SESSÃO (CHAT HISTORY)
# ==============================================================================
# Inicializa a memória volátil de mensagens da sessão ativa, se estiver vazia
if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

# ==============================================================================
# EXECUÇÃO DO PIPELINE DE DADOS (MOTOR PYTHON DETERMINÍSTICO)
# ==============================================================================
# Roda a esteira de análise matemática em segundo plano a cada ciclo da interface
try:
    contexto_atualizado = processar_motor_financeiro()
except Exception as e:
    st.error(f"Erro crítico ao carregar ou processar os arquivos locais na pasta /data: {e}")
    st.stop()

# ==============================================================================
# RENDERIZAÇÃO DA INTERFACE DE CONVERSA
# ==============================================================================
# Exibe todas as caixas de diálogos salvas no histórico da sessão corrente na tela
for mensagem in st.session_state.mensagens:
    with st.chat_message(mensagem["role"]):
        st.write(mensagem["content"])

# Loop ativo de captura de mensagens do input do chat
if pergunta_cliente := st.chat_input("Pergunte sobre sua saúde financeira, metas ou dívidas..."):
    
    # 1. Exibe e anexa a entrada em texto do cliente na interface
    st.chat_message("user").write(pergunta_cliente)
    st.session_state.mensagens.append({"role": "user", "content": pergunta_cliente})
    
    # 2. Aciona o pipeline conversacional com animação visual de carregamento
    with st.spinner("Analisando dados de caixa..."):
        resposta_finn = perguntar_finn(
            msg_usuario=pergunta_cliente, 
            contexto_financeiro=contexto_atualizado, 
            historico_chat=st.session_state.mensagens[:-1]  # Passa o histórico sem a pergunta atual
        )
        
    # 3. Exibe e armazena a resposta final tratada do Finn
    st.chat_message("assistant").write(resposta_finn)
    st.session_state.mensagens.append({"role": "assistant", "content": resposta_finn})