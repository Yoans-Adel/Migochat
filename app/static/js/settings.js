// Unified Settings Manager - Migochat Dashboard
// Author: Copilot AI Assistant
// Version: 2.0 - Consolidated & Enhanced

// ========================================
// Configuration State Management
// ========================================
const configState = {
    ai: {},
    messenger: {},
    whatsapp: {},
    webhooks: {},
    isDirty: false
};

// ========================================
// Initialization
// ========================================
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Settings Manager Initialized');
    refreshSystemStatus();
    loadCurrentConfig();
    setupAutoSave();
});

// ========================================
// System Status Check
// ========================================
async function refreshSystemStatus() {
    showLoading('Checking system status...');
    
    try {
        // Check AI Status
        const aiStatus = await checkAIStatus();
        updateStatusIndicator('ai', aiStatus);
        
        // Check Messenger Status
        const messengerStatus = await checkMessengerStatus();
        updateStatusIndicator('messenger', messengerStatus);
        
        // Check WhatsApp Status
        const whatsappStatus = await checkWhatsAppStatus();
        updateStatusIndicator('whatsapp', whatsappStatus);
        
        hideLoading();
        showToast('System status refreshed', 'success');
    } catch (error) {
        console.error('Status check failed:', error);
        hideLoading();
        showToast('Failed to refresh status', 'error');
    }
}

async function checkAIStatus() {
    const apiKey = document.getElementById('gemini_api_key')?.value;
    
    if (!apiKey || apiKey.length < 20) {
        return { active: false, message: 'Not Configured' };
    }
    
    try {
        const response = await fetch('/api/test/ai', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ api_key: apiKey })
        });
        
        const result = await response.json();
        return {
            active: result.success,
            message: result.success ? 'Active' : 'Connection Failed'
        };
    } catch (error) {
        return { active: false, message: 'Error' };
    }
}

async function checkMessengerStatus() {
    const token = document.getElementById('fb_page_access_token')?.value;
    
    if (!token || token.includes('...')) {
        return { active: false, message: 'Not Configured' };
    }
    
    try {
        const response = await fetch('/api/test/messenger', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ access_token: token })
        });
        
        const result = await response.json();
        return {
            active: result.success,
            message: result.success ? 'Active' : 'Connection Failed'
        };
    } catch (error) {
        return { active: false, message: 'Error' };
    }
}

async function checkWhatsAppStatus() {
    const token = document.getElementById('whatsapp_access_token')?.value;
    
    if (!token || token.includes('...')) {
        return { active: false, message: 'Not Configured' };
    }
    
    try {
        const response = await fetch('/api/test/whatsapp', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ access_token: token })
        });
        
        const result = await response.json();
        return {
            active: result.success,
            message: result.success ? 'Active' : 'Connection Failed'
        };
    } catch (error) {
        return { active: false, message: 'Error' };
    }
}

function updateStatusIndicator(service, status) {
    const iconElement = document.getElementById(`${service}StatusIcon`);
    const badgeElement = document.getElementById(`${service}StatusBadge`);
    
    if (!badgeElement) return;
    
    if (status.active) {
        badgeElement.className = 'badge bg-success';
        badgeElement.innerHTML = '<i class="fas fa-check-circle me-1"></i> ' + status.message;
        if (iconElement) iconElement.style.color = '#28a745';
    } else {
        badgeElement.className = 'badge bg-danger';
        badgeElement.innerHTML = '<i class="fas fa-times-circle me-1"></i> ' + status.message;
        if (iconElement) iconElement.style.color = '#dc3545';
    }
}

// ========================================
// Configuration Management
// ========================================
function loadCurrentConfig() {
    console.log('📥 Loading current configuration...');
    
    // This would typically fetch from the server
    // For now, we use the values already in the form
    configState.isDirty = false;
}

async function saveAllSettings() {
    if (!confirm('Save all configuration changes? This will update the environment variables.')) {
        return;
    }
    
    showLoading('Saving configuration...');
    
    try {
        const config = {
            ai: {
                gemini_api_key: document.getElementById('gemini_api_key')?.value,
                gemini_model: document.getElementById('gemini_model')?.value
            },
            messenger: {
                fb_page_access_token: document.getElementById('fb_page_access_token')?.value,
                fb_app_id: document.getElementById('fb_app_id')?.value,
                fb_page_id: document.getElementById('fb_page_id')?.value,
                fb_verify_token: document.getElementById('fb_verify_token')?.value
            },
            whatsapp: {
                whatsapp_access_token: document.getElementById('whatsapp_access_token')?.value,
                whatsapp_phone_number_id: document.getElementById('whatsapp_phone_number_id')?.value,
                whatsapp_verify_token: document.getElementById('whatsapp_verify_token')?.value
            }
        };
        
        const response = await fetch('/api/settings/update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });
        
        const result = await response.json();
        
        hideLoading();
        
        if (result.success) {
            showToast('✅ Configuration saved successfully!', 'success');
            configState.isDirty = false;
            
            // Refresh status after save
            setTimeout(() => refreshSystemStatus(), 1000);
        } else {
            showToast('❌ Failed to save configuration: ' + result.error, 'error');
        }
    } catch (error) {
        console.error('Save failed:', error);
        hideLoading();
        showToast('❌ Error saving configuration', 'error');
    }
}

// ========================================
// Connection Testing
// ========================================
async function testAIConnection() {
    const apiKey = document.getElementById('gemini_api_key')?.value;
    
    if (!apiKey) {
        showToast('Please enter a Gemini API key first', 'warning');
        return;
    }
    
    showLoading('Testing AI connection...');
    
    try {
        const response = await fetch('/api/test/ai', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                api_key: apiKey,
                test_message: 'Hello, this is a test message.'
            })
        });
        
        const result = await response.json();
        hideLoading();
        
        if (result.success) {
            showToast('✅ AI Connection successful!', 'success');
            updateStatusIndicator('ai', { active: true, message: 'Active' });
        } else {
            showToast('❌ AI Connection failed: ' + result.error, 'error');
            updateStatusIndicator('ai', { active: false, message: 'Failed' });
        }
    } catch (error) {
        console.error('AI test failed:', error);
        hideLoading();
        showToast('❌ Error testing AI connection', 'error');
    }
}

async function testMessengerConnection() {
    const token = document.getElementById('fb_page_access_token')?.value;
    
    if (!token) {
        showToast('Please enter a Page Access Token first', 'warning');
        return;
    }
    
    showLoading('Testing Messenger connection...');
    
    try {
        const response = await fetch('/api/test/messenger', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ access_token: token })
        });
        
        const result = await response.json();
        hideLoading();
        
        if (result.success) {
            showToast('✅ Messenger Connection successful!', 'success');
            updateStatusIndicator('messenger', { active: true, message: 'Active' });
        } else {
            showToast('❌ Messenger Connection failed: ' + result.error, 'error');
            updateStatusIndicator('messenger', { active: false, message: 'Failed' });
        }
    } catch (error) {
        console.error('Messenger test failed:', error);
        hideLoading();
        showToast('❌ Error testing Messenger connection', 'error');
    }
}

async function testWhatsAppConnection() {
    const token = document.getElementById('whatsapp_access_token')?.value;
    const phoneNumberId = document.getElementById('whatsapp_phone_number_id')?.value;
    
    if (!token) {
        showToast('Please enter an Access Token first', 'warning');
        return;
    }
    
    showLoading('Testing WhatsApp connection...');
    
    try {
        const response = await fetch('/api/test/whatsapp', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                access_token: token,
                phone_number_id: phoneNumberId
            })
        });
        
        const result = await response.json();
        hideLoading();
        
        if (result.success) {
            showToast('✅ WhatsApp Connection successful!', 'success');
            updateStatusIndicator('whatsapp', { active: true, message: 'Active' });
        } else {
            showToast('❌ WhatsApp Connection failed: ' + result.error, 'error');
            updateStatusIndicator('whatsapp', { active: false, message: 'Failed' });
        }
    } catch (error) {
        console.error('WhatsApp test failed:', error);
        hideLoading();
        showToast('❌ Error testing WhatsApp connection', 'error');
    }
}

// ========================================
// Utility Functions
// ========================================
function togglePassword(fieldId) {
    const field = document.getElementById(fieldId);
    const button = field.nextElementSibling;
    const icon = button.querySelector('i');
    
    if (field.type === 'password') {
        field.type = 'text';
        icon.className = 'fas fa-eye-slash';
    } else {
        field.type = 'password';
        icon.className = 'fas fa-eye';
    }
}

function copyToClipboard(elementId) {
    const element = document.getElementById(elementId);
    // Check if it's an input element or regular element
    const text = element.value || element.textContent || element.innerText;
    
    navigator.clipboard.writeText(text).then(() => {
        showToast('✅ Copied to clipboard!', 'success');
        
        // Select the text briefly to show it was copied
        if (element.select) {
            element.select();
            setTimeout(() => {
                element.setSelectionRange(0, 0);
            }, 500);
        }
    }).catch(err => {
        console.error('Failed to copy:', err);
        showToast('❌ Failed to copy', 'error');
    });
}

function generateToken(fieldId) {
    const randomToken = 'migochat_' + Math.random().toString(36).substring(2, 15) + 
                       Math.random().toString(36).substring(2, 15);
    document.getElementById(fieldId).value = randomToken;
    configState.isDirty = true;
    showToast('✅ Token generated', 'success');
}

function setupAutoSave() {
    // Track form changes
    const forms = document.querySelectorAll('input, select, textarea');
    forms.forEach(field => {
        field.addEventListener('change', () => {
            configState.isDirty = true;
        });
    });
    
    // Warn before leaving if unsaved changes
    window.addEventListener('beforeunload', (e) => {
        if (configState.isDirty) {
            e.preventDefault();
            e.returnValue = '';
        }
    });
}

// ========================================
// System Tools
// ========================================
async function viewLogs() {
    window.open('/api/logs/view', '_blank');
}

async function downloadConfig() {
    window.location.href = '/api/settings/export';
}

async function clearCache() {
    if (!confirm('Clear application cache? This may temporarily slow down responses.')) {
        return;
    }
    
    showLoading('Clearing cache...');
    
    try {
        const response = await fetch('/api/cache/clear', { method: 'POST' });
        const result = await response.json();
        
        hideLoading();
        
        if (result.success) {
            showToast('✅ Cache cleared successfully', 'success');
        } else {
            showToast('❌ Failed to clear cache', 'error');
        }
    } catch (error) {
        console.error('Clear cache failed:', error);
        hideLoading();
        showToast('❌ Error clearing cache', 'error');
    }
}

// ========================================
// UI Helpers
// ========================================
function showToast(message, type = 'info') {
    const toastElement = document.getElementById('notificationToast');
    const toastBody = document.getElementById('toastMessage');
    const toast = new bootstrap.Toast(toastElement);
    
    // Set message
    toastBody.textContent = message;
    
    // Set style based on type
    toastElement.className = 'toast';
    if (type === 'success') {
        toastElement.classList.add('bg-success', 'text-white');
    } else if (type === 'error') {
        toastElement.classList.add('bg-danger', 'text-white');
    } else if (type === 'warning') {
        toastElement.classList.add('bg-warning');
    }
    
    // Show toast
    toast.show();
}

function showLoading(message = 'Loading...') {
    // Show loading overlay
    const overlay = document.createElement('div');
    overlay.id = 'loadingOverlay';
    overlay.className = 'position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center';
    overlay.style.cssText = 'background: rgba(0,0,0,0.5); z-index: 9999;';
    overlay.innerHTML = `
        <div class="text-center text-white">
            <div class="spinner-border mb-3" role="status"></div>
            <div>${message}</div>
        </div>
    `;
    document.body.appendChild(overlay);
}

function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.remove();
    }
}

// ========================================
// Export for global access
// ========================================
window.settingsManager = {
    refreshSystemStatus,
    saveAllSettings,
    testAIConnection,
    testMessengerConnection,
    testWhatsAppConnection,
    togglePassword,
    copyToClipboard,
    generateToken,
    viewLogs,
    downloadConfig,
    clearCache
};
