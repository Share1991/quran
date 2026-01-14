import pandas as pd
from collections import Counter
from pathlib import Path
import os

# Configuration
BASE_PATH = Path(r"d:/Corporate Identity/Branding Assets/quran")
INPUT_PARQUET = BASE_PATH / "quran_universal.parquet"
OUTPUT_DIR = BASE_PATH / "results"
OUTPUT_FILE = OUTPUT_DIR / "word_frequency_analysis.txt"

def analyze_words():
    # 1. Load Data
    if not INPUT_PARQUET.exists():
        print(f"Error: {INPUT_PARQUET} not found. Please run build_universal_dataframe.py first.")
        return

    print(f"Loading {INPUT_PARQUET}...")
    df = pd.read_parquet(INPUT_PARQUET)
    
    # 2. Tokenize
    # We use 'text_normalized' effectively for math/counting as per guidelines.
    # This ignores harakat but preserves structural shape (Rasm-like but unified).
    # If the user wanted visual word forms (with vowels), we'd use 'text_rasm'.
    # Guidelines say: "text_normalized (Search/Math)". Word count is Math.
    
    print("Tokenizing words...")
    all_words = []
    
    # Iterate over verses to ensure we don't merge across boundaries
    for text in df['text_normalized'].dropna():
        # Split by whitespace
        # Filter out empty strings if any
        words = [w for w in text.split() if w.strip()]
        all_words.extend(words)
        
    total_words = len(all_words)
    word_counts = Counter(all_words)
    unique_words = len(word_counts)
    
    print(f"Total Words: {total_words}")
    print(f"Unique Words: {unique_words}")
    
    # 3. Format Output
    output_lines = []
    output_lines.append("--- Quran Word Frequency Analysis ---")
    output_lines.append(f"Source: {INPUT_PARQUET}")
    output_lines.append(f"Total Words Count: {total_words:,}")
    output_lines.append(f"Unique Words Count: {unique_words:,}")
    output_lines.append("\nTop Frequent Words:")
    output_lines.append(f"{'Rank':<6} | {'Word':<20} | {'Count':<10} | {'Frequency':<10}")
    output_lines.append("-" * 55)
    
    # List all words? Maybe just top 1000 for summary, or all? 
    # The request said "zählt alle wörter" (counts all words).
    # Usually printing 70,000 lines to console is bad.
    # But writing to file should contain ALL words if possible or a significant amount.
    # Let's write ALL unique words to the file.
    
    rank = 1
    for word, count in word_counts.most_common():
        percentage = (count / total_words) * 100
        output_lines.append(f"{rank:<6} | {word:<20} | {count:<10,} | {percentage:.4f}%")
        rank += 1
        
    output_text = "\n".join(output_lines)
    
    # 4. Save
    # Ensure directory exists (redundant check but safe)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(output_text)
        
    print(f"Analysis complete. Results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    analyze_words()
