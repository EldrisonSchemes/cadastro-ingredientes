import streamlit as st
import json
import os
from datetime import datetime

# Caminho para o banco de dados
DB_PATH = "ingredientes_db.json"

# Inicializa banco de dados se não existir
if not os.path.exists(DB_PATH):
    with open(DB_PATH, "w") as f:
        json.dump([], f)

# Função para carregar dados
def carregar_dados():
    with open(DB_PATH, "r") as f:
        return json.load(f)

# Função para salvar dados
def salvar_dados(data):
    with open(DB_PATH, "w") as f:
        json.dump(data, f, indent=4)

# Carrega os dados existentes
dados = carregar_dados()

# Obter listas únicas para sugestões
def obter_opcoes(campo):
    return sorted(list(set(d[campo] for d in dados if campo in d and d[campo])))

# Menu principal
st.sidebar.title("Menu")
opcao = st.sidebar.radio("Escolha uma opção:", ["Cadastrar Ingrediente", "Visualizar Ingredientes", "Editar/Excluir Ingredientes"])

# Cadastro
if opcao == "Cadastrar Ingrediente":
    st.header("Cadastro de Ingrediente")

    with st.form("cadastro_form"):
        uso = st.selectbox("Uso", ["Interno", "Venda"])
        categoria = st.selectbox("Categoria", ["Bebida", "Alimento", "Outros"])
        produto = st.text_input("Produto", value="", placeholder="Ex: Vinho", autocomplete=True)
        subproduto = st.text_input("Subproduto", value="", placeholder="Ex: Tinto", autocomplete=True)
        marca = st.text_input("Marca", value="", placeholder="Ex: Miolo", autocomplete=True)
        nome_comercial = st.text_input("Nome Comercial", value="", placeholder="Ex: Reserva", autocomplete=True)
        quantidade = st.number_input("Quantidade", min_value=0.0, step=0.1)
        unidade = st.selectbox("Unidade", ["Kg", "g", "ml", "un"])
        valor_total = st.number_input("Valor Total (R$)", min_value=0.0, step=0.01)
        submitted = st.form_submit_button("Salvar")

        if submitted:
            novo = {
                "data": datetime.today().strftime("%Y-%m-%d %H:%M"),
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
            dados.append(novo)
            salvar_dados(dados)
            st.success("Ingrediente salvo com sucesso!")
            st.experimental_rerun()

# Visualização com filtros fixos
elif opcao == "Visualizar Ingredientes":
    st.header("Lista de Ingredientes")

    st.subheader("Filtros")
    filtro_categoria = st.multiselect("Categoria", options=obter_opcoes("categoria"))
    filtro_produto = st.multiselect("Produto", options=obter_opcoes("produto"))

    filtrados = dados
    if filtro_categoria:
        filtrados = [d for d in filtrados if d["categoria"] in filtro_categoria]
    if filtro_produto:
        filtrados = [d for d in filtrados if d["produto"] in filtro_produto]

    if filtrados:
        st.dataframe(filtrados, use_container_width=True)
    else:
        st.info("Nenhum ingrediente encontrado com os filtros selecionados.")

# Edição e exclusão
elif opcao == "Editar/Excluir Ingredientes":
    st.header("Editar ou Excluir Ingredientes")

    for idx, item in enumerate(dados):
        with st.expander(f"{item['produto']} - {item['subproduto']} - {item['marca']}"):
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                if st.button("Editar", key=f"editar_{idx}"):
                    st.session_state["editar_idx"] = idx
                    st.experimental_rerun()
            with col2:
                if st.button("Excluir", key=f"excluir_{idx}"):
                    st.session_state["confirmar_exclusao"] = idx
                    st.experimental_rerun()

    # Edição
    if "editar_idx" in st.session_state:
        idx = st.session_state["editar_idx"]
        item = dados[idx]
        st.subheader("Editar Ingrediente")

        with st.form("editar_form"):
            uso = st.selectbox("Uso", ["Interno", "Venda"], index=["Interno", "Venda"].index(item["uso"]))
            categoria = st.selectbox("Categoria", ["Bebida", "Alimento", "Outros"], index=["Bebida", "Alimento", "Outros"].index(item["categoria"]))
            produto = st.text_input("Produto", value=item["produto"])
            subproduto = st.text_input("Subproduto", value=item["subproduto"])
            marca = st.text_input("Marca", value=item["marca"])
            nome_comercial = st.text_input("Nome Comercial", value=item["nome_comercial"])
            quantidade = st.number_input("Quantidade", min_value=0.0, value=item["quantidade"], step=0.1)
            unidade = st.selectbox("Unidade", ["Kg", "g", "ml", "un"], index=["Kg", "g", "ml", "un"].index(item["unidade"]))
            valor_total = st.number_input("Valor Total (R$)", min_value=0.0, value=item["valor_total"], step=0.01)
            atualizado = st.form_submit_button("Atualizar")

            if atualizado:
                dados[idx] = {
                    **item,
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
                salvar_dados(dados)
                del st.session_state["editar_idx"]
                st.success("Ingrediente atualizado com sucesso!")
                st.experimental_rerun()

    # Exclusão com confirmação
    if "confirmar_exclusao" in st.session_state:
        idx = st.session_state["confirmar_exclusao"]
        item = dados[idx]
        st.warning(f"Tem certeza que deseja excluir o ingrediente: {item['produto']} - {item['marca']}?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Confirmar Exclusão"):
                dados.pop(idx)
                salvar_dados(dados)
                del st.session_state["confirmar_exclusao"]
                st.success("Ingrediente excluído com sucesso!")
                st.experimental_rerun()
        with col2:
            if st.button("Cancelar"):
                del st.session_state["confirmar_exclusao"]
                st.experimental_rerun()

