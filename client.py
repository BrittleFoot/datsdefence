import json
from functools import wraps
from logging import basicConfig, getLogger
from os import environ

import requests
from dotenv import load_dotenv

load_dotenv()

TEST = "https://games-test.datsteam.dev/"
PROD = "https://games.datsteam.dev/"

KEY = environ["DAD_TOKEN"]


basicConfig(
    level="INFO",
    format="[%(name)s][%(levelname)s] %(message)s",
)


class ApiClient:
    def __init__(self, name):
        self.name = name
        self.base = TEST if name == "test" else PROD
        logger_name = __name__ + "." + name
        self.logger = getLogger(logger_name)

    ######################################
    # Boilerplate code for requests
    ######################################

    @wraps(requests.get)
    def get(self, url, **kwargs):
        """
        requests.get wrapper
        """
        return self.request("GET", url, **kwargs)

    @wraps(requests.get)
    def post(self, url, **kwargs):
        """
        requests.post wrapper
        """
        return self.request("POST", url, **kwargs)

    @wraps(requests.get)
    def put(self, url, **kwargs):
        """
        requests.put wrapper
        """
        return self.request("PUT", url, **kwargs)

    @wraps(requests.request)
    def request(self, method, url, **kwargs):
        """
        requests.request wrapper
        """
        # todo: implement retry / wait logic here
        response = self._request(method, url, **kwargs)

        return response

    def _request(self, method, url, **kwargs):
        """
        url without base - 'api/v1/games'
        requests.request wrapper
        """
        try:
            fullurl = self.base + url
            kwargs["headers"] = {
                **kwargs.get("headers", {}),
                "X-Auth-Token": KEY,
            }
            response = requests.request(method, fullurl, **kwargs)
        except Exception as e:
            self.logger.error(f"request error: {e}")
            raise

        self.logger.debug(f"{response.status_code} {method} /{url} ")

        if response.status_code >= 300:
            raise Exception(json.dumps(response.json(), indent=2))

        return response.json()

    ######################################
    ######################################
    ######################################
    ######################################
    ######################################

    def rounds(self):
        rounds = self.get("rounds/zombidef")
        rounds["rounds"] = [r for r in rounds["rounds"] if r["status"] != "ended"]
        return rounds

    def world(self):
        return self.get("play/zombidef/world")

    def units(self):
        return self.get("play/zombidef/units")

    def participate(self):
        return self.put("play/zombidef/participate")

    def command(self, commands):
        return self.post("play/zombidef/command", json=commands)


api_test = ApiClient("test")
api_prod = ApiClient("prod")
