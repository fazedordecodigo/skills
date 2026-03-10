#!/usr/bin/env python3
"""
Busca tweets recentes com suporte a campos expandidos da API X v2.
Últimos 7 dias. Suporta métricas, entidades, mídia, usuário, threads e polls.

Uso básico:
  python search_tweets.py --query "#IA -is:retweet lang:pt" --max 20

Com campos expandidos:
  python search_tweets.py --query "#IA" --fields all --max 20
  python search_tweets.py --query "ChatGPT" --fields metrics,user --max 30
  python search_tweets.py --query "has:polls lang:pt" --fields poll,metrics --max 10

Campos disponíveis (--fields):
  metrics   → retweets, likes, replies, quotes, impressions, bookmarks
  entities  → hashtags, mentions, urls, annotations no texto
  media     → imagens, vídeos, GIFs com metadados
  user      → perfil do autor, followers, verified
  thread    → conversation_id para rastrear threads
  poll      → opções de enquete e votos
  all       → todos os campos acima
"""

import argparse
import json
import os
import sys

try:
    import requests
except ImportError:
    print("❌ Instale as dependências: pip install requests python-dotenv")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# Mapeamento de campo → parâmetros da API
FIELD_CONFIG = {
    "metrics": {
        "tweet.fields": ["public_metrics"],
    },
    "entities": {
        "tweet.fields": ["entities"],
    },
    "media": {
        "tweet.fields": ["attachments"],
        "expansions": ["attachments.media_keys"],
        "media.fields": ["type", "url", "preview_image_url", "width", "height",
                         "alt_text", "public_metrics"],
    },
    "user": {
        "tweet.fields": ["author_id"],
        "expansions": ["author_id"],
        "user.fields": ["name", "username", "description", "verified",
                        "verified_type", "public_metrics", "profile_image_url"],
    },
    "thread": {
        "tweet.fields": ["conversation_id", "in_reply_to_user_id"],
    },
    "poll": {
        "tweet.fields": ["attachments"],
        "expansions": ["attachments.poll_ids"],
        "poll.fields": ["options", "duration_minutes", "end_datetime",
                        "voting_status"],
    },
}

ALL_FIELDS = list(FIELD_CONFIG.keys())


def build_params(query: str, max_results: int, fields_requested: list[str]) -> dict:
    """Monta os parâmetros da requisição com base nos campos solicitados."""
    tweet_fields = {"id", "text", "created_at"}
    expansions = set()
    media_fields = set()
    user_fields = set()
    poll_fields = set()

    for field in fields_requested:
        cfg = FIELD_CONFIG.get(field, {})
        tweet_fields.update(cfg.get("tweet.fields", []))
        expansions.update(cfg.get("expansions", []))
        media_fields.update(cfg.get("media.fields", []))
        user_fields.update(cfg.get("user.fields", []))
        poll_fields.update(cfg.get("poll.fields", []))

    params = {
        "query": query,
        "max_results": min(max(max_results, 10), 100),
        "tweet.fields": ",".join(sorted(tweet_fields)),
    }
    if expansions:
        params["expansions"] = ",".join(sorted(expansions))
    if media_fields:
        params["media.fields"] = ",".join(sorted(media_fields))
    if user_fields:
        params["user.fields"] = ",".join(sorted(user_fields))
    if poll_fields:
        params["poll.fields"] = ",".join(sorted(poll_fields))

    return params


def search_tweets(query: str, max_results: int, bearer_token: str,
                  fields: list[str]) -> dict:
    """Executa a busca na API."""
    url = "https://api.x.com/2/tweets/search/recent"
    params = build_params(query, max_results, fields)
    headers = {"Authorization": f"Bearer {bearer_token}"}

    response = requests.get(url, headers=headers, params=params, timeout=15)

    if response.status_code == 400:
        err = response.json()
        print(f"❌ Query inválida: {err.get('detail', response.text)}")
        print("   Dicas de sintaxe:")
        print("   - Hashtag: #IA")
        print("   - Sem retweets: -is:retweet")
        print("   - Idioma: lang:pt")
        print("   - Com mídia: has:images")
        print("   - De usuário: from:elonmusk")
        sys.exit(1)
    elif response.status_code == 401:
        print("❌ Bearer Token inválido. Verifique X_BEARER_TOKEN no .env")
        sys.exit(1)
    elif response.status_code == 429:
        reset = response.headers.get("x-rate-limit-reset", "desconhecido")
        print(f"⏳ Rate limit atingido. Tente após o timestamp Unix: {reset}")
        sys.exit(1)
    elif response.status_code != 200:
        print(f"❌ Erro {response.status_code}: {response.text}")
        sys.exit(1)

    return response.json()


def build_lookup_maps(data: dict) -> tuple[dict, dict, dict]:
    """Constrói mapas de lookup para includes (users, media, polls)."""
    includes = data.get("includes", {})

    users = {u["id"]: u for u in includes.get("users", [])}
    media = {m["media_key"]: m for m in includes.get("media", [])}
    polls = {p["id"]: p for p in includes.get("polls", [])}

    return users, media, polls


def format_user(user: dict) -> str:
    """Formata dados do usuário de forma compacta."""
    if not user:
        return ""
    name = user.get("name", "")
    username = user.get("username", "")
    metrics = user.get("public_metrics", {})
    followers = metrics.get("followers_count", 0)
    verified = user.get("verified", False)
    v_type = user.get("verified_type", "")

    badge = ""
    if v_type == "blue":
        badge = " ✓"
    elif verified:
        badge = " ✓"

    return f"@{username}{badge} ({name}) | {followers:,} seguidores"


def format_media(media_list: list) -> str:
    """Formata lista de mídias."""
    if not media_list:
        return ""
    parts = []
    for m in media_list:
        t = m.get("type", "unknown")
        icon = {"photo": "🖼️", "video": "🎥", "animated_gif": "🎞️"}.get(t, "📎")
        dims = f" {m.get('width')}x{m.get('height')}" if m.get("width") else ""
        url = m.get("url") or m.get("preview_image_url", "")
        view_count = m.get("public_metrics", {}).get("view_count")
        views = f" | {view_count:,} views" if view_count else ""
        alt = f' | alt: "{m.get("alt_text")}"' if m.get("alt_text") else ""
        parts.append(f"{icon} {t}{dims}{views}{alt}")
        if url:
            parts.append(f"     🔗 {url}")
    return "\n    ".join(parts)


def format_entities(entities: dict) -> str:
    """Formata entidades extraídas do tweet."""
    if not entities:
        return ""
    parts = []
    if entities.get("hashtags"):
        tags = " ".join(f"#{h['tag']}" for h in entities["hashtags"])
        parts.append(f"#️⃣ {tags}")
    if entities.get("mentions"):
        mentions = " ".join(f"@{m['username']}" for m in entities["mentions"])
        parts.append(f"👤 {mentions}")
    if entities.get("annotations"):
        anns = ", ".join(
            f"{a['normalized_text']} [{a['type']}, {a.get('probability', 0):.0%}]"
            for a in entities["annotations"][:3]
        )
        parts.append(f"🏷️  {anns}")
    if entities.get("urls"):
        for u in entities["urls"][:2]:
            exp = u.get("expanded_url", u.get("url", ""))
            if "t.co" not in exp:
                parts.append(f"🔗 {exp}")
    return " | ".join(parts) if parts else ""


def format_poll(poll: dict) -> str:
    """Formata dados de enquete."""
    if not poll:
        return ""
    total_votes = sum(o.get("votes", 0) for o in poll.get("options", []))
    status = poll.get("voting_status", "unknown")
    duration = poll.get("duration_minutes", 0)
    lines = [f"📊 Enquete ({status}) | {total_votes:,} votos | {duration//60}h duração"]
    for opt in poll.get("options", []):
        votes = opt.get("votes", 0)
        pct = votes / total_votes * 100 if total_votes > 0 else 0
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        lines.append(f"   {opt['label']}: {bar} {pct:.1f}% ({votes:,})")
    return "\n    ".join(lines)


def format_results(data: dict, query: str, fields: list[str]) -> None:
    """Exibe os tweets com todos os campos solicitados."""
    tweets = data.get("data", [])
    meta = data.get("meta", {})
    users_map, media_map, polls_map = build_lookup_maps(data)

    if not tweets:
        print(f"ℹ️  Nenhum tweet encontrado para: '{query}'")
        return

    total = meta.get("result_count", len(tweets))
    active_fields = " | ".join(f for f in fields if f in ALL_FIELDS) or "básico"
    print(f"\n🔍 Resultados para: '{query}'")
    print(f"📊 {total} tweet(s) | campos: [{active_fields}]")
    print("=" * 70)

    for i, tweet in enumerate(tweets, 1):
        tweet_id = tweet.get("id", "")
        text = tweet.get("text", "")
        created_at = tweet.get("created_at", "")

        print(f"\n[{i}] ID: {tweet_id}")
        if created_at:
            print(f"    📅 {created_at}")

        # Usuário
        if "user" in fields and tweet.get("author_id"):
            user = users_map.get(tweet["author_id"], {})
            print(f"    👤 {format_user(user)}")

        print(f"    💬 {text}")

        # Thread
        if "thread" in fields and tweet.get("conversation_id"):
            conv_id = tweet["conversation_id"]
            is_reply = conv_id != tweet_id
            role = "resposta na thread" if is_reply else "tweet raiz"
            print(f"    🧵 {role} | conversation_id: {conv_id}")

        # Métricas
        if "metrics" in fields and tweet.get("public_metrics"):
            m = tweet["public_metrics"]
            likes = m.get("like_count", 0)
            rts = m.get("retweet_count", 0)
            replies = m.get("reply_count", 0)
            quotes = m.get("quote_count", 0)
            impressions = m.get("impression_count")
            bookmarks = m.get("bookmark_count", 0)
            impr_str = f" | 👁️  {impressions:,}" if impressions else ""
            print(f"    ❤️  {likes:,}  🔁 {rts:,}  💬 {replies:,}  💬Q {quotes:,}"
                  f"  🔖 {bookmarks:,}{impr_str}")

        # Entidades
        if "entities" in fields and tweet.get("entities"):
            ent_str = format_entities(tweet["entities"])
            if ent_str:
                print(f"    🏷️  {ent_str}")

        # Mídia
        if "media" in fields and tweet.get("attachments", {}).get("media_keys"):
            media_list = [
                media_map[k]
                for k in tweet["attachments"]["media_keys"]
                if k in media_map
            ]
            media_str = format_media(media_list)
            if media_str:
                print(f"    {media_str}")

        # Polls
        if "poll" in fields and tweet.get("attachments", {}).get("poll_ids"):
            for poll_id in tweet["attachments"]["poll_ids"]:
                poll = polls_map.get(poll_id)
                if poll:
                    poll_str = format_poll(poll)
                    print(f"    {poll_str}")

        print(f"    🔗 https://x.com/i/web/status/{tweet_id}")

    print("\n" + "=" * 70)

    # Resumo de analytics
    if "metrics" in fields and tweets:
        all_metrics = [t.get("public_metrics", {}) for t in tweets if t.get("public_metrics")]
        if all_metrics:
            total_likes = sum(m.get("like_count", 0) for m in all_metrics)
            total_rts = sum(m.get("retweet_count", 0) for m in all_metrics)
            total_impressions = sum(m.get("impression_count", 0) for m in all_metrics if m.get("impression_count"))
            avg_eng = (total_likes + total_rts) / len(all_metrics)

            print(f"\n📈 Analytics do conjunto:")
            print(f"   Engajamento médio: {avg_eng:.0f} (likes + RTs)")
            print(f"   Total likes: {total_likes:,} | Total RTs: {total_rts:,}")
            if total_impressions:
                eng_rate = (total_likes + total_rts) / total_impressions * 100
                print(f"   Total impressões: {total_impressions:,} | Taxa: {eng_rate:.2f}%")

            # Top tweet
            top = max(tweets, key=lambda t: (t.get("public_metrics") or {}).get("like_count", 0))
            top_m = top.get("public_metrics", {})
            print(f"\n   🏆 Tweet mais engajado:")
            print(f"   ID: {top['id']} | ❤️ {top_m.get('like_count', 0):,} | 🔁 {top_m.get('retweet_count', 0):,}")
            print(f"   \"{top['text'][:100]}{'...' if len(top['text']) > 100 else ''}\"")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Busca tweets recentes no X com campos expandidos",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("--query", "-q", required=True,
                        help='Query de busca. Ex: "#IA -is:retweet lang:pt"')
    parser.add_argument("--max", "-m", type=int, default=20, dest="max_results",
                        help="Número máximo de resultados (10-100, padrão: 20)")
    parser.add_argument(
        "--fields", "-f",
        default="metrics",
        help=("Campos a incluir, separados por vírgula. "
              "Opções: metrics,entities,media,user,thread,poll,all  (padrão: metrics)")
    )
    parser.add_argument("--json", action="store_true", help="Saída em formato JSON bruto")
    args = parser.parse_args()

    # Resolver campos solicitados
    requested = [f.strip() for f in args.fields.split(",")]
    if "all" in requested:
        fields = ALL_FIELDS
    else:
        fields = [f for f in requested if f in ALL_FIELDS]
        unknown = [f for f in requested if f not in ALL_FIELDS and f != "all"]
        if unknown:
            print(f"⚠️  Campos desconhecidos ignorados: {unknown}")
            print(f"   Campos válidos: {', '.join(ALL_FIELDS)}, all")

    bearer_token = os.getenv("X_BEARER_TOKEN")
    if not bearer_token:
        print("❌ X_BEARER_TOKEN não encontrado.")
        print("   Crie um arquivo .env na pasta da skill com:")
        print("   X_BEARER_TOKEN=seu_token_aqui")
        print("   Obtenha em: https://developer.x.com/en/portal/dashboard")
        sys.exit(1)

    data = search_tweets(args.query, args.max_results, bearer_token, fields)

    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        format_results(data, args.query, fields)


if __name__ == "__main__":
    main()
