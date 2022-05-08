import os
import re
from collections import defaultdict

from github3 import GitHub

gh = GitHub(token=os.environ["GITHUB_TOKEN"])

html_escape_table = {
    ">": "&gt;",
    "<": "&lt;",
}


def html_escape(text: str) -> str:
    return "".join(html_escape_table.get(c, c) for c in text)


heading_lists: dict[list] = {}


def get_fragment_id(heading: str) -> str:
    base_fragment_id = re.sub("[^a-z-]+", "", heading.lower().replace(" ", "-"))
    if base_fragment_id not in heading_lists:
        heading_lists[base_fragment_id] = [heading]
        return base_fragment_id

    headings = heading_lists[base_fragment_id]
    if heading == headings[0]:
        return base_fragment_id
    i = 1
    for h in headings[1:]:
        if heading == h:
            return f"{base_fragment_id}-{i}"
        i += 1
    headings.append(heading)
    return f"{base_fragment_id}-{i}"


repo_list_dict = defaultdict(list)

for s in gh.starred_by("meribold"):
    repo_list_dict[s.language or "Miscellaneous"].append(
        [s.full_name, s.html_url, html_escape((s.description or "").strip())]
    )

repo_list_of_lists = sorted(repo_list_dict.items(), key=lambda r: r[0])

new_readme_content = "## Languages\n\n{}\n{}\n".format(
    "\n".join(
        f"*   [{language}](#{get_fragment_id(language)})"
        for language, _ in repo_list_of_lists
    ),
    "\n".join(
        f"\n## {language}\n\n"
        + "\n".join(
            f"*   [{name}]({url})" + (f": {desc}" if desc else "")
            for name, url, desc in repo_list
        )
        for language, repo_list in repo_list_of_lists
    ),
).encode()

readme = gh.repository("meribold", "github-stars").readme()

if new_readme_content != readme.decoded:
    readme.update("Update list of starred repositories", new_readme_content)
