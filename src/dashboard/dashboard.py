import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from base_page import BasePage

class DashboardFIDC(BasePage):
    """Classe que implementa o Dashboard do FIDC"""

    def __init__(self):
        super().__init__("📊 Dashboard Financeiro do FIDC")

    @staticmethod
    @st.cache_data
    def load_data(self, file_path):
        if os.path.exists(file_path):
            return pd.read_csv(file_path)
        else:
            return None  

    def display(self):
        """Método que exibe o dashboard"""
        super().display()

        file_path = "df_final.csv"
        df_final = self.load_data(file_path)

        if df_final is None: 
            uploaded_file = st.file_uploader("📂 Faça upload do arquivo CSV do FIDC", type=["csv"])
            if uploaded_file:
                df_final = pd.read_csv(uploaded_file, encoding="utf-8")
        else:
            st.info("🔄 Arquivo carregado automaticamente!")

        if df_final is not None:
            df_final['Valor de Vencimento Atualizado'] = df_final['Valor de Vencimento Atualizado'].astype('float32')
            df_final['Dias Corridos Vencidos'] = df_final['Dias Corridos Vencidos'].astype('int32')
            df_final['TIR'] = df_final['TIR'].astype('float32')
            df_final['Valor de PDD'] = df_final['Valor de PDD'].astype('float32')
            df_final['Classificação do Sacado'] = df_final['Classificação do Sacado'].astype('category')
            df_final['CAPAG Ente'] = df_final['CAPAG Ente'].astype('category')

            df_final['CAPAG Ente'] = df_final['CAPAG Ente'].cat.add_categories("Não informado").fillna('Não informado')

            class_options = ["Total"] + list(df_final['Classificação do Sacado'].unique())
            class_filter = st.selectbox("🔎 Selecione a Classificação do Sacado", class_options)

            if class_filter == "Total":
                filtered_df = df_final.copy()
            else:
                filtered_df = df_final[df_final['Classificação do Sacado'] == class_filter]

            min_date = pd.to_datetime(df_final['Data de Vencimento']).min()
            max_date = pd.to_datetime(df_final['Data de Vencimento']).max()
            date_filter = st.date_input("📅 Selecione um intervalo de Data de Vencimento", [min_date, max_date])

            date_filter_start = pd.to_datetime(date_filter[0])
            date_filter_end = pd.to_datetime(date_filter[1])

            filtered_df = filtered_df[(pd.to_datetime(filtered_df['Data de Vencimento']) >= date_filter_start) & 
                                    (pd.to_datetime(filtered_df['Data de Vencimento']) <= date_filter_end)]

            col1, col2, col3 = st.columns(3)

            with col1:
                valor_total = filtered_df['Valor de Vencimento Atualizado'].sum()
                st.metric(label="💰 Total de Valor de Vencimento Atualizado", value=f"R$ {valor_total:,.2f}")

            with col2:
                tir_media = filtered_df['TIR'].mean()
                st.metric(label="📈 Média da TIR", value=f"{tir_media:.2%}")

            with col3:
                valor_pdd = filtered_df['Valor de PDD'].sum()
                st.metric(label="⚠️ Total de PDD", value=f"R$ {valor_pdd:,.2f}")

            st.subheader("📊 Análises Gráficas")

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("📊 Distribuição de Dias Corridos Vencidos")
                fig, ax = plt.subplots(figsize=(5, 3))
                sns.histplot(filtered_df['Dias Corridos Vencidos'], bins=30, kde=True, ax=ax)
                st.pyplot(fig)

            with col2:
                st.subheader("🏦 Classificação do Sacado")
                fig, ax = plt.subplots(figsize=(5, 3))
                filtered_df['Classificação do Sacado'].value_counts().plot(kind='bar', ax=ax, color='skyblue')
                ax.set_xlabel("Classificação")
                ax.set_ylabel("Quantidade")
                st.pyplot(fig)

            with col3:
                st.subheader("🏛️ Classificação CAPAG Ente")
                fig, ax = plt.subplots(figsize=(5, 3))
                capag_counts = filtered_df['CAPAG Ente'].value_counts(dropna=False)
                if capag_counts.sum() > 0:
                    unique_colors = plt.cm.get_cmap('tab10', len(capag_counts))
                    capag_counts.plot(kind='pie', autopct='%1.1f%%', ax=ax, startangle=90, colors=[unique_colors(i) for i in range(len(capag_counts))])
                    ax.set_ylabel("")
                    st.pyplot(fig)
                else:
                    st.write("🔹 Nenhum dado disponível para exibição no gráfico de pizza.")

            st.markdown("📌 *Dashboard gerado automaticamente com dados do FIDC*")
