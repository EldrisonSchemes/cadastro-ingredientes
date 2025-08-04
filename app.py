import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime
import shutil
from fastapi import FastAPI
import uvicorn
import threading

# ================================================== #
#                     CONFIGURAÇÕES                  #
# ================================================== #
DB_FILE = "ingredientes_db.json"
BACKUP_DIR = "backups"
ingredientes = []  # Inicialização global

# ================================================== #
#                  FASTAPI (ENDPOINT BI)             #
# ================================================== #
app = FastAPI()

@app.get("/api/estoque")
async def get_estoque(bi_key: str):
    """Endpoint seguro para integração com BI"""
    if bi_key == st.secrets.get("BI_KEY"):
        return {
            "timestamp": datetime.now().isoformat(),
            "dados": ingredientes
        }
    return {"error": "Chave inválida"}

def start_api():
    """Inicia a API em segundo plano"""
    uvicorn.run(app, host="0.0.0.0", port=8000)

# ================================================== #
#                  FUNÇÕES PRINCIPAIS                #
# ================================================== #
def carregar_dados():
    """Carrega e padroniza dados do JSON"""
    global ingredientes
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            try:
                dados = json.load(f)
                # Padroniza IDs sequenciais
                for i, item in enumerate(dados, start=1):
                    if not str(item.get("id")).isdigit():
                        item["id"] = i
                return dados
            except json.JSONDecodeError:
                return []
    return []

def gerar_novo_id():
    """Gera IDs sequenciais"""
    return max((item["id"] for item in ingredientes), default=0) + 1

def fazer_backup():
    """Backup rotativo (mantém últimos 7)"""
    if not os.path.exists(DB_FILE):
        return

    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy2(DB_FILE, os.path.join(BACKUP_DIR, f"backup_{timestamp}.json"))
    
    # Limpeza de backups antigos
    backups = sorted([f for f in os.listdir(BACKUP_DIR) if f.startswith("backup_")])
    for old_backup in backups[:-7]:
        os.remove(os.path.join(BACKUP_DIR, old_backup))

def salvar_dados(dados):
    """Salva dados com backup automático"""
    fazer_backup()
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

# ================================================== #
#                INTERFACE STREAMLIT                 #
# ================================================== #
ingredientes = carregar_dados()
st.set_page_config(page_title="Gestão de Estoque", layout="wide")

# Menu principal
menu = st.sidebar.radio("Menu", [
    "Cadastro",
    "Lista Completa",
    "Editar Ingrediente",
    "Excluir Ingrediente"
])

# --- CADASTRO ---
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
        
        # Quantidade dinâmica
        qtd_step = 1 if unidade in ["Kg", "un"] else 0.01
        quantidade = st.number_input(
            "Quantidade*",
            min_value=0,
            step=qtd_step,
            format="%d" if unidade in ["Kg", "un"] else "%.2f"
        )
        
        if st.form_submit_button("💾 Salvar"):
            ingredientes.append({
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
                "data_atualizacao": datetime.now().strftime("%d/%m/%Y %H:%M")
            })
            salvar_dados(ingredientes)
            st.success("✅ Item cadastrado com sucesso!")
            st.rerun()

# --- LISTA COMPLETA ---
elif menu == "Lista Completa":
    st.title("📋 Lista de Ingredientes")
    
    # Filtros organizados
    cols = st.columns(3)
    with cols[0]:
        filtro_uso = st.selectbox("Uso", ["Todos"] + sorted({i["uso"] for i in ingredientes}))
    with cols[1]:
        filtro_categoria = st.selectbox("Categoria", ["Todos"] + sorted({i["categoria"] for i in ingredientes}))
    with cols[2]:
        filtro_produto = st.selectbox("Produto", ["Todos"] + sorted({i["produto"] for i in ingredientes}))

    # Aplicação dos filtros
    dados_filtrados = [
        i for i in ingredientes
        if (filtro_uso == "Todos" or i["uso"] == filtro_uso)
        and (filtro_categoria == "Todos" or i["categoria"] == filtro_categoria)
        and (filtro_produto == "Todos" or i["produto"] == filtro_produto)
    ]

    # Exibição dos dados
    if dados_filtrados:
        df = pd.DataFrame(dados_filtrados)[[
            "id", "nome_comercial", "uso", "categoria", "produto", 
            "subproduto", "marca", "quantidade", "unidade", 
            "valor_total", "data_cadastro", "data_atualizacao"
        ]]
        st.dataframe(
            df.assign(valor_total="R$ " + df["valor_total"].astype(str))
            .rename(columns={
                "id": "ID",
                "nome_comercial": "Nome Comercial",
                "uso": "Uso",
                "categoria": "Categoria",
                "produto": "Produto",
                "subproduto": "Subproduto",
                "marca": "Marca",
                "quantidade": "Quantidade",
                "unidade": "Unidade",
                "valor_total": "Valor Total",
                "data_cadastro": "Data Cadastro",
                "data_atualizacao": "Última Atualização"
            }).set_index("ID"),
            use_container_width=True,
            height=600
        )
    else:
        st.info("ℹ️ Nenhum item encontrado com os filtros selecionados")

# --- EDIÇÃO E EXCLUSÃO (MANTIDOS COMO NO SEU CÓDIGO) ---
# [...] (O restante permanece idêntico ao seu código original)

# ================================================== #
#                INICIALIZAÇÃO DA API                #
# ================================================== #
if __name__ == "__main__":
    threading.Thread(target=start_api, daemon=True).start()