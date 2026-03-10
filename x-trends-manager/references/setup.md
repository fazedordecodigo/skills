# Setup de Credenciais — X API v2

## Passo a passo completo

### 1. Criar conta de desenvolvedor

1. Acesse https://developer.x.com
2. Clique em **"Sign up"** e vincule sua conta do X
3. Responda as perguntas sobre uso da API (seja honesto e direto)
4. Aguarde aprovação (geralmente imediata para o plano Free/Basic)

### 2. Criar um App

1. Acesse https://developer.x.com/en/portal/dashboard
2. Clique em **"+ Create App"** ou acesse um projeto existente
3. Dê um nome ao App (ex: "Meu Analisador de Trends")
4. Anote as credenciais geradas na primeira tela (só aparecem uma vez!)

### 3. Configurar permissões de leitura e escrita

1. No painel do App, clique em **"Settings"**
2. Em **"User authentication settings"**, clique em **"Set up"**
3. Selecione **"Read and Write"** em App permissions
4. Em "Type of App", selecione "Web App, Automated App or Bot"
5. Preencha a Callback URI (pode ser `http://localhost` para scripts locais)
6. Salve as configurações

> ⚠️ **Importante:** Se as permissões forem "Read only", o posting falhará com erro 403.
> Após alterar as permissões, **regenere** o Access Token para que as novas permissões entrem em vigor.

### 4. Obter as credenciais

Vá em **"Keys and Tokens"** no painel do App:

| Credencial | Onde encontrar | Para que serve |
|-----------|---------------|----------------|
| `X_BEARER_TOKEN` | "Bearer Token" → Generate | Leitura (trends, busca) |
| `X_API_KEY` | "Consumer Keys" → API Key | OAuth (posting) |
| `X_API_SECRET` | "Consumer Keys" → API Key Secret | OAuth (posting) |
| `X_ACCESS_TOKEN` | "Authentication Tokens" → Access Token | OAuth (posting) |
| `X_ACCESS_TOKEN_SECRET` | "Authentication Tokens" → Access Token Secret | OAuth (posting) |

### 5. Criar o arquivo `.env`

Na pasta da skill (ou do projeto), crie o arquivo `.env`:

```bash
# Opção 1: via terminal
cat > .env << 'EOF'
X_BEARER_TOKEN=
X_API_KEY=
X_API_SECRET=
X_ACCESS_TOKEN=
X_ACCESS_TOKEN_SECRET=
EOF

# Depois edite com seu editor preferido:
nano .env
# ou
code .env
```

Preencha os valores (sem aspas, sem espaços):
```
X_BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAAAOxxx...
X_API_KEY=abc123xxx...
X_API_SECRET=xyz789xxx...
X_ACCESS_TOKEN=123456789-abc...
X_ACCESS_TOKEN_SECRET=def456xxx...
```

### 6. Proteger o `.env`

```bash
# Não versionar no git
echo ".env" >> .gitignore

# Permissões restritas (Linux/Mac)
chmod 600 .env
```

### 7. Instalar dependências Python

```bash
pip install requests requests-oauthlib python-dotenv
```

Ou se usar ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate   # Windows
pip install requests requests-oauthlib python-dotenv
```

### 8. Testar a configuração

```bash
# Teste de leitura (Bearer Token)
python scripts/get_trends.py --woeid 23424762

# Teste de posting (OAuth) — dry-run não posta de fato
python scripts/post_tweet.py --text "Teste de conexão" --dry-run
```

---

## Planos disponíveis e limites

| Plano | Custo | Rate limit (busca) | Rate limit (posting) | Trends |
|-------|-------|--------------------|---------------------|--------|
| Free | $0 | 1 req/15min | 17 tweets/24h | ❌ |
| Basic | $100/mês | 60 req/15min | 100 tweets/24h | ✅ |
| Pro | $5000/mês | 450 req/15min | 1000 tweets/24h | ✅ |
| Enterprise | Sob consulta | Ilimitado | Ilimitado | ✅ |

> ⚠️ **Nota:** O endpoint de Trends requer pelo menos o plano **Basic** ($100/mês).
> Para apenas ler tweets e fazer buscas, o plano **Free** funciona com limitações severas.

---

## Erros comuns de configuração

### "401 Unauthorized"
- Token incorreto ou com espaços extras no .env
- Bearer Token expirado → regenere no Dev Portal

### "403 Forbidden" ao postar
- App configurado como "Read only" → altere para "Read and Write"
- Access Token gerado antes de mudar as permissões → **regenere** o Access Token

### "453 Access to a subset of Twitter API v2 endpoints restricted"
- Sua conta de desenvolvedor ainda não foi aprovada
- Ou o endpoint requer um plano pago (ex: Trends no Free)

### "ModuleNotFoundError: No module named 'dotenv'"
```bash
pip install python-dotenv
```

### "ModuleNotFoundError: No module named 'requests_oauthlib'"
```bash
pip install requests-oauthlib
```
