import streamlit as st
import pandas as pd
import uuid
import json
import os

CAMINHO_ARQUIVO = 'ingredientes.json'

# ---------- Funções de manipulação de dados ----------

def carregar_dados():
    if os.path.exists(CAMINHO_ARQUIVO):
        with open(CAMINHO_ARQUIVO, 'r') as f:
            return json.load(f)
    return []

def salvar_dados(dados):
    with open(CAMINHO_ARQUIVO, 'w') as f:
        json.dump(dados, f, indent=4)

def gerar_id():
    dados = carregar_dados()
    if not dados:
        return 1
    return max(item['id'] for item in dados) + 1

def limpar_form():
    st.session_state.clear()

def adicionar_item():
    with st.form(key='form_adicionar'):
        uso = st.selectbox("Uso", ["Interno", "Venda"], help="Selecione o tipo de uso")
        categoria = st.selectbox("Categoria", ["Bebida", "Alimento", "Outros"], help="Escolha a categoria do item")

        # Sugestões com base em valores anteriores
        dados = carregar_dados()
        produtos = sorted(set(d['produto'] for d in dados))
        marcas = sorted(set(d['marca'] for d in dados))
        nomes = sorted(set(d['nome_comercial'] for d in dados))
        subprodutos = sorted(set(d['subproduto'] for d in dados))
        unidades = ["kg", "g", "ml", "un"]

        produto = st.selectbox("Produto", produtos + ["Outro"], index=len(produtos))
        if produto == "Outro":
            produto = st.text_input("Novo Produto")

        marca = st.selectbox("Marca", marcas + ["Outro"], index=len(marcas))
        if marca == "Outro":
            marca = st.text_input("Nova Marca")

        nome_comercial = st.selectbox("Nome Comercial", nomes + ["Outro"], index=len(nomes))
        if nome_comercial == "Outro":
            nome_comercial = st.text_input("Novo Nome Comercial")

        subproduto = st.selectbox("Subproduto", subprodutos + ["Outro"], index=len(subprodutos))
        if subproduto == "Outro":
            subproduto = st.text_input("Novo Subproduto")

        quantidade = st.number_input("Quantidade", min_value=0.0, format="%.2f")
        unidade = st.selectbox("Unidade", unidades)
        valor_total = st.number_input("Valor Total (R$)", min_value=0.0, format="%.2f")

        submit = st.form_submit_button("Salvar")
        if submit:
            novo_item = {
                "id": gerar_id(),
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
            salvar_dados(dados)
            st.success("Item cadastrado com sucesso!")
            st.experimental_rerun()

def excluir_item(id_excluir):
    dados = carregar_dados()
    dados = [d for d in dados if d['id'] != id_excluir]
    salvar_dados(dados)
    st.success("Item excluído com sucesso!")
    st.experimental_rerun()

def editar_item(id_item):
    dados = carregar_dados()
    item = next((d for d in dados if d['id'] == id_item), None)
    if item:
        st.subheader("Editar Item")
        with st.form(key=f"form_edicao_{id_item}"):
            uso = st.selectbox("Uso", ["Interno", "Venda"], index=["Interno", "Venda"].index(item['uso']))
            categoria = st.selectbox("Categoria", ["Bebida", "Alimento", "Outros"], index=["Bebida", "Alimento", "Outros"].index(item['categoria']))
            produto = st.text_input("Produto", value=item['produto'])
            marca = st.text_input("Marca", value=item['marca'])
            nome_comercial = st.text_input("Nome Comercial", value=item['nome_comercial'])
            subproduto = st.text_input("Subproduto", value=item['subproduto'])
            quantidade = st.number_input("Quantidade", min_value=0.0, value=item['quantidade'], format="%.2f")
            unidade = st.selectbox("Unidade", ["kg", "g", "ml", "un"], index=["kg", "g", "ml", "un"].index(item['unidade']))
            valor_total = st.number_input("Valor Total (R$)", min_value=0.0, value=item['valor_total'], format="%.2f")
            salvar = st.form_submit_button("Salvar Alterações")
            if salvar:
                item.update({
                    "uso": uso,
                    "categoria": categoria,
                    "produto": produto,
                    "marca": marca,
                    "nome_comercial": nome_comercial,
                    "subproduto": subproduto,
                    "quantidade": quantidade,
                    "unidade": unidade,
                    "valor_total": valor_total
                })
                salvar_dados(dados)
                st.success("Item atualizado com sucesso!")
                st.experimental_rerun()

# ---------- Menu lateral ----------

st.sidebar.title("Menu")
opcao = st.sidebar.radio("Escolha uma opção:", ["Cadastrar Ingrediente", "Lista Completa"])

if opcao == "Cadastrar Ingrediente":
    st.title("Cadastro de Ingredientes")
    adicionar_item()

elif opcao == "Lista Completa":
    st.title("Ingredientes Cadastrados")
    dados = carregar_dados()

    if dados:
        df = pd.DataFrame(dados)

        filtro_categoria = st.multiselect("Filtrar por Categoria", df['categoria'].unique())
        filtro_produto = st.multiselect("Filtrar por Produto", df['produto'].unique())
        filtro_uso = st.multiselect("Filtrar por Uso", df['uso'].unique())

        if filtro_categoria:
            df = df[df['categoria'].isin(filtro_categoria)]
        if filtro_produto:
            df = df[df['produto'].isin(filtro_produto)]
        if filtro_uso:
            df = df[df['uso'].isin(filtro_uso)]

        st.dataframe(df.drop(columns=['id']), use_container_width=True)

        for item in df.to_dict(orient='records'):
            with st.expander(f"{item['produto']} - {item['nome_comercial']}"):
                st.write(item)
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"Editar {item['id']}"):
                        editar_item(item['id'])
                with col2:
                    if st.button(f"Excluir {item['id']}"):
                        if st.confirm(f"Deseja realmente excluir {item['produto']} - {item['nome_comercial']}?"):
                            excluir_item(item['id'])
    else:
        st.warning("Nenhum ingrediente cadastrado.")

# ---------- Atualização automática no Streamlit Cloud ----------

if os.environ.get("STREAMLIT_BRANCH"):
    os.system("streamlit deploy")