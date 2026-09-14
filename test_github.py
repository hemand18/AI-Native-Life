from github_tool import get_repo_info, get_readme

info = get_repo_info("octocat", "Hello-World")
print(info)

readme = get_readme("octocat", "Hello-World")
print(readme[:300] if readme else "No README found")