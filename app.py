import streamlit as st
import json
import os
import uuid
import pandas as pd

# Caminho do arquivo JSON
DB_FILE = "ingredientes_db.json"

# Função para carregar dados do arquivo JSON
def carregar_dados():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return []

# Função para salvar dados no arquivo JSON
def salvar_dados(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Função para adicionar ou atualizar um ingrediente
def adicionar_ou_atualizar_ingrediente(novo_item, id_edicao=None):
    data = carregar_dados()
    if id_edicao:
        data = [item if item['id'] != id_edicao else novo_item for item in data]
    else:
        novo_item['id'] = str(uuid.uuid4())
        data.append(novo_item)
    salvar_dados(data)

# Função para excluir um ingrediente
def excluir_ingrediente(id_exclusao):
    data = carregar_dados()
    data = [item for item in data if item['id'] != id_exclusao]
    salvar_dados(data)

# Título principal
st.set_page_config(layout="wide")
st.title("📦 Cadastro de Ingredientes")

# Menu lateral
menu = st.sidebar.selectbox("Menu", ["Cadastrar novo", "Lista completa"])

# Carregar dados existentes
dados = carregar_dados()

# Sugestões automáticas com base nos dados anteriores
uso_sugestoes = list(set(item['uso'] for item in dados))
categoria_sugestoes = list(set(item['categoria'] for item in dados))
produto_sugestoes = list(set(item['produto'] for item in dados))
marca_sugestoes = list(set(item['marca'] for item in dados))
nome_comercial_sugestoes = list(set(item['nome_comercial'] for item in dados))
subproduto_sugestoes = list(set(item['subproduto'] for item in dados))
unidade_sugestoes = list(set(item['unidade'] for item in dados))

# CADASTRO
if menu == "Cadastrar novo":
    st.subheader("Adicionar Ingrediente ao Estoque")
    with st.form("formulario"):
        uso = st.selectbox("Uso", ["Interno", "Venda"], index=0)
        categoria = st.selectbox("Categoria", ["Bebida", "Alimento", "Outros"], index=0)
        produto = st.text_input("Produto", value="", placeholder="Digite ou selecione").strip()
        marca = st.text_input("Marca", value="", placeholder="Digite ou selecione").strip()
        nome_comercial = st.text_input("Nome Comercial", value="").strip()
        subproduto = st.text_input("Subproduto", value="").strip()
        quantidade = st.number_input("Quantidade", min_value=0.0, step=0.01, format="%f")
        unidade = st.selectbox("Unidade", ["Kg", "g", "ml", "un"])
        valor_total = st.number_input("Valor Total (R$)", min_value=0.0, step=0.01, format="%f")

        submit = st.form_submit_button("Salvar")
        if submit:
            novo_item = {
                "id": str(uuid.uuid4()),
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
            adicionar_ou_atualizar_ingrediente(novo_item)
            st.success("Ingrediente salvo com sucesso!")
            st.experimental_rerun()

# LISTA COMPLETA
elif menu == "Lista completa":
    st.subheader("📋 Ingredientes Cadastrados")

    df = pd.DataFrame(dados)
    if not df.empty:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            filtro_uso = st.selectbox("Filtrar por Uso", ["Todos"] + sorted(df['uso'].unique().tolist()))
        with col2:
            filtro_categoria = st.selectbox("Filtrar por Categoria", ["Todos"] + sorted(df['categoria'].unique().tolist()))
        with col3:
            filtro_produto = st.selectbox("Filtrar por Produto", ["Todos"] + sorted(df['produto'].unique().tolist()))
        with col4:
            filtro_marca = st.selectbox("Filtrar por Marca", ["Todos"] + sorted(df['marca'].unique().tolist()))

        if filtro_uso != "Todos":
            df = df[df['uso'] == filtro_uso]
        if filtro_categoria != "Todos":
            df = df[df['categoria'] == filtro_categoria]
        if filtro_produto != "Todos":
            df = df[df['produto'] == filtro_produto]
        if filtro_marca != "Todos":
            df = df[df['marca'] == filtro_marca]

        df_exibicao = df.drop(columns=["id"])
        st.dataframe(df_exibicao, use_container_width=True)

        st.markdown("### Editar ou Excluir")
        for i, row in df.iterrows():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{row['produto']}** - {row['nome_comercial']} ({row['quantidade']} {row['unidade']})")
            with col2:
                editar = st.button("✏️ Editar", key=f"editar_{row['id']}")
                excluir = st.button("🗑️ Excluir", key=f"excluir_{row['id']}")
            if editar:
                st.session_state['editar_id'] = row['id']
                st.experimental_rerun()
            if excluir:
                excluir_ingrediente(row['id'])
                st.success("Item excluído com sucesso!")
                st.experimental_rerun()
    else:
        st.info("Nenhum ingrediente cadastrado.")

# MODO DE EDIÇÃO (APÓS CLICAR EM 'EDITAR')
if 'editar_id' in st.session_state:
    item = next((i for i in dados if i['id'] == st.session_state['editar_id']), None)
    if item:
        st.subheader("✏️ Editar Ingrediente")
        with st.form("form_edicao"):
            uso = st.selectbox("Uso", ["Interno", "Venda"], index=["Interno", "Venda"].index(item['uso']))
            categoria = st.selectbox("Categoria", ["Bebida", "Alimento", "Outros"], index=["Bebida", "Alimento", "Outros"].index(item['categoria']))
            produto = st.text_input("Produto", value=item['produto'])
            marca = st.text_input("Marca", value=item['marca'])
            nome_comercial = st.text_input("Nome Comercial", value=item['nome_comercial'])
            subproduto = st.text_input("Subproduto", value=item['subproduto'])
            quantidade = st.number_input("Quantidade", min_value=0.0, step=0.01, value=item['quantidade'], format="%f")
            unidade = st.selectbox("Unidade", ["Kg", "g", "ml", "un"], index=["Kg", "g", "ml", "un"].index(item['unidade']))
            valor_total = st.number_input("Valor Total (R$)", min_value=0.0, step=0.01, value=item['valor_total'], format="%f")
            submit = st.form_submit_button("Salvar alterações")
            if submit:
                novo_item = {
                    "id": item['id'],
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
                adicionar_ou_atualizar_ingrediente(novo_item, id_edicao=item['id'])
                del st.session_state['editar_id']
                st.success("Ingrediente atualizado com sucesso!")
                st.experimental_rerun()

