import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

app_dir = Path(r"C:\Users\tantt\Downloads\medical-device-app")
css_path = app_dir / "web" / "css" / "style.css"
js_path = app_dir / "web" / "js" / "app.js"

with open(css_path, "r", encoding="utf-8") as f:
    css = f.read()

# 1. Add global overflow-x: hidden to html, body, .app-layout, .main-content
global_reset_css = """html, body {
    height: 100%;
    margin: 0;
    padding: 0;
    overflow-x: hidden;
    background-color: var(--bg-body);
    font-family: var(--font-family);
    color: var(--color-text-main);
    line-height: 1.5;
}

.app-layout {
    display: flex;
    min-height: 100vh;
    width: 100vw;
    max-width: 100%;
    overflow-x: hidden;
    position: relative;
}"""

css = re.sub(
    r'body\s*\{[\s\S]*?\}[\s\S]*?\.app-layout\s*\{[\s\S]*?\}',
    global_reset_css,
    css
)

# 2. Perfect Sidebar width transition (width: 255px -> 0px)
sidebar_perfect_css = """/* ==================== LEFT SIDEBAR & NAVIGATION (ZERO-OVERFLOW ARCHITECTURE) ==================== */
.sidebar-left {
    width: 255px !important;
    min-width: 255px !important;
    max-width: 255px !important;
    background: var(--sidebar-bg);
    color: var(--sidebar-text);
    display: flex !important;
    flex-direction: column !important;
    position: sticky;
    top: 0;
    height: 100vh;
    flex-shrink: 0;
    border-right: 1px solid var(--sidebar-border);
    z-index: 100;
    overflow: hidden !important;
    box-sizing: border-box;
    transition: width 0.25s cubic-bezier(0.4, 0, 0.2, 1),
                min-width 0.25s cubic-bezier(0.4, 0, 0.2, 1),
                max-width 0.25s cubic-bezier(0.4, 0, 0.2, 1),
                opacity 0.2s ease,
                border 0.2s ease;
}

.sidebar-collapsed .sidebar-left {
    width: 0 !important;
    min-width: 0 !important;
    max-width: 0 !important;
    border-right: none !important;
    opacity: 0 !important;
    visibility: hidden !important;
    pointer-events: none !important;
    overflow: hidden !important;
    padding: 0 !important;
    margin: 0 !important;
}

.sidebar-brand {
    padding: 1rem 1.15rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    border-bottom: 1px solid var(--sidebar-border);
    flex-shrink: 0;
    white-space: nowrap;
    min-width: 255px;
}

.sidebar-kpi-compact {
    background: var(--sidebar-card) !important;
    border: 1px solid var(--sidebar-border) !important;
    border-radius: var(--radius-sm) !important;
    padding: 0.55rem 0.75rem !important;
    margin: 0.65rem 0.75rem 0.25rem 0.75rem !important;
    flex-shrink: 0;
    min-width: 235px;
}

.sidebar-nav {
    padding: 0.4rem 0.55rem !important;
    flex: 1 1 auto !important;
    min-height: 0 !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;
    display: flex !important;
    flex-direction: column !important;
    flex-wrap: nowrap !important;
    gap: 0.12rem !important;
    min-width: 255px;
}

.sidebar-nav::-webkit-scrollbar {
    width: 4px;
}
.sidebar-nav::-webkit-scrollbar-track {
    background: transparent;
}
.sidebar-nav::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.15);
    border-radius: 4px;
}
.sidebar-nav::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.3);
}

.sidebar-nav .nav-item {
    width: 100% !important;
    display: block !important;
}

.sidebar-nav .nav-link {
    color: #cbd5e1 !important;
    padding: 0.45rem 0.7rem !important;
    border-radius: var(--radius-sm);
    display: flex !important;
    align-items: center !important;
    gap: 0.6rem;
    font-weight: 500;
    font-size: 0.81rem !important;
    transition: all 0.15s ease;
    text-decoration: none;
    border: none;
    background: transparent;
    width: 100% !important;
    text-align: left;
    white-space: nowrap !important;
    overflow: hidden !important;
}

.sidebar-nav .nav-link span:first-of-type {
    text-overflow: ellipsis;
    overflow: hidden;
    white-space: nowrap;
}

.sidebar-nav .nav-link:hover {
    color: #ffffff !important;
    background: rgba(255, 255, 255, 0.08) !important;
}

.sidebar-nav .nav-link.active {
    color: #ffffff !important;
    background: #0284c7 !important;
    font-weight: 600;
    box-shadow: 0 2px 8px rgba(2, 132, 199, 0.35);
}

.sidebar-footer {
    padding: 0.65rem 0.85rem !important;
    border-top: 1px solid var(--sidebar-border);
    background: rgba(9, 13, 22, 0.95);
    flex-shrink: 0 !important;
    min-width: 255px;
}

/* Main Workspace Zero-Overflow */
.main-content {
    flex: 1 1 auto;
    display: flex;
    flex-direction: column;
    min-width: 0;
    max-width: 100%;
    overflow-x: hidden;
    width: 100%;
}

.top-header {
    height: 56px;
    background: #ffffff;
    border-bottom: 1px solid var(--border-color);
    padding: 0 1.25rem;
    position: sticky;
    top: 0;
    z-index: 90;
    flex-shrink: 0;
}
"""

css = re.sub(
    r'/\* ==================== LEFT SIDEBAR & NAVIGATION \(FIXED BOUNDS & NO WRAP\) ==================== \*/[\s\S]*?\.top-header\s*\{[\s\S]*?\}',
    sidebar_perfect_css,
    css
)

with open(css_path, "w", encoding="utf-8") as f:
    f.write(css)

print("✅ Đã cập nhật CSS Sidebar với kiến trúc Width-Transition mượt mà, Zero-Overflow và 100% không gian màn hình!")
