import aws_chalice.chalicelib.message_retriever as mr


class TestMessageRetriever():
    
    def test_exclude_mentions(self) -> None:
        message = "<@U0LAN0Z89> is it everything a river should be?"
        assert mr.exclude_mentions(message) == "is it everything a river should be?"
    
    def test_retrieve_description(self) -> None:
        url = "https://note.com/piqcy/n/n03e88f666fa7"
        description = mr.retrieve_description(url)
        assert description.startswith("データからプロダクトのボトルネックを")
