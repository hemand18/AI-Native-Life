from github_tool import get_repo_info, get_readme


def test_get_repo_info_uses_requested_repo(monkeypatch):
    calls = []

    class DummyResponse:
        status_code = 200

        def json(self):
            return {
                "name": "Hello-World",
                "description": "A sample repo",
                "language": "Python",
                "stargazers_count": 42,
                "topics": ["demo"]
            }

    def fake_get(url, timeout=10, headers=None):
        calls.append((url, timeout, headers))
        return DummyResponse()

    monkeypatch.setattr("github_tool.requests.get", fake_get)

    info = get_repo_info("octocat", "Hello-World")

    assert info["name"] == "Hello-World"
    assert calls[0][0] == "https://api.github.com/repos/octocat/Hello-World"


def test_get_readme_uses_requested_repo(monkeypatch):
    calls = []

    class DummyResponse:
        status_code = 200
        text = "# Example README\n\nThis is a README."

    def fake_get(url, timeout=10, headers=None):
        calls.append((url, timeout, headers))
        return DummyResponse()

    monkeypatch.setattr("github_tool.requests.get", fake_get)

    readme = get_readme("octocat", "Hello-World")

    assert readme.startswith("# Example README")
    assert calls[0][0] == "https://api.github.com/repos/octocat/Hello-World/readme"