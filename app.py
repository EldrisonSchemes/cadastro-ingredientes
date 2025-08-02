import streamlit as st
import json
import os
import pandas as pd

# Caminho do arquivo de dados
DATA_FILE = "ingredientes_db.json"

# Carrega os dados existentes ou cria lista vazia
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        dados = json.load(f)
else:
    dados = []

# Título e menu lateral
st.set_page_config(page_title="Cadastro de Ingredientes", layout="wide")
st.sidebar.title("Menu")
opcao = st.sidebar.radio("Ir para:", ["Cadastro de Ingredientes", "Lista Completa"])

# Função para salvar dados no arquivo JSON
def salvar_dados():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)

# Página de cadastro
if opcao == "Cadastro de Ingredientes":
    st.title("Cadastro de Ingredientes")

    with st.form(key="form_ingrediente"):
        uso = st.selectbox("Uso", ["Interno", "Venda"])
        categoria = st.selectbox("Categoria", ["Bebida", "Alimento", "Outros"])
        produto = st.text_input("Produto")
        marca = st.text_input("Marca")
        nome_comercial = st.text_input("Nome Comercial")
        subproduto = st.text_input("Subproduto")
        quantidade = st.number_input("Quantidade", min_value=0.0, format="%.2f")
        unidade = st.selectbox("Unidade", ["Kg", "g", "ml", "un"])
        valor_total = st.number_input("Valor Total (R$)", min_value=0.0, format="%.2f")

        if st.form_submit_button("Salvar"):
            novo_item = {
                "uso": uso,
                "categoria": categoria,
                "produto": produto,
                "marca": marca,
                "nome_comercial": nome_comercial,
                "subproduto": subproduto,
                "quantidade": quantidade,
                "unidade": unidade,
                "valor_total": valor_total
            }
            dados.append(novo_item)
            salvar_dados()
            st.success("Ingrediente salvo com sucesso!")
            st.stop()

# Página de lista completa
elif opcao == "Lista Completa":
    st.title("Lista Completa de Ingredientes")

    if dados:
        df = pd.DataFrame(dados)

        # Filtros
        col1, col2, col3 = st.columns(3)
        with col1:
            filtro_uso = st.selectbox("Filtrar por uso", ["Todos"] + sorted(df["uso"].unique().tolist()))
        with col2:
            filtro_categoria = st.selectbox("Filtrar por categoria", ["Todos"] + sorted(df["categoria"].unique().tolist()))
        with col3:
            filtro_nome = st.text_input("Buscar por nome comercial")

        # Aplicar filtros
        if filtro_uso != "Todos":
            df = df[df["uso"] == filtro_uso]
        if filtro_categoria != "Todos":
            df = df[df["categoria"] == filtro_categoria]
        if filtro_nome:
            df = df[df["nome_comercial"].str.contains(filtro_nome, case=False)]

        # Mostrar tabela estilo Excel
        st.dataframe(df.reset_index(drop=True), use_container_width=True)
    else:
        st.info("Nenhum ingrediente cadastrado ainda.")