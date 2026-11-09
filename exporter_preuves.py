"""Exporter les états réellement enregistrés par le serveur Prefect local."""

import importlib.metadata
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen

RACINE = Path(__file__).resolve().parent
API = os.environ.get("PREFECT_API_URL", "http://127.0.0.1:4200/api").rstrip("/")


def requete(route, contenu=None):
    req = Request(
        API + route,
        data=None if contenu is None else json.dumps(contenu).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urlopen(req, timeout=30) as reponse:
        return json.load(reponse)


def main():
    runs = requete("/flow_runs/filter", {"limit": 100, "sort": "EXPECTED_START_TIME_DESC"})
    resultats = []
    for run in runs:
        if run["state_type"] not in ("COMPLETED", "FAILED"):
            continue
        tasks = requete("/task_runs/filter", {
            "flow_runs": {"id": {"any_": [run["id"]]}}, "limit": 100,
        })
        resultats.append({
            "id": run["id"], "nom": run["name"], "etat": run["state_name"],
            "debut": run["start_time"], "fin": run["end_time"],
            "duree_secondes": run["total_run_time"],
            "deployment_id": run["deployment_id"],
            "work_pool_name": run.get("work_pool_name"),
            "tasks": [{"nom": t["name"], "etat": t["state_name"]} for t in tasks],
        })
    preuve = {
        "versions": {p: importlib.metadata.version(p) for p in (
            "prefect", "dvc", "scikit-learn", "pandas", "numpy", "mlflow")},
        "executions": resultats,
        "deploiements": requete("/deployments/filter", {"limit": 100}),
        "work_pools": requete("/work_pools/filter", {"limit": 100}),
        "workers": requete("/work_pools/pool-tp/workers/filter", {}),
    }
    echecs = [r for r in resultats if r["nom"] == "TP6-C-modele-refuse"]
    assert echecs and echecs[0]["etat"] == "Failed"
    assert len(echecs[0]["tasks"]) == 3
    assert not any(t["nom"].startswith("notifier-") for t in echecs[0]["tasks"])
    sortie = RACINE / "reports/preuves_prefect.json"
    sortie.write_text(json.dumps(preuve, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{len(resultats)} executions exportees dans {sortie}")


if __name__ == "__main__":
    main()
