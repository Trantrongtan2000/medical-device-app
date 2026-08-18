from bs4 import BeautifulSoup
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_path = r'C:\Users\tantt\Downloads\asset-management-tools\quy_trinh_ttbyt.html'
with open(file_path, 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

print("All section tags and attributes:")
sections = soup.find_all('section')
for s in sections[:15]:
    print("Tag:", s.name, "Attributes:", s.attrs)
    head = s.find(class_=lambda c: c and 'head' in c)
    if head:
        print("   Head text:", head.get_text(strip=True)[:60])
