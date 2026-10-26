import hashlib
from io import BytesIO
from pathlib import Path

from curl_cffi import requests
from PIL import Image

from fetch import Fetcher

MAX_SIZE = (600, 800)
QUALITY = 80


def character_id(link: str) -> str:
  return hashlib.sha1(link.encode("utf-8")).hexdigest()[:8]


def compress(data: bytes, dest: Path) -> None:
  with Image.open(BytesIO(data)) as img:
    if img.mode not in ("RGB", "RGBA"):
      img = img.convert("RGBA")
    img.thumbnail(MAX_SIZE)  # no agranda, solo reduce
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest, "WEBP", quality=QUALITY, method=6)


def download_images(
  link: str,
  urls: dict[str, str | None] | None,
  fetcher: Fetcher,
  raw_dir: Path,
  out_dir: Path,
) -> dict[str, str | None] | None:
  if urls is None:
    return None

  char_id = character_id(link)
  paths: dict[str, str | None] = {}
  for key, url in urls.items():
    if url is None:
      paths[key] = None
      continue

    dest = out_dir / f"{char_id}_{key}.webp"
    try:
      if not dest.exists():
        data = fetcher.get_bytes(url, raw_dir / f"{char_id}_{key}.orig")
        compress(data, dest)
    except (requests.exceptions.RequestException, OSError) as e:
      print(f"  ERROR con imagen {key}: {e}")
      paths[key] = None
      continue
    paths[key] = f"{out_dir.name}/{dest.name}"
  return paths
