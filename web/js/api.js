/**
 * API Client cho Medical Device Management System (BV Quận 7)
 * Tương thích linh hoạt môi trường web
 */

const API_BASE_URL = window.location.origin.startsWith('http') 
    ? `${window.location.origin}/api` 
    : 'http://127.0.0.1:8000/api';

const apiClient = {
    /**
     * Gọi API với xử lý lỗi chung
     */
    async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            ...options,
        };

        try {
            const response = await fetch(url, config);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`API Error [${endpoint}]:`, error);
            throw error;
        }
    },

    /**
     * Lấy thống kê KPI dashboard
     */
    async getSummary() {
        return await this.request('/dashboard/summary');
    },

    /**
     * Lấy danh sách thiết bị kèm bộ lọc
     */
    async getDevices(params = {}) {
        const queryParams = new URLSearchParams();
        Object.entries(params).forEach(([key, value]) => {
            if (value !== undefined && value !== null && value !== '') {
                queryParams.append(key, value);
            }
        });
        const queryStr = queryParams.toString();
        const endpoint = queryStr ? `/devices?${queryStr}` : '/devices';
        return await this.request(endpoint);
    },

    /**
     * Lấy chi tiết 1 thiết bị theo ID (kèm chứng chỉ & lịch sử)
     */
    async getDevice(id) {
        return await this.request(`/devices/${id}`);
    },

    /**
     * Lấy danh sách khoa/phòng ban
     */
    async getFacilities() {
        return await this.request('/dashboard/facilities');
    },

    /**
     * Lấy danh sách loại thiết bị
     */
    async getCategories() {
        return await this.request('/dashboard/categories');
    },

    /**
     * Tạo đường dẫn xem PDF gốc
     */
    getPdfUrl(filename) {
        if (!filename) return null;
        return `${API_BASE_URL}/pdf/view?filename=${encodeURIComponent(filename)}`;
    },

    /**
     * Định dạng ngày tháng VN (dd/mm/yyyy)
     */
    formatDate(dateString) {
        if (!dateString) return '-';
        try {
            const parts = dateString.split('-');
            if (parts.length === 3) {
                return `${parts[2]}/${parts[1]}/${parts[0]}`;
            }
            const date = new Date(dateString);
            if (isNaN(date.getTime())) return dateString;
            const day = date.getDate().toString().padStart(2, '0');
            const month = (date.getMonth() + 1).toString().padStart(2, '0');
            const year = date.getFullYear();
            return `${day}/${month}/${year}`;
        } catch (e) {
            return dateString;
        }
    }
};

// Export cho browser & module
if (typeof module !== 'undefined' && module.exports) {
    module.exports = apiClient;
}