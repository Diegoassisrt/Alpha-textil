# -*- coding: utf-8 -*-
"""
================================================================================
 AUTH.PY — Autenticação, cadastro e controle de perfis de usuário
================================================================================
Implementa login/cadastro com senha protegida por hash (PBKDF2-HMAC-SHA256 +
salt individual por usuário), sem depender de bibliotecas externas.

Perfis suportados:
    - Administrador       -> acesso total (financeiro, custos, taxas, produtos)
    - Operador / Vendedor -> acesso restrito (apenas Produtos e Simulador)
================================================================================
"""

import hashlib
import secrets
import re
import streamlit as st

PERFIL_ADMIN = "Administrador"
PERFIL_OPERADOR = "Operador / Vendedor"
PERFIS_DISPONIVEIS = [PERFIL_ADMIN, PERFIL_OPERADOR]

EMAIL_ADMIN_PADRAO = "admin@manuz.com.br"
SENHA_ADMIN_PADRAO = "manuz2026"


# ------------------------------------------------------------------------------
# SEGURANÇA DE SENHA
# ------------------------------------------------------------------------------

def gerar_hash_senha(senha: str, salt: str = None):
    """Gera um hash seguro (PBKDF2-HMAC-SHA256, 100k iterações) para a senha."""
    if salt is None:
        salt = secrets.token_hex(16)
    hash_senha = hashlib.pbkdf2_hmac(
        "sha256", senha.encode("utf-8"), salt.encode("utf-8"), 100_000
    ).hex()
    return hash_senha, salt


def verificar_senha(senha_digitada: str, hash_salvo: str, salt: str) -> bool:
    """Confere se a senha digitada corresponde ao hash armazenado."""
    novo_hash, _ = gerar_hash_senha(senha_digitada, salt)
    return novo_hash == hash_salvo


def email_valido(email: str) -> bool:
    return re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email) is not None


# ------------------------------------------------------------------------------
# ESTADO INICIAL — BASE DE USUÁRIOS EM MEMÓRIA
# ------------------------------------------------------------------------------

def inicializar_usuarios():
    """Cria a base de usuários no session_state com um Administrador padrão."""
    if "usuarios" not in st.session_state:
        hash_senha, salt = gerar_hash_senha(SENHA_ADMIN_PADRAO)
        st.session_state.usuarios = [
            {
                "nome": "Administrador Manuz",
                "email": EMAIL_ADMIN_PADRAO,
                "senha_hash": hash_senha,
                "salt": salt,
                "perfil": PERFIL_ADMIN,
            }
        ]
    if "usuario_logado" not in st.session_state:
        st.session_state.usuario_logado = None


# ------------------------------------------------------------------------------
# CADASTRO E LOGIN
# ------------------------------------------------------------------------------

def cadastrar_usuario(nome: str, email: str, senha: str, confirmar_senha: str, perfil: str):
    """Valida os dados e cadastra um novo usuário. Retorna (sucesso: bool, mensagem: str)."""
    if not nome or not email or not senha:
        return False, "Preencha todos os campos obrigatórios."
    if not email_valido(email):
        return False, "Informe um e-mail válido."
    if len(senha) < 6:
        return False, "A senha deve ter pelo menos 6 caracteres."
    if senha != confirmar_senha:
        return False, "As senhas não coincidem."
    if any(u["email"].lower() == email.lower() for u in st.session_state.usuarios):
        return False, "Já existe um usuário cadastrado com este e-mail."

    hash_senha, salt = gerar_hash_senha(senha)
    st.session_state.usuarios.append({
        "nome": nome,
        "email": email,
        "senha_hash": hash_senha,
        "salt": salt,
        "perfil": perfil,
    })
    return True, "Conta criada com sucesso! Faça login para continuar."


def autenticar_usuario(email: str, senha: str):
    """Retorna o dicionário do usuário se as credenciais forem válidas, senão None."""
    for usuario in st.session_state.usuarios:
        if usuario["email"].lower() == email.lower():
            if verificar_senha(senha, usuario["senha_hash"], usuario["salt"]):
                return usuario
            return None
    return None


# ------------------------------------------------------------------------------
# TELA DE AUTENTICAÇÃO (LOGIN + CADASTRO)
# ------------------------------------------------------------------------------

def tela_autenticacao():
    """Renderiza as abas 'Entrar' e 'Criar Conta'. Libera o painel após login válido."""
    col1, col2, col3 = st.columns([1, 1.3, 1])
    with col2:
        st.markdown(
            """
            <div style="text-align:center; margin-top:40px; margin-bottom:10px;">
                <h1 style="font-size:34px;">🏭 MANUZ</h1>
                <p style="color:#333;">Gestão e Precificação para Shopee</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        aba_login, aba_cadastro = st.tabs(["🔐 Entrar", "🆕 Criar Conta"])

        # --- ABA DE LOGIN ---
        with aba_login:
            with st.form("form_login"):
                email = st.text_input("E-mail")
                senha = st.text_input("Senha", type="password")
                entrar = st.form_submit_button("Entrar", use_container_width=True)

                if entrar:
                    usuario = autenticar_usuario(email, senha)
                    if usuario:
                        st.session_state.usuario_logado = usuario
                        st.rerun()
                    else:
                        st.error("E-mail ou senha inválidos.")

            st.caption(
                f"Acesso demonstrativo — usuário: `{EMAIL_ADMIN_PADRAO}` "
                f"/ senha: `{SENHA_ADMIN_PADRAO}`"
            )

        # --- ABA DE CADASTRO ---
        with aba_cadastro:
            with st.form("form_cadastro", clear_on_submit=True):
                nome = st.text_input("Nome completo")
                email_novo = st.text_input("E-mail")
                perfil = st.selectbox("Tipo de perfil", PERFIS_DISPONIVEIS)
                senha_nova = st.text_input("Senha", type="password")
                confirmar = st.text_input("Confirmar senha", type="password")
                criar = st.form_submit_button("Criar conta", use_container_width=True)

                if criar:
                    sucesso, mensagem = cadastrar_usuario(nome, email_novo, senha_nova, confirmar, perfil)
                    if sucesso:
                        st.success(mensagem)
                    else:
                        st.warning(mensagem)

            st.caption(
                "⚠️ Em produção, recomenda-se que apenas Administradores possam "
                "atribuir o perfil 'Administrador' a novos usuários."
            )
