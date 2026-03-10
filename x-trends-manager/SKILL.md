---
name: x-trends-manager
description: >
  Analisa tendências (trends) do X (Twitter) por localização e publica novos tweets baseados nas tendências.
  Use esta skill SEMPRE que o usuário quiser: ver o que está em alta no X/Twitter, analisar trends por país/cidade,
  postar ou redigir tweets, criar conteúdo baseado em tendências, monitorar hashtags populares, publicar posts no X,
  buscar tweets com métricas completas (engajamento, entidades, annotations, threads, mídia, polls, usuários),
  ou qualquer combinação dessas tarefas. Aciona também quando o usuário mencionar "trending", "trends do X",
  "twittar", "publicar no X", "o que está bombando no Twitter", "hashtag em alta", "analytics do X", ou similar.
  Esta skill inclui scripts prontos para chamar a API do X v2 e um guia para configurar credenciais via .env.
---

# X Trends Manager

Skill para analisar tendências do X (Twitter), buscar tweets com campos expandidos, e publicar novos posts via API v2.

## Setup rápido — Configure seu `.env`

**Antes de qualquer coisa**, ajude o usuário a criar um arquivo `.env` na raiz do projeto (ou na pasta da skill). Esse arquivo guarda as credenciais de forma segura:

```bash
# .env — Credenciais da API do X
# Obtenha em: https://developer.x.com/en/portal/dashboard

# Leitura (trends, busca de tweets)
X_BEARER_TOKEN=seu_bearer_token_aqui

# Posting (publicar tweets) — OAuth 1.0a
X_API_KEY=sua_consumer_key_aqui
X_API_SECRET=seu_consumer_secret_aqui
X_ACCESS_TOKEN=seu_access_token_aqui
X_ACCESS_TOKEN_SECRET=seu_access_token_secret_aqui
```

**Como criar o `.env`:**

```bash
# Na pasta da skill ou do projeto:
cat > .env << 'EOF'
X_BEARER_TOKEN=
X_API_KEY=
X_API_SECRET=
X_ACCESS_TOKEN=
X_ACCESS_TOKEN_SECRET=
EOF
```

Depois preencha os valores. Os scripts carregam o `.env` automaticamente via `python-dotenv`.

**Onde obter cada credencial:**
1. Acesse https://developer.x.com/en/portal/dashboard
2. Crie ou selecione um App
3. Em **"Keys and Tokens"**:
   - `X_BEARER_TOKEN` → "Bearer Token" (App-only, para leitura)
   - `X_API_KEY` e `X_API_SECRET` → "Consumer Keys"
   - `X_ACCESS_TOKEN` e `X_ACCESS_TOKEN_SECRET` → "Authentication Tokens" → gere com "Read and Write" permissions
4. Em **"App Settings"** → User authentication settings → configure como **"Read and Write"**

> ⚠️ **Segurança:** Nunca commite o `.env` no git. Adicione `.env` ao `.gitignore`.

---

## Fluxo geral

1. **Setup** → verificar/criar `.env` com credenciais
2. **Buscar trends** → `get_trends.py` por localização (WOEID)
3. **Analisar** → `analyze_trends.py` — categorias, volumes, insights
4. **Explorar contexto** → `search_tweets.py` — tweets com campos completos
5. **Compor tweet** → rascunho baseado nas trends, respeitar 280 chars
6. **Confirmar com usuário** → mostrar preview e pedir aprovação
7. **Publicar** → `post_tweet.py` após confirmação explícita

Consulte `references/api-guide.md` para detalhes completos de endpoints, WOEIDs e exemplos.

---

## Credenciais por operação

| Operação | Credencial necessária |
|----------|----------------------|
| Ler trends | `X_BEARER_TOKEN` |
| Buscar tweets | `X_BEARER_TOKEN` |
| Postar tweets | `X_API_KEY` + `X_API_SECRET` + `X_ACCESS_TOKEN` + `X_ACCESS_TOKEN_SECRET` |

---

## Scripts disponíveis

| Script | Propósito |
|--------|-----------|
| `scripts/get_trends.py` | Busca trends por WOEID |
| `scripts/search_tweets.py` | Busca tweets com campos expandidos |
| `scripts/post_tweet.py` | Publica tweets |
| `scripts/analyze_trends.py` | Analisa trends e gera sugestões de conteúdo |

---

## Como usar cada funcionalidade

### 1. Buscar trends

Sempre cite o WOEID explicitamente na resposta para que o usuário possa reproduzir o comando:

```bash
python scripts/get_trends.py --woeid 23424762    # Brasil (WOEID: 23424762)
python scripts/get_trends.py --woeid 1           # Worldwide (WOEID: 1)
python scripts/get_trends.py --woeid 455827      # São Paulo (WOEID: 455827)
python scripts/get_trends.py --woeid 455826      # Rio de Janeiro (WOEID: 455826)
```

**Mapeamento rápido cidade → WOEID** (mencione sempre que o usuário pedir uma cidade específica):
- "São Paulo" → `--woeid 455827`
- "Rio" / "Rio de Janeiro" → `--woeid 455826`
- "Brasil" / "Brazil" → `--woeid 23424762`
- "Mundo" / "Global" / "Worldwide" → `--woeid 1`

### 2. Analisar trends com insights de conteúdo

```bash
python scripts/analyze_trends.py --woeid 23424762 --top 10
```

Retorna: categorias temáticas, volumes, sugestões de tweet por estilo (informativo, engajamento, humor).

### 3. Buscar tweets com campos completos

A opção `--fields` permite escolher quais dados retornar:

```bash
# Busca básica
python scripts/search_tweets.py --query "#IA -is:retweet lang:pt" --max 20

# Com campos de usuário, mídia, métricas e entidades
python scripts/search_tweets.py \
  --query "#IA -is:retweet lang:pt" \
  --max 20 \
  --fields all

# Campos disponíveis (separados por vírgula):
# metrics    → retweets, likes, replies, quotes, impressions
# entities   → hashtags, mentions, urls, annotations no texto
# media      → imagens, vídeos, GIFs com metadados
# user       → perfil, follower_count, verified, description
# thread     → conversation_id para rastrear threads
# poll       → opções de enquete e contagem de votos
# all        → todos os campos acima
```

**Exemplos por caso de uso:**

```bash
# Análise de engajamento — quais tweets performam melhor
python scripts/search_tweets.py --query "ChatGPT lang:pt" --fields metrics,user --max 50

# Rastrear threads e conversas sobre um tema
python scripts/search_tweets.py --query "#Python -is:retweet" --fields thread,entities --max 30

# Buscar tweets com mídia (imagens/vídeos)
python scripts/search_tweets.py --query "inteligência artificial has:images" --fields media,metrics --max 20

# Perfis de usuários influentes em um tema
python scripts/search_tweets.py --query "machine learning from:AndrewYNg OR from:karpathy" --fields user,metrics

# Polls ativos sobre um tema
python scripts/search_tweets.py --query "votação OR enquete has:polls lang:pt" --fields poll,metrics
```

### 4. Publicar um tweet

```bash
# Tweet simples
python scripts/post_tweet.py --text "Seu tweet aqui"

# Preview antes de publicar (--dry-run)
python scripts/post_tweet.py --text "Texto do tweet" --dry-run

# Responder a um tweet
python scripts/post_tweet.py --text "Resposta..." --reply-to 1234567890

# Quote tweet
python scripts/post_tweet.py --text "Meu comentário sobre isso:" --quote 1234567890

# Tweet com restrição de replies
python scripts/post_tweet.py --text "Texto" --reply-settings following
```

---

## Campos expandidos da API v2

Ao buscar tweets, estes campos podem ser solicitados. A skill deve escolher os mais relevantes para o objetivo do usuário:

### `public_metrics` — Métricas de engajamento
```json
{
  "retweet_count": 150,
  "like_count": 1200,
  "reply_count": 45,
  "quote_count": 30,
  "impression_count": 50000,
  "bookmark_count": 80
}
```

### `entities` — Entidades no texto
```json
{
  "hashtags": [{"tag": "IA", "start": 12, "end": 15}],
  "mentions": [{"username": "OpenAI", "id": "..."}],
  "urls": [{"url": "https://t.co/...", "expanded_url": "https://..."}],
  "annotations": [
    {"type": "Organization", "normalized_text": "OpenAI", "probability": 0.98}
  ]
}
```

### `attachments` + `media` — Mídia
```json
{
  "media_keys": ["3_1234567890"],
  "media": [{
    "type": "photo",
    "url": "https://pbs.twimg.com/...",
    "width": 1200, "height": 675,
    "alt_text": "descrição da imagem"
  }]
}
```
Para vídeos: `preview_image_url`, `public_metrics.view_count`.

### `author_id` + `users` — Dados do autor
```json
{
  "id": "123456",
  "name": "Emerson",
  "username": "emerson_dev",
  "description": "Dev & Professor de IA",
  "public_metrics": {
    "followers_count": 12500,
    "following_count": 800,
    "tweet_count": 4300
  },
  "verified": false,
  "verified_type": "blue"
}
```

### `conversation_id` — Threads
```json
{
  "conversation_id": "1750000000000000000"
}
```
Use `conversation_id:XXXX -is:reply` para buscar o tweet raiz, ou `conversation_id:XXXX is:reply` para todas as respostas de uma thread.

### `attachments.poll_ids` + `polls` — Enquetes
```json
{
  "id": "poll_id",
  "options": [
    {"position": 1, "label": "Python", "votes": 1823},
    {"position": 2, "label": "JavaScript", "votes": 945}
  ],
  "duration_minutes": 1440,
  "end_datetime": "2026-03-10T20:00:00Z",
  "voting_status": "closed"
}
```

---

## Workflow recomendado para conteúdo baseado em trends

1. `analyze_trends.py` para o WOEID desejado
2. Identificar a trend mais alinhada ao nicho do usuário
3. `search_tweets.py` com `--fields metrics,user,entities` para entender o contexto
4. Observar: quais ângulos têm mais engajamento? Quem são os influenciadores?
5. Compor 2-3 opções de tweet (estilos: informativo / pergunta / opinião forte)
6. Verificar 280 chars e mostrar preview ao usuário
7. **Aguardar aprovação explícita** antes de qualquer `post_tweet.py`

> ⚠️ **Regra de ouro:** Sempre mostre o tweet e peça confirmação antes de publicar.

---

## Boas práticas para tweets

- **280 chars**: verifique sempre; URLs contam como 23 chars
- **Hashtags**: 1-3 no máximo — mais reduz engajamento
- **Timing**: trends têm janelas curtas, aja rapidamente
- **Originalidade**: não copie tweets; traga um ângulo próprio
- **CTA**: perguntas geram mais replies; números geram mais RTs

---

## WOEIDs principais

| Local | WOEID | | Local | WOEID |
|-------|-------|---|-------|-------|
| Worldwide | 1 | | EUA | 23424977 |
| Brasil | 23424762 | | Reino Unido | 23424975 |
| São Paulo | 455827 | | Portugal | 23424925 |
| Rio de Janeiro | 455826 | | Espanha | 23424950 |
| Brasília | 455819 | | Japão | 23424856 |

Tabela completa em `references/api-guide.md`.

---

## Tratamento de erros

| Erro HTTP | Significado | Ação recomendada |
|-----------|-------------|-----------------|
| 401 | Token inválido/expirado | Verificar `.env` e regenerar credenciais |
| 403 | Sem permissão de escrita | Verificar "Read and Write" no Dev Portal |
| 429 | Rate limit atingido | Informar usuário e aguardar reset |
| 503 | API indisponível | Tentar novamente em 1-2 minutos |

Nunca exponha o erro bruto — sempre traduza para uma mensagem acionável em português.
