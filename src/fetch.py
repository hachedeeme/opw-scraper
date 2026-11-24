import random
import time
from pathlib import Path

from curl_cffi import requests

RETRY_STATUS = {429, 500, 502, 503, 504}


class Fetcher:
  def __init__(
    self,
    delay: tuple[float, float] = (1.0, 2.0),
    max_retries: int = 4,
  ) -> None:
    self.session = requests.Session(impersonate="chrome")
    self.delay = delay
    self.max_retries = max_retries

  def get_html(self, url: str, cache: Path) -> str:
    if cache.exists():
      return cache.read_text(encoding="utf-8")

    html = self._download(url).text
    self._write(cache, html.encode("utf-8"))
    return html

  def get_bytes(self, url: str, cache: Path) -> bytes:
    if cache.exists():
      return cache.read_bytes()

    data = self._download(url).content
    self._write(cache, data)
    return data

  def _write(self, path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".part")
    tmp.write_bytes(data)
    tmp.replace(path)
    # Pausa solo cuando efectivamente le pegamos a la red
    time.sleep(random.uniform(*self.delay))

  def _download(self, url: str) -> requests.Response:
    for attempt in range(self.max_retries + 1):
      response = self.session.get(url, timeout=30)
      if response.status_code not in RETRY_STATUS:
        response.raise_for_status()
        return response
      if attempt < self.max_retries:
        wait = self._wait_time(response, attempt)
        print(f"  {response.status_code} en {url}, reintento en {wait:.0f}s")
        time.sleep(wait)
    response.raise_for_status()
    return response

  @staticmethod
  def _wait_time(response: requests.Response, attempt: int) -> float:
    retry_after = response.headers.get("Retry-After", "")
    if retry_after.isdigit():
      return float(retry_after)
    return 5.0 * 2**attempt
