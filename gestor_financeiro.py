

# Gestor Financeiro Pessoal - Versão Mobile (Streamlit)
# Autor: Adriell José
# Descrição: Aplicativo web/mobile para controle financeiro pessoal

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

ARQUIVO_DADOS = "financas.csv"

# =========================
# Inicialização
# =========================
if not os.path.exists(ARQUIVO_DADOS):
    df_init = pd.DataFrame(columns=[
        "data", "descricao", "categoria", "tipo", "valor", "conta", "cartao"
    ])
    df_init.to_csv(ARQUIVO_DADOS, index=False)


def carregar_dados():
    return pd.read_csv(ARQUIVO_DADOS, parse_dates=["data"])


def salvar_dados(df):
    df.to_csv(ARQUIVO_DADOS, index=False)


# =========================
# Interface Mobile
# =========================
st.set_page_config(page_title="Minhas Finanças", layout="centered")
st.title("📱 Controle Financeiro Pessoal")

menu = st.sidebar.selectbox(
    "Menu",
    ["Lançar Movimento", "Resumo Mensal", "Gráficos", "Cartão de Crédito"]
)

# =========================
# Lançamentos
# =========================
if menu == "Lançar Movimento":
    st.subheader("➕ Novo Lançamento")

    data = st.date_input("Data", datetime.today())
    descricao = st.text_input("Descrição")
    categoria = st.text_input("Categoria")
    tipo = st.selectbox("Tipo", ["Receita", "Despesa"])
    valor = st.number_input("Valor", min_value=0.0, step=10.0)
    conta = st.text_input("Conta", value="Principal")
    cartao = st.text_input("Cartão (opcional)")

    if st.button("Salvar"):
        df = carregar_dados()
        novo = {
            "data": pd.to_datetime(data),
            "descricao": descricao,
            "categoria": categoria,
            "tipo": tipo,
            "valor": valor,
            "conta": conta,
            "cartao": cartao
        }
        df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
        salvar_dados(df)
        st.success("Lançamento salvo com sucesso!")

# =========================
# Resumo Mensal
# =========================
elif menu == "Resumo Mensal":
    st.subheader("📅 Resumo do Mês")

    ano = st.number_input("Ano", value=datetime.today().year)
    mes = st.number_input("Mês", min_value=1, max_value=12, value=datetime.today().month)

    df = carregar_dados()
    df_mes = df[(df['data'].dt.year == ano) & (df['data'].dt.month == mes)]

    receitas = df_mes[df_mes['tipo'] == 'Receita']['valor'].sum()
    despesas = df_mes[df_mes['tipo'] == 'Despesa']['valor'].sum()
    saldo = receitas - despesas

    st.metric("💰 Receitas", f"R$ {receitas:.2f}")
    st.metric("💸 Despesas", f"R$ {despesas:.2f}")
    st.metric("📊 Saldo", f"R$ {saldo:.2f}")

    st.dataframe(df_mes)

# =========================
# Gráficos
# =========================
elif menu == "Gráficos":
    st.subheader("📈 Gráficos")
    df = carregar_dados()

    if df.empty:
        st.info("Sem dados para exibir")
    else:
        df['saldo'] = df.apply(lambda x: x['valor'] if x['tipo'] == 'Receita' else -x['valor'], axis=1)
        df = df.sort_values('data')
        df['saldo_acumulado'] = df['saldo'].cumsum()

        st.line_chart(df.set_index('data')['saldo_acumulado'])

        despesas = df[df['tipo'] == 'Despesa']
        if not despesas.empty:
            fig, ax = plt.subplots()
            despesas.groupby('categoria')['valor'].sum().plot(kind='pie', autopct='%1.1f%%', ax=ax)
            ax.set_ylabel("")
            st.pyplot(fig)

# =========================
# Cartão de Crédito
# =========================
elif menu == "Cartão de Crédito":
    st.subheader("💳 Cartões")
    cartao_nome = st.text_input("Nome do Cartão")

    if cartao_nome:
        df = carregar_dados()
        df_cartao = df[df['cartao'] == cartao_nome]
        total = df_cartao['valor'].sum()
        st.metric("Total gasto", f"R$ {total:.2f}")
        st.dataframe(df_cartao)
