import streamlit as st
import json
import os
from datetime import datetime

DB_PATH = "ingredientes_db.json"

# Inicializa o banco se não existir
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

def limpar_campos():
    st.session_state.clear()

def atualizar_produto(index, novos_dados):
    dados = carregar_dados()
    dados[index] = novos_dados
    salvar_dados(dados)

def excluir_produto(index):
    dados = carregar_dados()
    dados.pop(index)
    salvar_dados(dados)

# Carrega banco para sugestões
dados = carregar_dados()
produtos_anteriores = sorted(list(set([d["produto"] for d in dados])))
subprodutos_anteriores = sorted(list(set([d["subproduto"] for d in dados])))
marcas_anteriores = sorted(list(set([d["marca"] for d in dados])))
nomes_comerciais_anteriores = sorted(list(set([d["nome_comercial"] for d in dados])))

# Filtros fixos
st.sidebar.title("Filtros")
filtro_uso = st.sidebar.selectbox("Filtrar por uso", ["Todos", "interno", "venda"])
filtro_categoria = st.sidebar.selectbox("Filtrar por categoria", ["Todos", "bebida", "alimento", "outros"])
filtro_produto = st.sidebar.selectbox("Filtrar por produto", ["Todos"] + produtos_anteriores)
filtro_subproduto = st.sidebar.selectbox("Filtrar por subproduto", ["Todos"] + subprodutos_anteriores)
filtro_marca = st.sidebar.selectbox("Filtrar por marca", ["Todos"] + marcas_anteriores)

st.title("Cadastro de Ingredientes")

# Formulário principal
with st.form("cadastro"):
    uso = st.selectbox("Uso", ["interno", "venda"])
    categoria = st.selectbox("Categoria", ["bebida", "alimento", "outros"])
    produto = st.selectbox("Produto", produtos_anteriores + ["Outro"], key="produto")
    if produto == "Outro":
        produto = st.text_input("Digite o novo produto", key="novo_produto")

    subproduto = st.selectbox("Subproduto", subprodutos_anteriores + ["Outro"], key="subproduto")
    if subproduto == "Outro":
        subproduto = st.text_input("Digite o novo subproduto", key="novo_subproduto")

    marca = st.selectbox("Marca", marcas_anteriores + ["Outro"], key="marca")
    if marca == "Outro":
        marca = st.text_input("Digite a nova marca", key="nova_marca")

    nome_comercial = st.selectbox("Nome Comercial", nomes_comerciais_anteriores + ["Outro"], key="nome_comercial")
    if nome_comercial == "Outro":
        nome_comercial = st.text_input("Digite o novo nome comercial", key="novo_nome_comercial")

    quantidade = st.number_input("Quantidade", min_value=0.0, step=0.1)
    unidade = st.selectbox("Unidade", ["Kg", "g", "ml", "un"])
    valor_total = st.number_input("Valor Total (R$)", min_value=0.0, step=0.01)

    submitted = st.form_submit_button("Salvar")

    if submitted:
        novo_ingrediente = {
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
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
        dados.append(novo_ingrediente)
        salvar_dados(dados)
        st.success("Ingrediente salvo com sucesso!")
        limpar_campos()

# Visualização
st.subheader("Ingredientes Cadastrados")
dados = carregar_dados()

# Aplica filtros
if filtro_uso != "Todos":
    dados = [d for d in dados if d["uso"] == filtro_uso]
if filtro_categoria != "Todos":
    dados = [d for d in dados if d["categoria"] == filtro_categoria]
if filtro_produto != "Todos":
    dados = [d for d in dados if d["produto"] == filtro_produto]
if filtro_subproduto != "Todos":
    dados = [d for d in dados if d["subproduto"] == filtro_subproduto]
if filtro_marca != "Todos":
    dados = [d for d in dados if d["marca"] == filtro_marca]

# Exibe os dados
for i, item in enumerate(dados):
    with st.expander(f"{item['produto']} - {item['nome_comercial']}"):
        st.write(f"**Data:** {item['data']}")
        st.write(f"**Uso:** {item['uso']}")
        st.write(f"**Categoria:** {item['categoria']}")
        st.write(f"**Subproduto:** {item['subproduto']}")
        st.write(f"**Marca:** {item['marca']}")
        st.write(f"**Quantidade:** {item['quantidade']} {item['unidade']}")
        st.write(f"**Valor Total:** R$ {item['valor_total']:.2f}")

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button(f"📝 Editar", key=f"edit_{i}"):
                st.warning("Função de edição será implementada em breve!")

        with col2:
            if st.button(f"🗑️ Excluir", key=f"delete_{i}"):
                if st.confirm(f"Tem certeza que deseja excluir {item['produto']} - {item['nome_comercial']}?", key=f"confirma_{i}"):
                    excluir_produto(i)
                    st.success("Ingrediente excluído com sucesso.")
                    st.experimental_rerun()

# Atualização automática - instrução
st.markdown("---")
st.markdown("✅ **Após salvar este arquivo no GitHub, a publicação no Streamlit Cloud é atualizada automaticamente.**")

