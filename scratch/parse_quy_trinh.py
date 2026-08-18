import re
import sys
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\tantt\Downloads\asset-management-tools\quy_trinh_ttbyt.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

soup = BeautifulSoup(html_content, 'html.parser')

print("=== SO TAY QUY TRINH & BIEU MAU (QUY_TRINH_TTBYT.HTML) ===")
groups = soup.find_all('div', class_='nav-group')
for g in groups:
    code_el = g.find('span', class_='nav-code')
    label_el = g.find('span', class_='nav-label')
    code = code_el.get_text(strip=True) if code_el else ''
    label = label_el.get_text(strip=True) if label_el else ''
    print(f"\n📂 [{code}] {label}")
    
    links = g.find_all('a', class_='nav-link')
    for a in links:
        chip = a.find('span', class_='chip')
        chip_text = chip.get_text(strip=True) if chip else ''
        text = a.get_text(strip=True).replace(chip_text, '').strip()
        print(f"   ├─ [{chip_text}] {text}")
