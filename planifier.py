"""Déploiement serve : laisser ce processus ouvert pour exécuter les runs."""

from prefect.schedules import Cron

from flow_mlops import reentrainement


if __name__ == "__main__":
    reentrainement.serve(
        name="hebdomadaire",
        schedule=Cron("0 6 * * 1", timezone="Africa/Casablanca"),
        limit=1,
    )
