# aeoi - Résumé pour les associations et leurs membres

État : septembre 2026. Pour les fiduciaires, trust companies, family offices et gérants de
fortune qui transmettent à l'AFC les déclarations EAR (CRS) de leurs véhicules. Une page ; les
justificatifs techniques sont dans les pages allemandes `docs/de/WAS-AENDERT-SICH-MIT-3.0.md` et
`docs/de/ANLEITUNG.md`. Les citations proviennent de l'édition française de la Directive
technique de l'AFC (septembre 2026).

## De quoi il s'agit

Les déclarations pour l'année 2026 (délai 30 juin 2027, art. 15, al. 1, LEAR) sont les premières
à devoir être établies dans le nouveau schéma OCDE CRS 3.0. Le portail de l'AFC : « Jusqu'au
14.12.2026 seule la version 2.0 est supportée. A partir du 16.1.2027 seule la version 3.0 est
supportée. » (Directive technique, chiffre 5.3.1). Le schéma 3.0 exige pour chaque compte de
nouvelles indications obligatoires (autocertification, procédure de diligence, type de compte,
type des personnes détenant le contrôle) ; un fichier dans l'ancienne structure sera rejeté dès
janvier. Qui établissait jusqu'ici ses déclarations avec le formulaire en ligne ou un script
maison doit adapter son processus.

## Ce qu'est aeoi

`aeoi` est un outil ouvert (Apache-2.0, code source consultable) qui crée le fichier CRS-XML à
partir d'un tableau Excel et le vérifie **avant** le téléchargement, comme le fait le portail :

- schéma OCDE 2.0 et 3.0, jeu de caractères, États partenaires de l'année de déclaration, clés
  de contrôle IBAN/ISIN ;
- 59 des 65 règles de la Directive technique, avec le code d'erreur et le texte de l'AFC. Les six
  autres (transport, déchiffrement, antivirus, enregistrement de l'institution) ne peuvent être
  vérifiées que par le portail ;
- chiffrement et empaquetage selon le chiffre 3.3.1, déclarations test avec les marqueurs
  corrects ;
- un registre local des déclarations envoyées, pour que corrections et annulations portent les
  bonnes références (chiffre 6), y compris lors du passage de la 2.0 à la 3.0 ; un registre
  perdu se reconstruit à partir des fichiers XML envoyés ;
- lecture de la réponse du portail : chaque code est expliqué.

Qui ne veut rien installer fait tout le flux sur une page web, directement dans le navigateur, en
français, italien ou allemand : télécharger le modèle, vérifier le modèle rempli, créer et
chiffrer la déclaration, saisir le résultat du portail, corriger l'année suivante. Le fichier ne
quitte pas le navigateur ; après la première visite, la page fonctionne aussi hors ligne. Le
téléchargement sur le portail EAR reste à l'institution.

## Ce qu'aeoi n'est pas

Pas de téléchargement : l'institution télécharge elle-même le paquet sur le portail EAR, comme
aujourd'hui. Pas de conseil sur l'obligation de déclarer ni sur la classification des comptes.
Pas de garantie avant le projet pilote : l'outil est construit sur les schémas publiés et sur la
Directive technique et couvert par 187 tests automatiques, mais seule une déclaration test via le
portail montre si l'AFC lit les fichiers de la même manière.

## Protection des données

Tout s'exécute sur l'ordinateur de l'institution ; les données de comptes ne le quittent pas. La
page web n'a ni serveur, ni analytique, ni journal ; une règle de sécurité du navigateur empêche
que la moindre adresse soit contactée après le choix du fichier. L'outil n'exige aucune
inscription et n'envoie rien à personne.

## Coûts

L'outil est et reste gratuit. **Pro** achète ce qui va au dossier : un procès-verbal de
contrôle (PDF) pour chaque contrôle et chaque déclaration créée - hash du fichier, constatations,
chaque règle vérifiée, identifiants et hashs du fichier envoyé -, la vue d'ensemble de tous les
véhicules (avant le 16.01.2027) et le support pendant la saison de déclaration. Prix **par
véhicule**, pour pouvoir le refacturer : 120 CHF par véhicule et par an, minimum 900 CHF par
organisation, utilisateurs illimités. Une fois 450 CHF : la première déclaration accompagnée (une
heure en ligne, aussi sans abonnement). Les institutions pilotes reçoivent Pro gratuitement la
première année.

## Ce que nous cherchons maintenant : une à trois institutions pilotes

Une institution financière déclarante enregistrée, avec accès aux déclarations test du portail
EAR, qui

1. en novembre 2026 télécharge une déclaration test dans le schéma 2.0 (vérifie la voie de
   transport : chiffrement, paquet, identifiants),
2. dans la semaine du 16 janvier 2027 télécharge une déclaration test dans le schéma 3.0,
3. nous communique ensuite uniquement les codes et identifiants de la confirmation de validation
   du portail - jamais le fichier, jamais de données de comptes.

Charge : environ une heure par déclaration test. Les déclarations test sont validées par le
portail, non transmises, et « sont effacées chaque semaine pendant la nuit du samedi au
dimanche » (chiffre 5.3.5). Les questions ouvertes sur la pratique de l'AFC, auxquelles le pilote
répond, sont dans `docs/OPEN-QUESTIONS.md`.

Contact : <nom, e-mail> - Code source et guide : https://github.com/aeoi-com/aeoi - Vérification dans le navigateur : https://meldbar.ch/
