import streamlit as st
import os
from PIL import Image
import pytesseract

# --- Configuração da Página ---
st.set_page_config(
    page_title="Painel de Inteligência Tática",
    page_icon="🧠",
    layout="wide"
)

# --- Título do Painel ---
st.title("SISTEMA MULTIAGENTE DE INTELIGÊNCIA TÁTICA")
st.subheader("Plataforma de Análise de Padrões para Trading Esportivo")

# --- Caminho para a pasta de prints ---
PRINTS_DIR = "."


# --- Função para listar os prints disponíveis ---
def listar_prints():
    # Lista apenas arquivos de imagem no diretório atual
    arquivos_permitidos = ('.png', '.jpg', '.jpeg')
    return [f for f in os.listdir(PRINTS_DIR) if f.lower().endswith(arquivos_permitidos)]

# --- Interface Principal ---
st.header("1. Arquivos para Análise")

lista_de_prints = listar_prints()

if not lista_de_prints:
    st.warning(f"Nenhum 'print' para análise encontrado na pasta principal.")
    st.info("Faça o upload de uma imagem de estatísticas para a pasta principal no GitHub para começar.")
else:
    st.success(f"Encontrados {len(lista_de_prints)} prints para análise.")

    # Menu para selecionar o print
    print_selecionado = st.selectbox("Selecione o arquivo de dados para processar:", lista_de_prints)

    if print_selecionado:
        caminho_completo = os.path.join(PRINTS_DIR, print_selecionado)
        st.image(caminho_completo, caption=f"Imagem selecionada: {print_selecionado}")

        # Botão para iniciar a análise
        if st.button("Analisar Print e Gerar Dossiê"):
            with st.spinner("Análise de imagem em andamento... O OCR pode levar alguns segundos."):
                try:
                    # --- LÓGICA DE OCR ---
                    # Abrir a imagem com a biblioteca Pillow
                    imagem = Image.open(caminho_completo)

                    # Extrair o texto da imagem usando o Tesseract (em português)
                    texto_extraido = pytesseract.image_to_string(imagem, lang='por')

                    st.success("Texto extraído da imagem com sucesso!")

                    # Exibir o texto bruto extraído
                    st.header("2. Texto Bruto Extraído (OCR)")
                    st.text_area("Conteúdo lido da imagem:", texto_extraido, height=400)

                except Exception as e:
                    st.error("Ocorreu um erro durante a análise OCR.")
                    st.exception(e)

# --- Rodapé ---
st.markdown("---")
st.text("Painel em desenvolvimento. Versão 2.1 (OCR Ativado)")
