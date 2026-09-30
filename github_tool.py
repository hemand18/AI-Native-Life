import requests


def get_repo_info(owner, repo):
    if not owner or not repo:
        return None

    url = f"https://api.github.com/repos/{owner}/{repo}"
    response = requests.get(url, timeout=10)
    if response.status_code != 200:
        return None
    data = response.json()
    return {
        "name": data.get("name"),
        "description": data.get("description"),
        "language": data.get("language"),
        "stars": data.get("stargazers_count"),
        "topics": data.get("topics", [])
    }


def get_readme(owner, repo):
    if not owner or not repo:
        return None

    url = f"https://api.github.com/repos/{owner}/{repo}/readme"
    headers = {"Accept": "application/vnd.github.raw"}
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code != 200:
        return None
    return response.text


def get_file_list(owner, repo, path=""):
    if not owner or not repo:
        return []

    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    response = requests.get(url, timeout=10)
    if response.status_code != 200:
        return []
    items = response.json()
    return [item["name"] for item in items if isinstance(items, list)]