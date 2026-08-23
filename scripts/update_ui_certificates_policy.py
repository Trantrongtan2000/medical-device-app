import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

app_dir = Path(r"C:\Users\tantt\Downloads\medical-device-app")
html_path = app_dir / "web" / "index.html"
app_js_path = app_dir / "web" / "js" / "app.js"

# 1. Update web/js/app.js
with open(app_js_path, "r", encoding="utf-8") as f:
    js = f.read()

# Update certificate section in renderStaff
old_cert_render = """<div class="mb-3">
                                <span class="small text-muted d-block" style="font-size: 0.72rem; font-weight: 700;">CHỨNG CHỈ NĂNG LỰC:</span>
                                <div class="d-flex flex-column gap-1 mt-1">
                                    ${(s.certificates || '').split(',').map(c => c.trim()).filter(Boolean).map(c => `
                                        <div class="small text-dark d-flex align-items-center gap-1" style="font-size: 0.76rem;">
                                            <i class="bi bi-patch-check-fill text-primary" style="font-size: 0.75rem;"></i>
                                            <span>${this.escapeHtml(c)}</span>
                                        </div>
                                    `).join('') || '<span class="small text-muted fst-italic">Đang cập nhật hồ sơ</span>'}
                                </div>
                            </div>"""

new_cert_render = """<div class="mb-3">
                                <span class="small text-muted d-block" style="font-size: 0.72rem; font-weight: 700;">HỒ SƠ VĂN BẰNG & CHỨNG CHỈ MINH CHỨNG:</span>
                                <div class="mt-1">
                                    ${s.certificates && s.certificates.trim() ? `
                                        <div class="d-flex flex-column gap-1">
                                            ${s.certificates.split(',').map(c => c.trim()).filter(Boolean).map(c => `
                                                <div class="small text-dark d-flex align-items-center gap-1" style="font-size: 0.76rem;">
                                                    <i class="bi bi-file-earmark-check-fill text-success" style="font-size: 0.75rem;"></i>
                                                    <span>${this.escapeHtml(c)}</span>
                                                </div>
                                            `).join('')}
                                        </div>
                                    ` : `
                                        <span class="badge bg-light text-muted border font-mono" style="font-size: 0.72rem;">
                                            <i class="bi bi-shield-lock me-1 text-secondary"></i>Chưa cập nhật văn bằng minh chứng
                                        </span>
                                    `}
                                </div>
                            </div>"""

if old_cert_render in js:
    js = js.replace(old_cert_render, new_cert_render)
    with open(app_js_path, "w", encoding="utf-8") as f:
        f.write(js)
    print("✅ Đã cập nhật chính sách hiển thị chứng chỉ thực trong `web/js/app.js`!")

# 2. Update web/index.html modals
with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

html = html.replace(
    'CHỨNG CHỈ NGHỀ NGHIỆP & AN TOÀN',
    'VĂN BẰNG & CHỨNG CHỈ MINH CHỨNG (Chỉ nhập khi có số hiệu / hồ sơ gốc đối soát)'
)

html = html.replace(
    'placeholder="VD: Chứng chỉ An toàn Bức xạ Y tế, Chứng chỉ Kiểm định An toàn Điện Y Sinh IEC 62353..."',
    'placeholder="Nhập chính xác số hiệu chứng chỉ, cơ quan cấp, ngày cấp (để trống nếu chưa có văn bản minh chứng)..."'
)

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)
print("✅ Đã cập nhật nhãn trường chứng chỉ minh chứng trong `web/index.html`!")
