import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
app_js = Path(r"C:\Users\tantt\Downloads\medical-device-app\web\js\app.js")

with open(app_js, "r", encoding="utf-8") as f:
    code = f.read()

# Fix provenance mapping in showDeviceDetails and explainDeviceProvenance
old_snippet = """                        <ul class="list-unstyled mb-0">
                            ${prov.causal_provenance_chain.map(p => `
                                <li class="p-2 mb-1 bg-white border rounded">
                                    <span class="badge bg-primary me-2">${p.step}</span>
                                    <strong>${p.relation}</strong>: ${p.target}
                                    <div class="text-muted" style="font-size: 0.74rem;">${p.evidence}</div>
                                </li>
                            `).join('')}
                        </ul>"""

new_snippet = """                        <ul class="list-unstyled mb-0">
                            ${prov.causal_provenance_chain.map((p, idx) => `
                                <li class="p-2 mb-2 bg-white border rounded shadow-sm">
                                    <div class="d-flex align-items-center gap-2">
                                        <span class="badge bg-primary font-mono">BƯỚC ${idx + 1}</span>
                                        <span class="fw-bold text-dark">${typeof p === 'string' ? p : (p.step + ': ' + p.relation)}</span>
                                    </div>
                                </li>
                            `).join('')}
                        </ul>"""

code = code.replace(old_snippet, new_snippet)

old_explain_snippet = """                    <ul class="list-unstyled mb-0" style="font-size: 0.82rem;">
                        ${data.causal_provenance_chain.map(p => `
                            <li class="p-2 mb-1 bg-white border rounded">
                                <span class="badge bg-primary me-2">${p.step}</span>
                                <strong>${p.relation}</strong>: ${p.target}
                                <div class="text-muted" style="font-size: 0.74rem;">${p.evidence}</div>
                            </li>
                        `).join('')}
                    </ul>"""

new_explain_snippet = """                    <ul class="list-unstyled mb-0" style="font-size: 0.82rem;">
                        ${data.causal_provenance_chain.map((p, idx) => `
                            <li class="p-2 mb-2 bg-white border rounded shadow-sm">
                                <div class="d-flex align-items-center gap-2">
                                    <span class="badge bg-primary font-mono">BƯỚC ${idx + 1}</span>
                                    <span class="fw-bold text-dark">${typeof p === 'string' ? p : (p.step + ': ' + p.relation)}</span>
                                </div>
                            </li>
                        `).join('')}
                    </ul>"""

code = code.replace(old_explain_snippet, new_explain_snippet)

with open(app_js, "w", encoding="utf-8") as f:
    f.write(code)

print("✅ Đã sửa định dạng chuỗi giải trình Semantica trong `web/js/app.js`!")
