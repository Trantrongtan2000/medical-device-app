import re

with open('web/index.html', encoding='utf-8') as f:
    text = f.read()

print(f"File size: {len(text):,} characters")
modals = re.findall(r'id=["\']([^"\']*[Mm]odal[^"\']*)["\']', text)
print(f"Modals in index.html ({len(modals)}):")
for m in sorted(set(modals)):
    print(f" - {m}")
