import streamlit as st
import json
import os
import uuid
import pandas as pd

DB_FILE = "ingredientes_db.json"

# Função para carregar dados
def carregar_dados():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# Função para salvar dados
def salvar_dados(dados):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

# Inicializa dados
ingredientes = carregar_dados()

st.set_page_config(page_title="Cadastro de Ingredientes", layout="wide")

# Barra lateral (com "Buscar Ingredientes" removido)
menu = st.sidebar.radio("Menu", [
    "Cadastro",
    "Lista Completa",
    "Editar Ingrediente",
    "Excluir Ingrediente"
])

# Cadastro de ingredientes
if menu == "Cadastro":
    st.title("Cadastro de Ingredientes")

    with st.form("cadastro_ingrediente", clear_on_submit=True):
        uso = st.selectbox("Uso", ["Interno", "Venda"])
        categoria = st.selectbox("Categoria", ["Alimento", "Bebida", "Outros"])
        produto = st.text_input("Produto", placeholder="Ex: Vinho")
        subproduto = st.text_input("Subproduto", placeholder="Ex: Merlot")
        marca = st.text_input("Marca", placeholder="Ex: Miolo")
        nome_comercial = st.text_input("Nome Comercial", placeholder="Ex: Miolo Reserva 2020")
        unidade = st.selectbox("Unidade", ["Kg", "g", "ml", "un"])

        if unidade in ["Kg", "un"]:
            quantidade = st.number_input("Quantidade", min_value=0, step=1, format="%d")
        else:
            quantidade = st.number_input("Quantidade", min_value=0.0, step=0.01, format="%.2f")

        valor_total = st.number_input("Valor Total (R$)", min_value=0.0, step=0.01, format="%.2f")
        submit = st.form_submit_button("Salvar")

        if submit:
            novo_item = {
                "id": str(uuid.uuid4()),
                "uso": uso,
                "categoria": categoria,
                "produto": produto,
                "subproduto": subproduto,
                "marca": marca,
                "nome_comercial": nome_comercial,
                "quantidade": quantidade,
                "unidade": unidade,
                "valor_total": valor_total
            }

            ingredientes.append(novo_item)
            salvar_dados(ingredientes)
            st.success("Ingrediente salvo com sucesso!")
            st.stop()

# Lista completa com filtros e visualização estilo tabela
elif menu == "Lista Completa":
    st.title("Lista de Ingredientes")

    # Filtros
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        filtro_uso = st.selectbox("Uso", ["Todos"] + sorted(list(set(i["uso"] for i in ingredientes))))
    with col2:
        filtro_categoria = st.selectbox("Categoria", ["Todos"] + sorted(list(set(i["categoria"] for i in ingredientes))))
    with col3:
        filtro_produto = st.selectbox("Produto", ["Todos"] + sorted(list(set(i["produto"] for i in ingredientes))))
    with col4:
        filtro_subproduto = st.selectbox("Subproduto", ["Todos"] + sorted(list(set(i["subproduto"] for i in ingredientes if i["subproduto"] != ""))))
    with col5:
        filtro_marca = st.selectbox("Marca", ["Todos"] + sorted(list(set(i["marca"] for i in ingredientes if i["marca"] != ""))))

    busca = st.text_input("Buscar por nome comercial, produto ou marca:")

    # Aplicar filtros
    ingredientes_filtrados = ingredientes
    if filtro_uso != "Todos":
        ingredientes_filtrados = [i for i in ingredientes_filtrados if i["uso"] == filtro_uso]
    if filtro_categoria != "Todos":
        ingredientes_filtrados = [i for i in ingredientes_filtrados if i["categoria"] == filtro_categoria]
    if filtro_produto != "Todos":
        ingredientes_filtrados = [i for i in ingredientes_filtrados if i["produto"] == filtro_produto]
    if filtro_subproduto != "Todos":
        ingredientes_filtrados = [i for i in ingredientes_filtrados if i["subproduto"] == filtro_subproduto]
    if filtro_marca != "Todos":
        ingredientes_filtrados = [i for i in ingredientes_filtrados if i["marca"] == filtro_marca]
    if busca:
        ingredientes_filtrados = [
            i for i in ingredientes_filtrados
            if busca.lower() in i["nome_comercial"].lower()
            or busca.lower() in i["produto"].lower()
            or busca.lower() in i["marca"].lower()
        ]

# Mostrar resultados como tabela (estilo Excel)
if ingredientes_filtrados:
    df = pd.DataFrame(ingredientes_filtrados)
    df = df[["id", "nome_comercial", "uso", "categoria", "produto", "subproduto", "marca", "quantidade", "unidade", "valor_total"]]
    df = df.rename(columns={
        "id": "ID",
        "nome_comercial": "Nome Comercial",
        "uso": "Uso",
        "categoria": "Categoria",
        "produto": "Produto",
        "subproduto": "Subproduto",
        "marca": "Marca",
        "quantidade": "Quantidade",
        "unidade": "Unidade",
        "valor_total": "Valor Total (R$)"
    })
    df.reset_index(drop=True, inplace=True)  # <-- ESSA LINHA corrige o índice
    st.dataframe(df, use_container_width=True)
else:
    st.info("Nenhum ingrediente encontrado com os filtros selecionados.")