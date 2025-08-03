import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime
import shutil
import uuid

#Principais Características: IDs sequenciais - Filtros fixos - Layout otimizado - Backup automático (7 dias)
# Configurações iniciais
DB_FILE = "ingredientes_db.json"
BACKUP_DIR = "backups"
# --- FUNÇÕES PRINCIPAIS ---
def carregar_dados():
    """Carrega os dados do arquivo JSON e padroniza IDs"""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            try:
                dados = json.load(f)
                # Converte IDs antigos para sequenciais
                for i, item in enumerate(dados, start=1):
                    if not str(item.get("id")).isdigit():
                        item["id"] = i
                return dados
            except json.JSONDecodeError:
                return []
    return []
def gerar_novo_id():
    """Gera IDs sequenciais a partir do maior ID existente"""
    if not ingredientes:
        return 1
    return max(int(item["id"]) for item in ingredientes) + 1
# --- BACKUP AUTOMÁTICO ---
def fazer_backup():
    """Cria backups rotativos mantendo as últimas 7 versões"""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    backup_file = os.path.join(BACKUP_DIR, f"backup_{timestamp}.json")
    shutil.copy2(DB_FILE, backup_file)
    # Limita a 7 backups
    backups = sorted([f for f in os.listdir(BACKUP_DIR) if f.startswith("backup_")])
    while len(backups) > 7:
        os.remove(os.path.join(BACKUP_DIR, backups[0]))
        backups = backups[1:]
def salvar_dados(dados):
    """Salva dados principais e executa backup"""
    fazer_backup()
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)
# --- INTERFACE STREAMLIT ---
ingredientes = carregar_dados()
st.set_page_config(page_title="Gestão de Estoque", layout="wide")
# Menu principal
menu = st.sidebar.radio("Menu", [
    "Cadastro",
    "Lista Completa",
    "Movimentar Estoque"
])

# --- CADASTRO DE ITENS ---
if menu == "Cadastro":
    st.title("📝 Cadastro de Ingredientes")
    
    with st.form("form_cadastro", clear_on_submit=True):
        cols = st.columns(2)
        with cols[0]:
            uso = st.selectbox("Uso*", ["Interno", "Venda"])
            categoria = st.selectbox("Categoria*", ["Alimento", "Bebida", "Outros"])
            produto = st.text_input("Produto*", placeholder="Ex: Vinho")
            subproduto = st.text_input("Subproduto", placeholder="Ex: Merlot")
        
        with cols[1]:
            marca = st.text_input("Marca", placeholder="Ex: Miolo")
            nome_comercial = st.text_input("Nome Comercial", placeholder="Ex: Reserva 2020")
            unidade = st.selectbox("Unidade*", ["Kg", "g", "ml", "un"])
            valor_total = st.number_input("Valor Total (R$)*", min_value=0.0, format="%.2f")
        
        # Quantidade dinâmica conforme unidade
        if unidade in ["Kg", "un"]:
            quantidade = st.number_input("Quantidade*", min_value=0, step=1)
        else:
            quantidade = st.number_input("Quantidade*", min_value=0.0, step=0.01, format="%.2f")
        
        if st.form_submit_button("💾 Salvar"):
            novo_item = {
                "id": gerar_novo_id(),
                "uso": uso,
                "categoria": categoria,
                "produto": produto,
                "subproduto": subproduto,
                "marca": marca,
                "nome_comercial": nome_comercial,
                "quantidade": quantidade,
                "unidade": unidade,
                "valor_total": valor_total,
                "data_cadastro": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "data_atualizacao": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "movimentacoes": []
            }
            
            ingredientes.append(novo_item)
            salvar_dados(ingredientes)
            st.success("✅ Item cadastrado com sucesso!")
            st.rerun()

elif menu == "Lista Completa":
    st.title("📋 Lista de Ingredientes")
    
    # Filtros organizados em 3 colunas
    cols_filtros = st.columns(3)
    with cols_filtros[0]:
        filtro_uso = st.selectbox("Uso", ["Todos"] + list(sorted(set(i["uso"] for i in ingredientes))))
    with cols_filtros[1]:
        filtro_categoria = st.selectbox("Categoria", ["Todos"] + list(sorted(set(i["categoria"] for i in ingredientes))))
    with cols_filtros[2]:
        filtro_produto = st.selectbox("Produto", ["Todos"] + list(sorted(set(i["produto"] for i in ingredientes))))

    # Aplicação dos filtros
    dados_filtrados = ingredientes
    if filtro_uso != "Todos":
        dados_filtrados = [i for i in dados_filtrados if i["uso"] == filtro_uso]
    if filtro_categoria != "Todos":
        dados_filtrados = [i for i in dados_filtrados if i["categoria"] == filtro_categoria]
    if filtro_produto != "Todos":
        dados_filtrados = [i for i in dados_filtrados if i["produto"] == filtro_produto]

    # Tabela fixa com colunas pré-definidas
    if dados_filtrados:
        df = pd.DataFrame(dados_filtrados)[[
            "id", "nome_comercial", "uso", "categoria", "produto", 
            "subproduto", "marca", "quantidade", "unidade", 
            "valor_total", "data_cadastro", "data_atualizacao"
        ]]
        
        # Formatação
        df["valor_total"] = "R$ " + df["valor_total"].astype(str)
        st.dataframe(
            df.rename(columns={
                "id": "ID",
                "nome_comercial": "Nome Comercial",
                # ... (outros renomeamentos)
            }).set_index("ID"),
            use_container_width=True,
            height=600
        )
    else:
        st.info("ℹ️ Nenhum item encontrado com os filtros selecionados")
