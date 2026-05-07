import csv
import requests
from requests.auth import HTTPBasicAuth


ORG = "SUA_ORG"
PROJECT = "SEU_PROJETO"
PAT = "SEU_PAT"

API_VERSION = "7.1"
AUTH = HTTPBasicAuth("", PAT)

OUTPUT_CSV = "workitems_por_sprint.csv"


def get_json(url):
    response = requests.get(url, auth=AUTH)
    response.raise_for_status()
    return response.json()


def chunks(lista, tamanho=200):
    for i in range(0, len(lista), tamanho):
        yield lista[i:i + tamanho]


def listar_teams():
    url = (
        f"https://dev.azure.com/{ORG}/_apis/projects/{PROJECT}/teams"
        f"?api-version={API_VERSION}"
    )
    return get_json(url).get("value", [])


def listar_sprints_do_team(team_name):
    url = (
        f"https://dev.azure.com/{ORG}/{PROJECT}/{team_name}"
        f"/_apis/work/teamsettings/iterations"
        f"?api-version={API_VERSION}"
    )
    return get_json(url).get("value", [])


def listar_ids_workitems_da_sprint(team_name, iteration_id):
    url = (
        f"https://dev.azure.com/{ORG}/{PROJECT}/{team_name}"
        f"/_apis/work/teamsettings/iterations/{iteration_id}/workitems"
        f"?api-version={API_VERSION}"
    )

    data = get_json(url)

    ids = []
    for rel in data.get("workItemRelations", []):
        target = rel.get("target") or {}
        wid = target.get("id")
        if wid:
            ids.append(wid)

    return ids


def buscar_detalhes_workitems(ids):
    if not ids:
        return []

    detalhes = []

    fields = [
        "System.Id",
        "System.Title",
        "System.WorkItemType",
        "System.AssignedTo",
        "System.State",
        "Microsoft.VSTS.Common.StateChangeDate",
        "System.Tags",
        "System.CreatedDate",
        "System.ChangedDate",
        "System.IterationPath",
        "System.AreaPath"
    ]

    for lote in chunks(ids, 200):
        ids_param = ",".join(map(str, lote))
        fields_param = ",".join(fields)

        url = (
            f"https://dev.azure.com/{ORG}/{PROJECT}/_apis/wit/workitems"
            f"?ids={ids_param}"
            f"&fields={fields_param}"
            f"&api-version={API_VERSION}"
        )

        data = get_json(url)
        detalhes.extend(data.get("value", []))

    return detalhes


def get_assigned_to(fields):
    assigned = fields.get("System.AssignedTo")

    if isinstance(assigned, dict):
        return assigned.get("displayName")

    return assigned


def main():
    linhas = []

    teams = listar_teams()
    print(f"Total de teams encontrados: {len(teams)}")

    for team in teams:
        team_name = team.get("name")
        print(f"\nTeam: {team_name}")

        sprints = listar_sprints_do_team(team_name)
        print(f"  Sprints encontradas: {len(sprints)}")

        for sprint in sprints:
            sprint_id = sprint.get("id")
            sprint_name = sprint.get("name")
            sprint_path = sprint.get("path")
            attributes = sprint.get("attributes") or {}

            print(f"  Sprint: {sprint_name}")

            ids = listar_ids_workitems_da_sprint(team_name, sprint_id)
            print(f"    Work items: {len(ids)}")

            workitems = buscar_detalhes_workitems(ids)

            for wi in workitems:
                fields = wi.get("fields", {})

                linhas.append({
                    "team": team_name,
                    "sprint_id": sprint_id,
                    "sprint_name": sprint_name,
                    "sprint_path": sprint_path,
                    "sprint_start_date": attributes.get("startDate"),
                    "sprint_finish_date": attributes.get("finishDate"),
                    "sprint_timeframe": attributes.get("timeFrame"),

                    "work_item_id": wi.get("id"),
                    "work_item_type": fields.get("System.WorkItemType"),
                    "title": fields.get("System.Title"),
                    "assigned_to": get_assigned_to(fields),
                    "state": fields.get("System.State"),
                    "state_change_date": fields.get("Microsoft.VSTS.Common.StateChangeDate"),
                    "tags": fields.get("System.Tags"),
                    "created_date": fields.get("System.CreatedDate"),
                    "changed_date": fields.get("System.ChangedDate"),
                    "iteration_path": fields.get("System.IterationPath"),
                    "area_path": fields.get("System.AreaPath"),
                })

    salvar_csv(linhas)
    print(f"\nArquivo gerado: {OUTPUT_CSV}")
    print(f"Total de linhas: {len(linhas)}")


def salvar_csv(linhas):
    campos = [
        "team",
        "sprint_id",
        "sprint_name",
        "sprint_path",
        "sprint_start_date",
        "sprint_finish_date",
        "sprint_timeframe",
        "work_item_id",
        "work_item_type",
        "title",
        "assigned_to",
        "state",
        "state_change_date",
        "tags",
        "created_date",
        "changed_date",
        "iteration_path",
        "area_path",
    ]

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(linhas)


if __name__ == "__main__":
    main()
