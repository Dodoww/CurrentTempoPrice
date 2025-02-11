"""Sensor Tempo Prix for Home Assistant."""
import logging
import calendar

from datetime import datetime, time, timedelta
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.event import async_track_time_change,async_track_time_interval
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)

from .const import DOMAIN, TEMPO_COLORS, DEFAULT_PRICES

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Configure the sensor based on configuration entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["sensor_coordinator"]
    
    # OLD METHOD WITH UNIQ SENSOR
    # async_add_entities([TempoPrixSensor(coordinator, entry)], True)

    async_add_entities([
        TempoPrixSensor(coordinator, entry),
        TempoPrixTotalSensor(coordinator, entry)
    ], True)

    async def update_at_fixed_times(event_time):
        """Forcer la mise à jour du capteur à des heures précises."""
        await coordinator.async_request_refresh()

#    async_track_time_interval(hass, update_at_fixed_times, timedelta(minutes=1))

    # Forcer la mise à jour à 00h00, 06h00 et 22h00
    async_track_time_change(hass, update_at_fixed_times, hour=[0, 6, 22], minute=0, second=30)
    
class TempoPrixSensor(CoordinatorEntity, SensorEntity):
    """Represents a Tempo Current Price sensor."""

    _attr_name = "Current Tempo Price"
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
        self.last_update_time = None  # Ajout de l'attribut pour stocker la dernière mise à jour
        self._last_processed_time = None  # Pour éviter les mises à jour redondantes

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
        
        options = self._config_entry.options or DEFAULT_PRICES
        # Utilisez directement self._config_entry.options
        hp_price = options.get(hp_key, DEFAULT_PRICES[hp_key])
        hc_price = options.get(hc_key, DEFAULT_PRICES[hc_key])

        # _LOGGER.debug(
        #     "Prix récupérés pour %s - HP: %s, HC: %s (clés: %s, %s)",
        #     color,
        #     hp_price,
        #     hc_price,
        #     hp_key,
        #     hc_key
        # )
        
        return {"HP": hp_price, "HC": hc_price}

    @property
    def native_value(self):
        """Return the current sensor value (price in €/kWh)."""
        data = self.coordinator.data
        if not data or "today" not in data:
            return None

        # Vérifier si une mise à jour est nécessaire
        current_minute = datetime.now().replace(second=0, microsecond=0)
        if self._last_processed_time == current_minute:
            _LOGGER.debug("Skipping redundant update for minute: %s", current_minute)
            return self._attr_native_value

        self._last_processed_time = current_minute
        _LOGGER.debug("Processing update for minute: %s", current_minute)

        # Le reste de votre logique de calcul existante
        now = datetime.now().time()
        timenow = datetime.now()
        self.last_update_time = timenow.strftime("%d %B %Y at %H:%M:%S")

        # Get colors for yesterday, today and tomorrow
        yesterday_color_code = data.get("yesterday", {}).get("codeJour")
        today_color_code = data.get("today", {}).get("codeJour")
        tomorrow_color_code = data.get("tomorrow", {}).get("codeJour")

        yesterday_color = TEMPO_COLORS.get(yesterday_color_code, "Unknown")
        today_color = TEMPO_COLORS.get(today_color_code, "Unknown")
        tomorrow_color = TEMPO_COLORS.get(tomorrow_color_code, "Unknown")

        if time(0, 0) < now < time(6, 0):
            effective_color = yesterday_color
        else:
            effective_color = today_color

        # Determine HP or HC based on time
        if time(6, 0) <= now < time(22, 00):
            current_tariff = "HP"
        else:
            current_tariff = "HC"

        prices = self.get_current_prices(effective_color)
        current_price = prices[current_tariff]

        self._attr_extra_state_attributes.update({
            "couleur_hier": yesterday_color,
            "couleur_aujourd'hui": today_color,
            "couleur_demain": tomorrow_color,
            "prix_aujourd'hui_hp": f"{prices['HP']:.4f}",
            "prix_aujourd'hui_hc": f"{prices['HC']:.4f}",
            "tarif_actuel": current_tariff,
            "couleur_effective": effective_color,
            "prix_actuel": f"{current_price:.4f}",
            "dernière_mise_à_jour": data.get("last_update", "Unknown"),
            "dernière_mise_à_jour_du_capteur": self.last_update_time,
        })

        self._attr_native_value = f"{current_price:.4f}"
        return self._attr_native_value
    
    def get_days_in_current_month(self):
        """Retourne le nombre de jours dans le mois actuel."""
        today = datetime.now()
        return calendar.monthrange(today.year, today.month)[1]


    @property
    def extra_state_attributes(self):
        """Retourne les attributs supplémentaires du capteur."""
        data = self.coordinator.data
        if not data or "today" not in data:
            return {}

        # Récupérer le nombre de jours du mois actuel
        days_in_month = self.get_days_in_current_month()

        # Autres attributs calculés
        daily_price = self.calculate_daily_price()
        hourly_price = self.calculate_hourly_price()

        self._attr_extra_state_attributes.update({
            "days_in_month": days_in_month,
            "daily_price_abo": f"{daily_price:.4f}",
            "hourly_price_abo": f"{hourly_price:.4f}"
        })

        return self._attr_extra_state_attributes

    def calculate_daily_price(self):    
        """Calcule le prix journalier de l'abonnement."""
        price_abo = self._config_entry.options.get("price_abo", 0)  # Supposons que ce prix soit configuré
        days_in_month = self.get_days_in_current_month()
        return price_abo / days_in_month if days_in_month else 0

    def calculate_hourly_price(self):
        """Calcule le prix horaire de l'abonnement."""
        price_abo = self._config_entry.options.get("price_abo", 0)  # Supposons que ce prix soit configuré
        hours_in_day = 24
        return price_abo / (self.get_days_in_current_month() * hours_in_day) if hours_in_day else 0


class TempoPrixTotalSensor(TempoPrixSensor):
    """Represents a Tempo sensor including the hourly subscription price."""

    _attr_name = "Current Tempo Price with Subscription"
    _attr_unique_id = "total_tempo_price"

    @property
    def native_value(self):
        """Return the total price (€/kWh including hourly subscription)."""
        base_price = super().native_value
        if base_price is None:
            return None

        base_price = float(base_price)

        # Récupérer le prix horaire de l'abonnement
        hourly_price = self.calculate_hourly_price()

        # Calcul du prix total
        total_price = base_price + hourly_price
        return f"{total_price:.7f}"
