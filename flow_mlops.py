"""Orchestrer le pipeline DVC du TP3 avec quatre tâches Prefect."""

import json
import os
from pathlib import Path
import subprocess
import sys

import yaml

# Même serveur dans le terminal, serve et le worker. Une variable existante prime.
os.environ.setdefault("PREFECT_API_URL", "http://127.0.0.1:4200/api")

from prefect import flow, get_run_logger, task
from prefect.cache_policies import NO_CACHE

from verifier_qualite import controler_f1

RACINE = Path(__file__).resolve().parent


@task(retries=2, retry_delay_seconds=10, cache_policy=NO_CACHE)
def rejouer_pipeline():
    env = os.environ.copy()
    # Les commandes `python` de dvc.yaml doivent utiliser le même environnement.
    env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + env.get("PATH", "")
    env["PYTHONIOENCODING"] = "utf-8"
    resultat = subprocess.run(
        [sys.executable, "-m", "dvc", "repro"],
        cwd=RACINE, env=env, capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )
    get_run_logger().info(resultat.stdout[-6000:])
    if resultat.returncode:
        raise RuntimeError(resultat.stderr[-3000:] or resultat.stdout[-3000:])
    return "pipeline rejoue"


@task(cache_policy=NO_CACHE)
def lire_metriques():
    with (RACINE / "reports/metrics.json").open(encoding="utf-8") as fichier:
        return json.load(fichier)


@task(retries=0, cache_policy=NO_CACHE)
def valider(mets):
    with (RACINE / "params.yaml").open(encoding="utf-8") as fichier:
        seuil = yaml.safe_load(fichier)["validation"]["seuil_f1"]
    controler_f1(mets["f1"], seuil)
    get_run_logger().info("F1 %s >= seuil %s : modele accepte", mets["f1"], seuil)
    return True


@task(cache_policy=NO_CACHE)
def notifier(mets):
    # Notification simulée dans les journaux, conformément au sujet.
    get_run_logger().info(
        "NOTIFICATION equipe : nouveau modele valide, F1 = %s", mets["f1"]
    )


@flow(name="reentrainement-fraude", log_prints=True)
def reentrainement():
    rejouer_pipeline()
    mets = lire_metriques()
    valider(mets)
    notifier(mets)
    return mets


if __name__ == "__main__":
    reentrainement()
