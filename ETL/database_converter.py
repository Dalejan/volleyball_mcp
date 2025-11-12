"""Convertidor de datos JSON a base de datos SQLite."""
import sqlite3
import json
from typing import Dict, List, Optional
from pathlib import Path


class VolleyballDBConverter:
    """Convierte datos JSON de partidos a base de datos SQLite."""
    
    def __init__(self, db_path: str = "volleyball_data.db"):
        self.db_path = db_path
    
    def _execute_sql(self, sql: str, params: tuple = None):
        """Ejecuta SQL y retorna cursor."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        cursor.execute(sql, params or ())
        conn.commit()
        conn.close()
        return cursor
    
    def _execute_many(self, sql: str, params_list: List[tuple]):
        """Ejecuta SQL múltiples veces."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        cursor.executemany(sql, params_list)
        conn.commit()
        conn.close()
    
    def create_schema(self):
        """Crea todas las tablas con relaciones y foreign keys."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        
        # Tablas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tournaments (
                no INTEGER PRIMARY KEY, name TEXT NOT NULL, start_date TEXT, end_date TEXT,
                discipline TEXT, discipline_text TEXT, city TEXT, country TEXT, country_name TEXT,
                gender TEXT, gender_text TEXT, competition_short_name TEXT, competition_full_name TEXT,
                competition_slug TEXT, logo TEXT, logo_square TEXT, logo_url TEXT, tickets_url TEXT,
                volley_ball_tv_link TEXT, you_tube_link TEXT, store_link TEXT, url TEXT,
                sub_competition_type TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS teams (
                no INTEGER PRIMARY KEY, code TEXT NOT NULL, name TEXT NOT NULL, country TEXT,
                translated_name TEXT, img TEXT, img_squared TEXT, alt_text TEXT, discipline TEXT,
                is_club INTEGER DEFAULT 0, tournament_code TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pools (
                no INTEGER PRIMARY KEY, name TEXT NOT NULL, code TEXT NOT NULL, tournament_no INTEGER,
                FOREIGN KEY (tournament_no) REFERENCES tournaments(no)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rounds (
                no INTEGER PRIMARY KEY, name TEXT NOT NULL, code TEXT, tournament_no INTEGER,
                FOREIGN KEY (tournament_no) REFERENCES tournaments(no)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS matches (
                match_no INTEGER PRIMARY KEY, match_no_in_tournament INTEGER, tournament_no INTEGER NOT NULL,
                team_a_no INTEGER NOT NULL, team_b_no INTEGER NOT NULL, winner_team_no INTEGER,
                team_a_score INTEGER DEFAULT 0, team_b_score INTEGER DEFAULT 0, match_date_utc TEXT NOT NULL,
                match_date_time_local TEXT, match_status INTEGER, current_set_no INTEGER,
                competition_slug TEXT, competition_short_name TEXT, competition_full_name TEXT,
                round_no INTEGER, pool_no INTEGER, city TEXT, country_code TEXT, country TEXT,
                gender TEXT, gender_text TEXT, discipline TEXT, discipline_text TEXT,
                pinned_competition INTEGER DEFAULT 0, is_match_tbd INTEGER DEFAULT 0,
                tournament_type INTEGER, season INTEGER, ticket_link TEXT, volley_ball_tv_link TEXT,
                you_tube_link TEXT, match_center_url TEXT, world_ranking_url TEXT,
                team_a_replacement_tbd TEXT, team_b_replacement_tbd TEXT, phase TEXT,
                court TEXT, court_text TEXT,
                FOREIGN KEY (tournament_no) REFERENCES tournaments(no),
                FOREIGN KEY (team_a_no) REFERENCES teams(no),
                FOREIGN KEY (team_b_no) REFERENCES teams(no),
                FOREIGN KEY (winner_team_no) REFERENCES teams(no),
                FOREIGN KEY (round_no) REFERENCES rounds(no),
                FOREIGN KEY (pool_no) REFERENCES pools(no)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sets (
                id INTEGER PRIMARY KEY AUTOINCREMENT, match_no INTEGER NOT NULL, set_number INTEGER NOT NULL,
                points_team_a INTEGER DEFAULT 0, points_team_b INTEGER DEFAULT 0,
                FOREIGN KEY (match_no) REFERENCES matches(match_no) ON DELETE CASCADE,
                UNIQUE(match_no, set_number)
            )
        """)
        
        # Índices
        indices = [
            "CREATE INDEX IF NOT EXISTS idx_matches_tournament ON matches(tournament_no)",
            "CREATE INDEX IF NOT EXISTS idx_matches_team_a ON matches(team_a_no)",
            "CREATE INDEX IF NOT EXISTS idx_matches_team_b ON matches(team_b_no)",
            "CREATE INDEX IF NOT EXISTS idx_matches_date ON matches(match_date_utc)",
            "CREATE INDEX IF NOT EXISTS idx_matches_winner ON matches(winner_team_no)",
            "CREATE INDEX IF NOT EXISTS idx_matches_pool ON matches(pool_no)",
            "CREATE INDEX IF NOT EXISTS idx_matches_round ON matches(round_no)",
            "CREATE INDEX IF NOT EXISTS idx_sets_match ON sets(match_no)",
            "CREATE INDEX IF NOT EXISTS idx_pools_tournament ON pools(tournament_no)",
            "CREATE INDEX IF NOT EXISTS idx_rounds_tournament ON rounds(tournament_no)",
            "CREATE INDEX IF NOT EXISTS idx_teams_code ON teams(code)",
            "CREATE INDEX IF NOT EXISTS idx_teams_tournament_code ON teams(tournament_code)"
        ]
        
        for idx_sql in indices:
            cursor.execute(idx_sql)
        
        conn.commit()
        conn.close()
        print("Schema creado con índices")
    
    def insert_tournaments(self, tournaments: List[Dict]):
        """Inserta torneos."""
        sql = """INSERT OR REPLACE INTO tournaments (
            no, name, start_date, end_date, discipline, discipline_text, city, country, country_name,
            gender, gender_text, competition_short_name, competition_full_name, competition_slug,
            logo, logo_square, logo_url, tickets_url, volley_ball_tv_link, you_tube_link,
            store_link, url, sub_competition_type
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        
        params = [(
            t.get("no"), t.get("name"), t.get("startDate"), t.get("endDate"),
            t.get("discipline"), t.get("disciplineText"), t.get("city"), t.get("country"),
            t.get("countryName"), t.get("gender"), t.get("genderText"),
            t.get("competitionShortName"), t.get("competitionFullName"), t.get("competitionSlug"),
            t.get("logo"), t.get("logoSquare"), t.get("logoUrl"), t.get("ticketsUrl"),
            t.get("volleyBallTvLink"), t.get("youTubeLink"), t.get("storeLink"), t.get("url"),
            t.get("subCompetitionType")
        ) for t in tournaments]
        
        self._execute_many(sql, params)
        print(f"Insertados {len(tournaments)} torneos")
    
    def insert_teams(self, teams: List[Dict]):
        """Inserta equipos."""
        sql = """INSERT OR REPLACE INTO teams (
            no, code, name, country, translated_name, img, img_squared, alt_text,
            discipline, is_club, tournament_code
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        
        params = [(
            t.get("no"), t.get("code"), t.get("name"), t.get("country"), t.get("translatedName"),
            t.get("img"), t.get("imgSquared"), t.get("altText"), t.get("discipline"),
            1 if t.get("isClub") else 0, t.get("tournamentCode")
        ) for t in teams]
        
        self._execute_many(sql, params)
        print(f"Insertados {len(teams)} equipos")
    
    def insert_pools(self, matches: List[Dict]):
        """Extrae e inserta pools únicos."""
        pools = {}
        for match in matches:
            pool = match.get("pool")
            if pool and pool.get("no"):
                pool_no = pool.get("no")
                if pool_no not in pools:
                    pools[pool_no] = (
                        pool_no, pool.get("name"), pool.get("code"), match.get("tournamentNo")
                    )
        
        if pools:
            sql = "INSERT OR REPLACE INTO pools (no, name, code, tournament_no) VALUES (?, ?, ?, ?)"
            self._execute_many(sql, list(pools.values()))
            print(f"Insertados {len(pools)} pools")
    
    def insert_rounds(self, matches: List[Dict]):
        """Extrae e inserta rounds únicos."""
        rounds = {}
        for match in matches:
            round_no = match.get("roundNo")
            if round_no and round_no not in rounds:
                rounds[round_no] = (
                    round_no, match.get("roundName"), match.get("roundCode"), match.get("tournamentNo")
                )
        
        if rounds:
            sql = "INSERT OR REPLACE INTO rounds (no, name, code, tournament_no) VALUES (?, ?, ?, ?)"
            self._execute_many(sql, list(rounds.values()))
            print(f"Insertados {len(rounds)} rounds")
    
    def insert_matches(self, matches: List[Dict]):
        """Inserta partidos."""
        sql = """INSERT OR REPLACE INTO matches (
            match_no, match_no_in_tournament, tournament_no, team_a_no, team_b_no, winner_team_no,
            team_a_score, team_b_score, match_date_utc, match_date_time_local, match_status,
            current_set_no, competition_slug, competition_short_name, competition_full_name,
            round_no, pool_no, city, country_code, country, gender, gender_text, discipline,
            discipline_text, pinned_competition, is_match_tbd, tournament_type, season,
            ticket_link, volley_ball_tv_link, you_tube_link, match_center_url, world_ranking_url,
            team_a_replacement_tbd, team_b_replacement_tbd, phase, court, court_text
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        
        params = []
        for match in matches:
            pool = match.get("pool", {})
            params.append((
                match.get("matchNo"), match.get("matchNoInTournament"), match.get("tournamentNo"),
                match.get("teamANo"), match.get("teamBNo"), match.get("winnerTeamNo"),
                match.get("teamAScore"), match.get("teamBScore"), match.get("matchDateUtc"),
                match.get("matchDateTimeLocal"), match.get("matchStatus"), match.get("currentSetNo"),
                match.get("competitionSlug"), match.get("competitionShortName"), match.get("competitionFullName"),
                match.get("roundNo"), pool.get("no") if pool else None, match.get("city"),
                match.get("countryCode"), match.get("country"), match.get("gender"), match.get("genderText"),
                match.get("discipline"), match.get("disciplineText"),
                1 if match.get("pinnedCompetition") else 0, 1 if match.get("isMatchTBD") else 0,
                match.get("tournamentType"), match.get("season"), match.get("ticketLink"),
                match.get("volleyBallTvLink"), match.get("youTubeLink"), match.get("matchCenterUrl"),
                match.get("worldRankingUrl"), match.get("teamAReplacementTBD"), match.get("teamBReplacementTBD"),
                match.get("phase"), match.get("court"), match.get("courtText")
            ))
        
        self._execute_many(sql, params)
        print(f"Insertados {len(matches)} partidos")
    
    def insert_sets(self, matches: List[Dict]):
        """Inserta sets de cada partido."""
        sql = "INSERT OR REPLACE INTO sets (match_no, set_number, points_team_a, points_team_b) VALUES (?, ?, ?, ?)"
        
        params = []
        for match in matches:
            match_no = match.get("matchNo")
            for set_data in match.get("sets", []):
                points_a = set_data.get("pointsTeamA", 0)
                points_b = set_data.get("pointsTeamB", 0)
                if points_a > 0 or points_b > 0:
                    params.append((match_no, set_data.get("no"), points_a, points_b))
        
        if params:
            self._execute_many(sql, params)
            print(f"Insertados {len(params)} sets")
    
    def convert_json_to_db(self, json_file: str, recreate: bool = True):
        """Convierte archivo JSON completo a base de datos SQLite."""
        if recreate and Path(self.db_path).exists():
            Path(self.db_path).unlink()
            print(f"BD eliminada: {self.db_path}")
        
        self.create_schema()
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Insertar en orden correcto (respetando foreign keys)
        if data.get("allTournaments"):
            self.insert_tournaments(data["allTournaments"])
        
        if data.get("allTeams"):
            self.insert_teams(data["allTeams"])
        
        if data.get("matches"):
            self.insert_pools(data["matches"])
            self.insert_rounds(data["matches"])
            self.insert_matches(data["matches"])
            self.insert_sets(data["matches"])
        
        print(f"\nConversión completada: {self.db_path}")


def main():
    """Ejemplo de uso."""
    converter = VolleyballDBConverter(db_path="volleyball_data.db")
    converter.convert_json_to_db("matches.json", recreate=True)


if __name__ == "__main__":
    main()
