import pandas as pd
import re
from collections import Counter
from pathlib import Path

# Configuration
BASE_PATH = Path(r"d:/Corporate Identity/Branding Assets/quran")
INPUT_PARQUET = BASE_PATH / "quran_universal.parquet"
OUTPUT_DIR = BASE_PATH / "results"
OUTPUT_FILE = OUTPUT_DIR / "conceptual_word_frequency.txt"

# Concept Mapping (German -> Arabic Normalized Stems)
# Notes:
# - 'ا' is normalized from Alef forms.
# - 'ه' is normalized from Ta Marbuta.
# - 'ي' is normalized from Alef Maqsura.
CONCEPT_MAP = {
    'Mann': ['رجل', 'رجال'], # Rajul, Rijal
    'Frau': ['امراه', 'نساء'], # Imra'ah, Nisa'
    'Kind': ['ولد', 'اولاد', 'طفل', 'اطفال'], # Walad, Awlad, Tifl, Atfal
    'Erde': ['ارض'], # Ard
    'Wasser': ['ماء'], # Ma'
    'Blut': ['دم', 'دماء'], # Dam, Dima'
    'Engel': ['ملك', 'ملائكه', 'ملئكه'], # Malak, Mala'ikah (Standard), Mla'ikh (Rasm)
                                # Our normalize function in build script:
                                # text = re.sub(r'[أإآٱ]', 'ا', text)
                                # It does NOT remove Hamza 'ء' or 'ئ' inside words usually unless strictly diacritic?
                                # Let's check: build_universal_dataframe.py text_normalized logic:
                                # remove harakat. alef->ا. ya->ي. ta->ه.
                                # It does NOT replace Hamza 'ء' with something else explicitly except in Alef forms.
                                # 'ملائكة' -> 'ملائكه' (Ta->Ha). Middle Hamza on Ya 'ئ'?
                                # Let's search for 'ملائكه' and 'مليكه' (if Ya normalized).
                                # To be safe, I'll iterate and check.
                                # Better: 'مليكه' or 'ملىكه' ? 
                                # Actually, usually written 'ملائكة'. Hamza on Ya is a letter.
    'Teufel': ['شيطن', 'شياطين', 'ابليس'], # Shaytan, Shayatin, Iblis
    'Allah': ['الله'],
    'Gebet': ['صلوه', 'صلاه'], # Salah (Rasm often Waw or Alif)
    'Zakat': ['زكوه', 'زكاه'], # Zakah
    'Fasten': ['صوم', 'صيام'], # Sawm, Siyam
    'Krieg': ['حرب', 'قتال'], # Harb, Qital
    'Frieden': ['سلم', 'سلام'], # Silm, Salam
    'Tag': ['يوم', 'ايام'], # Yawm, Ayyam
    'Monat': ['شهر', 'اشهر'], # Shahr, Ashhur
    'Jahr': ['سنه', 'عام', 'سنين'], # Sanah, 'Am, Sinin
    'Himmel': ['سماء', 'سموت'], # Sama', Samawat (Rasm: Smwt)
    'Nacht': ['ليل', 'اليل', 'ليلا'], # Layl, Al-Layl (Rasm), Laylan
}

# Prefix Pattern for Quranic Arabic (Wa, Fa, Bi, Ka, Li, Al...)
# Matches optional prefixes at the start of the word
PREFIX_PATTERN = r'^(?:و|ف|ب|ك|ل|ال|وال|فال|بال|كال|لل|ولل|ت|س|وس|فس)?'

def analyze_concepts():
    if not INPUT_PARQUET.exists():
        print(f"Error: {INPUT_PARQUET} not found.")
        return

    print(f"Loading {INPUT_PARQUET}...")
    df = pd.read_parquet(INPUT_PARQUET)
    
    # Flatten all words to search
    # We use a generator or just process line by line to keep track of locations if needed?
    # For simple counting, flat list is fine.
    
    all_words = []
    for text in df['text_normalized'].dropna():
        # Split and strip
        all_words.extend([w.strip() for w in text.split() if w.strip()])
        
    print(f"Total words to scan: {len(all_words)}")
    
    results = {}
    
    for concept, stems in CONCEPT_MAP.items():
        count = 0
        found_forms = Counter()
        
        # Build Regex for this concept
        # Pattern: ^(prefixes)(stem1|stem2|...)$
        # Note: We want exact word matches (with prefixes), not substrings inside words.
        
        stems_pattern = "|".join([re.escape(s) for s in stems])
        full_pattern = f"{PREFIX_PATTERN}({stems_pattern})$"
        
        regex = re.compile(full_pattern)
        
        for word in all_words:
            match = regex.match(word)
            if match:
                count += 1
                # Capture which stem matched effectively?
                # The regex matches the whole word. 
                # We can store the whole word to see variation (e.g. 'wal-ard', 'wa-ard')
                found_forms[word] += 1
                
        results[concept] = {
            'total': count,
            'forms': found_forms
        }
    
    # Output
    output_lines = []
    output_lines.append("--- Conceptual Word Frequency Analysis ---")
    output_lines.append("Counts based on Normalized Rasm (Aggressive Matching)")
    output_lines.append("Includes prefixes: wa-, fa-, bi-, ka-, li-, al-, etc.\n")
    
    output_lines.append(f"{'Concept (DE)':<15} | {'Count':<8} | {'Detailed Forms Top 5'}")
    output_lines.append("-" * 80)
    
    for concept, data in results.items():
        top_forms = ", ".join([f"{k}({v})" for k, v in data['forms'].most_common(5)])
        output_lines.append(f"{concept:<15} | {data['total']:<8,} | {top_forms}")
        
    output_text = "\n".join(output_lines)
    print(output_text)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(output_text)
    
    print(f"\nSaved to {OUTPUT_FILE}")

if __name__ == "__main__":
    analyze_concepts()
