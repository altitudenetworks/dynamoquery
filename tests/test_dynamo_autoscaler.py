from unittest.mock import MagicMock

from dynamo_query.dynamo_autoscaler import DynamoAutoscaler


class TestDynamoAutoscaler:
    def test_init(self):
        client_mock = MagicMock()
        result = DynamoAutoscaler(client_mock)
