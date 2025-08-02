import streamlit as st
import pandas as pd
import os

# Caminho do arquivo de dados
ARQUIVO_DADOS = "ingredientes.csv"

# Função para carregar os dados
def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        return pd.read_csv(ARQUIVO_DADOS)
    else:
        return pd.DataFrame(columns=[
            "Uso", "Categoria", "Produto", "Marca", "Nome Comercial",
            "Subproduto", "Quantidade", "Unidade", "Valor Total"
        ])

# Função para salvar os dados
def salvar_dados(df):
    df.to_csv(ARQUIVO_DADOS, index=False)

# Função para limpar campos
def limpar_campos():
    st.session_state.clear()

# Título
st.title("📦 Cadastro de Ingredientes")

# Menu lateral
menu = st.sidebar.radio("Navegação", ["Cadastro", "Lista completa", "Buscar", "Editar", "Excluir"])

# Carrega os dados
df = carregar_dados()

# Cadastro de ingredientes
if menu == "Cadastro":
    st.subheader("Adicionar Ingrediente")

    # Sugestões baseadas nos dados já existentes
    sugestoes_produto = df['Produto'].dropna().unique().tolist()
    sugestoes_marca = df['Marca'].dropna().unique().tolist()
    sugestoes_subproduto = df['Subproduto'].dropna().unique().tolist()

    with st.form("form_cadastro"):
        uso = st.selectbox("Uso", ["Interno", "Venda"])
        categoria = st.selectbox("Categoria", ["Bebida", "Alimento", "Outros"])
        produto = st.text_input("Produto", placeholder="Ex: Vinho")
        marca = st.text_input("Marca")
        nome_comercial = st.text_input("Nome Comercial")
        subproduto = st.text_input("Subproduto")
        quantidade = st.number_input("Quantidade", min_value=0.0, format="%.2f")
        unidade = st.selectbox("Unidade", ["Kg", "g", "ml", "un"])
        valor_total = st.number_input("Valor Total", min_value=0.0, format="%.2f")

        submitted = st.form_submit_button("Salvar")
        if submitted:
            novo = pd.DataFrame([{
                "Uso": uso,
                "Categoria": categoria,
                "Produto": produto,
                "Marca": marca,
                "Nome Comercial": nome_comercial,
                "Subproduto": subproduto,
                "Quantidade": quantidade,
                "Unidade": unidade,
                "Valor Total": valor_total
            }])
            df = pd.concat([df, novo], ignore_index=True)
            salvar_dados(df)
            st.success("Ingrediente salvo com sucesso!")
            limpar_campos()

# Lista com filtros fixos visíveis
elif menu == "Lista completa":
    st.subheader("Estoque de Ingredientes")

    # Filtros fixos
    col1, col2 = st.columns(2)
    with col1:
        filtro_categoria = st.selectbox("Filtrar por categoria", ["Todos"] + df["Categoria"].dropna().unique().tolist())
    with col2:
        filtro_produto = st.selectbox("Filtrar por produto", ["Todos"] + df["Produto"].dropna().unique().tolist())

    dados_filtrados = df.copy()
    if filtro_categoria != "Todos":
        dados_filtrados = dados_filtrados[dados_filtrados["Categoria"] == filtro_categoria]
    if filtro_produto != "Todos":
        dados_filtrados = dados_filtrados[dados_filtrados["Produto"] == filtro_produto]

    st.dataframe(dados_filtrados, use_container_width=True)

# Buscar ingredientes
elif menu == "Buscar":
    st.subheader("🔍 Buscar Ingredientes")
    termo = st.text_input("Digite o nome do produto ou marca para buscar:")
    if termo:
        resultado = df[df.apply(lambda row: termo.lower() in row.astype(str).str.lower().to_string(), axis=1)]
        st.dataframe(resultado)

# Editar ingredientes
elif menu == "Editar":
    st.subheader("✏️ Editar Ingredientes")
    index = st.number_input("Digite o número da linha para editar:", min_value=0, max_value=len(df)-1, step=1)
    if len(df) > 0:
        st.write("Ingrediente atual:")
        st.write(df.iloc[index])

        with st.form("form_edicao"):
            uso = st.selectbox("Uso", ["Interno", "Venda"], index=["Interno", "Venda"].index(df.iloc[index]["Uso"]))
            categoria = st.selectbox("Categoria", ["Bebida", "Alimento", "Outros"], index=["Bebida", "Alimento", "Outros"].index(df.iloc[index]["Categoria"]))
            produto = st.text_input("Produto", value=df.iloc[index]["Produto"])
            marca = st.text_input("Marca", value=df.iloc[index]["Marca"])
            nome_comercial = st.text_input("Nome Comercial", value=df.iloc[index]["Nome Comercial"])
            subproduto = st.text_input("Subproduto", value=df.iloc[index]["Subproduto"])
            quantidade = st.number_input("Quantidade", value=float(df.iloc[index]["Quantidade"]), format="%.2f")
            unidade = st.selectbox("Unidade", ["Kg", "g", "ml", "un"], index=["Kg", "g", "ml", "un"].index(df.iloc[index]["Unidade"]))
            valor_total = st.number_input("Valor Total", value=float(df.iloc[index]["Valor Total"]), format="%.2f")

            editar = st.form_submit_button("Salvar Alterações")
            if editar:
                df.loc[index] = [uso, categoria, produto, marca, nome_comercial, subproduto, quantidade, unidade, valor_total]
                salvar_dados(df)
                st.success("Ingrediente editado com sucesso!")

# Excluir ingrediente
elif menu == "Excluir":
    st.subheader("🗑️ Excluir Ingredientes")
    index = st.number_input("Digite o número da linha para excluir:", min_value=0, max_value=len(df)-1, step=1)
    if len(df) > 0:
        st.write("Ingrediente selecionado:")
        st.write(df.iloc[index])
        if st.button("Confirmar Exclusão"):
            df = df.drop(index).reset_index(drop=True)
            salvar_dados(df)
            st.success("Ingrediente excluído com sucesso!")