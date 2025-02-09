import streamlit as st
from dashboard import DashboardFIDC


st.set_page_config(page_title="Sistema de Relatórios", layout="wide")


st.title("📌 Bem-vindo ao Sistema de Relatórios")
st.write("Escolha uma das opções abaixo para navegar para a página desejada.")


col1, col2 = st.columns(2)

with col1:
    if st.button("📊 Acessar Dashboard FIDC"):
        st.session_state['page'] = "Dashboard"


if 'page' in st.session_state:
    if st.session_state['page'] == "Dashboard":
        DashboardFIDC().display()
