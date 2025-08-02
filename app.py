import streamlit as st
import json
import os
from datetime import datetime

ARQUIVO_DADOS = "dados_ingredientes.json"

st.set_page_config(page_title="Cadastro de Ingredientes", layout="wide")

# Funções de utilidade

@st.cache_data
def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def salvar_dados(dados):
    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

def adicionar_ingrediente(novo):
    dados = carregar_dados()
    for item in dados:
        if item['nome_comercial'].lower() == novo['nome_comercial'].lower() and item['marca'].lower() == novo['marca'].lower():
            total_valor = item['valor_total'] + novo['valor_total']
            total_quantidade = item['quantidade'] + novo['quantidade']
            item['valor_total'] = total_valor
            item['quantidade'] = total_quantidade
            item['valor_medio'] = round(total_valor / total_quantidade, 2) if total_quantidade else 0
            item['ultima_atualizacao'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            salvar_dados(dados)
            return
    novo['valor_medio'] = round(novo['valor_total'] / novo['quantidade'], 2) if novo['quantidade'] else 0
    novo['ultima_atualizacao'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    dados.append(novo)
    salvar_dados(dados)

def editar_ingrediente(index, atualizado):
    dados = carregar_dados()
    atualizado['valor_medio'] = round(atualizado['valor_total'] / atualizado['quantidade'], 2) if atualizado['quantidade'] else 0
    atualizado['ultima_atualizacao'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    dados[index] = atualizado
    salvar_dados(dados)

def excluir_ingrediente(index):
    dados = carregar_dados()
    del dados[index]
    salvar_dados(dados)

# Sidebar
st.sidebar.title("Menu")
pagina = st.sidebar.radio("Ir para:", ["Cadastro de Ingredientes", "Lista Completa"])

# Página: Cadastro de Ingredientes
if pagina == "Cadastro de Ingredientes":
    st.title("Cadastro de Ingredientes")

    with st.form("formulario"):
        uso = st.selectbox("Uso", ["interno", "venda"])
        categoria = st.selectbox("Categoria", ["bebida", "alimento", "outros"])
        produto = st.text_input("Produto (ex: Vinho)")
        marca = st.text_input("Marca (ex: Salton)")
        nome_comercial = st.text_input("Nome Comercial (ex: Tinto Suave)")
        subproduto = st.text_input("Subproduto (ex: Garrafa 750ml)")
        quantidade = st.number_input("Quantidade", min_value=0.01, format="%.2f")
        unidade = st.selectbox("Unidade", ["Kg", "g", "ml", "un"])
        valor_total = st.number_input("Valor Total da Compra (R$)", min_value=0.01, format="%.2f")

        submitted = st.form_submit_button("Salvar")
        if submitted:
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
            adicionar_ingrediente(novo_item)
            st.success("Ingrediente salvo com sucesso!")
            st.experimental_rerun()

# Página: Lista Completa
elif pagina == "Lista Completa":
    st.title("Lista de Ingredientes")

    dados = carregar_dados()

    busca = st.text_input("Buscar por nome comercial")
    uso_filtro = st.multiselect("Filtrar por uso", options=sorted(set(i['uso'] for i in dados)), default=list(set(i['uso'] for i in dados)))
    categoria_filtro = st.multiselect("Filtrar por categoria", options=sorted(set(i['categoria'] for i in dados)), default=list(set(i['categoria'] for i in dados)))
    produto_filtro = st.multiselect("Filtrar por produto", options=sorted(set(i['produto'] for i in dados)), default=list(set(i['produto'] for i in dados)))
    subproduto_filtro = st.multiselect("Filtrar por subproduto", options=sorted(set(i['subproduto'] for i in dados)), default=list(set(i['subproduto'] for i in dados)))
    marca_filtro = st.multiselect("Filtrar por marca", options=sorted(set(i['marca'] for i in dados)), default=list(set(i['marca'] for i in dados)))

    dados_filtrados = [i for i in dados if
        (busca.lower() in i['nome_comercial'].lower() if busca else True) and
        i['uso'] in uso_filtro and
        i['categoria'] in categoria_filtro and
        i['produto'] in produto_filtro and
        i['subproduto'] in subproduto_filtro and
        i['marca'] in marca_filtro
    ]

    for index, item in enumerate(dados_filtrados):
        with st.expander(f"{item['nome_comercial']} ({item['quantidade']} {item['unidade']}) - R$ {item.get('valor_medio', 0):.2f}"):
            st.markdown(f"**Uso:** {item['uso']}")
            st.markdown(f"**Categoria:** {item['categoria']}")
            st.markdown(f"**Produto:** {item['produto']}")
            st.markdown(f"**Marca:** {item['marca']}")
            st.markdown(f"**Nome Comercial:** {item['nome_comercial']}")
            st.markdown(f"**Subproduto:** {item['subproduto']}")
            st.markdown(f"**Quantidade:** {item['quantidade']} {item['unidade']}")
            st.markdown(f"**Valor Total:** R$ {item['valor_total']:.2f}")
            st.markdown(f"**Valor Médio:** R$ {item['valor_medio']:.2f}")
            st.markdown(f"**Última Atualização:** {item.get('ultima_atualizacao', 'N/A')}")

            col1, col2 = st.columns(2)
            if col1.button("Editar", key=f"editar_{index}"):
                st.session_state['editar_index'] = index
                st.switch_page("app.py")
            if col2.button("Excluir", key=f"excluir_{index}"):
                if st.confirm("Tem certeza que deseja excluir este ingrediente?"):
                    excluir_ingrediente(index)
                    st.success("Ingrediente excluído com sucesso!")
                    st.experimental_rerun()

    if not dados_filtrados:
        st.warning("Nenhum ingrediente encontrado com os filtros aplicados.")

    st.subheader("Visualização em formato Excel")
    st.dataframe(dados_filtrados, use_container_width=True)

