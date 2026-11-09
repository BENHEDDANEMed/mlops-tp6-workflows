# Orchestrateur ou intégration continue ? (TP06)

| Critère | Prefect (orchestrateur) | GitHub Actions (CI) |
|---|---|---|
| Ce qui déclenche l'exécution | Calendrier cron, Quick run dans l'interface ou appel API ; lundi à 6 h, Africa/Casablanca dans ce projet. | Chaque push et lancement manuel avec workflow_dispatch. |
| Où s'exécute le traitement | Sur le poste qui héberge serve, ou sur la machine du worker relié à pool-tp. | Sur une machine Linux éphémère fournie par GitHub, ubuntu-latest et Python 3.12. |
| Qui surveille, et où | Le serveur Prefect conserve les états et journaux ; l'équipe consulte Runs, Deployments et Work Pools. | GitHub conserve les résultats par commit dans Actions ; l'équipe consulte le job et les rapports téléchargeables. |
| Ce qui se passe en cas d'échec | Deux réessais pour le pipeline ; refus immédiat si F1 < 0,82, état Failed, tâche notifier absente. | Un code de sortie non nul échoue le job ; upload-artifact conserve les rapports même en cas d'échec. |
| Type de tâche adapté | Traitements de données et réentraînements récurrents observables, exécutés sur une infrastructure contrôlée. | Vérifications reproductibles du code et du modèle à chaque modification. |
| Ce qui est versionné dans Git | flow_mlops.py, planifier.py, prefect.yaml, params.yaml et pipeline DVC ; les états d'exécution sont dans le serveur. | .github/workflows/ci.yml, requirements-ci.txt, scripts de génération et verifier_qualite.py. |

## Observations locales

- Modèle normal : max_depth=12, F1=0,8423, précision=0,8698, rappel=0,8166, Completed.
- Modèle dégradé : max_depth=2, F1=0,25, précision=0,9429, rappel=0,1441, Failed dans valider ; notifier n'est pas exécutée.
- Restauration : max_depth=12, F1=0,8423, Completed ; params.yaml et reports/metrics.json identiques à l'état initial.
- La vérification utilisée par la CI renvoie localement les codes 0, 1 et 0 pour ces trois états.
- Les preuves Prefect et les éventuelles preuves GitHub restent distinctes : un test local ne prouve pas l'exécution sur GitHub.

## Observations GitHub Actions

| Essai en ligne | Commit | F1 | Résultat réel |
|---|---|---:|---|
| Run 1, modèle normal | 86386b99 | 0,8423 | success |
| Run 2, modèle volontairement dégradé | e3e6a8e2 | 0,25 | failure à l'étape Verifier la regle de qualite |
| Run 3, restauration avec git revert | 894b0553 | 0,8423 | success |

Les métriques et extraits des journaux téléchargés sont dans `mesures_github.json`.
Les trois exécutions sont consultables dans [GitHub Actions](https://github.com/BENHEDDANEMed/mlops-tp6-workflows/actions).
Les rapports restent disponibles comme artefact, y compris pour le run rouge.

## Conclusion (5 lignes)

La chaîne d'intégration continue valide chaque modification avant son utilisation opérationnelle.  
L'orchestrateur exécute et surveille les traitements récurrents sur le worker disponible.  
La même règle F1 empêche l'acceptation automatique d'un modèle insuffisant.  
Les journaux et les rapports permettent d'identifier l'étape fautive et de corriger la cause.  
Prefect et GitHub Actions sont complémentaires et ne se remplacent pas.
