# -*- coding: utf-8 -*-
"""
================================================================================
 TAXAS.PY — Regras automáticas de comissão da Shopee (Administrador)
================================================================================
"""

import streamlit as st
import pandas as pd

from calculos import FAIXAS_SHOPEE, obter_faixa_shopee, calcular_taxa_shopee_reais
from estilo import formatar_moeda


def pagina_taxas():
    st.header("⚙️ Configuração de Taxas da Shopee")
    st.markdown(
        "O sistema aplica **automaticamente** a faixa de comissão correspondente "
        "ao preço de venda calculado de cada produto. Estas são as regras vigentes:"
    )

    df_faixas = pd.DataFrame([
        {
            "Faixa de Preço": f["label"],
            "Comissão (%)": f"{f['comissao']*100:.0f}%",
            "Taxa Fixa": formatar_moeda(f["fixa"]),
        }
        for f in FAIXAS_SHOPEE
    ])
    st.dataframe(df_faixas, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("🔎 Consulta rápida de faixa")
    preco_teste = st.number_input(
        "Digite um preço para ver a faixa aplicada:", min_value=0.0, step=1.0, value=100.0
    )
    faixa = obter_faixa_shopee(preco_teste)
    taxa_reais = calcular_taxa_shopee_reais(preco_teste)

    c1, c2, c3 = st.columns(3)
    c1.metric("Faixa aplicada", faixa["label"])
    c2.metric("Comissão", f"{faixa['comissao']*100:.0f}% + {formatar_moeda(faixa['fixa'])}")
    c3.metric("Total descontado", formatar_moeda(taxa_reais))
