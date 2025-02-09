import streamlit as st

class BasePage:
    """Classe base para todas as páginas do Streamlit"""
    
    def __init__(self, title):
        self.title = title

    def display(self):
        """Método genérico para exibição da página"""
        st.title(self.title)
        st.write("Essa página ainda não foi implementada.")
