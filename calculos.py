# -*- coding: utf-8 -*-
"""
================================================================================
 CALCULOS.PY — Regras de negócio: taxas Shopee, custos e precificação
================================================================================
Todas as funções aqui são puras (recebem dados e devolvem resultados),
o que facilita testes e evita acoplamento com o session_state do Streamlit.
================================================================================
"""

import pandas as pd

# ------------------------------------------------------------------------------
# FAIXAS OFICIAIS DE COMISSÃO + TAXA FIXA DA SHOPEE
# ------------------------------------------------------------------------------
FAIXAS_SHOPEE = [
    {"min": 0.00, "max": 79.99, "comissao": 0.20, "fixa": 4.50, "label": "Até R$ 79,99"},
    {"min": 80.00, "max": 99.99, "comissao": 0.14, "fixa": 16.00, "label": "R$ 80,00 a R$ 99,99"},
    {"min": 100.00, "max": 199.99, "comissao": 0.14, "fixa": 20.00, "label": "R$ 100,00 a R$ 199,99"},
    {"min": 200.00, "max": float("inf"), "comissao": 0.14, "fixa": 26.00, "label": "Acima de R$ 200,00"},
]


def obter_faixa_shopee(preco: float) -> dict:
    """Retorna a faixa de comissão da Shopee correspondente ao preço informado."""
    for faixa in FAIXAS_SHOPEE:
        if faixa["min"] <= preco <= faixa["max"]:
            return faixa
    return FAIXAS_SHOPEE[-1]


def calcular_taxa_shopee_reais(preco: float) -> float:
    """Calcula o valor em R$ descontado pela Shopee para um dado preço de venda."""
    faixa = obter_faixa_shopee(preco)
    return (preco * faixa["comissao"]) + faixa["fixa"]


def calcular_embalagem_total(embalagens: dict) -> float:
    """Soma todos os custos unitários de embalagem cadastrados."""
    return sum(embalagens.values())


def calcular_rateio_fixo_por_produto(custos_fixos: list, qtd_produtos: int) -> float:
    """Divide o total de custos fixos mensais pela quantidade de produtos cadastrados."""
    total_fixo = sum(item["valor"] for item in custos_fixos)
    if qtd_produtos == 0:
        return 0.0
    return total_fixo / qtd_produtos


def calcular_preco_venda_sugerido(custo_total: float, margem_desejada_pct: float):
    """
    Calcula o preço de venda sugerido usando o cálculo matemático inverso "por dentro",
    garantindo que a margem de lucro desejada seja limpa após os descontos da Shopee.

        Preço = (Custo Total + Taxa Fixa) / (1 - % Taxa Shopee - % Margem Desejada)

    Como a faixa de taxa depende do próprio preço (é escalonada), testamos cada
    faixa e validamos se o preço resultante realmente pertence a ela — isso evita
    o erro clássico de calcular com a comissão errada.

    Retorna: (preco_sugerido, comissao_pct, taxa_fixa)
    """
    margem = margem_desejada_pct / 100
    candidatos_validos = []

    for faixa in FAIXAS_SHOPEE:
        denominador = 1 - faixa["comissao"] - margem
        if denominador <= 0:
            continue  # combinação de margem + comissão inviável nesta faixa
        preco_calculado = (custo_total + faixa["fixa"]) / denominador
        if faixa["min"] <= preco_calculado <= faixa["max"]:
            candidatos_validos.append((preco_calculado, faixa["comissao"], faixa["fixa"]))

    if candidatos_validos:
        candidatos_validos.sort(key=lambda x: x[0])
        return candidatos_validos[0]

    # Fallback de segurança: usa a última faixa se nenhuma bateu perfeitamente
    faixa = FAIXAS_SHOPEE[-1]
    denominador = max(1 - faixa["comissao"] - margem, 0.01)
    preco_calculado = (custo_total + faixa["fixa"]) / denominador
    return preco_calculado, faixa["comissao"], faixa["fixa"]


def status_margem(margem_real_pct: float) -> str:
    """Classifica a margem real em um badge textual para alertas visuais na tabela."""
    if margem_real_pct < 0:
        return "🔴 Prejuízo"
    elif margem_real_pct < 10:
        return "🟡 Risco"
    elif margem_real_pct < 20:
        return "🟢 Boa"
    else:
        return "🟧 Ótima"


def montar_tabela_precificacao(produtos: list, embalagens: dict, custos_fixos: list) -> pd.DataFrame:
    """
    Monta o DataFrame completo com todos os cálculos de custo, taxa, preço e
    lucro de cada produto cadastrado. Função central usada por todas as páginas.
    """
    embalagem_unit = calcular_embalagem_total(embalagens)
    rateio_fixo = calcular_rateio_fixo_por_produto(custos_fixos, len(produtos))

    linhas = []
    for p in produtos:
        custo_total = p["custo_fabricacao"] + embalagem_unit + rateio_fixo

        preco_sugerido, comissao_pct, taxa_fixa = calcular_preco_venda_sugerido(
            custo_total, p["margem_desejada"]
        )

        taxa_shopee_reais = calcular_taxa_shopee_reais(preco_sugerido)
        lucro_liquido = preco_sugerido - custo_total - taxa_shopee_reais
        margem_real = (lucro_liquido / preco_sugerido * 100) if preco_sugerido > 0 else 0

        linhas.append({
            "Código": p["codigo"],
            "Produto": p["nome"],
            "Categoria": p["categoria"],
            "Custo Fabricação": p["custo_fabricacao"],
            "Embalagem": embalagem_unit,
            "Rateio Fixo": rateio_fixo,
            "Custo Total": custo_total,
            "Margem Desejada (%)": p["margem_desejada"],
            "Comissão Shopee (%)": comissao_pct * 100,
            "Taxa Fixa Shopee": taxa_fixa,
            "Taxa Shopee (R$)": taxa_shopee_reais,
            "Preço Venda Sugerido": preco_sugerido,
            "Lucro Líquido (R$)": lucro_liquido,
            "Margem Real (%)": margem_real,
            "Status": status_margem(margem_real),
        })

    return pd.DataFrame(linhas)
