import streamlit as st
import json
import os
from datetime import datetime
from uuid import uuid4

DB_PATH = "ingredientes_db.json"

# Iniciar base de dados se não existir
if not os.path.exists(DB_PATH):
    with open(DB_PATH, "w") as f:
        json.dump([], f)

# Funções auxiliares
def carregar_dados():
    with open(DB_PATH, "r") as f:
        return json.load(f)

def salvar_dados(dados):
    with open(DB_PATH, "w") as f:
        json.dump(dados, f, indent=4)

def sugestoes_campo(campo):
    return list({item.get(campo, "") for item in dados if item.get(campo)})

def limpar_campos():
    st.session_state.clear()

# Layout
st.set_page_config(page_title="Cadastro de Ingredientes", layout="wide")
menu = st.sidebar.radio("Menu", ["Cadastrar Ingrediente", "Visualizar Ingredientes"])

dados = carregar_dados()

if menu == "Cadastrar Ingrediente":
    st.title("📦 Cadastro de Ingredientes")

    with st.form("formulario", clear_on_submit=False):
        uso = st.selectbox("Uso", ["Interno", "Venda"], key="uso")
        categoria = st.selectbox("Categoria", ["Alimento", "Bebida", "Outros"], key="categoria")
        produto = st.text_input("Produto", key="produto", placeholder="Ex: Vinho", value="", autocomplete=True)
        subproduto = st.text_input("Subproduto", key="subproduto", placeholder="Ex: Tinto Seco")
        marca = st.text_input("Marca", key="marca", placeholder="Ex: Miolo")
        nome = st.text_input("Nome Comercial", key="nome", placeholder="Ex: Miolo Seleção 750ml")
        quantidade = st.number_input("Quantidade", min_value=0.0, format="%.2f", step=0.1)
        unidade = st.selectbox("Unidade", ["kg", "g", "ml", "un"])
        valor_total = st.number_input("Valor Total (R$)", min_value=0.0, format="%.2f", step=0.1)

        submitted = st.form_submit_button("Salvar")
        if submitted:
            novo = {
                "id": str(uuid4()),
                "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "uso": uso,
                "categoria": categoria,
                "produto": produto.strip(),
                "subproduto": subproduto.strip(),
                "marca": marca.strip(),
                "nome": nome.strip(),
                "quantidade": quantidade,
                "unidade": unidade,
                "valor_total": valor_total
            }
            dados.append(novo)
            salvar_dados(dados)
            st.success("Ingrediente salvo com sucesso!")
            limpar_campos()

elif menu == "Visualizar Ingredientes":
    st.title("📊 Ingredientes Cadastrados")

    # Filtros
    col1, col2, col3, col4, col5 = st.columns(5)
    uso_filtro = col1.selectbox("Filtrar por Uso", ["Todos"] + list(sorted({i["uso"] for i in dados})))
    categoria_filtro = col2.selectbox("Filtrar por Categoria", ["Todos"] + list(sorted({i["categoria"] for i in dados})))
    produto_filtro = col3.selectbox("Filtrar por Produto", ["Todos"] + list(sorted({i["produto"] for i in dados})))
    subproduto_filtro = col4.selectbox("Filtrar por Subproduto", ["Todos"] + list(sorted({i["subproduto"] for i in dados if i.get("subproduto")})))
    marca_filtro = col5.selectbox("Filtrar por Marca", ["Todos"] + list(sorted({i["marca"] for i in dados if i.get("marca")})))

    # Aplicar filtros
    filtrados = dados
    if uso_filtro != "Todos":
        filtrados = [i for i in filtrados if i["uso"] == uso_filtro]
    if categoria_filtro != "Todos":
        filtrados = [i for i in filtrados if i["categoria"] == categoria_filtro]
    if produto_filtro != "Todos":
        filtrados = [i for i in filtrados if i["produto"] == produto_filtro]
    if subproduto_filtro != "Todos":
        filtrados = [i for i in filtrados if i["subproduto"] == subproduto_filtro]
    if marca_filtro != "Todos":
        filtrados = [i for i in filtrados if i["marca"] == marca_filtro]

    for item in filtrados:
        with st.expander(f"{item['produto']} - {item['nome']}"):
            st.write(f"📅 Data: `{item['data']}`")
            st.write(f"🔸 Uso: **{item['uso']}**")
            st.write(f"🔸 Categoria: **{item['categoria']}**")
            st.write(f"🔸 Subproduto: {item['subproduto']}")
            st.write(f"🔸 Marca: {item['marca']}")
            st.write(f"🔸 Quantidade: **{item['quantidade']} {item['unidade']}**")
            st.write(f"🔸 Valor Total: **R$ {item['valor_total']:.2f}**")

            col_ed, col_exc = st.columns(2)
            if col_ed.button("✏️ Editar", key=f"edit_{item['id']}"):
                st.warning("Edição ainda em construção. Em breve disponível.")
            if col_exc.button("🗑️ Excluir", key=f"del_{item['id']}"):
                if st.confirm("Tem certeza que deseja excluir?"):
                    dados = [d for d in dados if d["id"] != item["id"]]
                    salvar_dados(dados)
                    st.success("Ingrediente excluído.")
                    st.experimental_rerun()
