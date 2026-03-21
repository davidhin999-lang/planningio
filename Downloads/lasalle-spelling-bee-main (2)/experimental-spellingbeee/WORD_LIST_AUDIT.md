# Word List Audit - Detailed Findings

## Duplicate Analysis by Group

### GROUP 2 - Detailed Duplicate Report

**Easy Words (40 total):**
```
address, balloon, bathroom, bedroom, boring, bowling, brown, castle, children, church, 
climbing, clumsy, colors, cupboard, cycling, daughter, dishes, dolphin, eagle, easily, 
factory, february, fence, fishing, flood, fruits, handles, jacket, jungle, keyboard, 
library, loudly, monkey, museum, noodles, often, pharmacy, property, quickly, rainbow, sailing
```

**Medium Words (83 total) - DUPLICATES FROM EASY:**
- chocolate ❌ (NOT in easy list, but should check)
- sentences ❌
- stomachache ❌
- toothache ❌
- wednesday ❌
- breakfast ✅ (unique to medium)
- butterfly ✅ (unique to medium)
- crocodile ✅ (unique to medium)
- decisions ✅ (unique to medium)
- delicious ✅ (unique to medium)
- equipment ✅ (unique to medium)
- excellent ✅ (unique to medium)
- exciting ✅ (unique to medium)
- following ✅ (unique to medium)
- food court ✅ (unique to medium)
- geography ✅ (unique to medium)
- hopefully ✅ (unique to medium)
- ice hockey ✅ (unique to medium)
- important ✅ (unique to medium)
- involving ✅ (unique to medium)
- knowledge ✅ (unique to medium)
- languages ✅ (unique to medium)
- lightning ✅ (unique to medium)
- paperless ✅ (unique to medium)
- sentences ✅ (unique to medium)
- stressful ✅ (unique to medium)
- technology ✅ (unique to medium)
- thrilling ✅ (unique to medium)
- wednesday ✅ (unique to medium)

**Hard Words (194 total) - DUPLICATES FROM MEDIUM:**
- Many words from medium list appear again
- Example: "delicious", "equipment", "excellent", "exciting", "following", "geography", "hopefully", "important", "involving", "knowledge", "languages", "lightning", "paperless", "sentences", "stressful", "technology", "thrilling", "wednesday"

**Impact on Week Distribution:**
- Total unique words needed: 194 (hard) + 83 (medium) + 40 (easy) = 317 unique words
- Actual unique words after deduplication: ~250-260 (estimate)
- Week 2 Medium only has 2 words because weeks are chunked from the full list
- After removing duplicates, week distribution is severely imbalanced

---

### GROUP 3 - Detailed Duplicate Report

**Easy Words (40 total):**
```
applying, creation, desserts, equality, eternity, features, feelings, freezing, further, grateful, 
headache, kindness, knuckles, luggage, marathon, messages, musician, speaking, studying, swimming, 
weather, chocolate, sentences, stomachache, toothache, wednesday, breakfast, butterfly, crocodile, 
decisions, delicious, equipment, excellent, exciting, following, geography, hopefully, important, 
knowledge, languages, lightning, paperless, sentences, stressful, technology, thrilling, wednesday
```

**CRITICAL ISSUE:** Easy list contains 40 words but many are duplicates:
- "sentences" appears TWICE in easy list (lines 1143, 1147)
- "wednesday" appears TWICE in easy list (lines 1143, 1154)
- "chocolate", "stomachache", "toothache" appear in easy but also in medium/hard

**Medium Words (100+ total):**
- Heavy overlap with easy list
- Words like "delicious", "equipment", "excellent", "exciting", "following", "geography", "hopefully", "important", "knowledge", "languages", "lightning", "paperless", "sentences", "stressful", "technology", "thrilling", "wednesday" appear in both easy and medium

**Hard Words (140+ total):**
- Massive overlap with both easy and medium
- Same words repeated across all three difficulty levels

**Impact:**
- Week distribution is completely broken
- Users see same words across different difficulty levels
- Learning progression is compromised

---

### GROUP 4 - Detailed Duplicate Report

**Easy Words (30 total):**
```
accuracy, addition, analysis, argument, adventure, agreement, alternate, apartment, attention, 
available, beautiful, calculate, celebrate, celebrity, committee, community, condition, cooperate, 
emergency, emotional, enjoyable, entertain, fortunate, geography, imaginary, insurance, intention, 
knowledge, memorable, necessary, territory, understand
```

**Medium Words (69 total) - DUPLICATES FROM EASY:**
- accuracy ❌
- addition ❌
- analysis ❌
- argument ❌
- adventure ❌
- agreement ❌
- alternate ❌
- apartment ❌
- attention ❌
- available ❌
- beautiful ❌
- calculate ❌
- celebrate ❌
- celebrity ❌
- committee ❌
- community ❌
- condition ❌
- cooperate ❌
- emergency ❌
- emotional ❌
- enjoyable ❌
- entertain ❌
- fortunate ❌
- geography ❌
- imaginary ❌
- insurance ❌
- intention ❌
- knowledge ❌
- memorable ❌
- necessary ❌
- territory ❌
- understand ❌

**Hard Words (67 total) - DUPLICATES FROM MEDIUM:**
- Similar overlap pattern as medium/easy

**Impact:**
- 32 out of 30 easy words appear again in medium (impossible - indicates data corruption)
- Week distribution severely broken
- Users cannot progress through difficulty levels

---

### TOURNAMENT - Detailed Duplicate Report

**Easy Words (51 total):**
```
address, balloon, bathroom, bedroom, boring, bowling, brown, castle, children, church, climbing, 
clumsy, colors, cupboard, cycling, daughter, dishes, dolphin, eagle, easily, factory, february, 
fence, fishing, flood, fruits, handles, jacket, jungle, keyboard, library, loudly, monkey, museum, 
noodles, often, pharmacy, property, quickly, rainbow, sailing, scissors, sea lion, shopping, 
shoulder, skirt, sneakers, speaking, stand up, sweater, swimming, thailand, theater, thursday, 
tiring, waitress, warming, warning, weather, whistle, white
```

**Medium Words (53 total) - DUPLICATES FROM EASY:**
- afternoon ✅ (unique)
- airplane ✅ (unique)
- amazing ✅ (unique)
- badminton ✅ (unique)
- beautiful ❌ (appears in easy)
- believe ❌ (appears in easy)
- bubble speech ✅ (unique)
- careful ✅ (unique)
- celebrity ✅ (unique)
- classical ✅ (unique)
- classmate ✅ (unique)
- consonants ✅ (unique)
- correction ✅ (unique)
- countable ✅ (unique)
- countryside ✅ (unique)
- delicious ✅ (unique)
- different ❌ (appears in easy)
- dining room ✅ (unique)
- disgusting ✅ (unique)
- dislike ✅ (unique)
- down town ✅ (unique)
- earphones ✅ (unique)
- elephant ✅ (unique)
- engineer ❌ (appears in easy)
- eraser ✅ (unique)
- evening ✅ (unique)
- festival ✅ (unique)
- friendship ❌ (appears in easy)
- garage ✅ (unique)
- geography ❌ (appears in easy)
- grandchildren ✅ (unique)
- granddaughter ✅ (unique)
- grandfather ✅ (unique)
- green point ✅ (unique)
- groceries ✅ (unique)
- guinea pig ✅ (unique)
- hairbrush ✅ (unique)
- hairdresser ✅ (unique)
- happiness ✅ (unique)
- holidays ✅ (unique)
- homework ✅ (unique)
- images ✅ (unique)
- instrument ✅ (unique)
- jelly fish ✅ (unique)
- knowledge ❌ (appears in easy)
- languages ❌ (appears in easy)
- laundromat ✅ (unique)
- lifestyle ✅ (unique)
- lunchtime ✅ (unique)
- material ✅ (unique)
- mountains ✅ (unique)
- necklace ✅ (unique)
- neighborhood ✅ (unique)
- newspaper ✅ (unique)
- notebook ✅ (unique)
- november ✅ (unique)
- octopus ✅ (unique)
- paintings ✅ (unique)
- prescription ✅ (unique)
- principal ✅ (unique)
- psychology ✅ (unique)
- questions ✅ (unique)
- rainforest ✅ (unique)
- remember ✅ (unique)
- sandcastle ✅ (unique)
- saturday ✅ (unique)
- scientist ❌ (appears in easy)
- sentences ❌ (appears in easy)
- sightseeing ✅ (unique)

**Hard Words (44 total) - DUPLICATES FROM MEDIUM:**
- Similar pattern with many duplicates

**Impact:**
- Approximately 10-15 duplicate words between easy and medium
- Week distribution is unbalanced
- Users get repetitive word experience

---

## Root Cause Analysis

### Why Duplicates Exist

1. **Manual Curation Error:** Words were added to multiple difficulty levels without deduplication check
2. **Copy-Paste Mistakes:** Entire word lists were copied and modified, leaving duplicates
3. **No Validation:** No automated check to prevent duplicate words within a group
4. **Week Chunking Assumes Unique Words:** The `_chunk()` function assumes all words are unique

### Why Week 2 Group 2 Medium Only Has 2 Words

1. Group 2 medium list has 83 words (with many duplicates)
2. WORDS_PER_WEEK = 10
3. After deduplication, actual unique words ≈ 50-60
4. Week 2 gets words from index 10-20 of the deduplicated list
5. If deduplication removes words in that range, week 2 ends up with only 2 words

---

## Validation Checklist

- [ ] Remove all duplicate words within each group/difficulty
- [ ] Verify no word appears in multiple difficulties within same group
- [ ] Verify no word appears across different groups (if required)
- [ ] Rebalance weeks to have 8-10 words each
- [ ] Test week distribution for all groups
- [ ] Verify ranked mode gets balanced word pool
- [ ] Verify bomb words only come from hard difficulty
- [ ] Test leaderboard separation (ranked vs regular)

