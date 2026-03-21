"""
Download Pixabay images for all spelling bee words using the Pixabay API.
Saves images to static/img/words/<word>.jpg and updates word_images.json
with local paths instead of remote URLs.

Usage: python download_images.py
API key is read from PIXABAY_API_KEY env var or hardcoded below.
"""
import json
import os
import sys
import requests
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from words import EASY_WORDS, MEDIUM_WORDS, HARD_WORDS, PHRASE_WORDS, WORD_IMAGES

API_KEY = "54723755-38adbb506e2fa5ca1df1c373d"
PIXABAY_API = "https://pixabay.com/api/"
IMG_DIR = os.path.join(os.path.dirname(__file__), "static", "img", "words")
os.makedirs(IMG_DIR, exist_ok=True)

ALL_WORDS = sorted(set(EASY_WORDS + MEDIUM_WORDS + HARD_WORDS + PHRASE_WORDS))

downloaded = 0
skipped = 0
emoji_fallback = 0
failed = 0
results = {}

def search_and_download(word):
    """Search Pixabay API for word, download the image, return local path or None."""
    queries = [word]
    if " " in word:
        queries.append(word.split()[0])

    for query in queries:
        try:
            params = {
                "key": API_KEY,
                "q": query,
                "image_type": "photo",
                "safesearch": "true",
                "per_page": 3,
                "lang": "en",
            }
            resp = requests.get(PIXABAY_API, params=params, timeout=8)
            if resp.status_code == 429:
                print(f"  [rate limit] waiting 60s...")
                time.sleep(60)
                resp = requests.get(PIXABAY_API, params=params, timeout=8)
            if resp.status_code == 200:
                hits = resp.json().get("hits", [])
                if hits:
                    img_url = hits[0].get("webformatURL")
                    if img_url:
                        # Download the actual image
                        img_resp = requests.get(img_url, timeout=10)
                        if img_resp.status_code == 200:
                            ext = ".jpg"
                            filename = word.replace(" ", "_").lower() + ext
                            filepath = os.path.join(IMG_DIR, filename)
                            with open(filepath, "wb") as f:
                                f.write(img_resp.content)
                            return filename
        except Exception as e:
            print(f"  [err] {word}: {e}")
        time.sleep(0.15)
    return None

print(f"Downloading Pixabay images for {len(ALL_WORDS)} words into static/img/words/\n")

for i, word in enumerate(ALL_WORDS):
    w = word.lower()
    filename = word.replace(" ", "_").lower() + ".jpg"
    filepath = os.path.join(IMG_DIR, filename)

    # Skip if already downloaded
    if os.path.exists(filepath):
        print(f"  [skip] [{i+1}/{len(ALL_WORDS)}] {word}")
        results[w] = {"local": filename}
        skipped += 1
        continue

    filename = search_and_download(word)
    if filename:
        results[w] = {"local": filename}
        print(f"  [ok]   [{i+1}/{len(ALL_WORDS)}] {word} -> {filename}")
        downloaded += 1
    else:
        emoji = WORD_IMAGES.get(w, "")
        results[w] = {"emoji": emoji if emoji else "📝"}
        safe_emoji = results[w]['emoji'].encode('ascii', 'replace').decode('ascii')
        print(f"  [emoji][{i+1}/{len(ALL_WORDS)}] {word} -> {safe_emoji}")
        emoji_fallback += 1

    time.sleep(0.12)

# Save updated word_images.json with local paths
output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "word_images.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\nDone: {downloaded} downloaded, {skipped} already existed, {emoji_fallback} emoji fallback, {failed} failed")
print(f"Images saved to: {IMG_DIR}")
print(f"word_images.json updated with local paths")
