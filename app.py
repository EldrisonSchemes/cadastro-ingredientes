import streamlit as st
import pandas as pd
import json
import os

# Caminho para o banco de dados local
DB_PATH = "nexustech/estoque.json"

# Inicializa o banco de dados se não existir
if not os.path.exists(DB_PATH):
    with open(DB_PATH, "w") as f:
        json.dump([], f)

# Função para carregar dados
def carregar_dados():
    with open(DB_PATH, "r") as f:
        return json.load(f)

# Função para salvar dados
def salvar_dados(dados):
    with open(DB_PATH, "w") as f:
        json.dump(dados, f, indent=4)

# Gera ID único baseado nos campos principais
def gerar_id(produto):
    chave = f"{produto['Produto']}_{produto['Sub Produto']}_{produto['Marca']}_{produto['Nome Comercial']}"
    return chave.lower().replace(" ", "_")

# Interface do menu
menu = ["Cadastrar Produto", "Visualizar/Editar Produtos", "Adicionar Compra a Produto Existente", "Excluir Produto"]
opcao = st.sidebar.selectbox("Menu", menu)

# Página 1: Cadastro de Produto
if opcao == "Cadastrar Produto":
    st.header("Cadastro de Produto")

    uso = st.selectbox("Uso", ["Interno", "Venda"])
    categoria = st.selectbox("Categoria", ["Bebida", "Alimento", "Outros"])
    produto = st.text_input("Produto")
    sub_produto = st.text_input("Sub Produto")
    marca = st.text_input("Marca")
    nome_comercial = st.text_input("Nome Comercial")
    unidade = st.selectbox("Unidade", ["Kg", "g", "ml", "un"])

    inteiro = unidade in ["Kg", "un"]
    quantidade = st.number_input("Quantidade", min_value=0.0, format="%d" if inteiro else "%0.2f")

    valor = st.number_input("Valor (Total da compra)", min_value=0.0, format="%0.2f")

    if st.button("Salvar Produto"):
        dados = carregar_dados()
        novo = {
            "Uso": uso,
            "Categoria": categoria,
            "Produto": produto,
            "Sub Produto": sub_produto,
            "Marca": marca,
            "Nome Comercial": nome_comercial,
            "Unidade": unidade,
            "Quantidade": quantidade,
            "Valor Total": valor
        }
        novo["id"] = gerar_id(novo)
        dados.append(novo)
        salvar_dados(dados)
        st.success("Produto salvo com sucesso!")

# Página 2: Visualizar/Editar
elif opcao == "Visualizar/Editar Produtos":
    st.header("Produtos Cadastrados")
    dados = carregar_dados()
    df = pd.DataFrame(dados)

    if not df.empty:
        with st.expander("Filtros"):
            col1, col2 = st.columns(2)
            with col1:
                uso_filtro = st.multiselect("Uso", df["Uso"].unique())
                categoria_filtro = st.multiselect("Categoria", df["Categoria"].unique())
                produto_filtro = st.multiselect("Produto", df["Produto"].unique())
            with col2:
                subproduto_filtro = st.multiselect("Sub Produto", df["Sub Produto"].unique())
                marca_filtro = st.multiselect("Marca", df["Marca"].unique())

        if uso_filtro:
            df = df[df["Uso"].isin(uso_filtro)]
        if categoria_filtro:
            df = df[df["Categoria"].isin(categoria_filtro)]
        if produto_filtro:
            df = df[df["Produto"].isin(produto_filtro)]
        if subproduto_filtro:
            df = df[df["Sub Produto"].isin(subproduto_filtro)]
        if marca_filtro:
            df = df[df["Marca"].isin(marca_filtro)]

        st.dataframe(df.reset_index(drop=True))
    else:
        st.info("Nenhum produto cadastrado ainda.")

# Página 3: Adicionar Compra
elif opcao == "Adicionar Compra a Produto Existente":
    st.header("Adicionar Compra a Produto")
    dados = carregar_dados()
    produtos = [f"{d['Produto']} | {d['Sub Produto']} | {d['Marca']} | {d['Nome Comercial']}" for d in dados]

    if produtos:
        escolha = st.selectbox("Escolha o Produto", produtos)
        index = produtos.index(escolha)

        prod = dados[index]
        inteiro = prod['Unidade'] in ['Kg', 'un']
        qtd_nova = st.number_input("Quantidade comprada", min_value=0.0, format="%d" if inteiro else "%0.2f")
        valor_novo = st.number_input("Valor total da nova compra", min_value=0.0, format="%0.2f")

        if st.button("Adicionar"):
            qtd_antiga = float(prod['Quantidade'])
            valor_antigo = float(prod['Valor Total'])
            nova_qtd = qtd_antiga + qtd_nova
            novo_valor = valor_antigo + valor_novo

            prod['Quantidade'] = nova_qtd
            prod['Valor Total'] = novo_valor

            dados[index] = prod
            salvar_dados(dados)
            st.success("Compra adicionada com sucesso!")
    else:
        st.info("Nenhum produto disponível.")

# Página 4: Excluir Produto
elif opcao == "Excluir Produto":
    st.header("Excluir Produto")
    dados = carregar_dados()
    produtos = [f"{d['Produto']} | {d['Sub Produto']} | {d['Marca']} | {d['Nome Comercial']}" for d in dados]

    if produtos:
        escolha = st.selectbox("Escolha o Produto", produtos)
        index = produtos.index(escolha)

        if st.button("Confirmar Exclusão"):
            dados.pop(index)
            salvar_dados(dados)
            st.success("Produto excluído com sucesso!")
    else:
        st.info("Nenhum produto para excluir.")