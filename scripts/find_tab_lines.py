with open('web/index.html', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if 'id="deviceModalTabs"' in line or 'tab-modal-general' in line or 'deviceDetailsModal' in line:
            print(f"Line {i+1}: {line.strip()}")
