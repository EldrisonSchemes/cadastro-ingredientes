import streamlit as st
import pandas as pd
import os
import json

# Caminho do banco de dados local
DB_PATH = "ingredientes_db.json"

# Inicializa banco de dados
def carregar_dados():
    if os.path.exists(DB_PATH):
        with open(DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def salvar_dados(dados):
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

dados = carregar_dados()

# Função para atualizar valor médio e quantidade
def adicionar_ao_estoque(produto, nova_quantidade, novo_valor):
    for item in dados:
        if item["Produto"] == produto:
            quantidade_antiga = item["Quantidade"]
            valor_antigo = item["Valor"]

            quantidade_total = quantidade_antiga + nova_quantidade
            valor_total = valor_antigo + novo_valor

            item["Quantidade"] = quantidade_total
            item["Valor"] = valor_total
            item["Valor Médio Unitário"] = round(valor_total / quantidade_total, 2)
            salvar_dados(dados)
            return True
    return False

# Sidebar para navegação
menu = st.sidebar.radio("Navegação", ["Cadastrar Produto", "Visualizar / Editar / Excluir"])

if menu == "Cadastrar Produto":
    st.title("📦 Cadastro de Ingredientes")

    st.subheader("Preencha os dados do ingrediente:")

    uso = st.selectbox("Uso", ["Interno", "Venda"])
    categoria = st.selectbox("Categoria", ["Bebida", "Alimento", "Outros"])
    produto = st.text_input("Produto")
    subproduto = st.text_input("Sub Produto (opcional)")
    marca = st.text_input("Marca")
    nome_comercial = st.text_input("Nome Comercial (opcional)")
    unidade = st.selectbox("Unidade", ["Kg", "g", "ml", "un"])

    # Quantidade restrita a inteiro se unidade for Kg ou un
    if unidade in ["Kg", "un"]:
        quantidade = st.number_input("Quantidade", min_value=1, step=1)
    else:
        quantidade = st.number_input("Quantidade", min_value=0.01, step=0.01, format="%.2f")

    valor = st.number_input("Valor Total da Compra (R$)", min_value=0.01, step=0.01, format="%.2f", help="Valor total da compra, não por unidade")

    if st.button("Salvar Produto"):
        if produto:
            novo = {
                "Uso": uso,
                "Categoria": categoria,
                "Produto": produto,
                "Sub Produto": subproduto,
                "Marca": marca,
                "Nome Comercial": nome_comercial,
                "Unidade": unidade,
                "Quantidade": quantidade,
                "Valor": valor,
                "Valor Médio Unitário": round(valor / quantidade, 2)
            }

            if adicionar_ao_estoque(produto, quantidade, valor):
                st.success(f"✔ Estoque de '{produto}' atualizado.")
            else:
                dados.append(novo)
                salvar_dados(dados)
                st.success(f"✔ Produto '{produto}' cadastrado com sucesso!")
        else:
            st.warning("⚠ Por favor, preencha o campo Produto.")

elif menu == "Visualizar / Editar / Excluir":
    st.title("🔎 Ingredientes Cadastrados")

    if dados:
        df = pd.DataFrame(dados)

        # Campo de busca
        filtro = st.text_input("🔍 Buscar por nome, categoria, marca...")

        if filtro:
            df = df[df.apply(lambda row: filtro.lower() in str(row).lower(), axis=1)]

        st.dataframe(df, use_container_width=True)

        nomes_produtos = [d["Produto"] for d in dados]
        produto_selecionado = st.selectbox("Selecione um produto para editar ou excluir", [""] + nomes_produtos)

        if produto_selecionado:
            item = next((i for i in dados if i["Produto"] == produto_selecionado), None)

            if item:
                st.write("🔧 Dados atuais do produto:")
                st.json(item)

                if st.button("❌ Excluir Produto"):
                    dados.remove(item)
                    salvar_dados(dados)
                    st.success("Produto excluído com sucesso!")
                    st.experimental_rerun()

    else:
        st.warning("Nenhum produto cadastrado ainda.")