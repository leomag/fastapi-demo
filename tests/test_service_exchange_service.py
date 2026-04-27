import asyncio
from decimal import Decimal

import aiohttp

from app.enum import CurrencyEnum
from app.service import exchange_service


def test_get_exchange_rate_returns_fallback_on_exception(monkeypatch):
    class _ExplodingSession:
        async def __aenter__(self):
            raise RuntimeError("boom")

        async def __aexit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(aiohttp, "ClientSession", lambda timeout: _ExplodingSession())

    result = asyncio.run(exchange_service.get_exchange_rate(CurrencyEnum.USD, CurrencyEnum.RUB))

    assert result == exchange_service.FALLBACK_RATES[(CurrencyEnum.USD, CurrencyEnum.RUB)]


def test_get_exchange_rate_parses_rate_from_api(monkeypatch):
    class _Resp:
        def raise_for_status(self):
            return None

        async def json(self):
            return {CurrencyEnum.USD: {CurrencyEnum.RUB: 96.5}}

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

    class _Session:
        def get(self, url):
            self.url = url
            return _Resp()

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(aiohttp, "ClientSession", lambda timeout: _Session())

    result = asyncio.run(exchange_service.get_exchange_rate(CurrencyEnum.USD, CurrencyEnum.RUB))

    assert result == Decimal("96.5")
