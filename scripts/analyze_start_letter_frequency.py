import pandas as pd
from collections import Counter
from pathlib import Path
import os

# Configuration
BASE_PATH = Path(r"d:/Corporate Identity/Branding Assets/quran")
INPUT_PARQUET = BASE_PATH / "quran_universal.parquet"
OUTPUT_DIR = BASE_PATH / "results"
OUTPUT_FILE = OUTPUT_DIR / "word_start_letter_frequency.txt"

def analyze_start_letters():
    # 1. Load Data
    if not INPUT_PARQUET.exists():
        print(f"Error: {INPUT_PARQUET} not found. Please run build_universal_dataframe.py first.")
        return

    print(f"Loading {INPUT_PARQUET}...")
    df = pd.read_parquet(INPUT_PARQUET)
    
    # 2. Tokenize and Extract Start Letters
    print("Analyzing word start letters...")
    start_letters = []
    
    # Valid Arabic Letters (Normalized)
    # We want to ignore potential punctuation or anomalies if any
    VALID_LETTERS = set('ابتثجحخدذرزسشصضطظعغفقكلمنهوي')
    # Add normalized forms if not covered (Alif 'ا', Ya 'ي', Ha 'ه' are in there)
    # text_normalized uses 'ا' for all Alefs, 'ي' for Alif Maqsura, 'ه' for Ta Marbuta.
    
    total_words_processed = 0
    
    for text in df['text_normalized'].dropna():
        words = [w for w in text.split() if w.strip()]
        for word in words:
            if not word:
                continue
            
            first_char = word[0]
            
            # Only count if it's a valid Arabic letter or commonly accepted char
            # The normalized text might have some Quranic marks if not fully cleaned of ALL non-letters
            # but our normalize function cleaned harakat. 
            # Let's count it if it's in our valid set to contain noise.
            
            if first_char in VALID_LETTERS:
                start_letters.append(first_char)
            elif first_char == 'ء': # Hamza might occur at start (rare in normalized but possible if 'ء' was preserved)
                 start_letters.append(first_char)
            else:
                # Debug print for unexpected chars logic
                # print(f"Skipping char: {first_char} in word {word}")
                pass
            
            total_words_processed += 1
            
    total_starts = len(start_letters)
    counts = Counter(start_letters)
    
    # 3. Format Output
    output_lines = []
    output_lines.append("--- Quran Word Start Letter Frequency ---")
    output_lines.append(f"Source: {INPUT_PARQUET}")
    output_lines.append(f"Total Words Processed: {total_words_processed:,}")
    output_lines.append(f"Valid Start Letters Counted: {total_starts:,}")
    output_lines.append("\nFrequency by Letter (Descending):")
    output_lines.append(f"{'Letter':<10} | {'Count':<10} | {'Percentage':<10}")
    output_lines.append("-" * 40)
    
    for char, count in counts.most_common():
        percentage = (count / total_starts) * 100
        output_lines.append(f"'{char}'        | {count:<10,} | {percentage:.4f}%")
        
    output_text = "\n".join(output_lines)
    
    # 4. Save
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(output_text)
        
    print(output_text)
    print(f"\nAnalysis complete. Results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    analyze_start_letters()
