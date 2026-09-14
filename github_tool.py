import requests

def get_repo_info(owner, repo):
    url = f"https://api.github.com/repos/hemand18/AI-Native-Life"
    response = requests.get(url)
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
    url = f"https://api.github.com/repos/hemand18/AI-Native-Life/readme"
    headers = {"Accept": "application/vnd.github.raw"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None
    return response.text

def get_file_list(owner, repo, path=""):
    url = f"https://api.github.com/repos/hemand18/AI-Native-Life/contents/{path}"
    response = requests.get(url)
    if response.status_code != 200:
        return []
    items = response.json()
    return [item["name"] for item in items if isinstance(items, list)]