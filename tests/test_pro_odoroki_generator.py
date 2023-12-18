import aws_chalice.pro_odoroki_generator as pog


class TestProOdorokiGenerator:
    def test_generate(self) -> None:
        prompt = pog.generate("ChatGPT3.5が発表された")
        assert prompt
