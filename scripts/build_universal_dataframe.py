import json
import pandas as pd
import re
from pathlib import Path
import os

# --- Constants & Configuration ---
BASE_PATH = Path(r"d:/Corporate Identity/Branding Assets/quran")
SURAH_METADATA_PATH = BASE_PATH / "surah.json"
SURAH_FILES_DIR = BASE_PATH / "surah"
OUTPUT_PARQUET = BASE_PATH / "quran_universal.parquet"
OUTPUT_CSV = BASE_PATH / "quran_universal.csv"

# Standard Abjad Values (Hisab al-Jummal)
ABJAD_MAP = {
    'ا': 1, 'أ': 1, 'إ': 1, 'آ': 1, 'ٱ': 1, 'ء': 1, # Hamza/Alef forms usually counted as 1
    'ب': 2,
    'ج': 3,
    'د': 4,
    'ه': 5, 'ة': 5, # Ta Marbuta -> Ha value
    'و': 6,
    'ز': 7,
    'ح': 8,
    'ط': 9,
    'ي': 10, 'ى': 10, # Ya and Alef Maqsura
    'ك': 20,
    'ل': 30,
    'م': 40,
    'ن': 50,
    'س': 60,
    'ع': 70,
    'ف': 80,
    'ص': 90,
    'ق': 100,
    'ر': 200,
    'ش': 300,
    'ت': 400,
    'ث': 500,
    'خ': 600,
    'ذ': 700,
    'ض': 800,
    'ظ': 900,
    'غ': 1000
}

# --- Text Normalization Functions ---

def normalize_text(text: str) -> str:
    """
    Normalizes Arabic text for search and mathematical analysis.
    1. Removes all Harakat (diacritics).
    2. Unifies Alef forms to 'ا'.
    3. Unifies Ya forms to 'ي'.
    4. Converts Ta Marbuta 'ة' to 'ه'.
    """
    if not isinstance(text, str):
        return ""
    
    # 1. Remove Harakat and Tatweel
    # Fathatan, Dammatan, Kasratan, Fatha, Damma, Kasra, Shadda, Sukun, Superscript Alef, Tatweel
    text = re.sub(r'[\u064B-\u065F\u0670\u0640]', '', text) 
    
    # 2. Alef Normalization
    text = re.sub(r'[أإآٱ]', 'ا', text)
    
    # 3. Ya Normalization (Alef Maqsura -> Ya)
    text = re.sub(r'ى', 'ي', text)
    
    # 4. Ta Marbuta Normalization (-> Ha)
    text = re.sub(r'ة', 'ه', text)
    
    return text

def calculate_abjad_value(text: str) -> int:
    """Calculate the cumulative Abjad value of the normalized text."""
    # We use the normalized text logic specifically for calculation to ensure consistency
    # (e.g. ignoring harakat, treating hamza forms as 1)
    
    # Note: For strict Abjad, sometimes people want specific rules for Hamza.
    # Here we map all Alef/Hamza forms to 1 in the dictionary above.
    # Effectively, we filter only characters in our map.
    
    val = 0
    # Process each char. If it's a diacritic it won't be in the map (and thus ignored).
    # We should use the raw text but skip non-letters.
    # However, to be safe, let's normalize 'lightly' to match keys, 
    # but strictly speaking `normalize_text` above does replacements like Ta Marbuta -> Ha which implies 5.
    
    # Let's clean the text for calculation:
    # 1. Remove non-letters (preserving the letters we have in map)
    
    for char in text:
        if char in ABJAD_MAP:
            val += ABJAD_MAP[char]
        else:
            # Check if it is a normalization candidate that isn't in map directly?
            # Our ABJAD_MAP handles raw forms too (like 'أ').
            pass
            
    return val

# --- Main Build Process ---

def build_dataframe():
    print("Loading Metadata...")
    with open(SURAH_METADATA_PATH, 'r', encoding='utf-8') as f:
        surah_meta = json.load(f)
    
    # Convert metadata to dict for faster lookup by index
    # surah.json has "index": "001"
    meta_dict = {s['index']: s for s in surah_meta}
    
    all_verses = []
    
    print("Processing Surah files...")
    # Iterate 1 to 114
    for i in range(1, 115):
        index_str = f"{i:03d}"
        file_path = SURAH_FILES_DIR / f"surah_{i}.json"
        
        if not file_path.exists():
            print(f"WARNING: File not found {file_path}")
            continue
            
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        surah_name_en = data.get('name')
        surah_idx = int(data.get('index'))
        
        # Get metadata for this Surah
        smeta = meta_dict.get(index_str, {})
        revelation_place = smeta.get('place')
        revelation_type = smeta.get('type')
        
        verses_dict = data.get('verse', {})
        
        for v_key, v_text in verses_dict.items():
            # v_key is like "verse_1", "verse_2", "verse_0"
            if not v_key.startswith('verse_'):
                continue
                
            verse_num_str = v_key.replace('verse_', '')
            verse_num = int(verse_num_str)
            
            # Normalization
            norm_text = normalize_text(v_text)
            
            # Abjad
            # Calculate from the raw text (or normalized? - usually raw letters determine value, but norm helps unify shapes)
            # We iterate over raw chars and lookup in ABJAD_MAP which handles variants.
            abjad_val = calculate_abjad_value(v_text)
            
            # Determine Juz (This is a bit complex as Juz can split verses. 
            # The JSON structure provides juz ranges. For now, we can approximate or use the juz structure if needed.
            # surah.json has 'juz' array with start/end verses.
            
            juz_num = None
            if 'juz' in smeta:
                for j in smeta['juz']:
                    # j is like {"index": "01", "verse": {"start": "verse_1", "end": "verse_7"}}
                    j_idx = int(j['index'])
                    v_start = int(j['verse']['start'].replace('verse_', ''))
                    v_end = int(j['verse']['end'].replace('verse_', ''))
                    
                    if v_start <= verse_num <= v_end:
                        juz_num = j_idx
                        break
            
            row = {
                'surah_index': surah_idx,
                'surah_name_en': surah_name_en,
                'surah_name_ar': smeta.get('titleAr'),
                'verse_index': verse_num,
                'text_rasm': v_text,
                'text_normalized': norm_text,
                'abjad_value': abjad_val,
                'juz_index': juz_num,
                'revelation_place': revelation_place,
                'revelation_type': revelation_type,
                'page_number': smeta.get('pages') # This might be start page
            }
            all_verses.append(row)

    print(f"Constructed list with {len(all_verses)} verses.")
    
    df = pd.DataFrame(all_verses)
    
    # Sort
    df = df.sort_values(by=['surah_index', 'verse_index'])
    
    print("Saving to parquet...")
    df.to_parquet(OUTPUT_PARQUET, index=False)
    print("Saving to csv...")
    df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig') # sig for Excel support
    
    print("Done.")
    print(df.head())
    print(df.tail())

if __name__ == "__main__":
    build_dataframe()
