"""Config flow pour le composant Tempo Prix."""

import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN, DEFAULT_PRICES

_LOGGER = logging.getLogger(__name__)

# Schéma principal de configuration (nom de l'intégration)
CONFIG_SCHEMA = vol.Schema({
    vol.Required("name", default="Prix Tempo EDF"): str
})

# Schéma des options pour modifier les tarifs
def generate_options_schema(data):
    """Génère dynamiquement le formulaire avec les valeurs existantes."""
    return vol.Schema({
        vol.Required("BLEU HC", default=data.get("blue_hc", DEFAULT_PRICES["blue_hc"])): float,
        vol.Required("BLEU HP", default=data.get("blue_hp", DEFAULT_PRICES["blue_hp"])): float,
        vol.Required("BLANC HC", default=data.get("white_hc", DEFAULT_PRICES["white_hc"])): float,
        vol.Required("BLANC HP", default=data.get("white_hp", DEFAULT_PRICES["white_hp"])): float,
        vol.Required("ROUGE HC", default=data.get("red_hc", DEFAULT_PRICES["red_hc"])): float,
        vol.Required("ROUGE HP", default=data.get("red_hp", DEFAULT_PRICES["red_hp"])): float,
    })

class TempoPrixConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Gère le flux de configuration pour l'intégration Tempo Prix."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Gère la configuration initiale depuis l'UI."""
        errors = {}

        if user_input is not None:
            return self.async_create_entry(title=user_input["name"], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=CONFIG_SCHEMA,
            errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(entry):
        """Retourne le gestionnaire des options."""
        return TempoPrixOptionsFlow(entry)

class TempoPrixOptionsFlow(config_entries.OptionsFlow):
    """Gestion des options après installation."""

    def __init__(self, entry):
        self.entry = entry

    async def async_step_init(self, user_input=None):
        """Gère la page des options (modification des tarifs)."""
        errors = {}

        if user_input is not None:
            # Stocke les nouvelles valeurs
            result = self.async_create_entry(title="", data=user_input)
            
            # Déclenche une mise à jour immédiate du coordinator
            coordinator = self.hass.data[DOMAIN][self.entry.entry_id]
            await coordinator.async_request_refresh()
            
            return result

        # Création du schéma avec step de 0.0001 pour tous les champs de prix
        schema = {
            vol.Required(
                "blue_hp", 
                default=self.entry.options.get("blue_hp", DEFAULT_PRICES["blue_hp"])
            ): vol.All(float, vol.Range(min=0)),
            vol.Required(
                "blue_hc", 
                default=self.entry.options.get("blue_hc", DEFAULT_PRICES["blue_hc"])
            ): vol.All(float, vol.Range(min=0)),
            vol.Required(
                "white_hp", 
                default=self.entry.options.get("white_hp", DEFAULT_PRICES["white_hp"])
            ): vol.All(float, vol.Range(min=0)),
            vol.Required(
                "white_hc", 
                default=self.entry.options.get("white_hc", DEFAULT_PRICES["white_hc"])
            ): vol.All(float, vol.Range(min=0)),
            vol.Required(
                "red_hp", 
                default=self.entry.options.get("red_hp", DEFAULT_PRICES["red_hp"])
            ): vol.All(float, vol.Range(min=0)),
            vol.Required(
                "red_hc", 
                default=self.entry.options.get("red_hc", DEFAULT_PRICES["red_hc"])
            ): vol.All(float, vol.Range(min=0)),
        }

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(schema),
            errors=errors,
            description_placeholders={
                "step": "0.0001"  # Indique le pas dans la description
            }
        )                                                                                      
