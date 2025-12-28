from pwstrength.features import hibp_client


class DummyResponse:
    def __init__(self, status_code: int, text: str):
        self.status_code = status_code
        self.text = text

    def raise_for_status(self):
        raise RuntimeError("request failed")


class DummySession:
    def __init__(self, text: str):
        self.text = text
        self.calls = []

    def get(self, url, headers=None, timeout=10):
        self.calls.append({"url": url, "headers": headers, "timeout": timeout})
        return DummyResponse(200, self.text)


def test_get_count_parses_range_response():
    hibp_client.clear_cache()
    suffix = "1E4C9B93F3F0682250B6CF8331B7EE68FD8"
    session = DummySession(f"{suffix}:12\nAAAAAA:5")
    count = hibp_client.get_count("password", session=session)
    assert count == 12
    assert session.calls[0]["url"].endswith("5BAA6")
    assert session.calls[0]["headers"]["Add-Padding"] == "true"


def test_range_cache_prevents_duplicate_fetches():
    hibp_client.clear_cache()
    suffix = "1E4C9B93F3F0682250B6CF8331B7EE68FD8"
    first = DummySession(f"{suffix}:3")
    second = DummySession("SHOULDNOTMATCH:99")
    assert hibp_client.get_count("password", session=first) == 3
    assert hibp_client.get_count("password", session=second) == 3
    assert len(second.calls) == 0
