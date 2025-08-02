import streamlit as st
import pandas as pd
import json
import os

# Caminho do arquivo JSON onde os dados serão salvos
DB_PATH = "ingredientes_db.json"

# Função para carregar dados do JSON
def carregar_dados():
    if os.path.exists(DB_PATH):
        with open(DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return []

# Função para salvar dados no JSON
def salvar_dados(dados):
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

# Interface para adicionar ingredientes
def cadastrar_ingrediente():
    st.subheader("Adicionar Ingrediente")

    uso = st.selectbox("Uso", ["Interno", "Venda"])
    categoria = st.selectbox("Categoria", ["Bebida", "Alimento", "Outros"])
    produto = st.text_input("Produto")
    subproduto = st.text_input("Sub Produto")
    marca = st.text_input("Marca")
    nome_comercial = st.text_input("Nome Comercial")
    unidade = st.selectbox("Unidade", ["Kg", "g", "ml", "un"])
    
    # Quantidade conforme unidade
    if unidade in ["Kg", "un"]:
        quantidade = st.number_input("Quantidade", min_value=0, step=1, format="%d")
    else:
        quantidade = st.number_input("Quantidade", min_value=0.0, step=0.1, format="%.2f")
    
    valor = st.number_input("Valor Total (não por unidade)", min_value=0.0, format="%.2f")

    if st.button("Salvar"):
        novo = {
            "uso": uso,
            "categoria": categoria,
            "produto": produto,
            "subproduto": subproduto,
            "marca": marca,
            "nome_comercial": nome_comercial,
            "unidade": unidade,
            "quantidade": quantidade,
            "valor_total": valor,
        }
        dados = carregar_dados()
        dados.append(novo)
        salvar_dados(dados)
        st.success("Ingrediente salvo com sucesso!")

# Interface para visualizar e editar ingredientes
def visualizar_ingredientes():
    st.subheader("Visualizar Ingredientes")

    dados = carregar_dados()
    if not dados:
        st.info("Nenhum ingrediente cadastrado.")
        return

    df = pd.DataFrame(dados)

    with st.expander("🔍 Filtros"):
        col1, col2, col3 = st.columns(3)
        uso_filtro = col1.multiselect("Uso", options=df["uso"].unique())
        categoria_filtro = col2.multiselect("Categoria", options=df["categoria"].unique())
        produto_filtro = col3.multiselect("Produto", options=df["produto"].unique())
        subproduto_filtro = st.multiselect("Sub Produto", options=df["subproduto"].unique())
        marca_filtro = st.multiselect("Marca", options=df["marca"].unique())

        if uso_filtro:
            df = df[df["uso"].isin(uso_filtro)]
        if categoria_filtro:
            df = df[df["categoria"].isin(categoria_filtro)]
        if produto_filtro:
            df = df[df["produto"].isin(produto_filtro)]
        if subproduto_filtro:
            df = df[df["subproduto"].isin(subproduto_filtro)]
        if marca_filtro:
            df = df[df["marca"].isin(marca_filtro)]

    st.dataframe(df, use_container_width=True)

# Layout principal
def main():
    st.set_page_config(page_title="Cadastro de Ingredientes", layout="wide")
    st.title("📦 Cadastro de Ingredientes")

    menu = ["Cadastrar Ingrediente", "Visualizar Ingredientes"]
    escolha = st.sidebar.radio("Menu", menu)

    if escolha == "Cadastrar Ingrediente":
        cadastrar_ingrediente()
    elif escolha == "Visualizar Ingredientes":
        visualizar_ingredientes()

if __name__ == "__main__":
    main()