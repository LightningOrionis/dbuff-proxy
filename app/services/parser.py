import re
from datetime import datetime, time
from typing import List

from bs4 import BeautifulSoup

from app.constants import Team
from app.schemas import (
    AdvancedMatchHero,
    AggregatedMatchStats,
    BaseMatchHero,
    Match,
    MatchInfo,
    OverviewHero,
    PlayerMatch,
    PlayerProfile,
    Record,
)


class DotabuffParser:
    """Dotabuff parser service."""

    def _parse_time(self, time_str: str) -> time:
        """Parse time string into time object."""
        if time_str.count(":") == 1:
            hours = "0"
            minutes, seconds = time_str.split(":")
        else:
            hours, minutes, seconds = time_str.split(":")

        return time(int(hours), int(minutes), int(seconds))

    def _parse_int_from_k(self, s: str) -> int:
        """Parse K to thousands, e.g. 24.1K -> 24100."""
        s = s.replace("k", "")
        s = s.replace("-", "0.0")

        try:
            thousands, hundreds = [int(i) for i in s.split(".")]
        except ValueError:
            return int(s)
        return thousands * 1000 + hundreds * 100

    def parse_matches(self, data: bytes) -> List[PlayerMatch]:
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
            lobby_type = re.sub(r"x[1-5]", "", columns[4].text.replace(game_mode, "")[:6])
            timestamp = datetime.fromisoformat(columns[3].div.time["datetime"])
            duration = self._parse_time(columns[5].text)

            hero = BaseMatchHero(hero_name=hero_name, kills=kills, deaths=deaths, assists=assists)
            match_info = MatchInfo(game_mode=game_mode, timestamp=timestamp, lobby_type=lobby_type, duration=duration)
            match = PlayerMatch(hero=hero, match_info=match_info, result=match_result)

            matches.append(match)

        return matches

    def parse_match(self, data: bytes) -> Match:
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
            is_anonymous = False
            columns = result.find_all("td")

            hero_name = " ".join([word.capitalize() for word in columns[0].a["href"].split("/")[-1].split("-")])
            try:
                player_id = int(columns[3].a["href"].split("/")[-1])
            except TypeError:
                player_id = -1  # Anonymous player
                is_anonymous = True

            to_parse_columns = [5, 6, 7, 8, 9, 11, 12, 14, 15, 16, 17]
            if is_anonymous:
                to_parse_columns = list(map(lambda x: x - 2, to_parse_columns))

            kills, deaths, assists, net_worth, last_hits, denies, gpm, xpm, hero_damage, heal, tower_damage = map(
                lambda x: self._parse_int_from_k(columns[x].text), to_parse_columns
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

    def parse_profile(self, data: bytes) -> PlayerProfile:
        """Parse player profile data."""
        soup = BeautifulSoup(data)

        # profile info
        profile_info = list(soup.find("div", {"class": "header-content-primary"}).children)
        player_id = int(profile_info[0].a["href"].split("/")[-1])
        nickname = profile_info[1].h1.text.replace("Overview", "")

        # most played hero info
        most_played_heroes = []
        hero_overview = list(soup.find("div", {"class": "heroes-overview"}).children)

        for div in hero_overview:
            columns = list(div.children)
            hero_name = " ".join(
                [word.capitalize() for word in list(columns[0].children)[1].a["href"].split("/")[-1].split("-")]
            )
            matches_played = int(list(columns[1].children)[1].text)
            winrate = float(list(columns[2].children)[1].text.replace("%", ""))
            kda = float(list(columns[3].children)[1].text)

            most_played_heroes.append(
                OverviewHero(
                    match_stats=AggregatedMatchStats(winrate=winrate, matches_played=matches_played, avg_kda=kda),
                    hero_name=hero_name,
                )
            )

        # aggregated match info
        match_stats = {}
        stats_table = soup.table
        table_bodies = stats_table.find_all("tbody")

        aggregated_match_types = [
            *table_bodies[0].find_all("tr"),  # Overview
            *table_bodies[1].find_all("tr"),  # Lobby Type
            *table_bodies[2].find_all("tr"),  # Game Mode
            *table_bodies[3].find_all("tr"),  # Team
        ]

        for row in aggregated_match_types:
            columns = row.find_all("td")
            title = columns[0].text
            matches_played = int(columns[1].text.replace(",", ""))
            winrate = float(columns[2].text.replace("%", ""))
            match_stats[title] = AggregatedMatchStats(matches_played=matches_played, winrate=winrate)

        profile = PlayerProfile(
            match_stats=match_stats, player_id=player_id, nickname=nickname, most_played_heroes=most_played_heroes
        )
        return profile

    def parse_records(self, data: bytes) -> List[Record]:
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
            hero_name = " ".join(hero_parsed[:-1])
            duration = self._parse_time(hero_parsed[-1].strip("(").strip(")"))

            title = title.text
            value = value.text
            timestamp = datetime.fromisoformat(detail.time["datetime"])

            # parse details component
            details_parsed = [item.strip(" ") for item in detail.text.split(",")]
            game_result = details_parsed[0].split(" ")[0]
            lobby_type = details_parsed[1]
            game_mode = details_parsed[2]

            match_info = MatchInfo(lobby_type=lobby_type, game_mode=game_mode, timestamp=timestamp, duration=duration)
            records.append(
                Record(value=value, result=game_result, record_name=title, hero_name=hero_name, match_info=match_info)
            )

        return records
