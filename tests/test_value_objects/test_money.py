from decimal import Decimal

from pytest import fixture, mark, raises

from django_ontruck.value_objects.money import euros, pounds, Currencies, money


@fixture
def fifty_euros():
    return euros(50)


@mark.parametrize(
    ('operation', 'arg', 'expected'),
    (
        ('__eq__', euros('50.0'), True),
        ('__eq__', euros(49), False),
        ('__eq__', pounds(50), False),
        ('__lt__', euros(Decimal('49')), False),
        ('__lt__', euros('51.0'), True),
        ('__add__', euros('50.0'), euros('100')),
        ('__sub__', euros('50'), euros('0')),
        ('__mul__', 2, euros(100)),
        ('__truediv__', 25, euros(2)),
        ('__floordiv__', 40, euros(1)),
    )
)
def test_basic_valid_opertions(operation, arg, expected, fifty_euros):
    assert getattr(fifty_euros, operation)(arg) == expected


@mark.parametrize(
    ('operation', 'arg', 'raises_'),
    (
        ('__lt__', pounds('50'), ValueError),
        ('__add__', pounds('50.0'), ValueError),
        ('__sub__', pounds('50'), ValueError),
    )
)
def test_basic_invalid_opertions(operation, arg, raises_, fifty_euros):
    with raises(raises_):
        getattr(fifty_euros, operation)(arg)


@mark.parametrize(
    ('money_', 'expected'),
    (
        (euros('100.001'), euros('100.00')),
        (money(Currencies.JPY, '100.1'), money(Currencies.JPY, '100'))
    )
)
def test_allocate(money_, expected):
    assert money_.allocate() == expected


def test_str(fifty_euros):
    assert str(fifty_euros) == '50.00 €'
