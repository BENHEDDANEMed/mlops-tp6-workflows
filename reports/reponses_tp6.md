# Réponses aux questions du TP06

## 1. Deux rôles

Un orchestrateur planifie et exécute les traitements récurrents, suit leurs dépendances et conserve leurs états. La CI vérifie une modification du code dans un environnement reconstruit. Ici, Prefect pilote le réentraînement ; GitHub Actions rejoue le pipeline à chaque push et refuse un F1 insuffisant.

## 2. Lundi, 6 h du matin

L'équipe retrouve dans Prefect le run Failed, l'heure, la tâche fautive, son message d'erreur et les journaux DVC. Lors de notre essai, valider signale F1=0,25 < 0,82 et notifier ne s'exécute pas. La fonction notifier du sujet écrit uniquement un message de succès dans les journaux : elle n'envoie aucun e-mail et ne prévient personne d'un échec. Pour être avertie à 6 h sans consulter l'interface, une vraie équipe doit ajouter une automatisation d'alerte sur les états Failed/Crashed ou les exécutions en retard, avec un canal de notification configuré et testé. Le TP local ne configure pas cette alerte externe.

## 3. Les réessais

Une erreur temporaire du pipeline peut disparaître lors d'un nouvel essai : indisponibilité d'un fichier ou d'une ressource, par exemple. Deux réessais espacés de 10 secondes offrent cette possibilité, pour un maximum de trois tentatives. En revanche, relire le même F1 avec le même seuil ne peut pas améliorer le modèle : réessayer la validation retarderait inutilement le refus. Il faut corriger le modèle ou les données, puis relancer.

## 4. Interface ou fichier

L'interface facilite la lecture des états, le déclenchement manuel et la consultation des journaux. Des changements faits uniquement dans l'interface peuvent toutefois diverger de Git, être difficiles à revoir et disparaître lors d'un redéploiement. Un fichier versionné fournit un historique, une revue et une configuration reproductible. Ici, les définitions Python et prefect.yaml sont la référence ; les essais sont lancés et observés dans l'interface.

## 5. Un autre déclencheur

L'arrivée d'un lot suffisamment grand de nouvelles transactions, ou une dérive des distributions des variables, peut déclencher un réentraînement. Un traitement de surveillance peut comparer les nouveaux lots à une référence, calculer une mesure de dérive et émettre un événement lorsque le seuil est dépassé. Cet événement peut appeler l'API de déploiement Prefect. Il faut dédupliquer les événements et limiter la fréquence des lancements. Cette piste est une proposition, pas une fonctionnalité exécutée dans ce TP.

## 6. Les données de la CI

Le stockage DVC est un dossier local du poste et n'existe pas sur le runner Linux de GitHub. Les scripts donnees.py puis nouvelles_donnees.py reconstruisent les 7 000 transactions v2 avec les graines 7 et 8, sans publier les données brutes dans Git. Dans une vraie équipe, on utilise un stockage distant DVC partagé et accessible par le runner, avec authentification à privilèges limités via les secrets GitHub ou une identité fédérée. On versionne les tickets .dvc et dvc.lock et on contrôle l'accès aux données sensibles. Les fins de ligne CSV peuvent différer entre Windows et Linux ; DVC peut donc recalculer les étapes malgré les mêmes données numériques.
