"""Pre-fetch Pixabay images for all spelling bee words.
Usage: python fetch_images.py YOUR_PIXABAY_API_KEY
Saves results to word_images.json
"""
import sys, os, json, time, requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from words import EASY_WORDS, MEDIUM_WORDS, HARD_WORDS, PHRASE_WORDS, WORD_IMAGES

API_KEY = sys.argv[1] if len(sys.argv) > 1 else os.getenv("PIXABAY_KEY", "")
if not API_KEY:
    print("Usage: python fetch_images.py YOUR_PIXABAY_API_KEY")
    sys.exit(1)

ALL_WORDS = sorted(set(EASY_WORDS + MEDIUM_WORDS + HARD_WORDS + PHRASE_WORDS))
PIXABAY_URL = "https://pixabay.com/api/"

results = {}
found = 0
emoji_fallback = 0


def search_pixabay(query):
    """Search Pixabay for a photo. Returns the best match URL or None."""
    params = {
        "key": API_KEY,
        "q": query,
        "image_type": "photo",
        "safesearch": "true",
        "per_page": 3,
        "lang": "en",
    }
    try:
        resp = requests.get(PIXABAY_URL, params=params, timeout=8)
        if resp.status_code == 200:
            data = resp.json()
            hits = data.get("hits", [])
            if hits:
                # webformatURL is ~640px wide, good for display
                return hits[0].get("webformatURL")
    except Exception as e:
        print(f"  ERROR: {e}")
    return None


print(f"Fetching Pixabay images for {len(ALL_WORDS)} words...\n")

for i, word in enumerate(ALL_WORDS):
    # Try the word itself first
    url = search_pixabay(word)

    # If no result, try just the first word (for phrases)
    if not url and " " in word:
        url = search_pixabay(word.split()[0])

    emoji = WORD_IMAGES.get(word.lower(), "")

    if url:
        results[word.lower()] = {"url": url}
        found += 1
        status = "PHOTO"
    else:
        results[word.lower()] = {"emoji": emoji if emoji else ""}
        emoji_fallback += 1
        status = "EMOJI fallback"

    print(f"[{i+1}/{len(ALL_WORDS)}] {word:25s} -> {status}")
    time.sleep(0.12)  # stay well under 100 req/min limit

print(f"\n{'='*50}")
print(f"Photos found:   {found}/{len(ALL_WORDS)}")
print(f"Emoji fallback: {emoji_fallback}/{len(ALL_WORDS)}")
print(f"{'='*50}")

output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "word_images.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"\nSaved to: {output_path}")
