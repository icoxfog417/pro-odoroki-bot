from aws_chalice.chalicelib.bedrock import Bedrock


class TestBedrock:
    def test_build_request_for_claude(self) -> None:
        bedrock = Bedrock()
        message = "Please tell me how to create curry"
        max_length = 100
        temperature = 0.9
        top_p = 0.9
        body = bedrock._build_request_for_claude(
            message, max_length, temperature, top_p
        )

        assert body.get("prompt") == f"\n\nHuman: {message}\n\nAssistant:"
        assert body.get("max_tokens_to_sample") == max_length
        assert body.get("temperature") == temperature
        assert body.get("top_p") == top_p

    def test_anthropic(self) -> None:
        bedrock = Bedrock()
        assert (
            len(
                bedrock.ask_to_claude("Hello", version="1", instant=True, max_length=10)
            )
            <= 10
        )
        assert len(bedrock.ask_to_claude("Hello", version="2", max_length=10)) <= 10
        assert len(bedrock.ask_to_claude("Hello", version="2.1", max_length=10)) <= 10
