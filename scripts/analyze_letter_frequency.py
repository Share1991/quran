import pandas as pd
from collections import Counter
from pathlib import Path

# Configuration
BASE_PATH = Path(r"d:/Corporate Identity/Branding Assets/quran")
INPUT_PARQUET = BASE_PATH / "quran_universal.parquet"

def analyze_letters():
    if not INPUT_PARQUET.exists():
        print(f"Error: {INPUT_PARQUET} not found. Please run build_universal_dataframe.py first.")
        return

    print(f"Loading {INPUT_PARQUET}...")
    df = pd.read_parquet(INPUT_PARQUET)
    
    # Concatenate all normalized text
    # We drop NA just in case, though there shouldn't be any
    all_text = "".join(df['text_normalized'].dropna().tolist())
    
    # Define standard Arabic alphabet (plus Hamza chars)
    # We normalized Alef/Ya/Ta-Marbuta in the dataframe, but Hamza/Waw/etc might exist.
    # We want to exclude Quranic pause marks (Small High Jeem, etc.)
    
    valid_chars = set("hbtjivxdrzs$SDTZEgfqklmnywuh") # This is not arabic. 
    # Let's use direct characters.
    
    # Standard Arabic Letters (Abjad base + Hamza forms that might remain)
    # Alif, Ba, Ta, Tha, Jeem, Ha, Kha, Dal, Dhal, Ra, Zay, Seen, Sheen, Sad, Dad, Ta, Za, Ayn, Ghayn, Fa, Qaf, Kaf, Lam, Mim, Nun, Ha, Waw, Ya.
    # Plus Hamza (ء), Waw-Hamza (ؤ), Ya-Hamza (ئ)
    
    VALID_LETTERS = set('mcmnbvclkhgfderyuiopwqazsxdcfvgbhnjmkL') # Still wrong input method.
    
    # Correct Arabic Set
    VALID_LETTERS = set('ابتثجحخدذرزسشصضطظعغفقكلمنهوي')
    VALID_LETTERS.update(['ء', 'ؤ', 'ئ', 'ا', 'ى', 'ة']) # Add forms if they exist (though normalized)
    
    # Filter
    letters_only = [c for c in all_text if c in VALID_LETTERS]
    
    total_letters = len(letters_only)
    counts = Counter(letters_only)
    
    output_lines = []
    output_lines.append(f"--- Analysis Result (Strict Alphabet Filter) ---")
    output_lines.append(f"Total Letters Count: {total_letters:,}")
    output_lines.append(f"Unique Characters Found: {len(counts)}")
    output_lines.append(f"\nLetter Frequency (Descending):")
    output_lines.append(f"{'Letter':<10} | {'Count':<10} | {'Percentage':<10}")
    output_lines.append("-" * 36)
    
    for char, count in counts.most_common():
        percentage = (count / total_letters) * 100
        output_lines.append(f"'{char}'        | {count:<10,} | {percentage:.2f}%")
        
    output_text = "\n".join(output_lines)
    print(output_text)
    
    output_file = BASE_PATH / "letter_frequency_analysis.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(output_text)
    print(f"\nResults saved to {output_file}")

if __name__ == "__main__":
    analyze_letters()
