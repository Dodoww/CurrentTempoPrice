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
        vol.Required("Prix Abonnement", default=data.get("price_abo", 0)): float,
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
            # Convertir les clés du formulaire vers les clés utilisées dans les données
            new_options = {
                "price_abo": user_input["Prix Abonnement"],
                "blue_hc": user_input["BLEU HC"],
                "blue_hp": user_input["BLEU HP"],
                "white_hc": user_input["BLANC HC"],
                "white_hp": user_input["BLANC HP"],
                "red_hc": user_input["ROUGE HC"],
                "red_hp": user_input["ROUGE HP"]
            }

            # Log des nouvelles valeurs
            _LOGGER.debug("Nouvelles options sauvegardées: %s", new_options)

            try:
                # Mettre à jour les options de l'entrée
                return self.async_create_entry(title="", data=new_options)
            except Exception as err:
                _LOGGER.error("Erreur lors de la sauvegarde des options: %s", err)
                errors["base"] = "save_error"

        # Création du schéma avec les valeurs actuelles
        options = self.entry.options or DEFAULT_PRICES
        schema = {
            vol.Required(
                "Prix Abonnement", 
                default=options.get("price_abo", DEFAULT_PRICES["price_abo"])
            ): vol.All(float, vol.Range(min=0)),
            vol.Required(
                "BLEU HC", 
                default=options.get("blue_hc", DEFAULT_PRICES["blue_hc"])
            ): vol.All(float, vol.Range(min=0)),
            vol.Required(
                "BLEU HP", 
                default=options.get("blue_hp", DEFAULT_PRICES["blue_hp"])
            ): vol.All(float, vol.Range(min=0)),
            vol.Required(
                "BLANC HC", 
                default=options.get("white_hc", DEFAULT_PRICES["white_hc"])
            ): vol.All(float, vol.Range(min=0)),
            vol.Required(
                "BLANC HP", 
                default=options.get("white_hp", DEFAULT_PRICES["white_hp"])
            ): vol.All(float, vol.Range(min=0)),
            vol.Required(
                "ROUGE HC", 
                default=options.get("red_hc", DEFAULT_PRICES["red_hc"])
            ): vol.All(float, vol.Range(min=0)),
            vol.Required(
                "ROUGE HP", 
                default=options.get("red_hp", DEFAULT_PRICES["red_hp"])
            ): vol.All(float, vol.Range(min=0))
        }

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(schema),
            errors=errors,
            description_placeholders={
                "step": "0.0001"
            }
        )