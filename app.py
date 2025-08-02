import streamlit as st
import json
import os
import uuid

CAMINHO_ARQUIVO = 'ingredientes_db.json'

def carregar_dados():
    if os.path.exists(CAMINHO_ARQUIVO):
        with open(CAMINHO_ARQUIVO, 'r') as f:
            return json.load(f)
    return []

def salvar_dados(dados):
    with open(CAMINHO_ARQUIVO, 'w') as f:
        json.dump(dados, f, indent=4)

def limpar_form():
    st.session_state.clear()

def adicionar_item():
    st.subheader("Cadastro de Ingrediente")
    with st.form("formulario"):
        uso = st.selectbox("Uso", ["Interno", "Venda"])
        categoria = st.selectbox("Categoria", ["Alimento", "Bebida", "Outro"])
        produto = st.text_input("Produto")
        subproduto = st.text_input("Subproduto")
        marca = st.text_input("Marca")
        nome_comercial = st.text_input("Nome Comercial")
        unidade = st.selectbox("Unidade", ["Kg", "g", "ml", "un"])
        quantidade = st.number_input("Quantidade", min_value=0.0 if unidade not in ["Kg", "un"] else 0, format="%d" if unidade in ["Kg", "un"] else "%.2f")
        valor_total = st.number_input("Valor Total (R$)", min_value=0.0, format="%.2f")

        enviado = st.form_submit_button("Salvar")
        if enviado:
            novo_item = {
                "id": str(uuid.uuid4()),
                "uso": uso,
                "categoria": categoria,
                "produto": produto,
                "subproduto": subproduto,
                "marca": marca,
                "nome_comercial": nome_comercial,
                "unidade": unidade,
                "quantidade": quantidade,
                "valor_total": valor_total
            }
            dados = carregar_dados()
            dados.append(novo_item)
            salvar_dados(dados)
            st.success("Ingrediente salvo com sucesso!")
            st.button("Clique aqui para cadastrar outro", on_click=limpar_form)

def listar_completa():
    st.subheader("Lista Completa de Ingredientes")
    dados = carregar_dados()

    if not dados:
        st.info("Nenhum ingrediente cadastrado ainda.")
        return

    # Filtros no topo
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        uso_filtro = st.selectbox("Filtrar por Uso", ["Todos"] + sorted(set(i["uso"] for i in dados)))
    with col2:
        categoria_filtro = st.selectbox("Filtrar por Categoria", ["Todos"] + sorted(set(i["categoria"] for i in dados)))
    with col3:
        produto_filtro = st.selectbox("Filtrar por Produto", ["Todos"] + sorted(set(i["produto"] for i in dados if i["produto"])))
    with col4:
        subproduto_filtro = st.selectbox("Filtrar por Subproduto", ["Todos"] + sorted(set(i["subproduto"] for i in dados if i["subproduto"])))
    with col5:
        marca_filtro = st.selectbox("Filtrar por Marca", ["Todos"] + sorted(set(i["marca"] for i in dados if i["marca"])))

    # Aplicar filtros
    dados_filtrados = [item for item in dados if
                       (uso_filtro == "Todos" or item["uso"] == uso_filtro) and
                       (categoria_filtro == "Todos" or item["categoria"] == categoria_filtro) and
                       (produto_filtro == "Todos" or item["produto"] == produto_filtro) and
                       (subproduto_filtro == "Todos" or item["subproduto"] == subproduto_filtro) and
                       (marca_filtro == "Todos" or item["marca"] == marca_filtro)]

    # Mostrar como tabela
    st.dataframe(dados_filtrados, use_container_width=True)

    # Ações: editar/excluir
    for item in dados_filtrados:
        with st.expander(f"{item['nome_comercial']} - {item['quantidade']} {item['unidade']}"):
            col1, col2 = st.columns(2)
            if col1.button("Editar", key=f"editar_{item['id']}"):
                editar_item(item['id'])
            if col2.button("Excluir", key=f"excluir_{item['id']}"):
                confirmar_exclusao(item)

def confirmar_exclusao(item):
    st.warning(f"Tem certeza que deseja excluir '{item['nome_comercial']}'?")
    if st.button("Confirmar Exclusão", key=f"conf_excluir_{item['id']}"):
        dados = carregar_dados()
        dados = [i for i in dados if i["id"] != item["id"]]
        salvar_dados(dados)
        st.success("Item excluído com sucesso!")

def editar_item(item_id):
    dados = carregar_dados()
    item = next((i for i in dados if i["id"] == item_id), None)
    if not item:
        st.error("Item não encontrado.")
        return

    st.subheader("Editar Ingrediente")
    with st.form("form_edit"):
        uso = st.selectbox("Uso", ["Interno", "Venda"], index=["Interno", "Venda"].index(item["uso"]))
        categoria = st.selectbox("Categoria", ["Alimento", "Bebida", "Outro"], index=["Alimento", "Bebida", "Outro"].index(item["categoria"]))
        produto = st.text_input("Produto", value=item["produto"])
        subproduto = st.text_input("Subproduto", value=item["subproduto"])
        marca = st.text_input("Marca", value=item["marca"])
        nome_comercial = st.text_input("Nome Comercial", value=item["nome_comercial"])
        unidade = st.selectbox("Unidade", ["Kg", "g", "ml", "un"], index=["Kg", "g", "ml", "un"].index(item["unidade"]))
        quantidade = st.number_input("Quantidade", min_value=0.0 if unidade not in ["Kg", "un"] else 0, value=item["quantidade"], format="%d" if unidade in ["Kg", "un"] else "%.2f")
        valor_total = st.number_input("Valor Total (R$)", min_value=0.0, value=item["valor_total"], format="%.2f")

        enviado = st.form_submit_button("Salvar Alterações")
        if enviado:
            item.update({
                "uso": uso,
                "categoria": categoria,
                "produto": produto,
                "subproduto": subproduto,
                "marca": marca,
                "nome_comercial": nome_comercial,
                "unidade": unidade,
                "quantidade": quantidade,
                "valor_total": valor_total
            })
            salvar_dados(dados)
            st.success("Item atualizado com sucesso!")

# Interface principal
st.set_page_config(layout="wide")
menu = st.sidebar.selectbox("Menu", ["Cadastro", "Lista Completa"])
if menu == "Cadastro":
    adicionar_item()
elif menu == "Lista Completa":
    listar_completa()