# X API v2 — Guia de Referência

## Endpoints principais

### GET Trends by WOEID

```
GET https://api.x.com/2/trends/by/woeid/{id}
```

**Autenticação:** `Authorization: Bearer $X_BEARER_TOKEN`

**Resposta:**
```json
{
  "data": [
    {"trend_name": "#IA", "tweet_count": 250000},
    {"trend_name": "ChatGPT", "tweet_count": 180000}
  ]
}
```

**Exemplo com curl:**
```bash
curl "https://api.x.com/2/trends/by/woeid/23424762" \
  -H "Authorization: Bearer $X_BEARER_TOKEN"
```

---

### GET Search Recent Tweets

```
GET https://api.x.com/2/tweets/search/recent
```

**Autenticação:** `Authorization: Bearer $X_BEARER_TOKEN`

**Parâmetros de query:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `query` | string (obrigatório) | Expressão de busca, até 512 chars |
| `max_results` | int | 10-100 (padrão: 10) |
| `tweet.fields` | string | Campos adicionais (public_metrics, author_id, etc.) |
| `start_time` | datetime | ISO 8601, busca desde essa data |
| `end_time` | datetime | ISO 8601 |

**Operadores de busca:**
```
#hashtag              → tweets com a hashtag
"frase exata"         → correspondência exata
from:usuario          → tweets de um usuário
-is:retweet           → excluir retweets
-is:reply             → excluir respostas
lang:pt               → somente em português
has:images            → com imagens
has:links             → com links
```

**Exemplo:**
```bash
curl "https://api.x.com/2/tweets/search/recent?query=%23IA%20-is%3Aretweet%20lang%3Apt&max_results=20&tweet.fields=public_metrics" \
  -H "Authorization: Bearer $X_BEARER_TOKEN"
```

**Resposta:**
```json
{
  "data": [
    {
      "id": "1234567890",
      "text": "Texto do tweet...",
      "public_metrics": {
        "retweet_count": 10,
        "like_count": 50,
        "reply_count": 5
      }
    }
  ],
  "meta": {
    "result_count": 20,
    "next_token": "abc123"
  }
}
```

---

### POST Create Tweet

```
POST https://api.x.com/2/tweets
Content-Type: application/json
```

**Autenticação:** OAuth 2.0 User Context (Bearer Token do usuário, não App-only)
- Escopos necessários: `tweet.write`, `tweet.read`, `users.read`

**Body (JSON):**
```json
{
  "text": "Seu tweet aqui (máx 280 chars)"
}
```

**Campos opcionais do body:**
| Campo | Tipo | Descrição |
|-------|------|-----------|
| `text` | string (obrigatório) | Conteúdo do tweet, máx 280 chars |
| `reply.in_reply_to_tweet_id` | string | ID para responder |
| `reply.auto_populate_reply_metadata` | boolean | Popula @menções automaticamente |
| `media.media_ids` | array | IDs de mídia (máx 4) |
| `poll.options` | array | Opções de enquete (2-4) |
| `poll.duration_minutes` | int | Duração (5-10080 min) |
| `quote_tweet_id` | string | ID para quote tweet |
| `reply_settings` | string | `following`, `mentionedUsers`, `subscribers`, `verified` |

**Resposta sucesso (201):**
```json
{
  "data": {
    "id": "1346889436626259968",
    "text": "Seu tweet aqui"
  }
}
```

**Exemplo com Python (usando requests-oauthlib):**
```python
from requests_oauthlib import OAuth1Session

oauth = OAuth1Session(
    client_key=API_KEY,
    client_secret=API_SECRET,
    resource_owner_key=ACCESS_TOKEN,
    resource_owner_secret=ACCESS_TOKEN_SECRET
)

response = oauth.post(
    "https://api.x.com/2/tweets",
    json={"text": "Hello, X!"}
)
```

---

## Autenticação OAuth 2.0 com Bearer Token

Para operações de leitura (trends, search), use App-Only Bearer Token:
```python
headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}
response = requests.get(url, headers=headers)
```

Para posting (criação de tweets), use OAuth 1.0a (mais simples para scripts CLI):
```python
# pip install requests-oauthlib
from requests_oauthlib import OAuth1Session

oauth = OAuth1Session(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
response = oauth.post("https://api.x.com/2/tweets", json=payload)
```

---

## WOEIDs — Tabela Completa

### América do Sul
| País/Cidade | WOEID |
|-------------|-------|
| Brasil | 23424762 |
| São Paulo | 455827 |
| Rio de Janeiro | 455826 |
| Brasília | 455819 |
| Belo Horizonte | 455821 |
| Argentina | 23424747 |
| Buenos Aires | 332471 |
| Chile | 23424782 |
| Santiago | 349859 |
| Colômbia | 23424787 |
| Bogotá | 368148 |

### América do Norte
| País/Cidade | WOEID |
|-------------|-------|
| EUA | 23424977 |
| Nova York | 2459115 |
| Los Angeles | 2442047 |
| Chicago | 2379574 |
| México | 23424900 |
| Cidade do México | 116545 |
| Canadá | 23424775 |

### Europa
| País/Cidade | WOEID |
|-------------|-------|
| Reino Unido | 23424975 |
| Londres | 44418 |
| Portugal | 23424925 |
| Lisboa | 2267057 |
| Espanha | 23424950 |
| Madri | 766273 |
| França | 23424819 |
| Paris | 615702 |
| Alemanha | 23424829 |

### Ásia e Oceania
| País/Cidade | WOEID |
|-------------|-------|
| Japão | 23424856 |
| Tóquio | 1118370 |
| Índia | 23424848 |
| Austrália | 23424748 |
| Sydney | 1105779 |

### Global
| Local | WOEID |
|-------|-------|
| Worldwide | 1 |

---

## Rate Limits (estimativas)

| Endpoint | Limite estimado |
|----------|----------------|
| GET /2/trends/by/woeid | 75 req/15 min (Basic) |
| GET /2/tweets/search/recent | 180 req/15 min (Basic) |
| POST /2/tweets | 100 req/24h (Basic) |

> Nota: Rate limits variam por plano (Free, Basic, Pro, Enterprise). Sempre trate o erro 429 com retry após o período indicado no header `x-rate-limit-reset`.

---

## Dependências Python

```bash
pip install requests requests-oauthlib python-dotenv
```

Ou crie um `requirements.txt`:
```
requests>=2.31.0
requests-oauthlib>=1.3.1
python-dotenv>=1.0.0
```
