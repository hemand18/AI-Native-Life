def test_fallback_message_when_api_is_unavailable():
    message = (
        "Chat is unavailable because the Groq API key is missing or the Groq SDK is not "
        "installed. Add GROQ_API_KEY to your .env file or Streamlit secrets."
    )

    assert "GROQ_API_KEY" in message
    assert "not installed" in message or "missing" in message

