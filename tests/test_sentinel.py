from dynamo_query.sentinel import SentinelValue


class TestSentinelValue:
    @staticmethod
    def test_init() -> None:
        result = SentinelValue("not set")
        assert repr(result) == "not set"
        assert str(result) == "not set"
        assert repr(SentinelValue()) == "DEFAULT"
