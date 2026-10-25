import fitz

doc = fitz.open("GID-01.pdf")
text = ""
for page_num in range(len(doc)):
    page = doc.load_page(page_num)
    text += f"--- Page {page_num + 1} ---\n"
    text += page.get_text("text") + "\n\n"

with open("GID-01_extracted.txt", "w", encoding="utf-8") as f:
    f.write(text)

print(f"Extracted {len(doc)} pages to GID-01_extracted.txt")
