from dataclasses import dataclass
from decimal import Decimal
from functools import total_ordering, partial

from enum import Enum


@dataclass
class Currency:
    code: str
    name: str
    symbol: str
    template: str = '{symbol}{amount}'
    quantum: Decimal = Decimal('.01')


@total_ordering
@dataclass
class Money:
    currency: Currency
    amount: Decimal

    def __post_init__(self):
        self.amount = Decimal(self.amount)

    def allocate(self):
        return self.__class__(
            self.currency, self.amount.quantize(self.currency.quantum)
        )

    def currency_matches(self, other):
        return self.currency == other.currency

    def ensure_currency_matches(self, other):
        if not self.currency_matches(other):
            raise ValueError(
                f'Mismatched currencies: '
                f'{self.currency.name} / {other.currency.name}'
            )

    def __lt__(self, other):
        self.ensure_currency_matches(other)

        return self.amount < other.amount

    def __add__(self, other):
        self.ensure_currency_matches(other)

        return self.__class__(self.currency, self.amount + other.amount)

    def __sub__(self, other):
        self.ensure_currency_matches(other)

        return self.__class__(self.currency, self.amount - other.amount)

    def __mul__(self, other):
        return self.__class__(self.currency, self.amount * other)

    def __floordiv__(self, other):
        return self.__class__(self.currency, self.amount // other)

    def __truediv__(self, other):
        return self.__class__(self.currency, self.amount / other)

    def __str__(self):
        return self.currency.template.format(
            symbol=self.currency.symbol,
            amount=self.allocate().amount
        )


_AMOUNT_SYMBOL = '{amount} {symbol}'


class Currencies(Enum):
    EUR = Currency('EUR', 'Euros', '€', template=_AMOUNT_SYMBOL)
    GBP = Currency('GBP', 'British Pounds Sterling', '£')
    PLN = Currency('PLN', 'Polish Złoty', 'zł.', template=_AMOUNT_SYMBOL)
    DKK = Currency('DKK', 'Danish Krone', 'kr.', template=_AMOUNT_SYMBOL)
    SEK = Currency('SEK', 'Swedish Krona', 'kr.', template=_AMOUNT_SYMBOL)
    USD = Currency('USD', 'United States Dollars', '$')
    JPY = Currency('JPY', 'Japanese Yen', '¥', quantum=Decimal('1'))


def money(currency: Currencies, amount):
    return Money(currency.value, amount)


euros = partial(money, Currencies.EUR)
pounds = partial(money, Currencies.GBP)
