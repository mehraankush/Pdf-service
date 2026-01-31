import os

from src.main import process_pdf

file_path = "data/input/sample3.pdf"
chunks = process_pdf(file_path)

os.makedirs("data/output", exist_ok=True)
output_path = file_path.replace("data/input", "data/output").replace(".pdf", "_extracted.txt")
with open(output_path, "w", encoding="utf-8") as f:
    for i, chunk in enumerate(chunks):
        f.write(f"\n--- Chunk {i+1} ---\n\n")
        f.write(chunk)

print(f"\nWrote full extracted text to: {output_path}")

for i, chunk in enumerate(chunks):
    print(f"\n--- Chunk {i+1} (len={len(chunk)}) ---\n")
    print(chunk)
