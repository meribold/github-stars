import os
from collections import defaultdict

from github3 import GitHub

gh = GitHub(token=os.environ["GITHUB_TOKEN"])

html_escape_table = {
    ">": "&gt;",
    "<": "&lt;",
}


def html_escape(text):
    return "".join(html_escape_table.get(c, c) for c in text)


repo_list_dict = defaultdict(list)

for s in gh.starred_by("meribold"):
    repo_list_dict[s.language or "Miscellaneous"].append(
        [s.full_name, s.html_url, html_escape((s.description or "").strip())]
    )

repo_list_of_lists = sorted(repo_list_dict.items(), key=lambda r: r[0])

new_readme_content = (
    "## Languages\n\n"
    + "\n".join(
        "*   [{}](#{})".format(language, "-".join(language.lower().split()))
        for language, _ in repo_list_of_lists
    )
    + "\n"
    + "\n".join(
        f"\n## {language}\n\n"
        + "\n".join(
            f"*   [{name}]({url})" + (f": {desc}" if desc else "")
            for name, url, desc in repo_list
        )
        for language, repo_list in repo_list_of_lists
    )
    + "\n"
).encode()

readme = gh.repository("meribold", "github-stars").readme()

if new_readme_content != readme.decoded:
    readme.update("Update list of starred repositories", new_readme_content)
