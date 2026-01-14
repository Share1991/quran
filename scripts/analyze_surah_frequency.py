import pandas as pd
from collections import Counter
from pathlib import Path
import sys

# Configuration
BASE_PATH = Path(r"d:/Corporate Identity/Branding Assets/quran")
INPUT_PARQUET = BASE_PATH / "quran_universal.parquet"

def analyze_surah(surah_id: int):
    if not INPUT_PARQUET.exists():
        print(f"Error: {INPUT_PARQUET} not found. Please ensure the Universal DataFrame is built.")
        return

    print(f"Loading data...")
    try:
        df = pd.read_parquet(INPUT_PARQUET)
    except Exception as e:
        print(f"Error loading parquet: {e}")
        return

    # Validate Surah ID
    if surah_id not in df['surah_index'].unique():
        print(f"Error: Surah index {surah_id} not found in database.")
        return

    # Filter for specific Surah
    surah_df = df[df['surah_index'] == surah_id]
    
    # Get Surah Name from first row
    surah_name_en = surah_df.iloc[0]['surah_name_en']
    surah_name_ar = surah_df.iloc[0]['surah_name_ar']
    
    print(f"Analyzing Surah {surah_id}: {surah_name_en} ({surah_name_ar})")
    
    # Concatenate all normalized text
    # Normalize logic in build_universal_dataframe.py:
    # - Removes Harakat
    # - Alef forms -> 'ا'
    # - Alef Maqsura 'ى' -> 'ي'
    # - Ta Marbuta 'ة' -> 'ه'
    # - Hamza 'ء', 'ؤ', 'ئ' are preserved
    
    all_text = "".join(surah_df['text_normalized'].dropna().tolist())
    
    # Define Valid Arabic Letters for counting (excluding spaces data-cleaning might have left)
    # We want to count what is actually there, but filter out non-Arabic if any.
    # The build script cleaned most everything except letters.
    
    # Let's count all characters that are Arabic letters
    # ranges: \u0600-\u06FF common
    
    counts = Counter(all_text)
    
    # Filter only Arabic letters just in case
    # using a permissible set based on normalization
    valid_chars = set('ابتثجحخدذرزسشصضطظعغفقكلمنهويءؤئ')
    
    filtered_counts = {k: v for k, v in counts.items() if k in valid_chars}
    total_letters = sum(filtered_counts.values())
    
    # Prepare Output
    output_lines = []
    output_lines.append(f"Analysis for Surah {surah_id}: {surah_name_en} ({surah_name_ar})")
    output_lines.append(f"Total Verses: {len(surah_df)}")
    output_lines.append(f"Total Letters: {total_letters:,}")
    output_lines.append("-" * 40)
    output_lines.append(f"{'Letter':<10} | {'Count':<10} | {'Percentage':<10}")
    output_lines.append("-" * 40)
    
    # Sort by count descending
    sorted_counts = sorted(filtered_counts.items(), key=lambda x: x[1], reverse=True)
    
    for char, count in sorted_counts:
        percentage = (count / total_letters) * 100 if total_letters > 0 else 0
        output_lines.append(f"'{char}'        | {count:<10,} | {percentage:.2f}%")
    
    output_text = "\n".join(output_lines)
    print(output_text)
    
    # Save to file
    output_filename = BASE_PATH / f"surah_{surah_id}_frequency.txt"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(output_text)
    print(f"\nSaved analysis to {output_filename}")

def main():
    if len(sys.argv) > 1:
        try:
            surah_id = int(sys.argv[1])
        except ValueError:
            print("Usage: python analyze_surah_frequency.py [surah_id]")
            return
    else:
        try:
            input_str = input("Enter Surah ID (1-114): ")
            surah_id = int(input_str)
        except ValueError:
            print("Invalid input.")
            return

    analyze_surah(surah_id)

if __name__ == "__main__":
    main()
