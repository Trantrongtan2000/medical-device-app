import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

app_dir = Path(r"C:\Users\tantt\Downloads\medical-device-app")
js_path = app_dir / "web" / "js" / "app.js"

with open(js_path, "r", encoding="utf-8") as f:
    js_content = f.read()

# Replace setupNavigation in app.js
old_setup_nav_pattern = r'(\s+setupNavigation\(\)\s*\{[\s\S]*?)(// Quick Filter Chips for 4 Clinical Departments)'

new_setup_nav = """        activateTab(targetId, updateHash = true) {
            if (!targetId) return;
            if (!targetId.startsWith('#')) targetId = '#' + targetId;

            const targetPane = document.querySelector(targetId);
            if (!targetPane) return;

            const navButtons = document.querySelectorAll('.sidebar-nav .nav-link, .nav-pills .nav-link');
            const matchingBtn = document.querySelector(`.sidebar-nav .nav-link[data-bs-target="${targetId}"]`);
            const pageHeading = document.getElementById('page-heading');

            // Update nav button active states
            document.querySelectorAll('.sidebar-nav .nav-link').forEach(b => b.classList.remove('active'));
            if (matchingBtn) matchingBtn.classList.add('active');

            // Update tab panes
            document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('show', 'active'));
            targetPane.classList.add('show', 'active');

            // Update page heading
            if (matchingBtn && pageHeading) {
                const text = matchingBtn.querySelector('span')?.textContent || 'Quản lý TTBYT';
                const iconClass = matchingBtn.querySelector('i')?.className || 'bi bi-grid-fill';
                pageHeading.innerHTML = `<i class="${iconClass} text-primary me-2"></i>${text}`;
            }

            // Save state & update URL hash
            localStorage.setItem('active_htm_tab', targetId);
            if (updateHash && window.location.hash !== targetId) {
                try {
                    history.replaceState(null, null, targetId);
                } catch (e) {
                    window.location.hash = targetId;
                }
            }

            // Trigger specific tab data loaders
            if (targetId === '#tab-suppliers') {
                this.switchSupplierSubTab(this.currentSupplierSubTab || 'contracts');
            } else if (targetId === '#tab-staff') {
                this.loadStaff();
                this.loadOncallData();
            } else if (targetId === '#tab-ai-hub') {
                this.loadAPIKeysStatus();
            } else if (targetId === '#tab-semantica-graph') {
                this.loadSemanticaStats();
            } else if (targetId === '#tab-devices') {
                this.loadDevices();
            } else if (targetId === '#tab-inspections') {
                this.loadInspections();
            } else if (targetId === '#tab-transfers') {
                this.loadTransfers();
            } else if (targetId === '#tab-speedmaint') {
                this.loadWorkOrders();
            }
        },

        setupNavigation() {
            const navButtons = document.querySelectorAll('.sidebar-nav .nav-link');

            navButtons.forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.preventDefault();
                    const targetId = btn.getAttribute('data-bs-target');
                    if (targetId) {
                        this.activateTab(targetId, true);
                    }
                });
            });

            // Handle browser back/forward or hash changes
            window.addEventListener('hashchange', () => {
                if (window.location.hash) {
                    this.activateTab(window.location.hash, false);
                }
            });

            // Restore active tab on load
            const currentHash = window.location.hash;
            const savedTab = localStorage.getItem('active_htm_tab');
            const initialTab = (currentHash && document.querySelector(currentHash)) 
                ? currentHash 
                : (savedTab && document.querySelector(savedTab)) 
                    ? savedTab 
                    : '#tab-dashboard';

            this.activateTab(initialTab, false);

            // Search filter
            const searchInput = document.getElementById('search-input');
            if (searchInput) {
                searchInput.addEventListener('input', (e) => {
                    this.currentFilters.search = e.target.value;
                    this.loadDevices();
                });
            }

            // Facility filter
            const facFilter = document.getElementById('filter-facility');
            if (facFilter) {
                facFilter.addEventListener('change', (e) => {
                    this.currentFilters.facility_id = e.target.value;
                    this.loadDevices();
                });
            }

            // Risk filter
            const riskFilter = document.getElementById('filter-risk');
            if (riskFilter) {
                riskFilter.addEventListener('change', (e) => {
                    this.currentFilters.risk_level = e.target.value;
                    this.loadDevices();
                });
            }

            // Quick Filter Chips for 4 Clinical Departments"""

js_content = re.sub(old_setup_nav_pattern, new_setup_nav, js_content, count=1)

with open(js_path, "w", encoding="utf-8") as f:
    f.write(js_content)

print("✅ Đã nâng cấp cơ chế lưu trạng thái Tab (URL Hash & LocalStorage persistence) vào `web/js/app.js`!")
