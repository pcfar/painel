import streamlit as st
import os

# --- Configuração da Página ---
st.set_page_config(
    page_title="Painel de Inteligência Tática",
    page_icon="🧠",
    layout="wide"
)

# --- Título do Painel ---
st.title("SISTEMA MULTIAGENTE DE INTELIGÊNCIA TÁTICA")
st.subheader("Plataforma de Análise de Padrões para Trading Esportivo")

# --- Caminho para a pasta de prints (pasta principal) ---
PRINTS_DIR = "."

# --- Função para listar os prints disponíveis ---
def listar_prints_nao_processados():
    # Esta função, no futuro, será mais inteligente,
    # mostrando apenas os prints que ainda não foram usados em nenhum dossiê.
    # Por enquanto, ela lista todos os prints.
    arquivos_permitidos = ('.png', '.jpg', '.jpeg')
    return [f for f in os.listdir(PRINTS_DIR) if f.lower().endswith(arquivos_permitidos)]

# --- Interface Principal ---

st.header("1. Central de Comando: Criar Novo Dossiê")

# --- Formulário para etiquetar e criar um dossiê ---
with st.form("form_criar_dossie"):
    st.write("Preencha os dados abaixo para iniciar uma nova análise.")

    # Menus para o usuário definir o contexto da análise
    tipo_dossie = st.selectbox(
        "Selecione o Tipo de Dossiê:",
        [
            "Dossiê 1: Análise Geral da Liga",
            "Dossiê 2: Análise Aprofundada do Clube",
            "Dossiê 3: Briefing Pré-Jogo (Rodada)",
            "Dossiê 4: Análise Pós-Jogo (Rodada)"
        ]
    )

    liga_analisada = st.text_input("Qual a Liga ou País?", placeholder="Ex: HOL, ING, BRA")

    clube_analisado = st.text_input("Qual o Clube? (Deixe 'GERAL' para análise da liga)", value="GERAL")

    # Menu de múltipla seleção para escolher os prints
    prints_disponiveis = listar_prints_nao_processados()

    prints_selecionados = st.multiselect(
        "Selecione os 'prints' para esta análise:",
        prints_disponiveis,
        help="Você pode selecionar vários arquivos."
    )

    # Botão de envio do formulário
    submitted = st.form_submit_button("Iniciar Análise e Criar Dossiê")

# --- Lógica após o envio do formulário ---
if submitted:
    if not liga_analisada or not clube_analisado or not prints_selecionados:
        st.error("Por favor, preencha todos os campos e selecione pelo menos um print para continuar.")
    else:
        st.success("Comando de análise recebido!")
        st.write("---")
        st.subheader("Resumo do Comando:")
        st.write(f"**Tipo de Dossiê:** {tipo_dossie}")
        st.write(f"**Liga:** {liga_analisada}")
        st.write(f"**Clube/Alvo:** {clube_analisado}")
        st.write(f"**Prints a serem analisados:**")
        for p in prints_selecionados:
            st.write(f"- `{p}`")

        with st.spinner("Análise dos prints selecionados em andamento... (Simulação)"):
            # Futuramente, a lógica de OCR e criação do dossiê será inserida aqui
            st.write("---")
            st.header("Dossiê Gerado (Exemplo)")
            st.info("A análise foi concluída e o dossiê abaixo foi gerado e salvo no sistema.")
            st.markdown(f"""
            ### Dossiê de Análise da Liga: {liga_analisada.upper()}
            - **Padrão Identificado:** Liga com alta tendência ofensiva.
            - **Clubes Dominantes (sugestão):** PSV, Feyenoord, Ajax.
            - **Dados extraídos de:** {len(prints_selecionados)} arquivos de imagem.
            """)


# --- Rodapé ---
st.markdown("---")
st.text("Painel em desenvolvimento. Versão 3.0 (Interface Interativa)")
