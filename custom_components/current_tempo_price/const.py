from datetime import datetime, timedelta

DOMAIN = "current_tempo_price"

# New unified API endpoint
TEMPO_API_BASE_URL = "https://www.api-couleur-tempo.fr/api/joursTempo"

def get_tempo_api_url():
    """Generate the API URL with the required dates."""
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)
    
    return f"{TEMPO_API_BASE_URL}?dateJour[]={yesterday}&dateJour[]={today}&dateJour[]={tomorrow}"

# Rest of the constants remain unchanged
DEFAULT_PRICES = {
    "blue_hc": 0.1288,
    "blue_hp": 0.1552,
    "white_hc": 0.1447,
    "white_hp": 0.1792,
    "red_hc": 0.1518,
    "red_hp": 0.6586,
    "price_abo": 13.97",
}

TEMPO_COLORS = {
    1: "BLEU",
    2: "BLANC",
    3: "ROUGE",
}   