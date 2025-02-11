import logging
import datetime
from datetime import timedelta
import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.event import async_track_time_change, async_track_time_interval
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, get_tempo_api_url

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]

async def async_setup(hass: HomeAssistant, config: ConfigType):
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Configurer l'intégration via l'interface utilisateur."""
    
    hass.data.setdefault(DOMAIN, {})["tempo_data"] = {}

    async def async_update_data():
        """Récupérer les données de l'API Tempo."""
        _LOGGER.info(f"⏳ Mise à jour de l'API à {datetime.datetime.now()}")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(get_tempo_api_url()) as response:
                    data = await response.json()
                    # _LOGGER.debug("Données récupérées depuis l'API : %s", data)

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
                    
                    processed_data['last_update'] = datetime.datetime.now().strftime("%d %B %Y at %H:%M:%S")
                    
                    hass.data[DOMAIN]["tempo_data"] = processed_data
                    # _LOGGER.info(f"✅ Mise à jour API terminée à {datetime.datetime.now()}")
                    return processed_data
                    
        except Exception as err:
            _LOGGER.error("Erreur lors de la mise à jour des données Tempo : %s", err)
            raise UpdateFailed(f"Tempo API error: {err}")

    # Créer le coordinateur API
    api_coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"{DOMAIN}_api",
        update_method=async_update_data,
    )

    # Fonction de mise à jour périodique explicite
    async def force_api_update(now=None):
        """Force une mise à jour du coordinator."""
        _LOGGER.info(f"🔄 Forçage de la mise à jour API à {datetime.datetime.now()}")
        await api_coordinator.async_refresh()

    # Programmation de la mise à jour toutes les 3 minutes
    unsubscribe_interval = async_track_time_interval(
        hass,
        force_api_update,
        timedelta(hours=1)
    )

    # S'assurer que l'intervalle est nettoyé lors du déchargement
    entry.async_on_unload(unsubscribe_interval)

    # Forcer la première mise à jour -> necessaire, si non renseigné, API ne se met pas a jours et le sensor ne s'initialise pas
    await api_coordinator.async_config_entry_first_refresh()

    async def async_fetch_cached_data():
        """Renvoyer les dernières données disponibles."""
        return hass.data[DOMAIN].get("tempo_data", {})

    # Coordinateur pour les sensors
    sensor_coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"{DOMAIN}_sensor",
        update_interval=timedelta(minutes=1),
        update_method=async_fetch_cached_data,
    )

    # Mise à jour initiale du sensor
    # await sensor_coordinator.async_refresh()

    # Planifier la mise à jour du sensor à chaque minute
    async def update_sensor_at_exactly_00(event_time):
        await sensor_coordinator.async_refresh()

    async_track_time_change(
        hass, update_sensor_at_exactly_00, minute="*", second=0
    )

    # Stocker les coordonnateurs
    hass.data[DOMAIN][entry.entry_id] = {
        "api_coordinator": api_coordinator,
        "sensor_coordinator": sensor_coordinator,
    }
    
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True

async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Gérer les mises à jour des options."""
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Désinstaller l'intégration."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)