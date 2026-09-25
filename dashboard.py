# -*- coding: utf-8 -*-
"""
================================================================================
 DASHBOARD.PY — Painel de resultados (acesso exclusivo do Administrador)
================================================================================
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from calculos import montar_tabela_precificacao
from estilo import formatar_moeda, PALETA_GRAFICO, PRETO, LARANJA, CINZA_CARD


def pagina_dashboard():
    st.header("📊 Painel de Resultados")

    df = montar_tabela_precificacao(
        st.session_state.produtos, st.session_state.embalagens, st.session_state.custos_fixos
    )

    if df.empty:
        st.info("Nenhum produto cadastrado ainda. Vá até a aba **Produtos** para começar.")
        return

    total_pecas = len(df)
    faturamento_bruto = df["Preço Venda Sugerido"].sum()
    lucro_liquido_total = df["Lucro Líquido (R$)"].sum()
    margem_media = df["Margem Real (%)"].mean()
    custo_total_producao = df["Custo Total"].sum()
    total_taxas_shopee = df["Taxa Shopee (R$)"].sum()

    c1, c2, c3 = st.columns(3)
    c1.metric("📦 Produtos Cadastrados", f"{total_pecas}")
    c2.metric("💰 Faturamento Bruto Estimado", formatar_moeda(faturamento_bruto))
    c3.metric("🟧 Lucro Líquido Final", formatar_moeda(lucro_liquido_total))

    c4, c5, c6 = st.columns(3)
    c4.metric("📈 Margem Média Geral", f"{margem_media:.1f}%")
    c5.metric("🏭 Custo Total de Produção", formatar_moeda(custo_total_producao))
    c6.metric("🛍️ Total em Taxas Shopee", formatar_moeda(total_taxas_shopee))

    st.markdown("---")

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Margem Real por Produto")
        fig1 = px.bar(
            df, x="Produto", y="Margem Real (%)", color="Produto",
            color_discrete_sequence=PALETA_GRAFICO, text_auto=".1f",
        )
        fig1.update_layout(plot_bgcolor=CINZA_CARD, paper_bgcolor=CINZA_CARD,
                            font_color=PRETO, showlegend=False)
        fig1.update_traces(marker_line_color=PRETO, marker_line_width=1)
        st.plotly_chart(fig1, use_container_width=True)

    with col_b:
        st.subheader("Lucro Líquido por Produto (R$)")
        fig2 = px.bar(
            df, x="Produto", y="Lucro Líquido (R$)", color="Produto",
            color_discrete_sequence=PALETA_GRAFICO, text_auto=".2f",
        )
        fig2.update_layout(plot_bgcolor=CINZA_CARD, paper_bgcolor=CINZA_CARD,
                            font_color=PRETO, showlegend=False)
        fig2.update_traces(marker_line_color=PRETO, marker_line_width=1)
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Composição: Custo x Taxa Shopee x Lucro")
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(name="Custo Total", x=df["Produto"], y=df["Custo Total"], marker_color=PRETO))
    fig3.add_trace(go.Bar(name="Taxa Shopee", x=df["Produto"], y=df["Taxa Shopee (R$)"], marker_color="#8C8C8C"))
    fig3.add_trace(go.Bar(name="Lucro Líquido", x=df["Produto"], y=df["Lucro Líquido (R$)"], marker_color=LARANJA))
    fig3.update_layout(barmode="stack", plot_bgcolor=CINZA_CARD, paper_bgcolor=CINZA_CARD,
                        font_color=PRETO, legend_title_text="")
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Distribuição de Produtos por Status de Margem")
    contagem_status = df["Status"].value_counts().reset_index()
    contagem_status.columns = ["Status", "Quantidade"]
    fig4 = px.pie(
        contagem_status, names="Status", values="Quantidade", hole=0.45,
        color_discrete_sequence=PALETA_GRAFICO,
    )
    fig4.update_layout(paper_bgcolor=CINZA_CARD, font_color=PRETO)
    st.plotly_chart(fig4, use_container_width=True)
