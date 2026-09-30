import agent


def test_missing_api_key_returns_friendly_message(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    agent.client = None

    result = agent._ask("Give me a short answer")

    assert "GROQ_API_KEY" in result
    assert "not installed" in result or "missing" in result
