# -*- coding: utf-8 -*-
"""
================================================================================
 ALPHA TEXIL — GERENCIADOR DE PRECIFICAÇÃO E GESTÃO PARA SHOPEE
================================================================================
Aplicativo web em Streamlit com autenticação, cadastro de usuários e
perfis de acesso (Administrador / Operador-Vendedor).

Como executar:
    1. pip install -r requirements.txt
    2. streamlit run app.py

Login padrão (Administrador):
    e-mail: admin@alphatextil.com.br
    senha:  alpha2026

Estrutura modular:
    app.py        -> ponto de entrada e roteamento por perfil
    auth.py       -> autenticação, cadastro e segurança de senha
    calculos.py   -> regras de negócio (taxas Shopee e precificação)
    estilo.py     -> identidade visual (tema preto/laranja)
    dashboard.py  -> painel de resultados (Administrador)
    taxas.py      -> regras de comissão Shopee (Administrador)
    custos.py     -> embalagem e custos fixos (Administrador)
    produtos.py   -> catálogo e precificação (Administrador + Operador)
    simulador.py  -> simulador de preço (Administrador + Operador)
================================================================================
"""

import streamlit as st

from estilo import aplicar_estilo
from auth import inicializar_usuarios, tela_autenticacao, PERFIL_ADMIN

from dashboard import pagina_dashboard
from taxas import pagina_taxas
from custos import pagina_custos
from produtos import pagina_produtos
from simulador import pagina_simulador


st.set_page_config(
    page_title="Manuz | Gerenciador de Precificação",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)
aplicar_estilo()


# ------------------------------------------------------------------------------
# ESTADO INICIAL DE DADOS DE NEGÓCIO (produtos, embalagens, custos fixos)
# ------------------------------------------------------------------------------

def inicializar_dados_negocio():
    if "produtos" not in st.session_state:
        st.session_state.produtos = [
            {"codigo": "MZ001", "nome": "Camiseta Básica Algodão", "categoria": "Camisetas",
             "custo_fabricacao": 18.50, "margem_desejada": 30.0},
            {"codigo": "MZ002", "nome": "Moletom Canguru", "categoria": "Moletons",
             "custo_fabricacao": 45.00, "margem_desejada": 25.0},
            {"codigo": "MZ003", "nome": "Legging Fitness", "categoria": "Fitness",
             "custo_fabricacao": 22.00, "margem_desejada": 35.0},
        ]

    if "embalagens" not in st.session_state:
        st.session_state.embalagens = {
            "Saco plástico": 0.35,
            "Saco de envio": 0.60,
            "Etiqueta": 0.15,
            "Fita": 0.10,
            "Tag": 0.20,
        }

    if "custos_fixos" not in st.session_state:
        st.session_state.custos_fixos = [
            {"nome": "MEI", "valor": 76.00},
            {"nome": "Internet", "valor": 100.00},
        ]


# ------------------------------------------------------------------------------
# PAINEL PRINCIPAL (pós-login) COM ROTEAMENTO POR PERFIL
# ------------------------------------------------------------------------------

def painel_principal():
    usuario = st.session_state.usuario_logado
    eh_admin = usuario["perfil"] == PERFIL_ADMIN

    st.markdown(
        f"""
        <div class="manuz-header">
            <h1>🏭 MANUZ</h1>
            <p>Gestão e Precificação — Vendas Shopee</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown("## 🏭 MANUZ")
        st.markdown(f"**{usuario['nome']}**")
        st.markdown(f"<span class='badge-perfil'>{usuario['perfil']}</span>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown(f"**Produtos cadastrados:** {len(st.session_state.produtos)}")
        st.markdown("---")
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.usuario_logado = None
            st.rerun()

    # Roteamento de abas conforme o perfil do usuário logado
    if eh_admin:
        abas = st.tabs(["📊 Dashboard", "⚙️ Taxas Shopee", "📦 Custos", "🛍️ Produtos", "🧮 Simulador"])
        with abas[0]:
            pagina_dashboard()
        with abas[1]:
            pagina_taxas()
        with abas[2]:
            pagina_custos()
        with abas[3]:
            pagina_produtos(usuario["perfil"])
        with abas[4]:
            pagina_simulador()
    else:
        st.info(
            "🔒 Perfil **Operador/Vendedor** — acesso restrito ao Catálogo de "
            "Produtos e ao Simulador de Preços. Dados financeiros consolidados "
            "são visíveis apenas para Administradores."
        )
        abas = st.tabs(["🛍️ Produtos", "🧮 Simulador"])
        with abas[0]:
            pagina_produtos(usuario["perfil"])
        with abas[1]:
            pagina_simulador()


# ------------------------------------------------------------------------------
# PONTO DE ENTRADA
# ------------------------------------------------------------------------------

def main():
    inicializar_usuarios()
    inicializar_dados_negocio()

    if st.session_state.usuario_logado is None:
        tela_autenticacao()
    else:
        painel_principal()


if __name__ == "__main__":
    main()
