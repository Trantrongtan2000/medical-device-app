/**
 * API Client Module cho Medical Device Management App
 * Hỗ trợ các endpoint quản lý tài sản, Asset Tag, Kiểm kê riêng (Audits), Phụ kiện (Accessories), Điều chuyển, Lịch PM, Work Orders và Xuất dữ liệu
 */

const apiClient = {
    baseUrl: '',

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            if (!response.ok) {
                const error = await response.json().catch(() => ({ detail: response.statusText }));
                throw new Error(error.detail || `HTTP Error ${response.status}`);
            }

            return await response.json();
        } catch (err) {
            console.error(`API Error on ${endpoint}:`, err);
            throw err;
        }
    },

    // Devices (Snipe-IT Asset API)
    async getDevices(filters = {}) {
        const params = new URLSearchParams();
        if (filters.facility_id) params.append('facility_id', filters.facility_id);
        if (filters.category_id) params.append('category_id', filters.category_id);
        if (filters.alert_status) params.append('alert_status', filters.alert_status);
        if (filters.status) params.append('status', filters.status);
        if (filters.risk_level) params.append('risk_level', filters.risk_level);
        if (filters.search) params.append('search', filters.search);
        if (filters.limit) params.append('limit', filters.limit);
        if (filters.offset) params.append('offset', filters.offset);

        return this.request(`/api/devices?${params.toString()}`);
    },

    async getDevice(id) {
        return this.request(`/api/devices/${id}`);
    },

    // Dedicated Audit Module (Kiểm kê riêng)
    async getAudits() {
        return this.request('/api/audits');
    },

    async auditDevice(data) {
        return this.request('/api/devices/audit', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    // Accessories & Components
    async getAccessories() {
        return this.request('/api/accessories');
    },

    // Transfer Device (TLHD Mục 4 & Snipe-IT Check-out)
    async transferDevice(data) {
        return this.request('/api/devices/transfer', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    // Dashboard KPI
    async getSummary() {
        return this.request('/api/dashboard/summary');
    },

    async getFacilities() {
        return this.request('/api/dashboard/facilities');
    },

    async getCategories() {
        return this.request('/api/dashboard/categories');
    },

    // Work Orders & Tickets (SpeedMaint CMMS)
    async getWorkOrders() {
        return this.request('/api/work-orders');
    },

    async createWorkOrder(data) {
        return this.request('/api/work-orders', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    // Schedules (PM Calendar)
    async getSchedules() {
        return this.request('/api/schedules');
    },

    // PDF URL
    getPdfUrl(filename) {
        if (!filename) return '#';
        return `/api/pdf/view?filename=${encodeURIComponent(filename)}`;
    },

    // CSV Export URL
    getCsvExportUrl(filters = {}) {
        const params = new URLSearchParams();
        if (filters.facility_id) params.append('facility_id', filters.facility_id);
        if (filters.category_id) params.append('category_id', filters.category_id);
        if (filters.alert_status) params.append('alert_status', filters.alert_status);
        if (filters.search) params.append('search', filters.search);
        return `/api/export/csv?${params.toString()}`;
    },

    // Utility formatting
    formatDate(dateStr) {
        if (!dateStr) return '-';
        try {
            const parts = dateStr.split(/[-/]/);
            if (parts.length === 3) {
                if (parts[0].length === 4) {
                    return `${parts[2].padStart(2, '0')}/${parts[1].padStart(2, '0')}/${parts[0]}`;
                }
                return dateStr;
            }
            return dateStr;
        } catch {
            return dateStr;
        }
    }
};

window.apiClient = apiClient;