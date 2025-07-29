```python
import streamlit as st
import os
from github import Github
from github.GithubException import UnknownObjectException
from PIL import Image
import pytesseract
import io

# --- Configuração da Página ---
st.set_page_config(page_title="Painel Tático", page_icon="🧠", layout="wide")

# --- SISTEMA DE SENHA ÚNICA ---
def check_password():
    if st.session_state.get("password_correct", False):
        return True

    def password_entered():
        if st.session_state.get("password") == st.secrets.get("APP_PASSWORD"):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    st.text_input("Password", type="password", on_change=password_entered, key="password")
    if "password_correct" in st.session_state and not st.session_state["password_correct"]:
        st.error("😕 Senha incorreta.")
    return False

# --- APLICAÇÃO PRINCIPAL ---
if check_password():
    st.title("SISTEMA DE INTELIGÊNCIA TÁTICA")
    st.subheader("Plataforma de Análise para Trading Esportivo")

    # --- Conexão com o GitHub ---
    @st.cache_resource
    def get_github_connection():
        try:
            g = Github(st.secrets["GITHUB_TOKEN"])
            repo = g.get_repo("pcfar/painel")
            return repo
        except Exception:
            st.error("Erro ao conectar com o GitHub. Verifique o GITHUB_TOKEN.")
            st.stop()
    repo = get_github_connection()

    # --- Funções Auxiliares ---
    @st.cache_data(ttl=300)
    def listar_conteudo_pasta(caminho):
        try:
            return [item for item in repo.get_contents(caminho) if not item.name.startswith('.')]
        except UnknownObjectException:
            return []
    
    # --- CENTRAL DE UPLOAD ---
    st.header("1. Central de Upload e Organização")
    with st.expander("Clique aqui para enviar novos 'prints' para análise"):
        with st.form("form_upload_dossie", clear_on_submit=True):
            st.write("Preencha os dados para enviar os 'prints' para a análise.")
            temporada = st.text_input("Temporada:", placeholder="Ex: 2025-2026")
            liga = st.text_input("Liga (código):", placeholder="Ex: HOL")
            clube = st.text_input("Clube (código ou 'GERAL'):", placeholder="Ex: FEY")
            rodada = st.text_input("Rodada (se aplicável):", placeholder="Ex: R01")
            arquivos = st.file_uploader("Upload dos 'prints':", accept_multiple_files=True, type=['png', 'jpg'])
            
            if st.form_submit_button("Enviar Arquivos para Análise"):
                if not all([temporada, liga, clube, arquivos]):
                    st.error("Preencha todos os campos obrigatórios e envie pelo menos um arquivo.")
                else:
                    with st.spinner("Enviando arquivos..."):
                        temporada_fmt = temporada.replace('/', '-')
                        caminho_base = f"{temporada_fmt}/{liga.upper()}/{clube.upper()}"
                        if rodada:
                            caminho_base = os.path.join(caminho_base, rodada.upper())
                        for arq in arquivos:
                            caminho_repo = os.path.join(caminho_base, arq.name)
                            repo.create_file(caminho_repo, f"Adiciona {arq.name}", arq.getvalue())
                            st.success(f"Arquivo `{arq.name}` salvo em `{caminho_repo}`!")
                        st.balloons()

    # --- CENTRAL DE ANÁLISE ---
    st.markdown("---")
    st.header("2. Central de Análise: Gerar Dossiês")
    
    temporadas = [item.path for item in listar_conteudo_pasta("") if item.type == "dir"]
    if not temporadas:
        st.info("Nenhum dado disponível para análise. Comece enviando arquivos pela Central de Upload.")
    else:
        sel_temporada = st.selectbox("Passo 1: Selecione a Temporada", [""] + temporadas)
        if sel_temporada:
            ligas = [item.name for item in listar_conteudo_pasta(sel_temporada) if item.type == "dir"]
            if ligas:
                sel_liga = st.selectbox("Passo 2: Selecione a Liga", [""] + ligas)
                if sel_liga:
                    path_liga = os.path.join(sel_temporada, sel_liga)
                    clubes = [item.name for item in listar_conteudo_pasta(path_liga) if item.type == "dir"]
                    if clubes:
                        sel_clube = st.selectbox("Passo 3: Selecione o Clube/Alvo", [""] + clubes)
                        if sel_clube:
                            path_clube = os.path.join(path_liga, sel_clube)
                            st.success(f"Seleção: **{path_clube}**")
                            if st.button(f"Analisar e Gerar Dossiê para {sel_clube}"):
                                with st.spinner(f"Analisando..."):
                                    imagens = [f for f in listar_conteudo_pasta(path_clube) if f.name.lower().endswith(('.png', '.jpg'))]
                                    if not imagens:
                                        st.warning("Nenhuma imagem encontrada para análise nesta seleção.")
                                    else:
                                        # Lógica de OCR e Geração de Dossiê
                                        st.info(f"Simulação: Análise de {len(imagens)} imagens concluída.")
```
