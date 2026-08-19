import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\tantt\Downloads\asset-management-tools\quy_trinh_ttbyt.html', 'r', encoding='utf-8') as f:
    content = f.read()

idx = content.find('<div class="brand">')
if idx != -1:
    print("Found brand div:")
    print(content[idx:idx+400])
else:
    print("Not found")
