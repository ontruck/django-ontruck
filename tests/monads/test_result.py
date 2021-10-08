import pytest
from django_ontruck.monads import Ok, Error, Result


def __square(x: int) -> Result[int, int]:
    return Ok(x * x)


def __err(x: int) -> Result[int, int]:
    return Error(x)


def __stringify(n: int) -> str:
    return f'error code: {n}'


@pytest.mark.parametrize('result, expected', [
    (Ok("this is a valid result"), True),
    (Error("this is an error"), False)
])
def test_is_ok(result, expected):
    assert result.is_ok() is expected


@pytest.mark.parametrize('result, expected', [
    (Ok("this is a valid result"), True),
    (Error("this is an error"), False)
])
def test_bool(result, expected):
    assert bool(result) is expected


@pytest.mark.parametrize('result, expected', [
    (Ok("this is a valid result"), False),
    (Error("this is an error"), True)
])
def test_is_error(result, expected):
    assert result.is_error() is expected


@pytest.mark.parametrize('result, expected', [
    (Ok(2), Ok(4)),
    (Error(-1), Error(-1))
])
def test_and_then(result, expected):
    res = result.and_then(__square)
    assert type(res) == type(expected)
    assert res.unwrap() == expected.unwrap()


@pytest.mark.parametrize('result, first_fn, second_fn, expected', [
    (Ok(2), __square, __square, Ok(16)),
    (Ok(2), __square, __err, Error(4)),
    (Ok(2), __err, __square, Error(2)),
    (Error(3), __square, __square, Error(3)),
])
def test_and_then_chain(result, first_fn, second_fn, expected):
    res = result.and_then(first_fn).and_then(second_fn)
    assert type(res) == type(expected)
    assert res.unwrap() == expected.unwrap()


@pytest.mark.parametrize('result, expected', [
    (Ok(2), Ok(2)),
    (Error(3), Ok(9)),
])
def test_or_else(result, expected):
    res = result.or_else(__square)
    assert type(res) == type(expected)
    assert res.unwrap() == expected.unwrap()


@pytest.mark.parametrize('result, first_fn, second_fn, expected', [
    (Ok(2), __square, __square, Ok(2)),
    (Ok(2), __err, __square, Ok(2)),
    (Error(3), __square, __err, Ok(9)),
    (Error(3), __err, __err, Error(3)),
])
def test_or_else_chain(result, first_fn, second_fn, expected):
    res = result.or_else(first_fn).or_else(second_fn)
    assert type(res) == type(expected)
    assert res.unwrap() == expected.unwrap()


@pytest.mark.parametrize('result, default, expected', [
    (Ok(2), 3, 2),
    (Error("error"), 3, 3),
])
def test_unwrap_or(result, default, expected):
    res = result.unwrap_or(default=default)
    assert res == expected


@pytest.mark.parametrize('result, closure, expected', [
    (Ok(2), lambda x: len(x), 2),
    (Error("foobar"), lambda x: len(x), 6),
])
def test_unwrap_or_else(result, closure, expected):
    res = result.unwrap_or_else(closure)
    assert res == expected


@pytest.mark.parametrize('result, fn, expected', [
    (Ok(2), __square, Ok(4)),
    (Error(2), __square, Error(2)),
])
def test_map(result, fn, expected):
    res = result.map(fn)
    assert type(res) == type(expected)
    assert res.unwrap() == expected.unwrap()


@pytest.mark.parametrize('result, fn, default, expected', [
    (Ok("foo"), lambda x: x.upper(), 'baz', 'FOO'),
    (Error("bar"), lambda x: x.upper(), 'baz', 'baz'),
])
def test_map_or(result, fn, default, expected):
    res = result.map_or(fn, default)
    assert res == expected


@pytest.mark.parametrize('result, fn, defaultfn, expected', [
    (Ok("foo"), lambda x: len(x), lambda x: x * 2, 3),
    (Error("bar"), lambda x: len(x), lambda x: len(x) * 2, 6),
])
def test_map_or_else(result, fn, defaultfn, expected):
    res = result.map_or_else(fn, defaultfn)
    assert res == expected


@pytest.mark.parametrize('result, fn, expected', [
    (Ok(2), __stringify, Ok(2)),
    (Error(500), __stringify, Error('error code: 500')),
])
def test_map_err(result, fn, expected):
    res = result.map_err(lambda result_: Error(fn(result_)))
    assert type(res) == type(expected)
    assert res.unwrap() == expected.unwrap()


@pytest.mark.parametrize('result, expected', [
    (Ok("value"), "value"),
    (Error("error"), "error"),
])
def test_unwrap(result, expected):
    assert result.unwrap() == expected
