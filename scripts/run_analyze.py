#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script to run understand analysis"""

import sys
sys.path.insert(0, 'C:/Users/tantt/AppData/Local/npm-cache/_npx/1e7f6d9597241db0')

# Try importing understand
try:
    from understand import main as understand_main
    print("Running understand analysis...")
    understand_main(["--language", "en", "C:/Users/tantt/Downloads/medical-device-app"])
except ImportError as e:
    print(f"Cannot import understand: {e}")
    print("Creating manual analysis report...")
    
    # Manual analysis output
    import json
    from pathlib import Path
    
    project_root = Path("C:/Users/tantt/Downloads/medical-device-app")
    
    # Count files
    py_files = list(project_root.rglob("*.py"))
    js_files = list(project_root.rglob("*.js"))
    html_files = list(project_root.rglob("*.html"))
    css_files = list(project_root.rglob("*.css"))
    sql_files = list(project_root.rglob("*.sql"))
    
    analysis = {
        "project": "Medical Device Management System",
        "description": "Quan 7 TP.HCM Medical Equipment Management",
        "languages": ["Python", "JavaScript", "HTML", "CSS", "SQL"],
        "frameworks": ["FastAPI", "SQLite", "Bootstrap"],
        "files": {
            "python": len(py_files),
            "javascript": len(js_files),
            "html": len(html_files),
            "css": len(css_files),
            "sql": len(sql_files)
        },
        "total_files": len(py_files) + len(js_files) + len(html_files) + len(css_files) + len(sql_files)
    }
    
    print(json.dumps(analysis, indent=2, ensure_ascii=False))