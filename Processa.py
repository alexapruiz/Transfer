import os
import gitlab
from datetime import datetime, timedelta, timezone

data_corte = datetime.now(timezone.utc) - timedelta(days=30)

GITLAB_URL = "https://gitlab.com"

gl = gitlab.Gitlab(url=GITLAB_URL, private_token="glpat-TQ08L30wzFg1pcBNeZzypW86MQp1OjdjdWZxCw.01.121qm252v")
gl.auth()

PER_PAGE = 100
INCLUDE_SUBGROUPS = True

def iter_all_commits(project, branch_name: str):
    page = 1
    while True:
        commits = project.commits.list(ref_name=branch_name, per_page=PER_PAGE, page=page)
        if not commits:
            break
        for c in commits:
            yield c
        page += 1

# Use iterator=True para evitar o warning do debugger e reduzir memória
for grupo in gl.groups.list(iterator=True, per_page=PER_PAGE):

    obj_grupo = gl.groups.get(grupo.id)

    for projeto in obj_grupo.projects.list(iterator=True, per_page=PER_PAGE, include_subgroups=INCLUDE_SUBGROUPS):
        obj_projeto = gl.projects.get(projeto.id)
        print(f"{grupo.name};{obj_projeto.name};{obj_projeto.http_url_to_repo}")
