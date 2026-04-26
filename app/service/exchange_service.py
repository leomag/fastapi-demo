from decimal import Decimal
from typing import Dict, Tuple

import aiohttp

from app.enum import CurrencyEnum

FALLBACK_RATES: Dict[Tuple[str, str], Decimal] = {
    (CurrencyEnum.USD, CurrencyEnum.RUB): Decimal("95"),
    (CurrencyEnum.USD, CurrencyEnum.EUR): Decimal("0.92"),
    (CurrencyEnum.EUR, CurrencyEnum.RUB): Decimal("103.26"),
    (CurrencyEnum.RUB, CurrencyEnum.USD): Decimal("0.0105"),
    (CurrencyEnum.EUR, CurrencyEnum.USD): Decimal("1.087"),
    (CurrencyEnum.RUB, CurrencyEnum.EUR): Decimal("0.0097"),
}

# def get_exchange_rate(base: CurrencyEnum, target: CurrencyEnum) -> Decimal:
#     return FALLBACK_RATES.get((base, target), Decimal(1))


async def get_exchange_rate(base: CurrencyEnum, target: CurrencyEnum) -> Decimal:

    url = f"https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/{base}.json"

    timeout = aiohttp.ClientTimeout(total=5.0)

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
                base_map = data.get(base, {})
                rate = base_map.get(target)

        if rate is not None and isinstance(rate, (int, float)):
            return Decimal(rate)
        raise KeyError("Rate not found")
    except Exception:
        print("hello")
        return FALLBACK_RATES.get((base, target), Decimal(1))
