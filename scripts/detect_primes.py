import json
import re
import math
from pathlib import Path

# --- Constants & Configuration ---
BASE_PATH = Path(r"d:/Corporate Identity/Branding Assets/quran")
SURAH_METADATA_PATH = BASE_PATH / "surah.json"
SURAH_FILES_DIR = BASE_PATH / "surah"
OUTPUT_JSON = BASE_PATH / "prime-numbers.json"

# Standard Abjad Values (Hisab al-Jummal)
ABJAD_MAP = {
    'ا': 1, 'أ': 1, 'إ': 1, 'آ': 1, 'ٱ': 1, 'ء': 1,
    'ب': 2, 'ج': 3, 'د': 4,
    'ه': 5, 'ة': 5,
    'و': 6, 'ز': 7, 'ح': 8, 'ط': 9,
    'ي': 10, 'ى': 10,
    'ك': 20, 'ل': 30, 'م': 40, 'ن': 50,
    'س': 60, 'ع': 70, 'ف': 80, 'ص': 90,
    'ق': 100, 'ر': 200, 'ش': 300, 'ت': 400,
    'ث': 500, 'خ': 600, 'ذ': 700, 'ض': 800,
    'ظ': 900, 'غ': 1000
}

def normalize_text(text: str) -> str:
    """Normalizes Arabic text for analysis."""
    if not isinstance(text, str):
        return ""
    # Remove Harakat and Tatweel
    text = re.sub(r'[\u064B-\u065F\u0670\u0640]', '', text) 
    # Alef Normalization
    text = re.sub(r'[أإآٱ]', 'ا', text)
    # Ya Normalization
    text = re.sub(r'ى', 'ي', text)
    # Ta Marbuta Normalization
    text = re.sub(r'ة', 'ه', text)
    return text

def calculate_abjad_value(text: str) -> int:
    """Calculate the cumulative Abjad value of the text."""
    val = 0
    for char in text:
        if char in ABJAD_MAP:
            val += ABJAD_MAP[char]
    return val

def is_prime(n: int) -> bool:
    """Check if a number is prime."""
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

def analyze_primes():
    print("Loading Metadata...")
    with open(SURAH_METADATA_PATH, 'r', encoding='utf-8') as f:
        surah_meta = json.load(f)
    
    meta_dict = {s['index']: s for s in surah_meta}
    
    results = {
        "metadata": {
            "description": "Prime number analysis of Quranic metrics",
            "metrics": ["surah_index", "verse_count", "word_count", "letter_count", "abjad_value"]
        },
        "surahs": []
    }
    
    print("Processing Surah files...")
    for i in range(1, 115):
        index_str = f"{i:03d}"
        file_path = SURAH_FILES_DIR / f"surah_{i}.json"
        
        if not file_path.exists():
            continue
            
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        surah_idx = int(data.get('index'))
        surah_name_en = data.get('name')
        
        # Surah Level Analysis
        verse_count = int(data.get('count', 0))
        
        verses_dict = data.get('verse', {})
        total_words = 0
        total_letters = 0
        total_abjad = 0
        
        verse_details = []
        
        for v_key, v_text in verses_dict.items():
            if not v_key.startswith('verse_'):
                continue
            
            # Per Verse Analysis
            verse_num = int(v_key.replace('verse_', ''))
            norm_text = normalize_text(v_text)
            
            # Words (simple split)
            words = norm_text.split()
            w_count = len(words)
            
            # Letters (count non-whitespace chars in normalized text - strictly speaking abjad map keys? 
            # Let's count actual arabic letters from the normalized text)
            # Filter to just arabic letters to be precise for "letter count"? 
            # Or just len(norm_text) minus spaces?
            # Let's use the ABJAD_MAP keys as the definition of "letters" to be consistent.
            l_count = sum(1 for c in norm_text if c in ABJAD_MAP)
            
            abjad_val = calculate_abjad_value(v_text)
            
            total_words += w_count
            total_letters += l_count
            total_abjad += abjad_val
            
            # Check primes for verse
            verse_primes = []
            if is_prime(verse_num): verse_primes.append("verse_index")
            if is_prime(w_count): verse_primes.append("word_count")
            if is_prime(l_count): verse_primes.append("letter_count")
            if is_prime(abjad_val): verse_primes.append("abjad_value")
            
            if verse_primes:
                verse_details.append({
                    "verse_index": verse_num,
                    "metrics": {
                        "word_count": w_count,
                        "letter_count": l_count,
                        "abjad_value": abjad_val
                    },
                    "primes_found": verse_primes
                })

        # Check primes for Surah
        surah_primes = []
        if is_prime(surah_idx): surah_primes.append("surah_index")
        if is_prime(verse_count): surah_primes.append("verse_count")
        if is_prime(total_words): surah_primes.append("total_word_count")
        if is_prime(total_letters): surah_primes.append("total_letter_count")
        if is_prime(total_abjad): surah_primes.append("total_abjad_value")

        surah_result = {
            "index": surah_idx,
            "name_en": surah_name_en,
            "metrics": {
                "verse_count": verse_count,
                "total_word_count": total_words,
                "total_letter_count": total_letters,
                "total_abjad_value": total_abjad
            },
            "primes_found": surah_primes,
            "prime_verses": verse_details # Only verses with at least one prime metric
        }
        
        results["surahs"].append(surah_result)

    print(f"Analysis complete. Saving to {OUTPUT_JSON}...")
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
    
    # Generate Text Report
    txt_path = BASE_PATH / "prime-numbers.txt"
    print(f"Saving text report to {txt_path}...")
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write("Prime Number Analysis Report\n")
        f.write("============================\n\n")
        
        for surah in results["surahs"]:
            # Only print if there are interesting findings
            if surah["primes_found"] or surah["prime_verses"]:
                f.write(f"Surah {surah['index']}: {surah['name_en']}\n")
                if surah["primes_found"]:
                    f.write(f"  - Surah Primes: {', '.join(surah['primes_found'])}\n")
                    f.write(f"    (Verses: {surah['metrics']['verse_count']}, Words: {surah['metrics']['total_word_count']}, Letters: {surah['metrics']['total_letter_count']}, Abjad: {surah['metrics']['total_abjad_value']})\n")
                
                if surah["prime_verses"]:
                    f.write(f"  - Prime Verses ({len(surah['prime_verses'])} found):\n")
                    for v in surah["prime_verses"]:
                         f.write(f"    * Verse {v['verse_index']}: {', '.join(v['primes_found'])} ")
                         f.write(f"(W: {v['metrics']['word_count']}, L: {v['metrics']['letter_count']}, A: {v['metrics']['abjad_value']})\n")
                f.write("\n")

    print("Done.")

if __name__ == "__main__":
    analyze_primes()
