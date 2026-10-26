# opw-scraper

Scraper de la wiki de One Piece (Fandom) que genera la base de datos para un juego personal de adivinar personajes.

## Qué hace

1. Baja la página `List of Canon Characters` y extrae nombre y link de cada personaje (sin repetidos).
2. Baja la página de cada personaje y busca en el infobox las imágenes del manga.
3. Descarga esas imágenes, las redimensiona y las comprime a WebP.
4. Escribe `data/characters_with_images.json` con las rutas locales.

Todo se cachea en disco: cada página y cada imagen se baja una sola vez. Si el script se corta, se relanza y retoma desde donde quedó.

## Requisitos

- [uv](https://docs.astral.sh/uv/)
- Python 3.12 (fijado con `uv python pin 3.12`)

## Instalación

```bash
git clone <repo> opw-scraper
cd opw-scraper
uv sync
```

`uv sync` crea el `.venv` e instala las dependencias de runtime (`beautifulsoup4`, `curl_cffi`, `pillow`) y de desarrollo (`ruff`).

## Uso

Desde la raíz del repo:

```bash
# Prueba rápida con los primeros 20 personajes
uv run python src/main.py --limit 20

# Corrida completa (la primera vez tarda, ver "Tiempos")
uv run python src/main.py
```

Al terminar imprime un resumen:

```
Guardados 1547 en characters_with_images.json
Sin imagen de manga: 50
Páginas fallidas: 0 []
Imágenes fallidas: 0 []
```

Si hay páginas o imágenes fallidas, alcanza con volver a ejecutar el comando: solo se reintenta lo que falta.

### Estilo de código

El proyecto usa [ruff](https://docs.astral.sh/ruff/) con **indentación de 2 espacios**:

```bash
uv run ruff format .
uv run ruff check . --fix
```

## Formato de salida

`data/characters_with_images.json` es una lista de objetos:

```json
{
  "name": "Monkey D. Luffy",
  "link": "https://onepiece.fandom.com/wiki/Monkey_D._Luffy",
  "images": {
    "manga": null,
    "pre_timeskip": "https://.../Monkey_D._Luffy_Manga_Pre_Timeskip_Infobox.png/revision/latest",
    "post_timeskip": "https://.../Monkey_D._Luffy_Manga_Post_Timeskip_Infobox.png/revision/latest"
  },
  "local_images": {
    "manga": null,
    "pre_timeskip": "images/3f9a1c2e_pre_timeskip.webp",
    "post_timeskip": "images/3f9a1c2e_post_timeskip.webp"
  }
}
```

Reglas del formato:

- `images` tiene las URLs originales de Fandom, sin el parámetro `?cb=...`, que apuntan siempre a la última versión.
- `local_images` tiene la misma forma, con rutas **relativas a `data/`**.
- Un personaje con una sola pestaña `Manga` llena `manga` y deja pre y post en `null`. Uno con pestañas pre y post deja `manga` en `null`.
- Los personajes sin ninguna imagen de manga tienen `"images": null` y `"local_images": null`.
- Si una imagen individual falla al descargar, su entrada en `local_images` queda en `null`, pero la URL sigue en `images`.
- Los nombres de archivo son `<id>_<clave>.webp`, donde `id` son los primeros 8 caracteres del SHA-1 del link. Es estable entre corridas y no filtra el nombre del personaje.

`data/characters.json` es la lista base (solo `name` y `link`).

## Números actuales

| Dato | Valor |
|---|---|
| Personajes en la lista (sin repetidos) | 1547 |
| Con al menos una imagen de manga | 1497 |
| Sin imagen de manga (`images: null`) | 50 |
| Peso de `data/images/` (WebP) | 67 MB |
| Peso de `data/raw_images/` (originales) | 169 MB |
