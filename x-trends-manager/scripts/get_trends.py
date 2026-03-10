#!/usr/bin/env python3
"""
Busca trends do X (Twitter) por WOEID.
Uso: python get_trends.py --woeid 23424762
"""

import argparse
import json
import os
import sys
from datetime import datetime

try:
    import requests
except ImportError:
    print("❌ Instale as dependências: pip install requests python-dotenv")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv opcional


WOEID_NAMES = {
    1: "Worldwide",
    23424762: "Brasil",
    455827: "São Paulo",
    455826: "Rio de Janeiro",
    455819: "Brasília",
    455821: "Belo Horizonte",
    23424977: "EUA",
    2459115: "Nova York",
    44418: "Londres",
    23424975: "Reino Unido",
    23424925: "Portugal",
    116545: "Cidade do México",
    23424900: "México",
    1118370: "Tóquio",
}


def get_trends(woeid: int, bearer_token: str) -> dict:
    """Busca trends para o WOEID especificado."""
    url = f"https://api.x.com/2/trends/by/woeid/{woeid}"
    headers = {"Authorization": f"Bearer {bearer_token}"}

    response = requests.get(url, headers=headers, timeout=10)

    if response.status_code == 401:
        print("❌ Token inválido ou expirado. Verifique X_BEARER_TOKEN.")
        sys.exit(1)
    elif response.status_code == 403:
        print("❌ Acesso negado. Verifique as permissões do seu app no Developer Portal.")
        sys.exit(1)
    elif response.status_code == 429:
        reset = response.headers.get("x-rate-limit-reset", "desconhecido")
        print(f"⏳ Rate limit atingido. Tente novamente após o timestamp: {reset}")
        sys.exit(1)
    elif response.status_code != 200:
        print(f"❌ Erro {response.status_code}: {response.text}")
        sys.exit(1)

    return response.json()


def format_trends(data: dict, woeid: int, top: int = 20) -> None:
    """Formata e exibe as trends de forma legível."""
    location_name = WOEID_NAMES.get(woeid, f"WOEID {woeid}")
    trends = data.get("data", [])

    if not trends:
        print(f"ℹ️  Nenhuma trend encontrada para {location_name} (WOEID: {woeid})")
        return

    print(f"\n🔥 Top Trends — {location_name} (WOEID: {woeid})")
    print(f"📅 Atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("=" * 50)

    for i, trend in enumerate(trends[:top], 1):
        name = trend.get("trend_name", "N/A")
        count = trend.get("tweet_count")
        count_str = f"  ({count:,} tweets)" if count else ""
        print(f"{i:2}. {name}{count_str}")

    print("=" * 50)
    print(f"Total: {len(trends)} trends encontradas\n")

    # Retorna dados para uso programático
    return trends[:top]


def main():
    parser = argparse.ArgumentParser(
        description="Busca trends do X (Twitter) por localização"
    )
    parser.add_argument(
        "--woeid",
        type=int,
        default=23424762,
        help="WOEID da localização (padrão: 23424762 = Brasil)"
    )
    parser.add_argument(
        "--top",
        type=int,
        default=20,
        help="Número de trends a exibir (padrão: 20)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Saída em formato JSON"
    )
    args = parser.parse_args()

    bearer_token = os.getenv("X_BEARER_TOKEN")
    if not bearer_token:
        print("❌ Variável de ambiente X_BEARER_TOKEN não encontrada.")
        print("   Configure em seu .env ou exporte no terminal:")
        print("   export X_BEARER_TOKEN='seu_token_aqui'")
        print("   Obtenha em: https://developer.x.com/en/portal/dashboard")
        sys.exit(1)

    data = get_trends(args.woeid, bearer_token)

    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        format_trends(data, args.woeid, args.top)


if __name__ == "__main__":
    main()
