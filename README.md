# Current Tempo Price

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Cette intégration pour Home Assistant permet de suivre le prix EDF Tempo en temps réel. Elle fournit deux capteurs :
- Prix actuel du kWh
- Prix actuel du kWh incluant l'abonnement

## Installation


[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Dodoww&repository=CurrentTempoPrice&category=integration)

[![Open your Home Assistant instance and show an integration.](https://my.home-assistant.io/badges/integration.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=current_tempo_price)

1. Utilisez [HACS](https://hacs.xyz/) (Home Assistant Community Store) et ajoutez ce dépôt comme dépôt personnalisé
2. Recherchez "Current Tempo Price" dans HACS et installez-le
3. Redémarrez Home Assistant
4. Allez dans Paramètres -> Appareils et Services -> Ajouter une Intégration
5. Recherchez "Current Tempo Price"

## Configuration

La configuration se fait entièrement via l'interface utilisateur de Home Assistant. 

Une fois l'intégration installée, deux capteurs seront automatiquement créés :

- `sensor.tempo_current_price`
    - Affiche le prix du kWh en fonction de l'heure actuelle et de la couleur du jour
    - Unité : €/kWh

 - `sensor.tempo_total_price`
    - Affiche le prix du kWh incluant le coût de l'abonnement
    - Unité : €/kWh

## Crédits

Cette intégration utilise :
- [API Couleur Tempo](https://www.api-couleur-tempo.fr/) pour la récupération des données Tempo
- [Home Assistant](https://www.home-assistant.io/) pour la plateforme de domotique

