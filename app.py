import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime

DB_FILE = "ingredientes_db.json"

# Função para carregar dados
def carregar_dados():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            try:
                dados = json.load(f)
                # Atualizar IDs sequenciais se necessário
                for i, item in enumerate(dados, start=1):
                    if not str(item.get("id")).isdigit():
                        item["id"] = i
                return dados
            except json.JSONDecodeError:
                return []
    return []

# Função para salvar dados
def salvar_dados(dados):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

# Inicializa dados
ingredientes = carregar_dados()

# Configuração da página
st.set_page_config(page_title="Cadastro de Ingredientes", layout="wide")

# Barra lateral
menu = st.sidebar.radio("Menu", [
    "Cadastro",
    "Lista Completa",
    "Editar Ingrediente",
    "Excluir Ingrediente"
])

# Função para gerar novo ID sequencial
def gerar_novo_id():
    if not ingredientes:
        return 1
    return max(int(item["id"]) for item in ingredientes) + 1

# Função para exibir formulário (reutilizável para cadastro e edição)
def exibir_formulario(item=None):
    if item is None:
        item = {}
    
    with st.form(key="form_ingrediente", clear_on_submit=(item == {})):
        uso = st.selectbox("Uso", ["Interno", "Venda"], index=0 if not item else ["Interno", "Venda"].index(item.get("uso", "Interno")))
        categoria = st.selectbox("Categoria", ["Alimento", "Bebida", "Outros"], index=0 if not item else ["Alimento", "Bebida", "Outros"].index(item.get("categoria", "Alimento")))
        produto = st.text_input("Produto", value=item.get("produto", ""), placeholder="Ex: Vinho")
        subproduto = st.text_input("Subproduto", value=item.get("subproduto", ""), placeholder="Ex: Merlot")
        marca = st.text_input("Marca", value=item.get("marca", ""), placeholder="Ex: Miolo")
        nome_comercial = st.text_input("Nome Comercial", value=item.get("nome_comercial", ""), placeholder="Ex: Miolo Reserva 2020")
        unidade = st.selectbox("Unidade", ["Kg", "g", "ml", "un"], index=0 if not item else ["Kg", "g", "ml", "un"].index(item.get("unidade", "Kg")))
        
        if unidade in ["Kg", "un"]:
            quantidade = st.number_input("Quantidade", min_value=0, step=1, format="%d", value=item.get("quantidade", 0))
        else:
            quantidade = st.number_input("Quantidade", min_value=0.0, step=0.01, format="%.2f", value=item.get("quantidade", 0.0))
            
        valor_total = st.number_input("Valor Total (R$)", min_value=0.0, step=0.01, format="%.2f", value=item.get("valor_total", 0.0))
        
        submit = st.form_submit_button("Salvar" if not item else "Atualizar")
        
        if submit:
            return {
                "id": item.get("id", gerar_novo_id()),
                "uso": uso,
                "categoria": categoria,
                "produto": produto,
                "subproduto": subproduto,
                "marca": marca,
                "nome_comercial": nome_comercial,
                "quantidade": quantidade,
                "unidade": unidade,
                "valor_total": valor_total,
                "data_cadastro": item.get("data_cadastro", datetime.now().strftime("%d/%m/%Y %H:%M")),
                "data_atualizacao": datetime.now().strftime("%d/%m/%Y %H:%M")
            }
    return None

# Cadastro de ingredientes
if menu == "Cadastro":
    st.title("📝 Cadastro de Ingredientes")
    
    novo_item = exibir_formulario()
    
    if novo_item:
        ingredientes.append(novo_item)
        salvar_dados(ingredientes)
        st.success("✅ Ingrediente salvo com sucesso!")
        st.rerun()

# Lista completa com filtros e visualização estilo tabela
elif menu == "Lista Completa":
    st.title("📋 Lista de Ingredientes")

    # Adicionando opção de mostrar/ocultar colunas
    colunas_disponiveis = {
        "ID": "id",
        "Nome Comercial": "nome_comercial",
        "Uso": "uso",
        "Categoria": "categoria",
        "Produto": "produto",
        "Subproduto": "subproduto",
        "Marca": "marca",
        "Quantidade": "quantidade",
        "Unidade": "unidade",
        "Valor Total (R$)": "valor_total",
        "Data Cadastro": "data_cadastro",
        "Data Atualização": "data_atualizacao"
    }
    
    colunas_selecionadas = st.multiselect(
        "Selecione as colunas para exibir:",
        list(colunas_disponiveis.keys()),
        default=["ID", "Nome Comercial", "Uso", "Categoria", "Produto", "Marca", "Quantidade", "Unidade", "Valor Total (R$)"]
    )

    # Filtros
    col1, col2, col3 = st.columns(3)
    with col1:
        filtro_uso = st.selectbox("Uso", ["Todos"] + sorted(list(set(i["uso"] for i in ingredientes))))
    with col2:
        filtro_categoria = st.selectbox("Categoria", ["Todos"] + sorted(list(set(i["categoria"] for i in ingredientes))))
    with col3:
        filtro_produto = st.selectbox("Produto", ["Todos"] + sorted(list(set(i["produto"] for i in ingredientes))))

    busca = st.text_input("Buscar por nome comercial, produto ou marca:")

    # Aplicar filtros
    ingredientes_filtrados = ingredientes
    if filtro_uso != "Todos":
        ingredientes_filtrados = [i for i in ingredientes_filtrados if i["uso"] == filtro_uso]
    if filtro_categoria != "Todos":
        ingredientes_filtrados = [i for i in ingredientes_filtrados if i["categoria"] == filtro_categoria]
    if filtro_produto != "Todos":
        ingredientes_filtrados = [i for i in ingredientes_filtrados if i["produto"] == filtro_produto]
    if busca:
        ingredientes_filtrados = [
            i for i in ingredientes_filtrados
            if busca.lower() in i["nome_comercial"].lower()
            or busca.lower() in i["produto"].lower()
            or busca.lower() in i["marca"].lower()
        ]

    # Mostrar resultados como tabela
    if ingredientes_filtrados:
        # Converter para DataFrame
        df = pd.DataFrame(ingredientes_filtrados)
        
        # Selecionar e renomear colunas
        colunas_db = [colunas_disponiveis[col] for col in colunas_selecionadas]
        df = df[colunas_db]
        df = df.rename(columns={v: k for k, v in colunas_disponiveis.items()})
        
        # Formatação de valores
        if "Valor Total (R$)" in colunas_selecionadas:
            df["Valor Total (R$)"] = df["Valor Total (R$)"].apply(lambda x: f"R$ {x:,.2f}")
        
        st.dataframe(df.set_index("ID" if "ID" in colunas_selecionadas else None), 
                    use_container_width=True,
                    height=600)
        
        # Opção para exportar dados
        if st.button("📤 Exportar para CSV"):
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="⬇️ Baixar CSV",
                data=csv,
                file_name="estoque_ingredientes.csv",
                mime="text/csv"
            )
    else:
        st.info("ℹ️ Nenhum ingrediente encontrado com os filtros selecionados.")

# Edição de ingredientes
elif menu == "Editar Ingrediente":
    st.title("✏️ Editar Ingrediente")
    
    if not ingredientes:
        st.warning("⚠️ Nenhum ingrediente cadastrado para editar.")
    else:
        # Selecionar ingrediente para editar
        opcoes = {i["id"]: f"ID {i['id']} - {i.get('nome_comercial', 'Sem nome')} ({i.get('marca', 'Sem marca')})" for i in ingredientes}
        selecionado = st.selectbox("Selecione o ingrediente para editar:", list(opcoes.values()))
        
        # Encontrar o item selecionado
        id_selecionado = [k for k, v in opcoes.items() if v == selecionado][0]
        ingrediente_editar = next(i for i in ingredientes if i["id"] == id_selecionado)
        
        # Exibir formulário preenchido
        st.subheader(f"Editando: ID {ingrediente_editar['id']}")
        item_atualizado = exibir_formulario(ingrediente_editar)
        
        if item_atualizado:
            # Atualizar o item na lista
            index = next(i for i, item in enumerate(ingredientes) if item["id"] == id_selecionado)
            ingredientes[index] = item_atualizado
            salvar_dados(ingredientes)
            st.success("✅ Ingrediente atualizado com sucesso!")
            st.rerun()

# Exclusão de ingredientes
elif menu == "Excluir Ingrediente":
    st.title("❌ Excluir Ingrediente")
    
    if not ingredientes:
        st.warning("⚠️ Nenhum ingrediente cadastrado para excluir.")
    else:
        # Selecionar ingrediente para excluir
        opcoes = {i["id"]: f"ID {i['id']} - {i.get('nome_comercial', 'Sem nome')} ({i.get('marca', 'Sem marca')})" for i in ingredientes}
        selecionado = st.selectbox("Selecione o ingrediente para excluir:", list(opcoes.values()))
        
        # Encontrar o item selecionado
        id_selecionado = [k for k, v in opcoes.items() if v == selecionado][0]
        ingrediente_excluir = next(i for i in ingredientes if i["id"] == id_selecionado)
        
        # Mostrar detalhes do item selecionado de forma mais amigável
        st.subheader("Detalhes do Item Selecionado")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**ID:** {ingrediente_excluir['id']}")
            st.markdown(f"**Nome Comercial:** {ingrediente_excluir.get('nome_comercial', 'Não informado')}")
            st.markdown(f"**Produto:** {ingrediente_excluir.get('produto', 'Não informado')}")
            st.markdown(f"**Subproduto:** {ingrediente_excluir.get('subproduto', 'Não informado')}")
        
        with col2:
            st.markdown(f"**Marca:** {ingrediente_excluir.get('marca', 'Não informado')}")
            st.markdown(f"**Quantidade:** {ingrediente_excluir.get('quantidade', 0)} {ingrediente_excluir.get('unidade', '')}")
            st.markdown(f"**Valor Total:** R$ {ingrediente_excluir.get('valor_total', 0):,.2f}")
            st.markdown(f"**Data Cadastro:** {ingrediente_excluir.get('data_cadastro', 'Não informada')}")
        
        # Confirmação de exclusão
        st.error("⚠️ Atenção: Esta ação não pode ser desfeita!")
        if st.button("🗑️ Confirmar Exclusão", type="primary"):
            ingredientes = [i for i in ingredientes if i["id"] != id_selecionado]
            salvar_dados(ingredientes)
            st.success("✅ Ingrediente excluído com sucesso!")
            st.rerun()