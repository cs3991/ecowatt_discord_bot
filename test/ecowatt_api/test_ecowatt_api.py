import json

from ecowatt_api import EcoWattAPIRepository


def test_instantiate():
    repo = EcoWattAPIRepository()
    assert repo is not None
    assert repo.session is not None
    assert repo.ecowatt_url == "https://digital.iservices.rte-france.com/open_api/ecowatt/v4/signals"
    assert repo.signals is None
    assert repo.last_update is None


def test_instantiate_sandbox():
    repo = EcoWattAPIRepository(sandbox_mode=True)
    assert repo is not None
    assert repo.session is not None
    assert repo.ecowatt_url == "https://digital.iservices.rte-france.com/open_api/ecowatt/v4/sandbox/signals"
    assert repo.signals is None
    assert repo.last_update is None


class TestEcoWattAPIRepository:
    def setup_method(self):
        self.repo = EcoWattAPIRepository(sandbox_mode=True)
        with open('ecowatt_api/json_responses.json', 'r', encoding='utf8') as f:
            self.sandbox_response_json = json.load(f)

    def test_refresh_oauth_client(self):
        assert self.repo.session.token.get("access_token") is None
        self.repo.refresh_oauth_client()
        assert self.repo.session is not None
        assert self.repo.session.token is not None
        assert self.repo.session.token["access_token"] is not None

    def test_get_ecowatt_signals(self):
        response = self.repo.get_ecowatt_signals()
        assert response == self.sandbox_response_json

    def test_token_expired(self):
        self.repo.refresh_oauth_client()
        self.repo.session.token["access_token"] = "efe112e1223"
        response = self.repo.get_ecowatt_signals()
        assert response == self.sandbox_response_json
        self.repo.session.token["expires_at"] = 0
        response = self.repo.get_ecowatt_signals()
        assert response == self.sandbox_response_json
