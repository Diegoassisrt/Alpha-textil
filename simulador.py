# -*- coding: utf-8 -*-
"""
================================================================================
 SIMULADOR.PY — Simulador de Preço Avançado (Administrador e Operador)
================================================================================
"""

import streamlit as st
import plotly.graph_objects as go

from calculos import (
    calcular_embalagem_total,
    calcular_rateio_fixo_por_produto,
    obter_faixa_shopee,
    calcular_taxa_shopee_reais,
)
from estilo import formatar_moeda, PRETO, LARANJA, CINZA_CARD


def pagina_simulador():
    st.header("🧮 Simulador de Preço Avançado")
    st.markdown("Digite um preço de venda de teste para qualquer peça e veja instantaneamente o resultado.")

    if not st.session_state.produtos:
        st.info("Cadastre ao menos um produto na aba **Produtos** para usar o simulador.")
        return

    opcoes = [f"{p['codigo']} - {p['nome']}" for p in st.session_state.produtos]
    escolhido = st.selectbox("Selecione o produto:", opcoes)
    idx = opcoes.index(escolhido)
    produto = st.session_state.produtos[idx]

    embalagem_unit = calcular_embalagem_total(st.session_state.embalagens)
    rateio_fixo = calcular_rateio_fixo_por_produto(
        st.session_state.custos_fixos, len(st.session_state.produtos)
    )
    custo_total = produto["custo_fabricacao"] + embalagem_unit + rateio_fixo

    st.markdown("---")
    c1, c2 = st.columns([1, 1])
    with c1:
        st.info(
            f"**Custo Total desta peça:** {formatar_moeda(custo_total)}\n\n"
            f"(Fabricação {formatar_moeda(produto['custo_fabricacao'])} + "
            f"Embalagem {formatar_moeda(embalagem_unit)} + "
            f"Rateio Fixo {formatar_moeda(rateio_fixo)})"
        )
        preco_simulado = st.number_input(
            "💵 Digite o preço de venda de teste (R$):",
            min_value=0.0, step=1.0, value=99.90, format="%.2f",
        )

    faixa = obter_faixa_shopee(preco_simulado)
    taxa_shopee_reais = calcular_taxa_shopee_reais(preco_simulado)
    lucro_liquido = preco_simulado - custo_total - taxa_shopee_reais
    margem_real = (lucro_liquido / preco_simulado * 100) if preco_simulado > 0 else 0

    with c2:
        st.markdown(
            f"**Faixa de comissão aplicada:** {faixa['label']} "
            f"({faixa['comissao']*100:.0f}% + {formatar_moeda(faixa['fixa'])})"
        )

        m1, m2 = st.columns(2)
        m1.metric("Taxa Shopee Descontada", formatar_moeda(taxa_shopee_reais))
        m2.metric("Custo Total", formatar_moeda(custo_total))

        m3, m4 = st.columns(2)
        m3.metric("🟧 Lucro Líquido", formatar_moeda(lucro_liquido))
        m4.metric("Margem Real", f"{margem_real:.1f}%")

        if lucro_liquido < 0:
            st.error("⚠️ Atenção: com este preço a peça está dando PREJUÍZO!")
        elif margem_real < 10:
            st.warning("⚠️ Margem real abaixo de 10%. Considere revisar o preço.")
        else:
            st.success("✅ Preço saudável para esta peça.")

    st.markdown("---")
    st.subheader("Composição do Preço Simulado")
    fig = go.Figure(data=[go.Pie(
        labels=["Custo Total", "Taxa Shopee", "Lucro Líquido"],
        values=[custo_total, taxa_shopee_reais, max(lucro_liquido, 0)],
        marker_colors=[PRETO, "#8C8C8C", LARANJA],
        hole=0.45,
    )])
    fig.update_layout(paper_bgcolor=CINZA_CARD, font_color=PRETO)
    st.plotly_chart(fig, use_container_width=True)
