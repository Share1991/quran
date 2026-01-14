import pandas as pd
from collections import Counter
from pathlib import Path
import sys

# Configuration
BASE_PATH = Path(r"d:/Corporate Identity/Branding Assets/quran")
INPUT_PARQUET = BASE_PATH / "quran_universal.parquet"
OUTPUT_FILE = BASE_PATH / "all_surahs_frequency_analysis.txt"

def analyze_all_surahs():
    if not INPUT_PARQUET.exists():
        print(f"Error: {INPUT_PARQUET} not found. Please ensure the Universal DataFrame is built.")
        return

    print(f"Loading data...")
    try:
        df = pd.read_parquet(INPUT_PARQUET)
    except Exception as e:
        print(f"Error loading parquet: {e}")
        return

    print(f"Starting analysis for all 114 Surahs...")
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("=== QURAN LETTER FREQUENCY ANALYSIS BY SURAH ===\n")
        f.write("Generated from Normalized Text (Rasm Uthmani without Harakat)\n")
        f.write("================================================\n\n")

        for surah_id in range(1, 115):
            # Filter for specific Surah
            surah_df = df[df['surah_index'] == surah_id]
            
            if surah_df.empty:
                print(f"Warning: Surah {surah_id} not found/empty.")
                continue

            # Get Surah Name from first row
            surah_name_en = surah_df.iloc[0]['surah_name_en']
            # surah_name_ar might be missing if metadata wasn't fully populated in build, but let's try
            surah_name_ar = surah_df.iloc[0]['surah_name_ar'] if 'surah_name_ar' in surah_df.columns else "?"
            
            # Concatenate all normalized text
            all_text = "".join(surah_df['text_normalized'].dropna().tolist())
            
            counts = Counter(all_text)
            
            # Filter only Arabic letters
            valid_chars = set('ابتثجحخدذرزسشصضطظعغفقكلمنهويءؤئ')
            
            filtered_counts = {k: v for k, v in counts.items() if k in valid_chars}
            total_letters = sum(filtered_counts.values())
            
            # Prepare Output Block
            lines = []
            lines.append(f"SURAH {surah_id}: {surah_name_en} ({surah_name_ar})")
            lines.append(f"Total Verses: {len(surah_df)}")
            lines.append(f"Total Letters: {total_letters:,}")
            lines.append("-" * 40)
            lines.append(f"{'Letter':<10} | {'Count':<10} | {'Percentage':<10}")
            lines.append("-" * 40)
            
            # Sort by count descending
            sorted_counts = sorted(filtered_counts.items(), key=lambda x: x[1], reverse=True)
            
            for char, count in sorted_counts:
                percentage = (count / total_letters) * 100 if total_letters > 0 else 0
                lines.append(f"'{char}'        | {count:<10,} | {percentage:.2f}%")
            
            lines.append("\n" + "="*40 + "\n") # Separator between Surahs
            
            # Write block to file
            f.write("\n".join(lines))
            f.write("\n")
            
            print(f"Processed Surah {surah_id}: {surah_name_en}")

    print(f"\nAnalysis complete. Results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    analyze_all_surahs()
