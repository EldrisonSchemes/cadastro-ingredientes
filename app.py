import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime
import shutil

# Configurações
DB_FILE = "ingredientes_db.json"
BACKUP_DIR = "backups"

# --- FUNÇÕES PRINCIPAIS ---
def carregar_dados():
    """Carrega dados do JSON e padroniza IDs sequenciais"""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            try:
                dados = json.load(f)
                # Garante IDs sequenciais (1, 2, 3...)
                for i, item in enumerate(dados, start=1):
                    if not str(item.get("id")).isdigit():
                        item["id"] = i
                return dados
            except json.JSONDecodeError:
                return []
    return []

def gerar_novo_id():
    """Gera o próximo ID sequencial"""
    if not ingredientes:
        return 1
    return max(int(item["id"]) for item in ingredientes) + 1

# --- BACKUP AUTOMÁTICO ---
def fazer_backup():
    """Cria backup rotativo (mantém últimos 7)"""
    if not os.path.exists(DB_FILE):
        return

    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"backup_{timestamp}.json")
    shutil.copy2(DB_FILE, backup_file)

    # Remove backups antigos (mantém 7)
    backups = sorted([f for f in os.listdir(BACKUP_DIR) if f.startswith("backup_")])
    while len(backups) > 7:
        os.remove(os.path.join(BACKUP_DIR, backups[0]))
        backups = backups[1:]

def salvar_dados(dados):
    """Salva dados e executa backup"""
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
                "data_atualizacao": datetime.now().strftime("%d/%m/%Y %H:%M")
            }
            ingredientes.append(novo_item)
            salvar_dados(ingredientes)
            st.success("✅ Item cadastrado com sucesso!")
            st.rerun()

# --- LISTA COMPLETA ---
elif menu == "Lista Completa":
    st.title("📋 Lista de Ingredientes")
    
    # Filtros fixos (organizados em colunas)
    st.subheader("Filtros")
    col1, col2, col3 = st.columns(3)
    with col1:
        filtro_uso = st.selectbox("Uso", ["Todos"] + sorted(list(set(i["uso"] for i in ingredientes))))
    with col2:
        filtro_categoria = st.selectbox("Categoria", ["Todos"] + sorted(list(set(i["categoria"] for i in ingredientes))))
    with col3:
        filtro_produto = st.selectbox("Produto", ["Todos"] + sorted(list(set(i["produto"] for i in ingredientes))))
    
    col4, col5, col6 = st.columns(3)
    with col4:
        filtro_subproduto = st.selectbox("Subproduto", ["Todos"] + sorted(list(set(i["subproduto"] for i in ingredientes if i["subproduto"]))))
    with col5:
        filtro_marca = st.selectbox("Marca", ["Todos"] + sorted(list(set(i["marca"] for i in ingredientes if i["marca"]))))
    with col6:
        filtro_nome = st.selectbox("Nome Comercial", ["Todos"] + sorted(list(set(i["nome_comercial"] for i in ingredientes if i["nome_comercial"]))))

    # Aplicar filtros
    dados_filtrados = ingredientes
    if filtro_uso != "Todos":
        dados_filtrados = [i for i in dados_filtrados if i["uso"] == filtro_uso]
    if filtro_categoria != "Todos":
        dados_filtrados = [i for i in dados_filtrados if i["categoria"] == filtro_categoria]
    if filtro_produto != "Todos":
        dados_filtrados = [i for i in dados_filtrados if i["produto"] == filtro_produto]
    if filtro_subproduto != "Todos":
        dados_filtrados = [i for i in dados_filtrados if i["subproduto"] == filtro_subproduto]
    if filtro_marca != "Todos":
        dados_filtrados = [i for i in dados_filtrados if i["marca"] == filtro_marca]
    if filtro_nome != "Todos":
        dados_filtrados = [i for i in dados_filtrados if i["nome_comercial"] == filtro_nome]

    # Tabela fixa
    if dados_filtrados:
        df = pd.DataFrame(dados_filtrados)[[
            "id", "nome_comercial", "uso", "categoria", "produto", 
            "subproduto", "marca", "quantidade", "unidade", 
            "valor_total", "data_cadastro", "data_atualizacao"
        ]]
        df["valor_total"] = "R$ " + df["valor_total"].astype(str)
        st.dataframe(
            df.rename(columns={
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

# --- EDIÇÃO ---
elif menu == "Editar Ingrediente":
    st.title("✏️ Editar Ingrediente")
    
    if not ingredientes:
        st.warning("⚠️ Nenhum item cadastrado para editar")
    else:
        # Seleção do item
        opcoes = [f"{i['id']} - {i['nome_comercial']} ({i['marca']})" for i in ingredientes]
        selecionado = st.selectbox("Selecione o item:", opcoes)
        id_selecionado = int(selecionado.split(" - ")[0])
        item_editar = next(i for i in ingredientes if i["id"] == id_selecionado)
        
        # Formulário de edição
        with st.form("form_edicao"):
            cols = st.columns(2)
            with cols[0]:
                novo_uso = st.selectbox("Uso", ["Interno", "Venda"], index=["Interno", "Venda"].index(item_editar["uso"]))
                novo_categoria = st.selectbox("Categoria", ["Alimento", "Bebida", "Outros"], index=["Alimento", "Bebida", "Outros"].index(item_editar["categoria"]))
                novo_produto = st.text_input("Produto", value=item_editar["produto"])
                novo_subproduto = st.text_input("Subproduto", value=item_editar["subproduto"])
            with cols[1]:
                novo_marca = st.text_input("Marca", value=item_editar["marca"])
                novo_nome = st.text_input("Nome Comercial", value=item_editar["nome_comercial"])
                novo_unidade = st.selectbox("Unidade", ["Kg", "g", "ml", "un"], index=["Kg", "g", "ml", "un"].index(item_editar["unidade"]))
                novo_valor = st.number_input("Valor Total (R$)", min_value=0.0, value=float(item_editar["valor_total"]), format="%.2f")
            
            # Quantidade dinâmica
            if novo_unidade in ["Kg", "un"]:
                novo_quantidade = st.number_input("Quantidade", min_value=0, value=int(item_editar["quantidade"]), step=1)
            else:
                novo_quantidade = st.number_input("Quantidade", min_value=0.0, value=float(item_editar["quantidade"]), step=0.01, format="%.2f")
            
            if st.form_submit_button("🔄 Atualizar"):
                item_editar.update({
                    "uso": novo_uso,
                    "categoria": novo_categoria,
                    "produto": novo_produto,
                    "subproduto": novo_subproduto,
                    "marca": novo_marca,
                    "nome_comercial": novo_nome,
                    "quantidade": novo_quantidade,
                    "unidade": novo_unidade,
                    "valor_total": novo_valor,
                    "data_atualizacao": datetime.now().strftime("%d/%m/%Y %H:%M")
                })
                salvar_dados(ingredientes)
                st.success("✅ Item atualizado com sucesso!")
                st.rerun()

# --- EXCLUSÃO ---
elif menu == "Excluir Ingrediente":
    st.title("❌ Excluir Ingrediente")
    
    if not ingredientes:
        st.warning("⚠️ Nenhum item cadastrado para excluir")
    else:
        # Seleção do item
        opcoes = [f"{i['id']} - {i['nome_comercial']} ({i['marca']})" for i in ingredientes]
        selecionado = st.selectbox("Selecione o item para excluir:", opcoes)
        id_selecionado = int(selecionado.split(" - ")[0])
        item_excluir = next(i for i in ingredientes if i["id"] == id_selecionado)
        
        # Confirmação
        st.error("⚠️ Atenção: Esta ação não pode ser desfeita!")
        st.write("**Detalhes do Item:**")
        cols = st.columns(2)
        with cols[0]:
            st.write(f"**ID:** {item_excluir['id']}")
            st.write(f"**Nome:** {item_excluir['nome_comercial']}")
            st.write(f"**Marca:** {item_excluir['marca']}")
        with cols[1]:
            st.write(f"**Quantidade:** {item_excluir['quantidade']} {item_excluir['unidade']}")
            st.write(f"**Valor:** R$ {item_excluir['valor_total']:.2f}")
            st.write(f"**Cadastrado em:** {item_excluir['data_cadastro']}")
        
        if st.button("🗑️ Confirmar Exclusão", type="primary"):
            ingredientes = [i for i in ingredientes if i["id"] != id_selecionado]
            salvar_dados(ingredientes)
            st.success("✅ Item excluído com sucesso!")
            st.rerun()
