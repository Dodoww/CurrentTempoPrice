"""Sensor Tempo Prix for Home Assistant."""
import logging
from datetime import datetime, time, timedelta
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)

from .const import DOMAIN, TEMPO_COLORS, PRIX_TEMPO, DEFAULT_PRICES

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Configure the sensor based on configuration entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([TempoPrixSensor(coordinator, entry)], True)

class TempoPrixSensor(CoordinatorEntity, SensorEntity):
    """Represents a Tempo Current Price sensor."""

    _attr_name = "Tempo Current Price"
    _attr_unique_id = "current_tempo_price"
    _attr_native_unit_of_measurement = "€/kWh"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.TOTAL
    
    def __init__(self, coordinator, config_entry):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._attr_native_value = None
        self._attr_extra_state_attributes = {}
        self._attr_should_poll = True
        self._attr_scan_interval = timedelta(minutes=1)

    def get_current_prices(self, color):
        """Get the current prices based on color."""
                
        color_mapping = {
            "BLEU": "blue",
            "BLANC": "white",
            "ROUGE": "red"
        }
        
        color_en = color_mapping.get(color, "blue").lower()
        
        # Construction des clés pour les prix
        hp_key = f"{color_en}_hp"
        hc_key = f"{color_en}_hc"
        
        # Utilisez directement self._config_entry.options
        hp_price = self._config_entry.options.get(hp_key, DEFAULT_PRICES[hp_key])
        hc_price = self._config_entry.options.get(hc_key, DEFAULT_PRICES[hc_key])

        _LOGGER.debug(
            "Prix récupérés pour %s - HP: %s, HC: %s (clés: %s, %s)",
            color,
            hp_price,
            hc_price,
            hp_key,
            hc_key
        )
        
        return {"HP": hp_price, "HC": hc_price}

    @property
    def native_value(self):
        """Return the current sensor value (price in €/kWh)."""
        data = self.coordinator.data
        if not data or "today" not in data:
            return None

        # Current time
        now = datetime.now().time()
        
        # Get colors for yesterday, today and tomorrow
        yesterday_color_code = data.get("yesterday", {}).get("codeJour")
        today_color_code = data.get("today", {}).get("codeJour")
        tomorrow_color_code = data.get("tomorrow", {}).get("codeJour")

        yesterday_color = TEMPO_COLORS.get(yesterday_color_code, "BLEU")
        today_color = TEMPO_COLORS.get(today_color_code, "BLEU")
        tomorrow_color = TEMPO_COLORS.get(tomorrow_color_code, "BLEU")

        # Determine effective color (6h-5h59)
        if now < time(6, 0):
            effective_color = yesterday_color
        else:
            effective_color = today_color

        # Determine HP or HC based on time
        if time(6, 0) <= now < time(22, 0):
            current_tariff = "HP"
        else:
            current_tariff = "HC"

        # Get prices for the effective color
        prices = self.get_current_prices(effective_color)
        current_price = prices[current_tariff]

        # Log pour debug
        _LOGGER.debug(
            "Prix actuels - Couleur: %s, Tarif: %s, Prix: %s, Options: %s",
            effective_color,
            current_tariff,
            current_price,
            self._config_entry.options
        )

        self._attr_extra_state_attributes = {
            "couleur_hier": yesterday_color,
            "couleur_aujourd'hui": today_color,
            "couleur_demain": tomorrow_color,
            "prix_aujourd'hui_hp": f"{prices['HP']:.4f}",
            "prix_aujourd'hui_hc": f"{prices['HC']:.4f}",
            "tarif_actuel": current_tariff,
            "couleur_effective": effective_color,
            "prix_actuel": f"{current_price:.4f}",
            "dernière_mise_à_jour": data.get("last_update", "Inconnue"),
        }

        return f"{current_price:.4f}"

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        return self._attr_extra_state_attributes
