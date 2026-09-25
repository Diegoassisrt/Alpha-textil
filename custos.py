# -*- coding: utf-8 -*-
"""
================================================================================
 CUSTOS.PY — Custos de embalagem e custos fixos mensais (Administrador)
================================================================================
"""

import streamlit as st

from calculos import calcular_embalagem_total, calcular_rateio_fixo_por_produto
from estilo import formatar_moeda


def pagina_custos():
    st.header("📦 Custos de Embalagem e Custos Fixos")

    tab_emb, tab_fixo = st.tabs(["🧾 Embalagem (por peça)", "🏠 Custos Fixos Mensais"])

    # --- EMBALAGEM ---
    with tab_emb:
        st.markdown("Informe o custo unitário de cada item de embalagem utilizado por peça.")
        embalagens = st.session_state.embalagens

        with st.form("form_embalagem"):
            novos_valores = {}
            cols = st.columns(len(embalagens))
            for col, (item, valor) in zip(cols, embalagens.items()):
                novos_valores[item] = col.number_input(
                    item, min_value=0.0, value=float(valor), step=0.05, format="%.2f"
                )
            salvar_emb = st.form_submit_button("💾 Salvar custos de embalagem")
            if salvar_emb:
                st.session_state.embalagens.update(novos_valores)
                st.success("Custos de embalagem atualizados!")
                st.rerun()

        total_embalagem = calcular_embalagem_total(st.session_state.embalagens)
        st.metric("Custo Total de Embalagem por Peça", formatar_moeda(total_embalagem))

    # --- CUSTOS FIXOS ---
    with tab_fixo:
        st.markdown("Cadastre as despesas fixas mensais da empresa (MEI, internet, etc).")

        with st.form("form_novo_custo_fixo", clear_on_submit=True):
            c1, c2, c3 = st.columns([2, 1, 1])
            nome_custo = c1.text_input("Nome da despesa")
            valor_custo = c2.number_input("Valor mensal (R$)", min_value=0.0, step=10.0)
            adicionar = c3.form_submit_button("➕ Adicionar", use_container_width=True)
            if adicionar and nome_custo:
                st.session_state.custos_fixos.append({"nome": nome_custo, "valor": valor_custo})
                st.success(f"Despesa '{nome_custo}' adicionada!")
                st.rerun()

        if st.session_state.custos_fixos:
            for i, item in enumerate(st.session_state.custos_fixos):
                c1, c2, c3 = st.columns([2, 1, 0.5])
                c1.write(item["nome"])
                c2.write(formatar_moeda(item["valor"]))
                if c3.button("🗑️", key=f"del_fixo_{i}"):
                    st.session_state.custos_fixos.pop(i)
                    st.rerun()
        else:
            st.info("Nenhuma despesa fixa cadastrada.")

        st.markdown("---")
        total_fixo = sum(item["valor"] for item in st.session_state.custos_fixos)
        qtd_produtos = len(st.session_state.produtos)
        rateio = calcular_rateio_fixo_por_produto(st.session_state.custos_fixos, qtd_produtos)

        c1, c2, c3 = st.columns(3)
        c1.metric("Total de Custos Fixos", formatar_moeda(total_fixo))
        c2.metric("Produtos Cadastrados", qtd_produtos)
        c3.metric("Rateio Fixo por Produto", formatar_moeda(rateio))
