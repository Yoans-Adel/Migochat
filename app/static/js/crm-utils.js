// Enhanced CRM Utilities - Advanced Features

// ============================================================
// Performance Monitoring
// ============================================================

const performanceMonitor = {
    timers: {},
    
    start(name) {
        this.timers[name] = performance.now();
    },
    
    end(name) {
        if (this.timers[name]) {
            const duration = performance.now() - this.timers[name];
            console.log(`⏱️ ${name}: ${duration.toFixed(2)}ms`);
            delete this.timers[name];
            return duration;
        }
    }
};

// ============================================================
// Data Validation
// ============================================================

function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePhone(phone) {
    // Egyptian phone numbers: 01x-xxxx-xxxx
    const re = /^(01)[0-9]{9}$/;
    return re.test(phone.replace(/[\s-]/g, ''));
}

function sanitizeInput(input) {
    if (!input) return '';
    return input
        .replace(/[<>]/g, '') // Remove potential HTML
        .trim();
}

// ============================================================
// Local Storage Cache
// ============================================================

const cache = {
    set(key, value, ttl = 300000) { // 5 minutes default
        const item = {
            value: value,
            expiry: Date.now() + ttl
        };
        localStorage.setItem(key, JSON.stringify(item));
    },
    
    get(key) {
        const itemStr = localStorage.getItem(key);
        if (!itemStr) return null;
        
        const item = JSON.parse(itemStr);
        if (Date.now() > item.expiry) {
            localStorage.removeItem(key);
            return null;
        }
        
        return item.value;
    },
    
    clear(key) {
        if (key) {
            localStorage.removeItem(key);
        } else {
            localStorage.clear();
        }
    }
};

// ============================================================
// Enhanced Error Handling
// ============================================================

function handleApiError(error, context = 'API Call') {
    console.error(`❌ ${context}:`, error);
    
    let message = 'An error occurred';
    
    if (error.response) {
        // Server responded with error
        message = error.response.data?.detail || error.response.statusText;
    } else if (error.request) {
        // Request made but no response
        message = 'No response from server. Please check your connection.';
    } else {
        // Something else happened
        message = error.message;
    }
    
    showToast(message, 'error');
    return message;
}

// ============================================================
// Retry Mechanism
// ============================================================

async function fetchWithRetry(url, options = {}, maxRetries = 3) {
    for (let i = 0; i < maxRetries; i++) {
        try {
            const response = await fetch(url, options);
            if (response.ok) return response;
            
            // Don't retry 4xx errors (client errors)
            if (response.status >= 400 && response.status < 500) {
                throw new Error(`Client error: ${response.status}`);
            }
            
        } catch (error) {
            if (i === maxRetries - 1) throw error;
            
            // Exponential backoff
            const delay = Math.pow(2, i) * 1000;
            console.log(`⏳ Retry ${i + 1}/${maxRetries} after ${delay}ms...`);
            await new Promise(resolve => setTimeout(resolve, delay));
        }
    }
}

// ============================================================
// Keyboard Shortcuts
// ============================================================

function initKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K: Focus search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.getElementById('leadSearchInput') || 
                              document.getElementById('userSearchInput');
            if (searchInput) searchInput.focus();
        }
        
        // Ctrl/Cmd + R: Refresh current tab
        if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
            e.preventDefault();
            refreshAll();
        }
        
        // Escape: Clear search
        if (e.key === 'Escape') {
            const searchInputs = document.querySelectorAll('[id$="SearchInput"]');
            searchInputs.forEach(input => {
                if (input.value) {
                    input.value = '';
                    handleSearch('');
                }
            });
        }
    });
}

// ============================================================
// Analytics Tracking
// ============================================================

const analytics = {
    track(event, data = {}) {
        console.log('📊 Analytics:', event, data);
        
        // Store locally for session stats
        const events = JSON.parse(sessionStorage.getItem('crm_events') || '[]');
        events.push({
            event,
            data,
            timestamp: Date.now()
        });
        sessionStorage.setItem('crm_events', JSON.stringify(events));
    },
    
    getSessionStats() {
        const events = JSON.parse(sessionStorage.getItem('crm_events') || '[]');
        return {
            totalEvents: events.length,
            events: events
        };
    }
};

// ============================================================
// Bulk Operations Queue
// ============================================================

class BulkOperationQueue {
    constructor() {
        this.queue = [];
        this.processing = false;
        this.batchSize = 10;
    }
    
    add(operation) {
        this.queue.push(operation);
        if (!this.processing) {
            this.process();
        }
    }
    
    async process() {
        if (this.queue.length === 0) {
            this.processing = false;
            return;
        }
        
        this.processing = true;
        const batch = this.queue.splice(0, this.batchSize);
        
        for (const operation of batch) {
            try {
                await operation();
            } catch (error) {
                console.error('Bulk operation failed:', error);
            }
        }
        
        // Process next batch
        setTimeout(() => this.process(), 100);
    }
}

const bulkQueue = new BulkOperationQueue();

// ============================================================
// Advanced Filters
// ============================================================

function applyAdvancedFilters(items, filters) {
    return items.filter(item => {
        // Date range filter
        if (filters.dateFrom && item.created_at) {
            if (new Date(item.created_at) < new Date(filters.dateFrom)) {
                return false;
            }
        }
        
        if (filters.dateTo && item.created_at) {
            if (new Date(item.created_at) > new Date(filters.dateTo)) {
                return false;
            }
        }
        
        // Score range filter
        if (filters.minScore && item.lead_score < filters.minScore) {
            return false;
        }
        
        if (filters.maxScore && item.lead_score > filters.maxScore) {
            return false;
        }
        
        // Custom field filters
        if (filters.customField && filters.customValue) {
            if (item[filters.customField] !== filters.customValue) {
                return false;
            }
        }
        
        return true;
    });
}

// ============================================================
// Data Export Utilities
// ============================================================

function exportToExcel(data, filename) {
    // Convert to CSV format (Excel compatible)
    const csv = convertToCSV(data);
    const BOM = '\uFEFF'; // UTF-8 BOM for Excel
    const blob = new Blob([BOM + csv], { type: 'text/csv;charset=utf-8;' });
    downloadBlob(blob, filename + '.csv');
}

function exportToPDF(data, filename) {
    // Note: Requires jsPDF library
    showToast('PDF export coming soon!', 'info');
}

function downloadBlob(blob, filename) {
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

// ============================================================
// Real-time Updates (WebSocket placeholder)
// ============================================================

class RealtimeUpdates {
    constructor() {
        this.enabled = false;
        this.interval = null;
    }
    
    start(refreshInterval = 30000) {
        if (this.interval) return;
        
        this.enabled = true;
        this.interval = setInterval(() => {
            if (document.visibilityState === 'visible') {
                console.log('🔄 Auto-refresh...');
                refreshAll();
            }
        }, refreshInterval);
    }
    
    stop() {
        if (this.interval) {
            clearInterval(this.interval);
            this.interval = null;
            this.enabled = false;
        }
    }
}

const realtimeUpdates = new RealtimeUpdates();

// ============================================================
// Initialize Enhanced Features
// ============================================================

document.addEventListener('DOMContentLoaded', function() {
    // Initialize keyboard shortcuts
    initKeyboardShortcuts();
    
    // Start realtime updates
    realtimeUpdates.start();
    
    // Log analytics
    analytics.track('CRM_LOADED', {
        userAgent: navigator.userAgent,
        screenSize: `${window.innerWidth}x${window.innerHeight}`
    });
    
    console.log('✨ Enhanced CRM utilities loaded');
});

// Export for global use
window.crmUtils = {
    performanceMonitor,
    cache,
    analytics,
    bulkQueue,
    validateEmail,
    validatePhone,
    sanitizeInput,
    handleApiError,
    fetchWithRetry,
    exportToExcel,
    exportToPDF,
    realtimeUpdates
};
