from datetime import date
from typing import List

from httpx import AsyncClient, HTTPStatusError, Response

import settings
from app.exceptions import (
    ItemNotFoundError,
    RateLimitExceededError,
    UnhandledExternalError,
)
from app.schemas import Match, PlayerMatch, PlayerProfile, Record
from app.services.parser import DotabuffParser


class DotabuffClient:
    """Dotabuff service to request data."""

    DOTABUFF_BASE_URL = settings.DOTABUFF_BASE_URL

    def __init__(self) -> None:
        """Init method."""
        self.parser = DotabuffParser()

    def _raise_for_status(self, response: Response) -> None:
        """Raise for response status to check errors."""
        try:
            response.raise_for_status()
        except HTTPStatusError as exc:
            if response.status_code == 404:
                raise ItemNotFoundError(str(exc))
            elif response.status_code == 429:
                raise RateLimitExceededError(str(exc))
            elif response.status_code > 500:
                raise UnhandledExternalError(str(exc))
            else:
                raise exc

    async def _request(self, url: str, query_params: dict = None) -> Response:
        """Make request to dotabuff."""
        if query_params is None:
            query_params = {}

        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0"}

        async with AsyncClient(base_url=self.DOTABUFF_BASE_URL) as client:
            response = await client.get(url, params=query_params, headers=headers)

        self._raise_for_status(response)

        return response

    async def get_records(self, player_id: int) -> List[Record]:
        """Get user dota records."""
        url = f"players/{player_id}/records"
        response = await self._request(url)

        return self.parser.parse_records(response.content)

    async def get_matches(self, player_id: int, start_date: date = None, end_date: date = None) -> List[PlayerMatch]:
        """Get list of user matches."""
        url = f"players/{player_id}/matches"
        query_params = {"page": 1}
        results = []

        while True:
            response = await self._request(url, query_params)

            matches = self.parser.parse_matches(response.content)
            results.extend(matches)

            if (
                start_date is None
                or matches[-1].match_info.timestamp.date() < start_date
                or len(matches) < settings.DOTABUFF_PAGE_SIZE
            ):
                break

            query_params["page"] += 1

        if start_date is None:
            start_date = matches[-1].match_info.timestamp.date()
        if end_date is None:
            end_date = date.today()

        return list(filter(lambda x: end_date >= x.match_info.timestamp.date() >= start_date, results))  # type: ignore

    async def get_match(self, match_id: int) -> Match:
        """Get match information."""
        url = f"matches/{match_id}"
        response = await self._request(url)

        return self.parser.parse_match(response.content)

    async def get_player_profile(self, player_id: int) -> PlayerProfile:
        """Get player profile information."""
        url = f"players/{player_id}"
        response = await self._request(url)

        return self.parser.parse_profile(response.content)
