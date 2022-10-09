import logging
import os
from datetime import datetime, timedelta
from typing import Optional

from dotenv import load_dotenv
from oauthlib.oauth2 import BackendApplicationClient, TokenExpiredError
from requests import HTTPError
from requests_oauthlib import OAuth2Session

from ecowatt_api.ecowatt_day import EcoWattDay, EcoWattValue, EcoWattHour

# logging.basicConfig(level=logging.INFO)
# _LOGGER = logging.getLogger("ecowatt_api.repository")

load_dotenv()
RTE_APP_CLIENT_ID = os.getenv('RTE_APP_CLIENT_ID')
RTE_APP_CLIENT_SECRET = os.getenv('RTE_APP_CLIENT_SECRET')
UPDATE_INTERVAL_MINUTES = 16  # l'api n'accepte pas plus d'une requête toutes les 15 minutes


class EcoWattAPIRepository:
    """A repository exposing common methods to interact with the EcoWatt API"""

    def __init__(self, sandbox_mode=False) -> None:
        if sandbox_mode:
            self.ecowatt_url = f"{self._base_url}/open_api/ecowatt/v4/sandbox/signals"
        else:
            self.ecowatt_url = f"{self._base_url}/open_api/ecowatt/v4/signals"
        client = BackendApplicationClient(client_id=RTE_APP_CLIENT_ID)
        self.session: Optional[OAuth2Session] = OAuth2Session(client=client)
        self.signals: Optional[tuple[EcoWattDay]] = None
        self.last_update: Optional[datetime] = None

    _base_url = "https://digital.iservices.rte-france.com"

    def refresh_oauth_client(self) -> None:
        """Fetch a new OAuth2 token"""
        try:
            self.session.fetch_token(token_url=f"{self._base_url}/token/oauth/",
                                     auth=(RTE_APP_CLIENT_ID, RTE_APP_CLIENT_SECRET))
            logging.debug(f"Fetched a token for RTE API")
        except Exception as e:
            logging.error(f"Error while fetching token for RTE API: {e}")
            raise e

    def get_ecowatt_signals(self) -> dict[str, object]:
        """Fetches the EcoWatt signals from the API"""
        logging.debug("Starting collecting data")
        if self.session is None:
            logging.debug("No client, creating one")
            self.refresh_oauth_client()
        try:
            response = self.session.get(self.ecowatt_url)
            response.raise_for_status()  # permet de lever une exception si le status code de la réponse n'est pas 200
        except (TokenExpiredError, HTTPError):  # si le token a expiré, on le rafraîchit et on relance la requête
            logging.debug("Token expired, refreshing it")
            self.refresh_oauth_client()
            response = self.session.get(self.ecowatt_url)
            response.raise_for_status()
        logging.debug(f"Received data from API:")
        logging.debug(response.json())
        return response.json()

    def fetch_ecowatt_values(self) -> tuple[EcoWattDay]:
        """Fetches the EcoWatt signals from the API and processes them into EcoWattDay objects"""
        # si on a déjà récupéré les données et que la dernière récupération date d'il y a moins de 15 minutes, on ne les
        # récupère pas à nouveau :
        if self.signals is None or self.last_update is None or self.last_update < datetime.now() - timedelta(
                minutes=UPDATE_INTERVAL_MINUTES):
            response_json = self.get_ecowatt_signals()
            self.signals = tuple(EcoWattDay.from_json(day) for day in response_json["signals"])
            self.last_update = datetime.now()
            logging.info("Data fetched from API")
        else:
            logging.info("Using cached data")
        return self.signals
