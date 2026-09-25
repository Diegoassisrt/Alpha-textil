# -*- coding: utf-8 -*-
"""
================================================================================
 PRODUTOS.PY — Catálogo e Tabela de Precificação Inteligente
================================================================================
Acessível por Administrador e Operador/Vendedor. Colunas financeiras
sensíveis (custo total, lucro líquido em R$, taxa Shopee em R$) só são
exibidas para o perfil Administrador.
================================================================================
"""

import streamlit as st

from calculos import montar_tabela_precificacao
from estilo import formatar_moeda
from auth import PERFIL_ADMIN

# Cores de fundo por status, usadas no realce da tabela (pandas Styler)
CORES_STATUS = {
    "🔴 Prejuízo": "#FFD6D6",
    "🟡 Risco": "#FFF3CD",
    "🟢 Boa": "#D9F2D9",
    "🟧 Ótima": "#FFE0C2",
}


def _colorir_status(linha):
    cor = CORES_STATUS.get(linha["Status"], "")
    return [f"background-color: {cor}" for _ in linha]


def pagina_produtos(perfil: str):
    st.header("🛍️ Produtos e Precificação Inteligente")
    eh_admin = perfil == PERFIL_ADMIN

    # --- Formulário para adicionar novo produto ---
    with st.expander("➕ Adicionar novo produto", expanded=False):
        with st.form("form_novo_produto", clear_on_submit=True):
            c1, c2 = st.columns(2)
            codigo = c1.text_input("Código do produto")
            nome = c2.text_input("Nome do produto")
            c3, c4 = st.columns(2)
            categoria = c3.text_input("Categoria")
            custo_fab = c4.number_input("Custo de confecção/fabricação (R$)", min_value=0.0, step=0.5)
            margem = st.slider("Margem de lucro desejada (%)", min_value=1.0, max_value=90.0, value=30.0, step=0.5)

            adicionar = st.form_submit_button("Adicionar Produto", use_container_width=True)
            if adicionar:
                if codigo and nome:
                    st.session_state.produtos.append({
                        "codigo": codigo, "nome": nome,
                        "categoria": categoria or "Sem categoria",
                        "custo_fabricacao": custo_fab, "margem_desejada": margem,
                    })
                    st.success(f"Produto '{nome}' adicionado com sucesso!")
                    st.rerun()
                else:
                    st.warning("Preencha ao menos Código e Nome do produto.")

    st.markdown("---")

    if not st.session_state.produtos:
        st.info("Nenhum produto cadastrado ainda.")
        return

    df = montar_tabela_precificacao(
        st.session_state.produtos, st.session_state.embalagens, st.session_state.custos_fixos
    )

    st.subheader("📋 Catálogo de Produtos")

    if eh_admin:
        colunas_exibir = [
            "Código", "Produto", "Categoria", "Custo Total",
            "Comissão Shopee (%)", "Taxa Shopee (R$)", "Preço Venda Sugerido",
            "Lucro Líquido (R$)", "Margem Real (%)", "Status",
        ]
    else:
        # Operador/Vendedor: sem dados financeiros confidenciais (custo e lucro)
        colunas_exibir = ["Código", "Produto", "Categoria", "Preço Venda Sugerido", "Status"]
        st.caption("🔒 Como Operador/Vendedor, você visualiza apenas o catálogo e o preço de venda.")

    df_exibicao = df[colunas_exibir].copy()

    colunas_moeda = [c for c in ["Custo Total", "Taxa Shopee (R$)", "Preço Venda Sugerido", "Lucro Líquido (R$)"]
                      if c in df_exibicao.columns]
    for col in colunas_moeda:
        df_exibicao[col] = df_exibicao[col].apply(formatar_moeda)
    if "Comissão Shopee (%)" in df_exibicao.columns:
        df_exibicao["Comissão Shopee (%)"] = df_exibicao["Comissão Shopee (%)"].apply(lambda x: f"{x:.0f}%")
    if "Margem Real (%)" in df_exibicao.columns:
        df_exibicao["Margem Real (%)"] = df_exibicao["Margem Real (%)"].apply(lambda x: f"{x:.1f}%")

    # Realce de badges de cor por status (alerta visual de margem/risco)
    styler = df_exibicao.style.apply(_colorir_status, axis=1)
    st.dataframe(styler, use_container_width=True, hide_index=True)

    # --- Edição/remoção — disponível para ambos os perfis, pois faz parte do catálogo ---
    st.markdown("---")
    st.subheader("✏️ Editar ou Remover Produto")

    opcoes = [f"{p['codigo']} - {p['nome']}" for p in st.session_state.produtos]
    escolhido = st.selectbox("Selecione um produto:", opcoes)
    idx = opcoes.index(escolhido)
    produto_atual = st.session_state.produtos[idx]

    with st.form("form_editar_produto"):
        c1, c2 = st.columns(2)
        codigo_edit = c1.text_input("Código", value=produto_atual["codigo"])
        nome_edit = c2.text_input("Nome", value=produto_atual["nome"])
        c3, c4 = st.columns(2)
        categoria_edit = c3.text_input("Categoria", value=produto_atual["categoria"])
        custo_edit = c4.number_input("Custo de fabricação (R$)", min_value=0.0,
                                      value=float(produto_atual["custo_fabricacao"]), step=0.5,
                                      disabled=not eh_admin)
        margem_edit = st.slider("Margem de lucro desejada (%)", min_value=1.0, max_value=90.0,
                                 value=float(produto_atual["margem_desejada"]), step=0.5,
                                 disabled=not eh_admin)

        if not eh_admin:
            st.caption("🔒 Apenas o Administrador pode alterar custo de fabricação e margem.")

        col_salvar, col_remover = st.columns(2)
        salvar = col_salvar.form_submit_button("💾 Salvar Alterações", use_container_width=True)
        remover = col_remover.form_submit_button(
            "🗑️ Remover Produto", use_container_width=True, disabled=not eh_admin
        )

        if salvar:
            st.session_state.produtos[idx] = {
                "codigo": codigo_edit, "nome": nome_edit, "categoria": categoria_edit,
                "custo_fabricacao": custo_edit if eh_admin else produto_atual["custo_fabricacao"],
                "margem_desejada": margem_edit if eh_admin else produto_atual["margem_desejada"],
            }
            st.success("Produto atualizado!")
            st.rerun()

        if remover and eh_admin:
            st.session_state.produtos.pop(idx)
            st.success("Produto removido!")
            st.rerun()
