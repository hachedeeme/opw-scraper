from urllib.parse import urlsplit, urlunsplit

from bs4 import BeautifulSoup

# Título de la pestaña en la wiki -> clave en nuestro JSON
MANGA_TABS = {
  "Manga": "manga",
  "Manga pre-timeskip": "pre_timeskip",
  "Manga post-timeskip": "post_timeskip",
}


def clean_url(url: str) -> str:
  # Sacamos el ?cb=... para que apunte siempre a la última versión
  parts = urlsplit(url)
  return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


def parse_manga_images(html: str) -> dict[str, str | None] | None:
  soup = BeautifulSoup(html, "html.parser")
  infobox = soup.select_one("aside.portable-infobox")
  if infobox is None:
    return None

  images: dict[str, str | None] = dict.fromkeys(MANGA_TABS.values())
  for link in infobox.select("a.image[title]"):
    key = MANGA_TABS.get(link["title"])
    if key is not None and link.get("href") and images[key] is None:
      images[key] = clean_url(link["href"])

  if not any(images.values()):
    return None
  return images
