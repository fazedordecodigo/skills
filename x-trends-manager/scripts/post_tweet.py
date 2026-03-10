#!/usr/bin/env python3
"""
Publica um tweet no X (Twitter) via OAuth 1.0a.
Uso: python post_tweet.py --text "Seu tweet aqui"
     python post_tweet.py --text "Resposta..." --reply-to 1234567890
"""

import argparse
import json
import os
import sys

try:
    from requests_oauthlib import OAuth1Session
except ImportError:
    print("❌ Instale as dependências: pip install requests-oauthlib python-dotenv")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

TWEET_MAX_CHARS = 280


def count_chars(text: str) -> int:
    """Conta caracteres (URLs são tratadas como 23 chars pelo X)."""
    import re
    url_pattern = r'https?://\S+'
    urls = re.findall(url_pattern, text)
    text_without_urls = re.sub(url_pattern, '', text)
    return len(text_without_urls) + len(urls) * 23


def post_tweet(text: str, reply_to: str = None, quote_tweet_id: str = None) -> dict:
    """Publica um tweet usando OAuth 1.0a."""

    # Verificar credenciais
    api_key = os.getenv("X_API_KEY")
    api_secret = os.getenv("X_API_SECRET")
    access_token = os.getenv("X_ACCESS_TOKEN")
    access_token_secret = os.getenv("X_ACCESS_TOKEN_SECRET")

    missing = []
    if not api_key:
        missing.append("X_API_KEY")
    if not api_secret:
        missing.append("X_API_SECRET")
    if not access_token:
        missing.append("X_ACCESS_TOKEN")
    if not access_token_secret:
        missing.append("X_ACCESS_TOKEN_SECRET")

    if missing:
        print("❌ Credenciais ausentes para posting:")
        for var in missing:
            print(f"   - {var}")
        print("\n📖 Como obter:")
        print("   1. Acesse https://developer.x.com/en/portal/dashboard")
        print("   2. Crie ou selecione um App")
        print("   3. Em 'Keys and Tokens', gere as credenciais necessárias")
        print("   4. Configure 'App permissions' como 'Read and Write'")
        sys.exit(1)

    # Verificar tamanho do tweet
    char_count = count_chars(text)
    if char_count > TWEET_MAX_CHARS:
        print(f"❌ Tweet muito longo: {char_count} chars (máximo: {TWEET_MAX_CHARS})")
        print(f"   Reduza {char_count - TWEET_MAX_CHARS} caracteres.")
        sys.exit(1)

    # Montar payload
    payload = {"text": text}

    if reply_to:
        payload["reply"] = {
            "in_reply_to_tweet_id": reply_to,
            "auto_populate_reply_metadata": True
        }

    if quote_tweet_id:
        payload["quote_tweet_id"] = quote_tweet_id

    # Criar sessão OAuth 1.0a
    oauth = OAuth1Session(
        client_key=api_key,
        client_secret=api_secret,
        resource_owner_key=access_token,
        resource_owner_secret=access_token_secret
    )

    response = oauth.post(
        "https://api.x.com/2/tweets",
        json=payload
    )

    if response.status_code == 401:
        print("❌ Autenticação falhou. Verifique suas credenciais OAuth.")
        print("   Certifique-se que o App tem permissão 'Read and Write'.")
        sys.exit(1)
    elif response.status_code == 403:
        error = response.json()
        print(f"❌ Proibido: {error.get('detail', response.text)}")
        print("   Possível causa: App sem permissão de escrita ou duplicata de tweet.")
        sys.exit(1)
    elif response.status_code == 429:
        print("⏳ Rate limit de posting atingido (100 tweets/24h no plano Basic).")
        print("   Tente novamente amanhã.")
        sys.exit(1)
    elif response.status_code not in (200, 201):
        print(f"❌ Erro {response.status_code}: {response.text}")
        sys.exit(1)

    return response.json()


def main():
    parser = argparse.ArgumentParser(
        description="Publica um tweet no X (Twitter)"
    )
    parser.add_argument(
        "--text", "-t",
        required=True,
        help="Texto do tweet (máx 280 chars)"
    )
    parser.add_argument(
        "--reply-to", "-r",
        dest="reply_to",
        help="ID do tweet para responder"
    )
    parser.add_argument(
        "--quote",
        dest="quote_tweet_id",
        help="ID do tweet para fazer quote"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simula o posting sem publicar de fato"
    )
    args = parser.parse_args()

    char_count = count_chars(args.text)
    print(f"\n📝 Tweet ({char_count}/{TWEET_MAX_CHARS} chars):")
    print(f"   {args.text}")

    if args.reply_to:
        print(f"   ↩️  Respondendo ao tweet: {args.reply_to}")
    if args.quote_tweet_id:
        print(f"   💬 Quote do tweet: {args.quote_tweet_id}")

    if args.dry_run:
        print("\n🔍 [DRY RUN] Tweet NÃO publicado. Remova --dry-run para publicar.")
        return

    print("\n🚀 Publicando...")
    result = post_tweet(args.text, args.reply_to, args.quote_tweet_id)

    tweet_data = result.get("data", {})
    tweet_id = tweet_data.get("id")

    print(f"✅ Tweet publicado com sucesso!")
    print(f"   ID: {tweet_id}")
    print(f"   🔗 https://x.com/i/web/status/{tweet_id}")


if __name__ == "__main__":
    main()
