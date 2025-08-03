import streamlit as st
import json
import os
import uuid
import pandas as pd

DB_FILE = "ingredientes_db.json"

# Função para carregar dados
def carregar_dados():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
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
                "id": item.get("id", str(uuid.uuid4())),
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
    return None

# Cadastro de ingredientes
if menu == "Cadastro":
    st.title("Cadastro de Ingredientes")
    
    novo_item = exibir_formulario()
    
    if novo_item:
        ingredientes.append(novo_item)
        salvar_dados(ingredientes)
        st.success("Ingrediente salvo com sucesso!")
        st.experimental_rerun()

# Lista completa com filtros e visualização estilo tabela
elif menu == "Lista Completa":
    st.title("Lista de Ingredientes")

    # Filtros
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        filtro_uso = st.selectbox("Uso", ["Todos"] + sorted(list(set(i["uso"] for i in ingredientes))))
    with col2:
        filtro_categoria = st.selectbox("Categoria", ["Todos"] + sorted(list(set(i["categoria"] for i in ingredientes))))
    with col3:
        filtro_produto = st.selectbox("Produto", ["Todos"] + sorted(list(set(i["produto"] for i in ingredientes))))
    with col4:
        filtro_subproduto = st.selectbox("Subproduto", ["Todos"] + sorted(list(set(i["subproduto"] for i in ingredientes if i["subproduto"] != ""))))
    with col5:
        filtro_marca = st.selectbox("Marca", ["Todos"] + sorted(list(set(i["marca"] for i in ingredientes if i["marca"] != ""))))

    busca = st.text_input("Buscar por nome comercial, produto ou marca:")

    # Aplicar filtros
    ingredientes_filtrados = ingredientes
    if filtro_uso != "Todos":
        ingredientes_filtrados = [i for i in ingredientes_filtrados if i["uso"] == filtro_uso]
    if filtro_categoria != "Todos":
        ingredientes_filtrados = [i for i in ingredientes_filtrados if i["categoria"] == filtro_categoria]
    if filtro_produto != "Todos":
        ingredientes_filtrados = [i for i in ingredientes_filtrados if i["produto"] == filtro_produto]
    if filtro_subproduto != "Todos":
        ingredientes_filtrados = [i for i in ingredientes_filtrados if i["subproduto"] == filtro_subproduto]
    if filtro_marca != "Todos":
        ingredientes_filtrados = [i for i in ingredientes_filtrados if i["marca"] == filtro_marca]
    if busca:
        ingredientes_filtrados = [
            i for i in ingredientes_filtrados
            if busca.lower() in i["nome_comercial"].lower()
            or busca.lower() in i["produto"].lower()
            or busca.lower() in i["marca"].lower()
        ]

    # Mostrar resultados como tabela (estilo Excel)
    if ingredientes_filtrados:
        df = pd.DataFrame(ingredientes_filtrados)
        df = df[["id", "nome_comercial", "uso", "categoria", "produto", "subproduto", "marca", "quantidade", "unidade", "valor_total"]]
        df = df.rename(columns={
            "id": "ID",
            "nome_comercial": "Nome Comercial",
            "uso": "Uso",
            "categoria": "Categoria",
            "produto": "Produto",
            "subproduto": "Subproduto",
            "marca": "Marca",
            "quantidade": "Quantidade",
            "unidade": "Unidade",
            "valor_total": "Valor Total (R$)"
        })
        st.dataframe(df.set_index("ID"), use_container_width=True)
    else:
        st.info("Nenhum ingrediente encontrado com os filtros selecionados.")

# Edição de ingredientes
elif menu == "Editar Ingrediente":
    st.title("Editar Ingrediente")
    
    if not ingredientes:
        st.warning("Nenhum ingrediente cadastrado para editar.")
    else:
        # Selecionar ingrediente para editar
        opcoes = [f"{i['nome_comercial']} ({i['marca']}) - {i['produto']}" for i in ingredientes]
        selecionado = st.selectbox("Selecione o ingrediente para editar:", opcoes)
        index_selecionado = opcoes.index(selecionado)
        ingrediente_editar = ingredientes[index_selecionado]
        
        # Exibir formulário preenchido
        item_atualizado = exibir_formulario(ingrediente_editar)
        
        if item_atualizado:
            ingredientes[index_selecionado] = item_atualizado
            salvar_dados(ingredientes)
            st.success("Ingrediente atualizado com sucesso!")
            st.experimental_rerun()

# Exclusão de ingredientes
elif menu == "Excluir Ingrediente":
    st.title("Excluir Ingrediente")
    
    if not ingredientes:
        st.warning("Nenhum ingrediente cadastrado para excluir.")
    else:
        # Selecionar ingrediente para excluir
        opcoes = [f"{i['nome_comercial']} ({i['marca']}) - {i['produto']}" for i in ingredientes]
        selecionado = st.selectbox("Selecione o ingrediente para excluir:", opcoes)
        index_selecionado = opcoes.index(selecionado)
        
        # Mostrar detalhes do item selecionado
        st.write("Detalhes do item selecionado:")
        st.json(ingredientes[index_selecionado])
        
        # Confirmação de exclusão
        if st.button("Confirmar Exclusão"):
            del ingredientes[index_selecionado]
            salvar_dados(ingredientes)
            st.success("Ingrediente excluído com sucesso!")
            st.experimental_rerun()