from scripts import simple_matmul as sm


class TestSimpleMatmul:
    def test_simple_matmul(self) -> None:
        assert sm.f(2, 3) == 6
