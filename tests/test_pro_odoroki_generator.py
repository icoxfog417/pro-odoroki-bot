import xml.etree.ElementTree as ET

import aws_chalice.chalicelib.pro_odoroki_generator as pog
from aws_chalice.chalicelib.bedrock import Bedrock


class TestProOdorokiGenerator:
    def test_generate(self) -> None:
        prompt = pog.generate("ChatGPT3.5が発表された")
        assert prompt

    def test_retrieve(self) -> None:
        prompt_body = pog.generate("ChatGPT3.5が発表された")
        bedrock = Bedrock()
        reply = bedrock.ask_to_claude(prompt_body, instant=True)

        valid = True
        try:
            root = ET.fromstring(reply)  # noqa
        except Exception as ex:  # noqa
            valid = False

        if valid:
            result = pog.retrieve(reply)
            assert result.get("news")
            assert result.get("character")
            assert result.get("focus")
            assert result.get("reaction")
        else:
            import warnings

            warnings.warn(f"Returned reply was not valid XML:\n{reply}")
