# TP06 - Automatiser les workflows MLOps

BENHEDDANE Mohamed - 5IASD - G8

Le pipeline de détection de fraude du TP3 est conservé dans `dvc.yaml`.
Prefect orchestre quatre tâches : rejouer le pipeline, lire les métriques,
valider le seuil F1, puis écrire une notification simulée dans les journaux.
GitHub Actions régénère les données v2 et applique la même règle de qualité.

## Résultats réellement vérifiés

| Essai | F1 | Résultat |
|---|---:|---|
| Modèle normal, profondeur 12 | 0,8423 | Completed, quatre tâches |
| Modèle dégradé, profondeur 2 | 0,25 | Failed dans valider ; notifier absente |
| Modèle restauré, profondeur 12 | 0,8423 | Completed |
| Quick run avec serve | 0,8423 | Completed |
| Quick run sur pool-tp via le worker | 0,8423 | Completed |

Les preuves détaillées sont dans `reports/essais_tp6.json` et
`reports/preuves_prefect.json`. La vérification en ligne est documentée
séparément après les exécutions de GitHub Actions.

## Reprendre le TP sous PowerShell

Depuis `C:\Users\pc\Documents\mlops-workspace\tp6-workflows` :

```powershell
# Terminal 1 : serveur local et interface http://127.0.0.1:4200
.\demarrer.ps1 -Role serveur

# Terminal 2 : exécution directe puis vérification indépendante
.\demarrer.ps1 -Role workflow
.\demarrer.ps1 -Role qualite

# Terminal 3 : variante serve, à laisser ouverte pour les Quick runs
.\demarrer.ps1 -Role serve
```

Pour utiliser le work pool, arrêter serve avec Ctrl+C, puis :

```powershell
# Terminal 2 : enregistrer le déploiement de prefect.yaml
.\demarrer.ps1 -Role pool

# Terminal 3 : démarrer le worker
.\demarrer.ps1 -Role worker
```

Dans Prefect, ouvrir Deployments, sélectionner `hebdomadaire` ou
`hebdomadaire-pool`, puis Run > Quick run. Les deux déploiements utilisent
`0 6 * * 1` et le fuseau `Africa/Casablanca`. Le serveur et le processus
d'exécution doivent rester actifs pour que les runs démarrent.

Le script PowerShell place la base Prefect dans `.prefect/`, à l'intérieur
du projet, et définit l'API locale pour chaque commande. Il n'est donc pas
nécessaire de modifier le profil Prefect global du poste.

## Refaire les essais de refus et de restauration

```powershell
$env:PREFECT_HOME = Join-Path (Get-Location) '.prefect'
$env:PREFECT_API_URL = 'http://127.0.0.1:4200/api'
& .\.venv\Scripts\python.exe essais_tp6.py
& .\.venv\Scripts\python.exe exporter_preuves.py
```

`essais_tp6.py` restaure les octets originaux de `params.yaml` même si
l'essai de refus échoue. L'état final doit contenir `max_depth: 12`.
Les journaux seuls simulent la notification ; aucune alerte externe
d'échec n'est configurée dans ce TP.

## Environnement et CI

- Poste : Python 3.14.7, Prefect 3.9.2 et DVC 3.67.1.
- CI : Ubuntu fourni par GitHub, Python 3.12, dépendances numériques figées
  dans `requirements-ci.txt` d'après l'environnement testé.
- Le runner ne dispose pas du stockage DVC local. `donnees.py` puis
  `nouvelles_donnees.py` recréent les 7 000 transactions avec les graines fixes.
- `verifier_qualite.py` renvoie 1 pour F1 < 0,82, et 0 pour un modèle accepté.
- Les rapports de métriques et la matrice de confusion sont conservés par
  `upload-artifact`, y compris quand la règle de qualité échoue.
- Les fichiers Python du TP3 sont inchangés. Le recalcul initial de `dvc.lock`
  enregistre leurs empreintes CRLF sous Windows ; le F1 reste 0,8423.

## Documents

- `reports/tp6_synthese.md` : comparaison Prefect / intégration continue.
- `reports/reponses_tp6.md` : réponses argumentées aux six questions.
- Le rapport PDF réunit les résultats et les captures de l'interface.

Le dépôt source du TP3 conserve son historique et ses tags v1/v2 ; le TP6
est publié dans un dépôt séparé. Aucun e-mail n'est envoyé automatiquement.
