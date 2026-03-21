"""Test image coverage for all spelling bee words.
Tries: Wikipedia → Wikimedia Commons → reports emoji fallback.
Run: python test_images.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from words import EASY_WORDS, MEDIUM_WORDS, HARD_WORDS, PHRASE_WORDS, WORD_IMAGES
import requests
import json
import time

ALL_WORDS = sorted(set(EASY_WORDS + MEDIUM_WORDS + HARD_WORDS + PHRASE_WORDS))
HEADERS = {"User-Agent": "SpellingBeeApp/1.0 (educational)"}

results = {}  # word -> {"source": ..., "url": ..., "emoji": ...}

def try_wikipedia(word):
    """Get thumbnail from Wikipedia page summary."""
    lookup = word.split()[0] if " " in word else word
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{lookup}"
        resp = requests.get(url, headers=HEADERS, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            thumb = data.get("thumbnail", {}).get("source")
            if thumb:
                return thumb
    except Exception:
        pass
    return None

def try_wikimedia_commons(word):
    """Search Wikimedia Commons for an image."""
    lookup = word.split()[0] if " " in word else word
    try:
        url = "https://commons.wikimedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": f"{lookup} filetype:bitmap",
            "srnamespace": "6",
            "srlimit": "3",
            "format": "json"
        }
        resp = requests.get(url, params=params, headers=HEADERS, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            results_list = data.get("query", {}).get("search", [])
            for r in results_list:
                title = r.get("title", "")
                if title.startswith("File:"):
                    # Get the actual image URL
                    img_url = get_commons_image_url(title)
                    if img_url:
                        return img_url
    except Exception:
        pass
    return None

def get_commons_image_url(file_title):
    """Get direct URL for a Wikimedia Commons file."""
    try:
        url = "https://commons.wikimedia.org/w/api.php"
        params = {
            "action": "query",
            "titles": file_title,
            "prop": "imageinfo",
            "iiprop": "url|size",
            "iiurlwidth": "300",
            "format": "json"
        }
        resp = requests.get(url, params=params, headers=HEADERS, timeout=5)
        if resp.status_code == 200:
            pages = resp.json().get("query", {}).get("pages", {})
            for page in pages.values():
                info = page.get("imageinfo", [{}])[0]
                thumb = info.get("thumburl") or info.get("url")
                if thumb:
                    return thumb
    except Exception:
        pass
    return None

def try_pexels_free(word):
    """Try Pexels free (limited, no key needed for search page scraping - skip for now)."""
    return None

print(f"Testing image coverage for {len(ALL_WORDS)} words...\n")

found_photo = 0
found_emoji = 0
no_image = 0

for i, word in enumerate(ALL_WORDS):
    status = ""
    url = None
    
    # Try Wikipedia
    url = try_wikipedia(word)
    if url:
        source = "wikipedia"
    else:
        # Try Wikimedia Commons
        url = try_wikimedia_commons(word)
        if url:
            source = "wikimedia"
    
    emoji = WORD_IMAGES.get(word.lower(), "")
    
    if url:
        results[word] = {"source": source, "url": url}
        found_photo += 1
        status = f"PHOTO ({source})"
    elif emoji:
        results[word] = {"emoji": emoji}
        found_emoji += 1
        status = "EMOJI"
    else:
        results[word] = {"emoji": ""}
        no_image += 1
        status = "NO IMAGE"
    
    print(f"[{i+1}/{len(ALL_WORDS)}] {word:25s} -> {status}")
    time.sleep(0.15)  # rate limiting

print(f"\n{'='*50}")
print(f"RESULTS:")
print(f"  Photos found:    {found_photo}/{len(ALL_WORDS)}")
print(f"  Emoji fallback:  {found_emoji}/{len(ALL_WORDS)}")
print(f"  No image at all: {no_image}/{len(ALL_WORDS)}")
print(f"{'='*50}")

# Save results to JSON
output_path = os.path.join(os.path.dirname(__file__), "word_images.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"\nSaved to: {output_path}")
