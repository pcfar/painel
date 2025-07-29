import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# --- Configuração da Página ---
st.set_page_config(page_title="Painel de Inteligência Tática", page_icon="🧠", layout="wide")

# --- SISTEMA DE AUTENTICAÇÃO ---
# Carrega a configuração do novo arquivo config.yaml
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# Chamada da função de login
authenticator.login(location='main')

# --- LÓGICA DE ACESSO ---
if st.session_state.get("authentication_status"):
    # --- APLICAÇÃO PRINCIPAL (SÓ APARECE APÓS LOGIN) ---
    col1, col2 = st.columns([0.85, 0.15])
    with col2:
        authenticator.logout('Logout', key='unique_key')

    st.write(f'Bem-vindo, *{st.session_state["name"]}*!')
    st.title("SISTEMA MULTIAGENTE DE INTELIGÊNCIA TÁTICA")
    # (O resto do código da aplicação viria aqui...)

elif st.session_state.get("authentication_status") == False:
    st.error('Nome de utilizador/senha incorreto(a)')
elif st.session_state.get("authentication_status") == None:
    st.warning('Por favor, introduza o seu nome de utilizador e senha')
