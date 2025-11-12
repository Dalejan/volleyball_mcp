"""Scrapper para obtener datos de partidos de voleibol desde la API de VolleyballWorld."""
import requests
from typing import Dict, Optional
import json


class VolleyballScrapper:
    """Obtiene datos de partidos desde la API de VolleyballWorld."""
    
    BASE_URL = "https://en.volleyballworld.com/api/v1/volley-tournament"
    COMPETITIONS_URL = "https://en.volleyballworld.com/api/v1/globalschedule/competitions"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def _fetch_competition_info(self, tournament_no: int, year: int) -> Optional[Dict]:
        """Obtiene información de la competición para extraer fechas exactas del torneo."""
        url = f"{self.COMPETITIONS_URL}/{year}/"
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Buscar el torneo por menTournaments o womenTournaments
            for competition in data.get("competitions", []):
                if (competition.get("menTournaments") == str(tournament_no) or 
                    competition.get("womenTournaments") == str(tournament_no)):
                    return competition
            
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error obteniendo información de competición: {e}")
            return None
    
    def _fetch_range(self, start_date: str, end_date: str, tournament_no: int) -> Optional[Dict]:
        """Obtiene datos de un rango de fechas."""
        url = f"{self.BASE_URL}/{start_date}/{end_date}/{tournament_no}"
        try:
            response = self.session.get(url, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error obteniendo datos de {start_date} a {end_date}: {e}")
            return None
    
    def fetch_full_tournament(self, tournament_no: int, year: int = None, output_file: Optional[str] = None) -> Dict:
        """Obtiene todos los partidos de un torneo usando las fechas exactas de la competición."""
        # Intentar obtener fechas exactas del torneo desde competitions API
        if year:
            competition = self._fetch_competition_info(tournament_no, year)
        else:
            # Si no se proporciona año, intentar años recientes
            for y in range(2025, 2020, -1):
                competition = self._fetch_competition_info(tournament_no, y)
                if competition:
                    year = y
                    break
            else:
                competition = None
        
        if competition:
            # Extraer fechas exactas del torneo
            start_date_iso = competition.get("startDate", "")
            end_date_iso = competition.get("endDate", "")
            
            if start_date_iso and end_date_iso:
                start_date = start_date_iso.split("T")[0]
                end_date = end_date_iso.split("T")[0]
                print(f"Torneo: {competition.get('competitionFullName', 'N/A')}")
                print(f"Fechas exactas: {start_date} a {end_date}")
            else:
                print("No se encontraron fechas en la información de la competición")
                return {"matches": [], "allTeams": [], "allTournaments": []}
        else:
            # Fallback: usar año completo si no se encuentra la competición
            if not year:
                year = 2025  # Default
            start_date = f"{year}-01-01"
            end_date = f"{year}-12-31"
            print(f"Torneo {tournament_no} no encontrado en competitions API, usando año completo: {start_date} a {end_date}")
        
        print(f"Obteniendo partidos del torneo {tournament_no}...")
        
        # Intentar obtener todo el año en una sola request
        data = self._fetch_range(start_date, end_date, tournament_no)
        
        if data:
            # Consolidar datos (evitar duplicados)
            matches = {m.get("matchNo"): m for m in data.get("matches", []) if m.get("matchNo")}
            teams = {t.get("no"): t for t in data.get("allTeams", []) if t.get("no")}
            tournaments = {t.get("no"): t for t in data.get("allTournaments", []) if t.get("no") == tournament_no}
            
            result = {
                "matches": list(matches.values()),
                "allTeams": list(teams.values()),
                "allTournaments": list(tournaments.values())
            }
        else:
            print("No se pudieron obtener datos en una sola request, dividiendo el rango...")
            # Fallback: dividir el rango en dos mitades si falla la request completa
            result = self._fetch_by_range_split(start_date, end_date, tournament_no)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"\nGuardado: {output_file}")
            print(f"Partidos: {len(result['matches'])}, Equipos: {len(result['allTeams'])}")
        
        return result
    
    def _fetch_by_range_split(self, start_date: str, end_date: str, tournament_no: int) -> Dict:
        """Divide un rango de fechas en dos mitades como fallback."""
        from datetime import datetime, timedelta
        
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        mid = start + (end - start) / 2
        mid_date = mid.strftime("%Y-%m-%d")
        
        matches = {}
        teams = {}
        tournaments = {}
        
        # Primera mitad
        print("Obteniendo primera mitad del rango...")
        data1 = self._fetch_range(start_date, mid_date, tournament_no)
        if data1:
            for m in data1.get("matches", []):
                if m.get("matchNo"):
                    matches[m["matchNo"]] = m
            for t in data1.get("allTeams", []):
                if t.get("no"):
                    teams[t["no"]] = t
            for t in data1.get("allTournaments", []):
                if t.get("no") == tournament_no:
                    tournaments[tournament_no] = t
        
        # Segunda mitad
        print("Obteniendo segunda mitad del rango...")
        next_date = (mid + timedelta(days=1)).strftime("%Y-%m-%d")
        data2 = self._fetch_range(next_date, end_date, tournament_no)
        if data2:
            for m in data2.get("matches", []):
                if m.get("matchNo"):
                    matches[m["matchNo"]] = m
            for t in data2.get("allTeams", []):
                if t.get("no"):
                    teams[t["no"]] = t
            for t in data2.get("allTournaments", []):
                if t.get("no") == tournament_no:
                    tournaments[tournament_no] = t
        
        return {
            "matches": list(matches.values()),
            "allTeams": list(teams.values()),
            "allTournaments": list(tournaments.values())
        }


def main():
    """Ejemplo de uso."""
    scrapper = VolleyballScrapper()
    # El año es opcional - se puede detectar automáticamente
    scrapper.fetch_full_tournament(tournament_no=1520, year=2025, output_file="matches.json")


if __name__ == "__main__":
    main()
