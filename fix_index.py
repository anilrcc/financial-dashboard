import re

def fix_index_structure():
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern finding open span directly followed by next span tag, implying missing closing tag
    # We look for: <div class="card-meta">\s*<span>TEXT... (newline/space) <span class="arrow-icon">
    pattern = re.compile(r'(<div class="card-meta">\s*<span>)([^<]+?)(\s*<span class="arrow-icon">)', re.DOTALL)

    def repl(m):
        # Check if it looks like the corrupted commodities ones (contains key chars)
        text = m.group(2).strip()
        # Corrupted text example: "Dec 27, 2025Dec 27, 2025"
        if "Dec" in text and "Updated" not in text and "International" not in text:
            # We enforce a clean structure
            print(f"Fixing broken span: {text[:20]}...")
            return f'{m.group(1)}Dec 29, 2025</span>{m.group(3)}'
        return m.group(0)

    new_content = pattern.sub(repl, content)

    # Also fix duplicates if they are inside <span>...</span> now?
    # Pattern: <span>Dec 29, 2025Dec 29, 2025</span>
    pattern2 = re.compile(r'(<span>)([^<]+?)(</span>)')
    def repl2(m):
        text = m.group(2)
        if text == "Dec 29, 2025Dec 29, 2025":
            print(f"Fixing duplicate in span: {text}")
            return f'{m.group(1)}Dec 29, 2025{m.group(3)}'
        if text == "Dec 27, 2025Dec 27, 2025":
             print(f"Fixing duplicate in span: {text}")
             return f'{m.group(1)}Dec 29, 2025{m.group(3)}'
        return m.group(0)
    
    new_content = pattern2.sub(repl2, new_content)

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("Fixed index.html structure.")

if __name__ == "__main__":
    fix_index_structure()
