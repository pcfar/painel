# painel\_arquivo\_inteligente.py

import streamlit as st
import base64
from github import Github, UnknownObjectException
import re

# --- CONFIGURAÇÃO DA PÁGINA ---

st.set\_page\_config(page\_title="Central de Arquivo Tático", page\_icon="📚", layout="wide")

# --- CSS MODERNO E ESCURO PARA VISUALIZAÇÃO DOS DOSSIÊS ---

def apply\_enhanced\_styling():
st.markdown(""" <style>
.dossier-viewer {
font-family: 'Georgia', serif;
background-color: #1f2937;
padding: 2rem;
border-radius: 12px;
color: #f1f5f9;
box-shadow: 0 0 20px rgba(0,0,0,0.2);
line-height: 1.9;
}
.dossier-viewer h1, .dossier-viewer h2 {
color: #a5b4fc;
margin-top: 2rem;
border-bottom: 2px solid #6366f1;
padding-bottom: 0.3rem;
}
.dossier-viewer blockquote {
font-style: italic;
color: #93c5fd;
background: rgba(147, 197, 253, 0.1);
border-left: 4px solid #60a5fa;
padding: 1rem;
margin: 2rem 0;
border-radius: 6px;
}
.dossier-viewer ul li {
margin: 0.5rem 0;
padding-left: 1rem;
position: relative;
}
.dossier-viewer ul li::before {
content: "\027A4";
color: #38bdf8;
position: absolute;
left: 0;
} </style>
""", unsafe\_allow\_html=True)

# --- VERIFICAÇÃO DE SENHA ---

def check\_password():
if st.session\_state.get("password\_correct", False): return True
def password\_entered():
if st.session\_state.get("password") == st.secrets.get("APP\_PASSWORD"):
st.session\_state["password\_correct"] = True
del st.session\_state["password"]
else:
st.session\_state["password\_correct"] = False
st.text\_input("Senha", type="password", on\_change=password\_entered, key="password")
if "password\_correct" in st.session\_state and not st.session\_state["password\_correct"]:
st.error("Senha incorreta.")
return False

# --- FUNÇÕES GITHUB ---

@st.cache\_resource
def get\_github\_repo():
if not all(k in st.secrets for k in ["GITHUB\_TOKEN", "GITHUB\_USERNAME", "GITHUB\_REPO\_NAME"]):
st.error("Secrets GitHub incompletas.")
return None
try:
g = Github(st.secrets["GITHUB\_TOKEN"])
repo = g.get\_repo(f"{st.secrets['GITHUB\_USERNAME']}/{st.secrets['GITHUB\_REPO\_NAME']}")
return repo
except Exception as e:
st.error(f"Erro GitHub: {e}")
return None

# --- EXIBIÇÃO DO REPOSITÓRIO ---

def display\_repo\_contents(repo, path=""):
try:
contents = repo.get\_contents(path)
dirs = sorted([c for c in contents if c.type == 'dir'], key=lambda x: x.name)
files = sorted([c for c in contents if c.type == 'file'], key=lambda x: x.name)

```
    for content in dirs:
        with st.expander(f"📁 {content.name}"):
            display_repo_contents(repo, content.path)

    for content in files:
        if content.name.endswith(".md"):
            if st.button(f"📄 {content.name}", key=content.path, use_container_width=True):
                st.session_state.viewing_file_content = base64.b64decode(content.content).decode('utf-8')
                st.session_state.viewing_file_name = content.name
except Exception as e:
    st.error(f"Erro: {e}")
```

# --- APLICAÇÃO PRINCIPAL ---

if check\_password():
apply\_enhanced\_styling()
repo = get\_github\_repo()

```
st.title("📚 Central de Arquivo de Inteligência")
tab1, tab2, tab3 = st.tabs(["📤 Upload de Dossiês", "📚 Biblioteca de Dossiês", "🛠️ Geração (IA)"])

# --- UPLOAD ---
with tab1:
    st.header("📤 Envio de Novo Dossiê para o GitHub")
    with st.form("form_upload"):
        tipo = st.selectbox("Tipo de Dossiê", ["Dossiê de Liga", "Dossiê de Clube", "Briefing Pré-Jogo", "Relatório Pós-Jogo"])
        pais = st.text_input("País*")
        liga = st.text_input("Liga*")
        temporada = st.text_input("Temporada*")
        clube = st.text_input("Clube (se aplicável)")
        rodada = st.text_input("Rodada / Adversário (se aplicável)")
        conteudo_md = st.text_area("Conteúdo em Markdown", height=250)
        enviado = st.form_submit_button("Salvar no GitHub")

        if enviado:
            path_parts = [pais.replace(" ", "_"), liga.replace(" ", "_"), temporada]
            file_name = ""
            if tipo == "Dossiê de Liga":
                file_name = "Dossie_Liga.md"
            elif tipo == "Dossiê de Clube" and clube:
                path_parts.append(clube.replace(" ", "_"))
                file_name = "Dossie_Clube.md"
            elif tipo in ["Briefing Pré-Jogo", "Relatório Pós-Jogo"] and clube and rodada:
                path_parts.append(clube.replace(" ", "_"))
                path_parts.append(rodada.replace(" ", "_"))
                file_name = "Briefing_Pre.md" if tipo.startswith("Briefing") else "Relatorio_Pos.md"

            if file_name:
                full_path = "/".join(path_parts) + "/" + file_name
                try:
                    existing = repo.get_contents(full_path)
                    repo.update_file(full_path, "Atualiza dossiê", conteudo_md, existing.sha)
                    st.success("Dossiê atualizado com sucesso.")
                except UnknownObjectException:
                    repo.create_file(full_path, "Adiciona novo dossiê", conteudo_md)
                    st.success("Dossiê salvo com sucesso.")
                except Exception as e:
                    st.error(f"Erro: {e}")

# --- LEITURA ---
with tab2:
    st.header("📚 Biblioteca de Dossiês")
    if repo:
        col1, col2 = st.columns([1,2])
        with col1:
            display_repo_contents(repo)
        with col2:
            if "viewing_file_content" in st.session_state:
                st.markdown(f"#### {st.session_state.viewing_file_name}")
                cleaned = re.sub(r':contentReference\[.*?\]\{.*?\}', '', st.session_state.viewing_file_content)
                html = f"<div class='dossier-viewer'>{cleaned}</div>"
                st.markdown(html, unsafe_allow_html=True)
            else:
                st.info("Selecione um dossiê na árvore ao lado.")
    else:
        st.warning("GitHub não conectado.")

# --- GERAÇÃO (MANUTENÇÃO) ---
with tab3:
    st.info("Módulo reservado para futuras integrações de geração via IA.")
```
