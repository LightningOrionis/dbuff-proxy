import re
from datetime import datetime, time
from typing import List

from bs4 import BeautifulSoup

from app.constants import Team
from app.schemas import PlayerMatch, PlayerProfile, Match, Record, BaseMatchHero, MatchInfo, AdvancedMatchHero


class DotabuffParser:
    """Dotabuff parser service."""
    def _parse_time(self, time_str: str) -> time:
        """Parses time string into time object."""
        if time_str.count(":") == 1:
            hours = 0
            minutes, seconds = time_str.split(":")
        else:
            hours, minutes, seconds = time_str.split(":")

        hours, minutes, seconds = int(hours), int(minutes), int(seconds)

        return time(hours, minutes, seconds)

    def _parse_thousands_from_k(self, s: str) -> str:
        """Parses K to thousands, e.g. 24.1K -> 24100."""
        s = s.replace("k", "")
        s = s.replace("-", "0.0")
        thousands, hundreds = [int(i) for i in s.split(".")]
        return thousands * 1000 + hundreds * 100

    def parse_matches(self, data: str) -> List[PlayerMatch]:
        """Parse matches data."""
        matches = []
        soup = BeautifulSoup(data)
        table = soup.table
        rows = table.tbody.find_all("tr")

        for row in rows:
            columns = row.find_all("td")

            # Hero info
            hero_name = columns[1].find("a").text
            kda = columns[6].text
            kills, deaths, assists = kda.split("/")

            match_result = columns[3].find("a").text.split(" ")[0]

            # Match info
            game_mode = columns[4].div.text
            lobby_type = columns[4].text.replace(game_mode, "")[:6]  # TODO: Add replace of x2
            timestamp = datetime.fromisoformat(columns[3].div.time["datetime"])
            duration = self._parse_time(columns[5].text)

            hero = BaseMatchHero(hero_name=hero_name, kills=kills, deaths=deaths, assists=assists)
            match_info = MatchInfo(game_mode=game_mode, timestamp=timestamp, lobby_type=lobby_type, duration=duration)
            match = PlayerMatch(hero=hero, match_info=match_info, result=match_result)

            matches.append(match)

        return matches

    def parse_match(self, data: str) -> Match:
        """Parse match data."""
        soup = BeautifulSoup(data)

        # match info component
        match_info_component_lines = soup.find("div", {"class": "header-content-secondary"}).find_all("dl")
        lobby_type = match_info_component_lines[0].dd.text
        game_mode = match_info_component_lines[1].dd.text
        duration = self._parse_time(match_info_component_lines[3].dd.text)
        timestamp = datetime.fromisoformat(match_info_component_lines[4].dd.time["datetime"])
        match_info = MatchInfo(duration=duration, game_mode=game_mode, timestamp=timestamp, lobby_type=lobby_type)

        # hero-player component
        heroes = []
        team_results = soup.find("div", {"class": "team-results"})
        results = [
            *team_results.find("section", {"class": "radiant"}).tbody.find_all("tr"),
            *team_results.find("section", {"class": "dire"}).tbody.find_all("tr"),
        ]
        for result in results:
            columns = result.find_all("td")
            hero_name = " ".join([word.capitalize() for word in columns[0].a["href"].split("/")[-1].split("-")])
            player_id = int(columns[3].a["href"].split("/")[-1])
            to_int_columns = [5, 6, 7, 9, 11, 12, 14]
            to_parse_from_k_columns = [8, 15, 17, 16]
            kills, deaths, assists, last_hits, denies, gpm, xpm = map(lambda x: int(columns[x].text), to_int_columns)
            net_worth, hero_damage, tower_damage, heal = map(
                lambda x: self._parse_thousands_from_k(columns[x].text), to_parse_from_k_columns
            )
            heroes.append(
                AdvancedMatchHero(
                    hero_name=hero_name,
                    player_id=player_id,
                    kills=kills,
                    deaths=deaths,
                    assists=assists,
                    last_hits=last_hits,
                    denies=denies,
                    gpm=gpm,
                    xpm=xpm,
                    net_worth=net_worth,
                    hero_damage=hero_damage,
                    tower_damage=tower_damage,
                    heal=heal,
                )
            )

        winner = soup.find("div", {"class": "match-result"}).text.split(" ")[0]
        match = Match(
            match_info=match_info, winner=winner, players={Team.RADIANT.value: heroes[:5], Team.DIRE.value: heroes[5:]}
        )

        return match

    def parse_profile(self, data: str) -> PlayerProfile:
        """Parse player profile data."""
        return data

    def parse_records(self, data: str) -> List[Record]:
        """Parse player record data."""
        records = []
        soup = BeautifulSoup(data)

        records_component = soup.find("div", {"class": "content-inner"}).find_all("article")[3]
        titles = records_component.find_all("div", {"class": "title"})
        values = records_component.find_all("div", {"class": "value"})
        heroes = records_component.find_all("div", {"class": "hero"})
        details = records_component.find_all("div", {"class": "details"})

        components_gathered = zip(titles, values, heroes, details)

        for title, value, hero, detail in components_gathered:
            # parse hero component
            hero_parsed = hero.text.split(" ")
            hero_name = hero_parsed[0]
            duration = self._parse_time(hero_parsed[1].strip("(").strip(")"))

            title = title.text
            value = value.text
            timestamp = datetime.fromisoformat(detail.time["datetime"])

            # parse details component
            details_parsed = [item.strip(" ") for item in details.text.split(",")]
            game_result = details_parsed[0].split(" ")[0]
            lobby_type = details_parsed[1]
            game_mode = details_parsed[2]

            match_info = MatchInfo(lobby_type=lobby_type, game_mode=game_mode, timestamp=timestamp, duration=duration)
            records.append(
                Record(
                    value=value, game_result=game_result, result_name=title, hero_name=hero_name, match_info=match_info
                )
            )

        return records
