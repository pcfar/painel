import streamlit as st
import os
from github import Github
from github.GithubException import UnknownObjectException

# --- Configuração da Página ---
st.set_page_config(
    page_title="Painel de Inteligência Tática",
    page_icon="🧠",
    layout="wide"
)

# --- Título do Painel ---
st.title("SISTEMA MULTIAGENTE DE INTELIGÊNCIA TÁTICA")
st.subheader("Plataforma de Análise de Padrões para Trading Esportivo")

# --- Autenticação no GitHub ---
# Função para memoizar (cache) a conexão com o GitHub para melhor performance
@st.cache_resource
def get_github_connection():
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo("pcfar/painel")
        return repo
    except Exception as e:
        st.error("Erro ao conectar com o GitHub. Verifique o GITHUB_TOKEN nos seus Segredos (Secrets).")
        st.exception(e)
        st.stop()

repo = get_github_connection()

# --- Função para listar o conteúdo de um diretório no GitHub ---
# Usamos cache para evitar chamadas repetidas à API
@st.cache_data(ttl=60)
def listar_conteudo_pasta(caminho):
    try:
        conteudo = repo.get_contents(caminho)
        return [item for item in conteudo if item.type == "dir"]
    except UnknownObjectException:
        # A pasta pode não existir, o que é um estado válido
        return []
    except Exception as e:
        st.error(f"Erro ao listar conteúdo da pasta '{caminho}'.")
        st.exception(e)
        return []

# --- CENTRAL DE UPLOAD ---
st.header("1. Central de Upload e Organização")
with st.expander("Clique aqui para enviar novos 'prints' para análise"):
    with st.form("form_upload_dossie", clear_on_submit=True):
        st.write("Preencha os dados abaixo para enviar os 'prints' para a análise correta.")
        # ... (código do formulário de upload permanece o mesmo) ...
        temporada = st.text_input("Temporada:", placeholder="Ex: 2025 ou 2025-2026")
        tipo_dossie = st.selectbox("Selecione o Tipo de Dossiê:", ["Dossiê 1: Análise Geral da Liga", "Dossiê 2: Análise Aprofundada do Clube", "Dossiê 3: Briefing Pré-Jogo (Rodada)", "Dossiê 4: Análise Pós-Jogo (Rodada)"])
        liga_analisada = st.text_input("Liga ou País (código de 3 letras):", placeholder="Ex: HOL, ING, BRA")
        clube_analisado = st.text_input("Clube (código de 3 letras ou 'GERAL'):", placeholder="Ex: FEY, AJA, ou GERAL")
        rodada_dossie = st.text_input("Rodada (se aplicável):", placeholder="Ex: R01, R02...")
        arquivos_enviados = st.file_uploader("Upload dos 'prints':", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])
        submitted = st.form_submit_button("Enviar Arquivos para Análise")

        if submitted:
            # ... (lógica de upload permanece a mesma) ...
            if not all([temporada, liga_analisada, clube_analisado, arquivos_enviados]):
                st.error("Por favor, preencha Temporada, Liga, Clube e envie pelo menos um arquivo.")
            else:
                # ... (código de upload) ...
                pass # O código de upload está omitido aqui por brevidade, mas deve ser mantido

# --- CENTRAL DE ANÁLISE ---
st.markdown("---")
st.header("2. Central de Análise: Gerar Dossiês")

# Nível 1: Seleção da Temporada
temporadas = listar_conteudo_pasta("")
nomes_temporadas = [item.path for item in temporadas]

if not nomes_temporadas:
    st.info("Nenhum dossiê pronto para análise. Comece enviando arquivos pela Central de Upload.")
else:
    st.write("Selecione os dados que deseja processar:")
    temporada_selecionada = st.selectbox("Passo 1: Selecione a Temporada", nomes_temporadas)

    if temporada_selecionada:
        # Nível 2: Seleção da Liga
        ligas = listar_conteudo_pasta(temporada_selecionada)
        nomes_ligas = [item.name for item in ligas]

        if nomes_ligas:
            liga_selecionada = st.selectbox("Passo 2: Selecione a Liga", nomes_ligas)

            if liga_selecionada:
                # Nível 3: Seleção do Clube/Alvo
                caminho_liga = os.path.join(temporada_selecionada, liga_selecionada)
                clubes = listar_conteudo_pasta(caminho_liga)
                nomes_clubes = [item.name for item in clubes]

                if nomes_clubes:
                    clube_selecionado = st.selectbox("Passo 3: Selecione o Clube ou Análise 'GERAL'", nomes_clubes)

                    if clube_selecionado:
                        st.success(f"Você selecionou a análise para: **{temporada_selecionada} / {liga_selecionada} / {clube_selecionado}**")
                        # Botão para iniciar a análise final
                        if st.button(f"Gerar Dossiê para {clube_selecionado} ({liga_selecionada})"):
                            # A lógica final de OCR e geração do dossiê entrará aqui
                            st.write("Análise iniciada... (Simulação)")


# --- Rodapé ---
st.markdown("---")
st.text("Painel em desenvolvimento. Versão 5.1 (Navegação em Cascata)")
