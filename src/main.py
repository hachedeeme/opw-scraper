import json
from pathlib import Path

from bs4 import BeautifulSoup
from curl_cffi import requests

BASE_URL = "https://onepiece.fandom.com"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CHARACTERS_HTML = DATA_DIR / "List_of_Canon_Characters.html"
CHARACTERS_JSON = DATA_DIR / "characters.json"


def get_html(url: str, cache: Path) -> str:
  if cache.exists():
    print(f"Leyendo {cache.name} local...")
    return cache.read_text(encoding="utf-8")

  print(f"Descargando {url}...")
  response = requests.get(url, impersonate="chrome", timeout=30)
  response.raise_for_status()
  cache.parent.mkdir(parents=True, exist_ok=True)
  cache.write_text(response.text, encoding="utf-8")
  return response.text


def parse_characters(html: str) -> list[dict[str, str]]:
  soup = BeautifulSoup(html, "html.parser")
  table = soup.find("table")
  if table is None:
    raise SystemExit("No se encontró ninguna tabla en el HTML.")

  characters = []
  for row in table.find_all("tr"):
    link = row.find("a")
    if link is None or not link.get("title"):
      continue
    name = link["title"]
    if "List of Canon Characters" in name:
      continue
    characters.append({"name": name, "link": BASE_URL + link["href"]})
  return characters


def main() -> None:
  html = get_html(f"{BASE_URL}/wiki/List_of_Canon_Characters", CHARACTERS_HTML)
  characters = parse_characters(html)
  CHARACTERS_JSON.write_text(
    json.dumps(characters, ensure_ascii=False, indent=2),
    encoding="utf-8",
  )
  print(f"{len(characters)} personajes guardados en {CHARACTERS_JSON}")


if __name__ == "__main__":
  main()
