import logging
import datetime
from datetime import timedelta
import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, get_tempo_api_url

_LOGGER = logging.getLogger(__name__)

# Ajout de la constante pour Home Assistant
PLATFORMS = ["sensor"]

async def async_setup(hass: HomeAssistant, config: ConfigType):
    """Chargement du composant via configuration.yaml (non utilisé)."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Configuration de l'intégration via l'interface utilisateur."""

    async def async_update_data():
        """Récupérer les nouvelles données de Tempo Prix depuis l'API."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(get_tempo_api_url()) as response:
                    data = await response.json()
                    
                    processed_data = {}
                    today = datetime.datetime.now().date()
                    
                    for item in data:
                        date = datetime.datetime.strptime(item['dateJour'], '%Y-%m-%d').date()
                        if date == today - timedelta(days=1):
                            processed_data['yesterday'] = item
                        elif date == today:
                            processed_data['today'] = item
                        elif date == today + timedelta(days=1):
                            processed_data['tomorrow'] = item
                    
                    processed_data['last_update'] = datetime.datetime.now().strftime("%d %B %Y à %H:%M:%S")
                    return processed_data
                    
        except Exception as err:
            _LOGGER.error("Erreur de mise à jour des données Tempo: %s", err)
            return {}

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_interval=timedelta(hours=1),
        update_method=async_update_data,
    )

    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    # Ajout d'un listener pour les changements d'options
    entry.async_on_unload(
        entry.add_update_listener(_async_update_listener)
    )
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True

async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Gérer les mises à jour des options."""
    await hass.config_entries.async_reload(entry.entry_id)

    
async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Déchargement de l'intégration."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
