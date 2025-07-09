import requests
import logging
from typing import Optional, Dict, Any, List
import json
import os
import time

logging.basicConfig(level=logging.INFO)

class TennisDataCollector:
    """
    Collects tennis data from the SofaScore API.
    """
    def __init__(self):
        self.base_url = "https://www.sofascore.com/api/v1"
        self.default_headers = {
            'user-agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/121.0.0.0 Safari/537.36'
            )
        }
        self.session = requests.Session()
        self.session.headers.update(self.default_headers)

    def _call_api(self,endpoint: str = "",headers: Optional[Dict[str, str]] = None,method: str = "GET",data: Any = None,json: Any = None
    ) -> Any:
        """
        Makes an HTTP request to the SofaScore API.
        """
        url = self.base_url + endpoint
        req_headers = self.default_headers.copy()
        if headers:
            req_headers.update(headers)
        response = self.session.request(
            method=method,
            url=url,
            headers=req_headers,
            data=data,
            json=json
        )
        response.raise_for_status()
        return response.json()

    def _validate_response(self, data: Any, required_keys: List[str], context: str = "") -> None:
        """
        Validates that the API response is a dictionary and contains the required keys.
        Raises ValueError or KeyError if validation fails.
        """
        if not isinstance(data, dict):
            raise ValueError(f"API response for {context or 'request'} is not a dictionary: {type(data)}")
        for key in required_keys:
            if key not in data:
                raise KeyError(f"Missing expected key '{key}' in API response for {context or 'request'}")

    def get_tournaments(self, save_dir: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Returns a list of ATP tournaments with selected fields.
        Optionally saves the data if save_dir is provided.
        """
        data = self._call_api(
            endpoint="/config/default-unique-tournaments/NL/tennis"
        )
        self._validate_response(data, ["uniqueTournaments"], context="get_tournaments")
        tournaments = data.get("uniqueTournaments", [])
        relevant_fields = ['name', 'slug', 'category', 'tennisPoints', 'id']
        filtered = [
            {k: t.get(k) for k in relevant_fields}
            for t in tournaments
            if t.get("category", {}).get("name") == "ATP"
        ]
        if save_dir:
            self.save_data(filtered, os.path.join(save_dir, "tournaments.json"))
        return filtered

    def get_seasons(self, tournament_id: int, save_dir: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Returns a list of seasons for a given tournament ID.
        Optionally saves the data if save_dir is provided.
        """
        endpoint = f"/unique-tournament/{tournament_id}/seasons"
        data = self._call_api(endpoint=endpoint)
        self._validate_response(data, ["seasons"], context="get_seasons")
        seasons = data.get("seasons", [])
        if save_dir:
            self.save_data(seasons, os.path.join(save_dir, f"seasons_{tournament_id}.json"))
        return seasons

    def get_cuptrees(self, tournament_id: int, season_id: int, save_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Returns the cup trees for a specific tournament season.
        Optionally saves the data if save_dir is provided.
        """
        endpoint = f"/unique-tournament/{tournament_id}/season/{season_id}/cuptrees"
        data = self._call_api(endpoint=endpoint)
        self._validate_response(data, ["cupTrees"], context="get_cuptrees")
        cuptrees = data.get("cupTrees", {})
        if save_dir:
            self.save_data(cuptrees, os.path.join(save_dir, f"cuptrees_{tournament_id}_{season_id}.json"))
        return cuptrees

    def get_players(self) -> List[Dict[str, Any]]:
        """
        Returns players data.
        """
        # Placeholder for future implementation
        return []

    def save_data(self, data: Any, filename: str) -> None:
        """
        Saves the given data to a file in JSON format.
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logging.info("Data successfully saved to %s", filename)
        except Exception as e:
            logging.error("Failed to save data to %s: %s", filename, e)

    def get_all_data(self, max_tournaments: Optional[int] = None, save_dir: Optional[str] = os.path.join("datacollector", "data")) -> Dict[str, Any]:
        """
        Collects and saves data for up to max_tournaments ATP tournaments.
        Data is saved in separate files for tournaments, seasons, and cuptrees.
        Returns a dictionary with all collected data.
        """
        if save_dir:
            os.makedirs(save_dir, exist_ok=True)

        all_data: Dict[str, Any] = {
            "tournaments": [],
            "seasons": {},
            "cuptrees": {}
        }

        tournaments = self.get_tournaments(save_dir=save_dir)
        if max_tournaments is not None:
            tournaments = tournaments[:max_tournaments]
        all_data["tournaments"] = tournaments

        for t in tournaments:
            tid = t["id"]
            try:
                seasons = self.get_seasons(tid, save_dir=save_dir)
                all_data["seasons"][tid] = seasons
                time.sleep(1)  # Add delay between tournament requests
                for season in seasons:
                    sid = season["id"]
                    try:
                        cuptrees = self.get_cuptrees(tid, sid, save_dir=save_dir)
                        all_data["cuptrees"][(tid, sid)] = cuptrees
                    except Exception as e:
                        logging.warning(f"Failed to get cuptrees for tournament {tid} season {sid}: {e}")
                    time.sleep(1)  # Add delay between season requests
            except Exception as e:
                logging.warning(f"Failed to get seasons for tournament {tid}: {e}")

        return all_data

if __name__ == "__main__":
    collector = TennisDataCollector()
    data = collector.get_all_data(max_tournaments=1)
