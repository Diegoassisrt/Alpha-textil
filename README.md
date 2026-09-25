# Manuz — Gerenciador de Precificação e Gestão (Shopee)

Aplicativo web em Streamlit com autenticação, cadastro de usuários, perfis de
acesso (Administrador / Operador-Vendedor) e precificação automática para
vendas na Shopee.

## Estrutura do projeto

```
manuz_app/
├── app.py         → ponto de entrada e roteamento por perfil
├── auth.py        → login, cadastro e segurança de senha (hash + salt)
├── calculos.py    → regras de negócio: taxas Shopee e precificação
├── estilo.py       → identidade visual (tema preto/laranja da marca)
├── dashboard.py    → painel de resultados (Administrador)
├── taxas.py        → regras de comissão Shopee (Administrador)
├── custos.py       → embalagem e custos fixos (Administrador)
├── produtos.py      → catálogo e precificação (Administrador + Operador)
├── simulador.py    → simulador de preço (Administrador + Operador)
├── requirements.txt
└── README.md
```

Importante: **mantenha todos os arquivos `.py` na mesma pasta**, pois `app.py`
importa os demais módulos diretamente (ex: `from calculos import ...`).

## Como executar localmente

1. Instale o Python 3.9 ou superior.
2. Na pasta `manuz_app`, instale as dependências:
   ```
   pip install -r requirements.txt
   ```
3. Execute:
   ```
   streamlit run app.py
   ```
4. O navegador abrirá em `http://localhost:8501`.

## Login padrão

- **Administrador**
  - E-mail: `admin@manuz.com.br`
  - Senha: `manuz2026`
- Novas contas podem ser criadas na aba **"Criar Conta"**, escolhendo o
  perfil desejado (Administrador ou Operador/Vendedor).

⚠️ Em um ambiente de produção real, recomenda-se restringir a criação de
contas com perfil "Administrador" a um fluxo controlado (ex: convite enviado
por um administrador já existente), em vez de deixar aberto no cadastro
público.

## Perfis de acesso

| Recurso | Administrador | Operador / Vendedor |
|---|---|---|
| Dashboard (faturamento, lucro total) | ✅ | ❌ |
| Configuração de Taxas Shopee | ✅ | ❌ |
| Custos de Embalagem e Fixos | ✅ | ❌ |
| Catálogo de Produtos (visão completa) | ✅ | Visão restrita (sem custo/lucro) |
| Simulador de Preço | ✅ | ✅ |

## Hospedagem gratuita (Streamlit Community Cloud)

1. Crie uma conta no [GitHub](https://github.com) (gratuita).
2. Crie um repositório e envie **todos os arquivos** desta pasta
   (`app.py`, `auth.py`, `calculos.py`, `estilo.py`, `dashboard.py`,
   `taxas.py`, `custos.py`, `produtos.py`, `simulador.py`,
   `requirements.txt`).
3. Acesse [share.streamlit.io](https://share.streamlit.io) e faça login com
   sua conta do GitHub.
4. Clique em **"New app"**, selecione o repositório e informe `app.py` como
   arquivo principal.
5. Clique em **Deploy**. Em poucos minutos você recebe um link público
   gratuito, do tipo `https://manuz-precificacao.streamlit.app`, que já
   funciona em computadores e celulares.

Qualquer atualização enviada ao repositório no GitHub é automaticamente
refletida no site publicado.

## Observação sobre persistência de dados

Este protótipo guarda usuários, produtos e custos em memória
(`st.session_state`), ou seja, os dados são perdidos ao reiniciar o servidor
ou quando o app "dorme" por inatividade no plano gratuito. Para uso real em
produção, recomenda-se conectar a um banco de dados (SQLite, PostgreSQL,
Google Sheets, Firebase, etc.) para persistir usuários e produtos de forma
definitiva — posso ajudar a implementar essa camada se for do interesse da
Manuz.
