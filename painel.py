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
try:
    g = Github(st.secrets["GITHUB_TOKEN"])
    repo = g.get_repo("pcfar/painel")
except Exception as e:
    st.error("Erro ao conectar com o GitHub. Verifique o GITHUB_TOKEN nos seus Segredos (Secrets).")
    st.stop()


# --- ABA 1: CENTRAL DE UPLOAD ---
st.header("1. Central de Upload e Organização")
with st.expander("Clique aqui para enviar novos 'prints' para análise"):
    with st.form("form_upload_dossie", clear_on_submit=True):
        st.write("Preencha os dados abaixo para enviar os 'prints' para a análise correta.")

        temporada = st.text_input("Temporada:", placeholder="Ex: 2025 ou 2025-2026")
        tipo_dossie = st.selectbox("Selecione o Tipo de Dossiê:", ["Dossiê 1: Análise Geral da Liga", "Dossiê 2: Análise Aprofundada do Clube", "Dossiê 3: Briefing Pré-Jogo (Rodada)", "Dossiê 4: Análise Pós-Jogo (Rodada)"])
        liga_analisada = st.text_input("Liga ou País (código de 3 letras):", placeholder="Ex: HOL, ING, BRA")
        clube_analisado = st.text_input("Clube (código de 3 letras ou 'GERAL'):", placeholder="Ex: FEY, AJA, ou GERAL")
        rodada_dossie = st.text_input("Rodada (se aplicável):", placeholder="Ex: R01, R02...")
        arquivos_enviados = st.file_uploader("Upload dos 'prints':", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])
        submitted = st.form_submit_button("Enviar Arquivos para Análise")

        if submitted:
            if not all([temporada, liga_analisada, clube_analisado, arquivos_enviados]):
                st.error("Por favor, preencha Temporada, Liga, Clube e envie pelo menos um arquivo.")
            else:
                try:
                    with st.spinner(f"Processando {len(arquivos_enviados)} arquivo(s)..."):
                        # Padroniza a temporada com hífen se contiver barra
                        temporada_formatada = temporada.replace('/', '-')
                        caminho_base = f"{temporada_formatada}/{liga_analisada.upper()}/{clube_analisado.upper()}"
                        if "Rodada" in tipo_dossie and rodada_dossie:
                            caminho_base = os.path.join(caminho_base, rodada_dossie.upper())

                    for arquivo in arquivos_enviados:
                        conteudo_arquivo = arquivo.getvalue()
                        caminho_no_repo = os.path.join(caminho_base, arquivo.name)
                        commit_message = f"Adiciona print {arquivo.name} para o dossiê {tipo_dossie}"
                        repo.create_file(caminho_no_repo, commit_message, conteudo_arquivo)
                        st.success(f"Arquivo `{arquivo.name}` enviado com sucesso para `{caminho_no_repo}`!")
                    st.balloons()
                except Exception as e:
                    st.error("Ocorreu um erro durante o upload para o GitHub.")
                    st.exception(e)

# --- ABA 2: CENTRAL DE ANÁLISE ---
st.markdown("---")
st.header("2. Central de Análise: Gerar Dossiês")

try:
    with st.spinner("Buscando dados no repositório..."):
        conteudo_repo = repo.get_contents("")
        # Filtra apenas por diretórios (pastas) que não começam com '.'
        temporadas = [item.path for item in conteudo_repo if item.type == "dir" and not item.path.startswith('.')]

    if not temporadas:
        st.info("Nenhum dossiê pronto para análise. Comece enviando arquivos pela Central de Upload.")
    else:
        st.write("Selecione os dados que deseja processar:")

        # Filtros de navegação
        temporada_selecionada = st.selectbox("Selecione a Temporada:", temporadas)

        # (Futuramente, adicionaremos mais filtros para Liga, Clube, etc.)

        st.write(f"Analisando a temporada: **{temporada_selecionada}**")

        # (Lógica de análise e botão para gerar dossiê entrarão aqui)
        st.success("Pronto para análise!")


except Exception as e:
    st.error("Não foi possível listar os dossiês do repositório.")
    st.exception(e)


# --- Rodapé ---
st.markdown("---")
st.text("Painel em desenvolvimento. Versão 5.0 (Central de Análise Ativa)")
