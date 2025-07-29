import streamlit as st
import os
from github import Github
from github.GithubException import UnknownObjectException
from PIL import Image
import pytesseract
import io

# --- Configuração da Página ---
st.set_page_config(page_title="Painel de Inteligência Tática", page_icon="🧠", layout="wide")

# --- Título do Painel ---
st.title("SISTEMA MULTIAGENTE DE INTELIGÊNCIA TÁTICA")
st.subheader("Plataforma de Análise de Padrões para Trading Esportivo")

# --- Autenticação no GitHub ---
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
@st.cache_data(ttl=60)
def listar_conteudo_pasta(caminho):
    try:
        return repo.get_contents(caminho)
    except UnknownObjectException:
        return []
    except Exception as e:
        st.error(f"Erro ao listar conteúdo da pasta '{caminho}'.")
        return []

# --- CENTRAL DE UPLOAD ---
st.header("1. Central de Upload e Organização")
with st.expander("Clique aqui para enviar novos 'prints' para análise"):
    with st.form("form_upload_dossie", clear_on_submit=True):
        # ... (código do formulário de upload) ...
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
                with st.spinner(f"Processando {len(arquivos_enviados)} arquivo(s)..."):
                    temporada_formatada = temporada.replace('/', '-')
                    caminho_base = f"{temporada_formatada}/{liga_analisada.upper()}/{clube_analisado.upper()}"
                    if "Rodada" in tipo_dossie and rodada_dossie:
                        caminho_base = os.path.join(caminho_base, rodada_dossie.upper())
                    for arquivo in arquivos_enviados:
                        repo.create_file(os.path.join(caminho_base, arquivo.name), f"Adiciona {arquivo.name}", arquivo.getvalue())
                        st.success(f"Arquivo `{arquivo.name}` enviado com sucesso para `{caminho_base}`!")
                    st.balloons()

# --- CENTRAL DE ANÁLISE ---
st.markdown("---")
st.header("2. Central de Análise: Gerar Dossiês")

# Nível 1: Seleção da Temporada
conteudo_repo = listar_conteudo_pasta("")
nomes_temporadas = [item.path for item in conteudo_repo if item.type == "dir" and not item.path.startswith('.')]
if not nomes_temporadas:
    st.info("Nenhum dossiê pronto para análise. Comece enviando arquivos pela Central de Upload.")
else:
    temporada_selecionada = st.selectbox("Passo 1: Selecione a Temporada", [""] + nomes_temporadas)
    if temporada_selecionada:
        # Nível 2: Seleção da Liga
        conteudo_liga = listar_conteudo_pasta(temporada_selecionada)
        nomes_ligas = [item.name for item in conteudo_liga if item.type == "dir"]
        if nomes_ligas:
            liga_selecionada = st.selectbox("Passo 2: Selecione a Liga", [""] + nomes_ligas)
            if liga_selecionada:
                # Nível 3: Seleção do Clube/Alvo
                caminho_liga = os.path.join(temporada_selecionada, liga_selecionada)
                conteudo_clube = listar_conteudo_pasta(caminho_liga)
                nomes_clubes = [item.name for item in conteudo_clube if item.type == "dir"]
                if nomes_clubes:
                    clube_selecionado = st.selectbox("Passo 3: Selecione o Clube ou Análise 'GERAL'", [""] + nomes_clubes)
                    if clube_selecionado:
                        caminho_final = os.path.join(caminho_liga, clube_selecionado)
                        st.success(f"Você selecionou a análise para: **{caminho_final}**")

                        # Botão para iniciar a análise final
                        if st.button(f"Analisar e Gerar Dossiê para {clube_selecionado}"):
                            with st.spinner(f"Analisando arquivos em '{caminho_final}'..."):
                                try:
                                    texto_completo_dossie = ""
                                    arquivos_no_dossie = listar_conteudo_pasta(caminho_final)
                                    imagens_para_analisar = [f for f in arquivos_no_dossie if f.name.lower().endswith(('.png', '.jpg', '.jpeg'))]

                                    if not imagens_para_analisar:
                                        st.warning("Nenhuma imagem encontrada nesta pasta para análise.")
                                    else:
                                        # Loop para ler cada imagem
                                        for i, imagem_obj in enumerate(imagens_para_analisar):
                                            st.write(f"Lendo imagem {i+1}/{len(imagens_para_analisar)}: `{imagem_obj.name}`")
                                            conteudo_imagem = imagem_obj.decoded_content
                                            imagem_pil = Image.open(io.BytesIO(conteudo_imagem))
                                            texto_extraido = pytesseract.image_to_string(imagem_pil, lang='por')
                                            texto_completo_dossie += f"\n\n--- CONTEÚDO DO ARQUIVO: {imagem_obj.name} ---\n\n{texto_extraido}"

                                        st.header("3. Dossiê Gerado (Dados Brutos)")
                                        st.text_area("Conteúdo extraído de todos os 'prints':", texto_completo_dossie, height=600)
                                        st.success("Análise OCR concluída com sucesso!")

                                except Exception as e:
                                    st.error("Ocorreu um erro fatal durante a análise OCR.")
                                    st.exception(e)

# --- Rodapé ---
st.markdown("---")
st.text("Painel em desenvolvimento. Versão 6.0 (MVP Funcional)")
