import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# Caminho do arquivo de dados
CAMINHO_ARQUIVO = 'ingredientes.json'

# Função para carregar os dados
@st.cache_data

def carregar_dados():
    if os.path.exists(CAMINHO_ARQUIVO):
        with open(CAMINHO_ARQUIVO, 'r') as f:
            return json.load(f)
    else:
        return []

# Função para salvar os dados
def salvar_dados(dados):
    with open(CAMINHO_ARQUIVO, 'w') as f:
        json.dump(dados, f, indent=4)

# Função para redefinir campos após salvar
def limpar_campos():
    st.session_state.clear()

# Carrega os dados existentes
dados = carregar_dados()

# Menu lateral
menu = st.sidebar.selectbox("Menu", ["Cadastro de Ingredientes", "Lista Completa"])

# Cadastro de Ingredientes
if menu == "Cadastro de Ingredientes":
    st.title("Cadastro de Ingredientes")

    uso = st.selectbox("Uso", ["Interno", "Venda"], help="Escolha se o ingrediente será usado internamente ou para venda")
    categoria = st.selectbox("Categoria", ["Bebida", "Alimento", "Outros"], help="Selecione a categoria do ingrediente")
    produto = st.text_input("Produto", placeholder="Ex: Vinho")
    subproduto = st.text_input("Subproduto", placeholder="Ex: Tinto Seco")
    marca = st.text_input("Marca", placeholder="Ex: Miolo")
    nome_comercial = st.text_input("Nome Comercial", placeholder="Ex: Miolo Reserva Tinto")
    unidade = st.selectbox("Unidade", ["Kg", "g", "ml", "un"])

    if unidade in ["Kg", "un"]:
        quantidade = st.number_input("Quantidade", min_value=0, step=1, format="%d")
    else:
        quantidade = st.number_input("Quantidade", min_value=0.0, step=0.1, format="%.2f")

    valor_total = st.number_input("Valor Total (R$)", min_value=0.0, step=0.01, format="%.2f")

    if st.button("Salvar Ingrediente"):
        if not produto or not nome_comercial or quantidade == 0 or valor_total == 0:
            st.warning("Por favor, preencha todos os campos obrigatórios corretamente.")
        else:
            existente = next((item for item in dados if item['nome_comercial'].lower() == nome_comercial.lower()), None)
            if existente:
                # Atualiza valor médio ponderado e quantidade
                nova_quantidade = existente['quantidade'] + quantidade
                novo_valor_total = existente['valor_total'] + valor_total
                valor_medio = novo_valor_total / nova_quantidade
                existente.update({
                    'quantidade': nova_quantidade,
                    'valor_total': novo_valor_total,
                    'valor_medio': round(valor_medio, 2),
                    'ultima_atualizacao': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
            else:
                dados.append({
                    "uso": uso,
                    "categoria": categoria,
                    "produto": produto,
                    "subproduto": subproduto,
                    "marca": marca,
                    "nome_comercial": nome_comercial,
                    "unidade": unidade,
                    "quantidade": quantidade,
                    "valor_total": valor_total,
                    "valor_medio": round(valor_total / quantidade, 2) if quantidade else 0,
                    "ultima_atualizacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

            salvar_dados(dados)
            st.success("Ingrediente salvo com sucesso!")
            limpar_campos()

# Lista Completa
elif menu == "Lista Completa":
    st.title("Lista de Ingredientes")

    # Filtros
    col1, col2, col3 = st.columns(3)
    with col1:
        filtro_uso = st.selectbox("Filtrar por Uso", ["Todos"] + sorted(set(d['uso'] for d in dados)))
    with col2:
        filtro_categoria = st.selectbox("Filtrar por Categoria", ["Todos"] + sorted(set(d['categoria'] for d in dados)))
    with col3:
        filtro_produto = st.selectbox("Filtrar por Produto", ["Todos"] + sorted(set(d['produto'] for d in dados if d['produto'])))

    col4, col5 = st.columns(2)
    with col4:
        filtro_subproduto = st.selectbox("Filtrar por Subproduto", ["Todos"] + sorted(set(d['subproduto'] for d in dados if d['subproduto'])))
    with col5:
        filtro_marca = st.selectbox("Filtrar por Marca", ["Todos"] + sorted(set(d['marca'] for d in dados if d['marca'])))

    busca = st.text_input("Buscar por Nome Comercial")

    # Aplica os filtros
    dados_filtrados = dados
    if filtro_uso != "Todos":
        dados_filtrados = [d for d in dados_filtrados if d['uso'] == filtro_uso]
    if filtro_categoria != "Todos":
        dados_filtrados = [d for d in dados_filtrados if d['categoria'] == filtro_categoria]
    if filtro_produto != "Todos":
        dados_filtrados = [d for d in dados_filtrados if d['produto'] == filtro_produto]
    if filtro_subproduto != "Todos":
        dados_filtrados = [d for d in dados_filtrados if d['subproduto'] == filtro_subproduto]
    if filtro_marca != "Todos":
        dados_filtrados = [d for d in dados_filtrados if d['marca'] == filtro_marca]
    if busca:
        dados_filtrados = [d for d in dados_filtrados if busca.lower() in d['nome_comercial'].lower()]

    df = pd.DataFrame(dados_filtrados)
    if not df.empty:
        st.dataframe(df.drop(columns=['valor_total']), use_container_width=True)
    else:
        st.info("Nenhum ingrediente encontrado com os filtros selecionados.")

    # Edição e exclusão
    for idx, item in enumerate(dados_filtrados):
        st.markdown(f"**{item['nome_comercial']} ({item['quantidade']} {item['unidade']}) - R$ {item['valor_medio']}**")
        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("Editar", key=f"editar_{idx}"):
                st.warning("Edição ainda não implementada.")
        with col2:
            if st.button("Excluir", key=f"excluir_{idx}"):
                if st.confirm(f"Deseja realmente excluir '{item['nome_comercial']}'?"):
                    dados.remove(item)
                    salvar_dados(dados)
                    st.success(f"{item['nome_comercial']} removido com sucesso.")
                    st.experimental_rerun()
