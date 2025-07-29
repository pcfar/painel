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

# --- Interface Principal ---

st.header("1. Central de Upload e Organização")

# --- Formulário para enviar arquivos para um dossiê específico ---
with st.form("form_upload_dossie", clear_on_submit=True):
    st.write("Preencha os dados abaixo para enviar os 'prints' para a análise correta.")

    # --- NOVO: Inputs para criar a estrutura de pastas ---
    temporada = st.text_input("Temporada:", placeholder="Ex: 2025-2026")

    tipo_dossie = st.selectbox(
        "Selecione o Tipo de Dossiê:",
        [
            "Dossiê 1: Análise Geral da Liga",
            "Dossiê 2: Análise Aprofundada do Clube",
            "Dossiê 3: Briefing Pré-Jogo (Rodada)",
            "Dossiê 4: Análise Pós-Jogo (Rodada)"
        ],
        key="tipo_dossie"
    )

    liga_analisada = st.text_input("Liga ou País (código de 3 letras):", placeholder="Ex: HOL, ING, BRA")
    clube_analisado = st.text_input("Clube (código de 3 letras ou 'GERAL'):", placeholder="Ex: FEY, AJA, ou GERAL")
    rodada_dossie = st.text_input("Rodada (se aplicável):", placeholder="Ex: R01, R02...")

    # --- NOVO: Componente de Upload de Arquivos ---
    arquivos_enviados = st.file_uploader(
        "Upload dos 'prints':",
        accept_multiple_files=True,
        type=['png', 'jpg', 'jpeg']
    )

    # Botão de envio do formulário
    submitted = st.form_submit_button("Enviar Arquivos para Análise")

# --- Lógica de Upload para o GitHub ---
if submitted:
    if not all([temporada, liga_analisada, clube_analisado, arquivos_enviados]):
        st.error("Por favor, preencha Temporada, Liga, Clube e envie pelo menos um arquivo.")
    else:
        try:
            with st.spinner(f"Processando {len(arquivos_enviados)} arquivo(s)... Conectando ao GitHub..."):
                # Autenticação no GitHub usando o Token guardado no "cofre"
                g = Github(st.secrets["GITHUB_TOKEN"])
                repo = g.get_repo("pcfar/painel")

                # Monta o caminho da pasta
                caminho_base = f"{temporada}/{liga_analisada.upper()}/{clube_analisado.upper()}"
                if "Rodada" in tipo_dossie and rodada_dossie:
                    caminho_base = os.path.join(caminho_base, rodada_dossie.upper())

            for arquivo in arquivos_enviados:
                # Lê o conteúdo do arquivo enviado
                conteudo_arquivo = arquivo.getvalue()
                # Define o caminho completo do arquivo no repositório
                caminho_no_repo = os.path.join(caminho_base, arquivo.name)

                commit_message = f"Adiciona print {arquivo.name} para o dossiê {tipo_dossie}"

                # Tenta criar o arquivo no GitHub
                repo.create_file(caminho_no_repo, commit_message, conteudo_arquivo)
                st.success(f"Arquivo `{arquivo.name}` enviado com sucesso para `{caminho_no_repo}`!")

            st.balloons()
            st.header("Upload Concluído!")

        except Exception as e:
            st.error("Ocorreu um erro durante o upload para o GitHub.")
            st.exception(e)

# --- Rodapé ---
st.markdown("---")
st.text("Painel em desenvolvimento. Versão 4.0 (Central de Upload Ativa)")
