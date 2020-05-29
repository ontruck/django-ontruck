from pytest import fixture, mark

from .test_app.queries import CountFooQuery


class TestQueries:

    @mark.django_db
    def test_query(self, foo_model, foo_query):
        query = foo_query.execute({'title': 'tit'})
        assert query['count'] == 1
