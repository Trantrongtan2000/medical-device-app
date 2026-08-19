import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

html_path = Path(r"C:\Users\tantt\Downloads\medical-device-app\web\index.html")
app_js_path = Path(r"C:\Users\tantt\Downloads\medical-device-app\web\js\app.js")
css_path = Path(r"C:\Users\tantt\Downloads\medical-device-app\web\css\style.css")

print("🎨 BẮT ĐẦU NÂNG CẤP TOÀN DIỆN GIAO DIỆN UI/UX PRO MAX & DIAGRAM-DESIGN:\n" + "=" * 75)

# 1. Cập nhật CSS với Design Tokens cao cấp
css_content = """/* ==========================================================================
   🏥 Medical Device Management System (BV Quận 7 / PKĐK Tâm Anh Q7)
   ✨ UI/UX Pro Max Design System & Editorial Diagram System
   ========================================================================== */

@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600;700&display=swap');

:root {
    --font-sans: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    --font-mono: 'JetBrains Mono', monospace;

    --color-primary: #0284c7;
    --color-primary-dark: #0369a1;
    --color-primary-light: #f0f9ff;

    --color-teal: #0d9488;
    --color-indigo: #4f46e5;
    --color-success: #059669;
    --color-warning: #d97706;
    --color-danger: #dc2626;

    --surface-page: #f8fafc;
    --surface-card: #ffffff;
    --surface-glass: rgba(255, 255, 255, 0.85);
    
    --border-color: #e2e8f0;
    --border-subtle: #f1f5f9;

    --sidebar-bg: #0f172a;
    --sidebar-card: #1e293b;
    --sidebar-text: #94a3b8;
    --sidebar-active: #ffffff;

    --text-main: #0f172a;
    --text-muted: #64748b;

    --radius-sm: 6px;
    --radius-md: 10px;
    --radius-lg: 14px;
    --shadow-soft: 0 4px 20px -2px rgba(15, 23, 42, 0.06);
    --shadow-card: 0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px -1px rgba(0, 0, 0, 0.05);
}

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: var(--font-sans);
    background-color: var(--surface-page);
    color: var(--text-main);
    font-size: 0.875rem;
    line-height: 1.5;
    -webkit-font-smoothing: antialiased;
}

.font-mono {
    font-family: var(--font-mono);
}

.app-layout {
    display: flex;
    min-height: 100vh;
}

/* Sidebar Styling */
.sidebar-left {
    width: 250px;
    background: var(--sidebar-bg);
    color: var(--sidebar-text);
    display: flex;
    flex-direction: column;
    position: sticky;
    top: 0;
    height: 100vh;
    flex-shrink: 0;
    border-right: 1px solid #1e293b;
    z-index: 100;
}

.sidebar-brand {
    padding: 1.1rem 1.25rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    border-bottom: 1px solid #1e293b;
}

.sidebar-kpi-compact {
    margin: 0.75rem 1rem;
    padding: 0.75rem;
    background: var(--sidebar-card);
    border-radius: var(--radius-md);
    border: 1px solid rgba(255, 255, 255, 0.05);
}

.sidebar-nav .nav-link {
    display: flex;
    align-items: center;
    gap: 0.65rem;
    padding: 0.65rem 1.15rem;
    color: var(--sidebar-text);
    font-size: 0.84rem;
    font-weight: 600;
    border-radius: 0;
    transition: all 0.15s ease;
    border-left: 3px solid transparent;
}

.sidebar-nav .nav-link:hover {
    color: #f8fafc;
    background: rgba(255, 255, 255, 0.04);
}

.sidebar-nav .nav-link.active {
    color: #ffffff;
    background: rgba(2, 132, 199, 0.15);
    border-left-color: #38bdf8;
}

.main-content {
    flex: 1;
    min-width: 0;
    background: var(--surface-page);
    display: flex;
    flex-direction: column;
    height: 100vh;
    overflow-y: auto;
}

.top-header {
    background: #ffffff;
    border-bottom: 1px solid var(--border-color);
    padding: 0.85rem 1.5rem;
    position: sticky;
    top: 0;
    z-index: 90;
}

/* Card & Table Styling */
.clinical-card {
    background: #ffffff;
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-card);
    transition: box-shadow 0.2s ease, transform 0.2s ease;
}

.clinical-card:hover {
    box-shadow: var(--shadow-soft);
}

.btn-clinical {
    border-radius: var(--radius-sm);
    font-size: 0.82rem;
    padding: 0.4rem 0.85rem;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 0.35rem;
}

/* Badge Risk styling */
.badge-risk-A { background-color: #f1f5f9; color: #475569; border: 1px solid #cbd5e1; }
.badge-risk-B { background-color: #e0f2fe; color: #0369a1; border: 1px solid #bae6fd; }
.badge-risk-C { background-color: #fef3c7; color: #b45309; border: 1px solid #fde68a; }
.badge-risk-D { background-color: #fee2e2; color: #b91c1c; border: 1px solid #fecaca; }

/* Diagram wrapper */
.diagram-svg-box svg {
    max-height: 280px;
}
"""

with open(css_path, "w", encoding="utf-8") as f:
    f.write(css_content)
print("✅ Đã cập nhật CSS UI/UX Pro Max!")

