============
Features
============


*********
Use cases
*********

Use case layer is in charge of handle business logic.

- Manages transaction
- Manages executions dependent of committed transaction
- Returns data to caller (i.e for API responses purposes)
- Hides complexity
- Allows nesting to DRY
- Establishes events as the only way to propagate on_commit execution


.. code-block:: python

    from django_ontruck.use_cases import UseCaseBase
    from .events import FooEvent
    from .models import FooModel

    class FooUseCase(UseCaseBase):

    def execute_in_commit(self, command, executed_by=None):
        example = FooModel.objects.create(**command)
        self.events.append(FooEvent(attr1='attr1_value'))
        return example


Events created will be published when outermost transaction is committed

*********
Events
*********

Abstraction to decouple contexts wrapping django signals

.. code-block:: python

    from django.dispatch import Signal
    from django_ontruck.events import EventBase

    class FooEvent(EventBase):
        signal = Signal(['attr1'])


Check `show_events` command to `List all events`_.

.. code-block:: shell

    python manage.py show_events

.. image:: images/show_events_command.png


*********
Queries
*********

Analogue to CQRS, a separation between the logic that writes (use cases) from the one that reads (queries).

.. code-block:: python

    class CountFooQuery(QueryBase):

        def execute(self, command, executed_by=None):
            text = command.get('title')
            return {'count': FooModel.objects.filter(title__contains=text).count()}


*********
Models
*********

Base model to track some CRUD dates and author. Safe delete is implemented.


.. code-block:: python

    from django.db import models
    from django_ontruck.models import BaseModel

    class FooModel(BaseModel):
        title = models.CharField(max_length=50)


*********
Notifiers
*********

Base classes to notify events to 3rd party systems like Slack, Segment, etc.


.. code-block:: python

    from django.db import models
    from django_ontruck.notifiers.segment import SegmentNotifier
    from django_ontruck.notifiers import AsyncNotifier

    class FooNotifier(segmentNotifier):
        async_class = AsyncNotifier
        event_id = 'test_event'


*********
Views
*********

Collections of DRF views extended to fit with BaseModel and UseCases

***************
Value Objects
***************

Objects for which equality is determined by their attributes as opposed to by identity.
That is, they are **fungible**: one instance of an object can be swapped for
any other instance as long as their attributes are the same (much like coins, or stamps.)

Money
-----
The `Money` class represents a monetary value together with its currency.

- The value is stored without rounding until the `allocate` method is invoked. How rounding is performed depends on the currency.

.. code-block:: python

   from django_ontruck.value_objects.money import euros, pounds, Currencies, money, Currency

   # commonly used currencies have their own helpers:
   two_euros = euros('2.00')  # 50.00 €
   one_hundred_pounds = pounds('100.00') # £100.00

   # Other currencies can be created using the `money` helper and the currency
   twenty_zloty = money(Currencies.PLN, '20')

   # Any missing currencies can be created
   alt = Currency('ALT', 'Altarian Dollars', '$')
   one_altarian_dollar = money(alt, '1')

   # We can apply arithmetic operations and the value is stored without rounding.
   divided = two_euros / 3
   divided.amount  # Decimal('0.6666666666666666666666666667'))

   # We can round the value (according to the currency) using `allocate`
   divided.allocate().amount  # Decimal('0.67'))



*********
Testing
*********

Utils for testing.

Patch transactions and run transaction.on_commit
------------------------------------------------



After last transaction inside test is exit

Create a fixture

.. code-block:: python

    @pytest.fixture(autouse=True)
    def _run_on_commit_callbacks(request):
        marker = request.node.get_closest_marker("run_on_commit_callbacks")

        if marker:
            with PatchedAtomic():
                yield
        else:
            yield

Mark your tests you want to use it

.. code-block:: python

        @mark.run_on_commit_callbacks
        def test_use_case_post_commit(self, mocker, foo_use_case):
            mock_event_send = mocker.patch('django_ontruck.events.EventBase.send')
            foo_use_case.execute({})
            mock_event_send.assert_called_once()



*********
Commands
*********

List all events
-----------------

Show all events defined in each app and handlers connected.

.. code-block:: shell

    python manage.py show_events

.. image:: images/show_events_command.png


App template
-------------

Start app with directory/files structure.

.. code-block:: python

    python manage.py startontruckapp appname



*********
Monads
*********

We provide an implementation of useful monads.


Result
------

Result monad is used to encapsulate return results whenever they are
sucessful or not in order to treat the responses like a streamlined pipeline.

.. code-block: python
    result = my_use_case.execute(cmd, user)  # type: Result[int, str]

    # result should contain a Journey id when Ok or a message when Error

    res = result.and_then(get_journey_object) \       # get Journey model from ID
                .and_then(prefetch_related_tables) \  # prefetch stuff
                .and_then(serialize_response) \       # compose JSON response
                .or_else(serialize_error)             # compose JSON response when error

    if res.is_ok():
        return Response(data=res.unwrap(), status_code=status.HTTP_200_OK)
    else:
        return Response(data=res.unwrap(), status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
