# Calendrier Saint-Nicolas-du-Chardonnet

Ce projet permet de générer automatiquement des calendriers (fichiers `.ics`) pour la paroisse Saint-Nicolas-du-Chardonnet. Les calendriers sont mis à jour quotidiennement en analysant le site officiel grâce à l'IA (Google Gemini).

## Calendriers disponibles

Une fois le projet mis en place sur GitHub, vous pourrez vous abonner à ces calendriers en utilisant les liens suivants (remplacez `VOTRE_USER` et `VOTRE_REPO` par votre nom d'utilisateur et le nom de votre dépôt) :

- **Messes et Offices** : `https://raw.githubusercontent.com/Vit73520/Calendrier_Saint_nicolas/master/messes.ics`
- **Conférences et Cours** : `https://raw.githubusercontent.com/Vit73520/Calendrier_Saint_nicolas/master/conferences.ics`
- **Permanence des prêtres** : `https://raw.githubusercontent.com/Vit73520/Calendrier_Saint_nicolas/master/permanence.ics`

## Comment s'abonner (iOS)

1. Allez dans **Réglages** > **Calendrier** > **Comptes** > **Ajouter un compte**.
2. Choisissez **Autre**, puis **Ajouter un cal. avec abonnement**.
3. Collez le lien du fichier `.ics` souhaité (ex: le lien vers `messes.ics` ci-dessus) et cliquez sur **Suivant** puis **Enregistrer**.

## Comment s'abonner (Android / Google Calendar)

1. Ouvrez Google Calendar sur un ordinateur.
2. Dans le menu de gauche, à côté de "Autres agendas", cliquez sur **+** puis sur **À partir de l'URL**.
3. Collez le lien du fichier `.ics` souhaité.
4. Cliquez sur **Ajouter l'agenda**. L'agenda se synchronisera ensuite sur votre téléphone Android.

## Configuration (Pour l'administrateur)

Pour que l'automatisation GitHub Actions fonctionne correctement :

1. Poussez ce dépôt sur GitHub.
2. Allez dans les paramètres de votre dépôt GitHub (**Settings**).
3. Dans la barre latérale gauche, cliquez sur **Secrets and variables** > **Actions**.
4. Cliquez sur **New repository secret**.
5. Ajoutez un secret avec :
   - **Name**: `GEMINI_API_KEY`
   - **Secret**: Votre clé d'API Google Gemini (que vous pouvez obtenir sur Google AI Studio).
6. Le script s'exécutera automatiquement chaque jour à minuit. Vous pouvez aussi le lancer manuellement dans l'onglet **Actions**.

## Exécution locale

```bash
pip install -r requirements.txt
export GEMINI_API_KEY="votre_cle_api"
python scraper.py
```
