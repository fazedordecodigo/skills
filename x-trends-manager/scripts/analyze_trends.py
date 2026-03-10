#!/usr/bin/env python3
"""
Analisa trends do X e gera insights e sugestões de conteúdo.
Uso: python analyze_trends.py --woeid 23424762 --top 10
"""

import argparse
import json
import os
import re
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


# Categorias temáticas com palavras-chave
CATEGORIES = {
    "🏅 Esportes": [
        "futebol", "copa", "gol", "neymar", "flamengo", "corinthians",
        "palmeiras", "brasileirao", "nba", "formula1", "moto gp", "jogo",
        "campeonato", "selecao", "cruzeiro", "atletico", "grêmio", "sport",
        "vasco", "botafogo", "santos", "lol", "esports", "champion",
    ],
    "🎬 Entretenimento": [
        "netflix", "série", "filme", "ator", "atriz", "musica", "show",
        "album", "youtube", "tiktok", "instagram", "streaming", "bbb",
        "reality", "novela", "globo", "record", "sbt", "podcast", "k-pop",
        "taylor", "spotify", "grammy", "oscar", "emmy", "concert",
    ],
    "💻 Tecnologia": [
        "ia", "gpt", "chatgpt", "inteligência artificial", "tech", "app",
        "software", "programação", "python", "javascript", "github",
        "openai", "google", "apple", "microsoft", "meta", "tesla", "spacex",
        "blockchain", "crypto", "bitcoin", "web3", "nft", "startup",
    ],
    "🏛️ Política": [
        "governo", "presidente", "congresso", "senado", "câmara", "lula",
        "bolsonaro", "eleição", "voto", "partido", "ministério", "pec",
        "stf", "supremo", "deputado", "senador", "prefeito", "governador",
    ],
    "💰 Economia": [
        "dolar", "real", "inflação", "ipca", "selic", "bolsa", "ibovespa",
        "pib", "economia", "mercado", "banco", "imposto", "reforma",
        "petrobras", "vale", "b3", "cdi", "investimento", "renda",
    ],
    "🌍 Mundo": [
        "eua", "china", "russia", "ucrania", "guerra", "onu", "otan",
        "nato", "trump", "biden", "macron", "europa", "oriente médio",
        "israel", "palestina", "argentina", "chile", "venezuela",
    ],
    "🔬 Ciência/Saúde": [
        "saude", "vacina", "covid", "virus", "pesquisa", "estudo",
        "cancer", "medicina", "nasa", "ciencia", "discovery", "espaço",
        "clima", "aquecimento", "sustentabilidade", "ambiente",
    ],
    "😄 Humor/Viral": [
        "meme", "viral", "trend", "challenge", "funny", "humor",
        "pegadinha", "vídeo", "engraçado", "zuera", "kkk",
    ],
}


def categorize_trend(trend_name: str) -> str:
    """Categoriza uma trend baseado no nome."""
    name_lower = trend_name.lower().replace("#", "").replace("_", " ")

    for category, keywords in CATEGORIES.items():
        for keyword in keywords:
            if keyword in name_lower:
                return category

    return "📌 Outros"


def get_trends_data(woeid: int, bearer_token: str) -> list:
    """Busca dados de trends da API."""
    url = f"https://api.x.com/2/trends/by/woeid/{woeid}"
    headers = {"Authorization": f"Bearer {bearer_token}"}

    response = requests.get(url, headers=headers, timeout=10)

    if response.status_code == 401:
        print("❌ Bearer Token inválido. Verifique X_BEARER_TOKEN.")
        sys.exit(1)
    elif response.status_code == 429:
        print("⏳ Rate limit atingido.")
        sys.exit(1)
    elif response.status_code != 200:
        print(f"❌ Erro {response.status_code}: {response.text}")
        sys.exit(1)

    return response.json().get("data", [])


WOEID_NAMES = {
    1: "Worldwide",
    23424762: "Brasil",
    455827: "São Paulo",
    455826: "Rio de Janeiro",
    23424977: "EUA",
    44418: "Londres",
    23424975: "Reino Unido",
}


def analyze_and_suggest(trends: list, top: int = 10) -> None:
    """Analisa trends e gera insights + sugestões de conteúdo."""

    if not trends:
        print("ℹ️  Nenhuma trend disponível para análise.")
        return

    top_trends = trends[:top]

    # Categorizar trends
    categorized = {}
    for trend in top_trends:
        name = trend.get("trend_name", "")
        count = trend.get("tweet_count", 0)
        category = categorize_trend(name)

        if category not in categorized:
            categorized[category] = []
        categorized[category].append({"name": name, "count": count})

    # === RELATÓRIO ===
    print("\n" + "=" * 60)
    print("📊 ANÁLISE DE TRENDS — X (Twitter)")
    print("=" * 60)

    # Top trends por volume
    sorted_by_volume = sorted(
        top_trends,
        key=lambda x: x.get("tweet_count") or 0,
        reverse=True
    )

    print("\n🔥 Top 5 por volume de tweets:")
    for i, t in enumerate(sorted_by_volume[:5], 1):
        count = t.get("tweet_count")
        count_str = f" ({count:,} tweets)" if count else ""
        print(f"   {i}. {t['trend_name']}{count_str}")

    # Por categoria
    print("\n📂 Distribuição por categoria:")
    for cat, items in sorted(categorized.items(), key=lambda x: -len(x[1])):
        names = ", ".join(i["name"] for i in items[:3])
        more = f" +{len(items)-3}" if len(items) > 3 else ""
        print(f"   {cat}: {names}{more}")

    # === OPORTUNIDADES ===
    print("\n💡 SUGESTÕES DE CONTEÚDO:")
    print("-" * 60)

    suggestions_made = 0
    for trend in top_trends[:5]:
        name = trend["trend_name"]
        count = trend.get("tweet_count", 0)
        category = categorize_trend(name)

        is_hashtag = name.startswith("#")
        hashtag = name if is_hashtag else f"#{name.replace(' ', '')}"

        print(f"\n📌 Trend: {name}  [{category}]")
        if count:
            print(f"   Volume: {count:,} tweets")
        print("   Sugestões de tweet:")

        # Sugestões baseadas na categoria
        if "Tecnologia" in category:
            print(f'   → "Minha visão sobre {name}: [sua opinião] {hashtag} #tech"')
            print(f'   → "O que mudou com {name}? Thread 🧵 {hashtag}"')
        elif "Esportes" in category:
            print(f'   → "Análise: por que {name} está dominando o X hoje? {hashtag}"')
            print(f'   → "Sua opinião sobre {name}? 👇 {hashtag}"')
        elif "Política" in category:
            print(f'   → "Os fatos sobre {name} que você precisa saber 📋 {hashtag}"')
        elif "Entretenimento" in category:
            print(f'   → "Minha opinião quente sobre {name}: [seu take] {hashtag}"')
            print(f'   → "Quem mais está falando sobre {name}? 🙋 {hashtag}"')
        else:
            print(f'   → "O que você precisa saber sobre {name} {hashtag}"')
            print(f'   → "Thread sobre {name} 🧵 {hashtag}"')

        suggestions_made += 1

    print("\n" + "=" * 60)
    print("⚡ Dica: Use search_tweets.py para explorar o contexto de cada trend")
    print("   antes de criar conteúdo. Ex:")
    print(f'   python search_tweets.py --query "{top_trends[0]["trend_name"]} -is:retweet" --max 20')
    print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Analisa trends do X e sugere conteúdo"
    )
    parser.add_argument(
        "--woeid",
        type=int,
        default=23424762,
        help="WOEID da localização (padrão: Brasil = 23424762)"
    )
    parser.add_argument(
        "--top",
        type=int,
        default=10,
        help="Quantas trends analisar (padrão: 10)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Saída em formato JSON"
    )
    args = parser.parse_args()

    bearer_token = os.getenv("X_BEARER_TOKEN")
    if not bearer_token:
        print("❌ X_BEARER_TOKEN não configurado.")
        print("   export X_BEARER_TOKEN='seu_token_aqui'")
        sys.exit(1)

    location = WOEID_NAMES.get(args.woeid, f"WOEID {args.woeid}")
    print(f"🌐 Buscando trends para: {location}...")

    trends = get_trends_data(args.woeid, bearer_token)

    if args.json:
        output = []
        for t in trends[:args.top]:
            t["category"] = categorize_trend(t.get("trend_name", ""))
            output.append(t)
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        analyze_and_suggest(trends, args.top)


if __name__ == "__main__":
    main()
