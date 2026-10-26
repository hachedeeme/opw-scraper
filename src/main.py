import argparse
import json
from pathlib import Path
from urllib.parse import quote, unquote

from bs4 import BeautifulSoup
from curl_cffi import requests

from fetch import Fetcher
from images import parse_manga_images

BASE_URL = "https://onepiece.fandom.com"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PAGES_DIR = DATA_DIR / "pages"
CHARACTERS_HTML = DATA_DIR / "List_of_Canon_Characters.html"
CHARACTERS_JSON = DATA_DIR / "characters.json"
IMAGES_JSON = DATA_DIR / "characters_with_images.json"


def parse_characters(html: str) -> list[dict[str, str]]:
  soup = BeautifulSoup(html, "html.parser")
  table = soup.find("table")
  if table is None:
    raise SystemExit("No se encontró ninguna tabla en el HTML.")

  characters: dict[str, dict[str, str]] = {}
  for row in table.find_all("tr"):
    link = row.find("a")
    if link is None or not link.get("title"):
      continue
    name = link["title"]
    if "List of Canon Characters" in name:
      continue
    url = BASE_URL + link["href"]
    characters.setdefault(url, {"name": name, "link": url})
  return list(characters.values())


def page_cache_path(link: str) -> Path:
  slug = unquote(link.rsplit("/wiki/", 1)[1])
  return PAGES_DIR / f"{quote(slug, safe='')}.html"


def main() -> None:
  parser = argparse.ArgumentParser()
  parser.add_argument("--limit", type=int, default=None)
  args = parser.parse_args()

  fetcher = Fetcher()

  html = fetcher.get_html(f"{BASE_URL}/wiki/List_of_Canon_Characters", CHARACTERS_HTML)
  characters = parse_characters(html)
  CHARACTERS_JSON.write_text(
    json.dumps(characters, ensure_ascii=False, indent=2),
    encoding="utf-8",
  )
  print(f"{len(characters)} personajes en la lista")

  if args.limit is not None:
    characters = characters[: args.limit]

  results = []
  failed = []
  for i, character in enumerate(characters, start=1):
    print(f"[{i}/{len(characters)}] {character['name']}")
    try:
      page = fetcher.get_html(character["link"], page_cache_path(character["link"]))
    except requests.exceptions.RequestException as e:
      print(f"  ERROR: {e}")
      failed.append(character["name"])
      continue
    results.append({**character, "images": parse_manga_images(page)})

  IMAGES_JSON.write_text(
    json.dumps(results, ensure_ascii=False, indent=2),
    encoding="utf-8",
  )

  without_image = sum(1 for r in results if r["images"] is None)
  print(f"\nGuardados {len(results)} en {IMAGES_JSON.name}")
  print(f"Sin imagen de manga: {without_image}")
  print(f"Fallidos: {len(failed)} {failed}")


if __name__ == "__main__":
  main()
