# Alpha Têxtil — Gerenciador de Precificação Shopee

## Como rodar

1. Instale o Python 3.9+ na sua máquina.
2. No terminal, dentro da pasta do projeto, instale as dependências:
   ```
   pip install -r requirements.txt
   ```
3. Execute o aplicativo:
   ```
   streamlit run app.py
   ```
4. O navegador abrirá automaticamente em `http://localhost:8501`.

## Login padrão

- **Usuário:** admin
- **Senha:** alpha2026

Você pode alterar essas credenciais diretamente no início do arquivo `app.py`,
nas constantes `USUARIO_PADRAO` e `SENHA_PADRAO`.

## Observação sobre os dados

Este protótipo guarda os dados em memória (`st.session_state`), ou seja,
produtos, custos e taxas cadastrados são perdidos ao fechar o navegador ou
reiniciar o servidor. Para uso em produção, recomenda-se conectar o app a um
banco de dados (SQLite, PostgreSQL, Google Sheets, etc.) — posso te ajudar a
implementar essa persistência se quiser evoluir o projeto.
