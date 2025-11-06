// Settings page JavaScript functionality
const configState = {
    ai: {},
    messenger: {},
    whatsapp: {},
    isDirty: false
};

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Settings Manager Initialized');
    refreshSystemStatus();
    loadCurrentConfig();
    setupAutoSave();
});

async function refreshSystemStatus() {
    showLoading('Checking system status...');
    
    try {
        const aiStatus = await checkAIStatus();
        updateStatusIndicator('ai', aiStatus);
        
        const messengerStatus = await checkMessengerStatus();
        updateStatusIndicator('messenger', messengerStatus);
        
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

// Check WhatsApp service status
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
        
        // Update legacy status elements
        const statusElements = [
            document.getElementById('whatsappStatusBadge'),
            document.getElementById('whatsappSystemStatus')
        ];
        
        statusElements.forEach(element => {
            if (element) {
                if (result.success) {
                    element.className = 'badge bg-success';
                    element.innerHTML = '<i class="fas fa-check-circle me-1"></i> Active';
                } else {
                    element.className = 'badge bg-danger';
                    element.innerHTML = '<i class="fas fa-times-circle me-1"></i> Inactive';
                }
            }
        });
        
        return {
            active: result.success,
            message: result.success ? 'Active' : 'Connection Failed'
        };
    } catch (error) {
        console.error('Error checking WhatsApp status:', error);
        const statusElements = [
            document.getElementById('whatsappStatusBadge'),
            document.getElementById('whatsappSystemStatus')
        ];
        
        statusElements.forEach(element => {
            if (element) {
                element.className = 'badge bg-warning';
                element.textContent = 'Unknown';
            }
        });
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

function loadCurrentConfig() {
    console.log('📥 Loading current configuration...');
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

// Toggle password visibility
function togglePasswordField(inputId) {
    const input = document.getElementById(inputId);
    if (!input) return;
    
    const button = input.parentElement.querySelector('button');
    const icon = button ? button.querySelector('i') : null;
    
    if (input.type === 'password') {
        input.type = 'text';
        if (icon) {
            icon.classList.remove('fa-eye');
            icon.classList.add('fa-eye-slash');
        }
    } else {
        input.type = 'password';
        if (icon) {
            icon.classList.remove('fa-eye-slash');
            icon.classList.add('fa-eye');
        }
    }
}

function togglePassword(fieldId) {
    togglePasswordField(fieldId);
}

// Copy to clipboard function
function copyToClipboard(elementIdOrText) {
    const element = document.getElementById(elementIdOrText);
    const text = element ? element.textContent : elementIdOrText;
    
    navigator.clipboard.writeText(text).then(() => {
        showToast('✅ Copied to clipboard!', 'success');
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
    const forms = document.querySelectorAll('input, select, textarea');
    forms.forEach(field => {
        field.addEventListener('change', () => {
            configState.isDirty = true;
        });
    });
    
    window.addEventListener('beforeunload', (e) => {
        if (configState.isDirty) {
            e.preventDefault();
            e.returnValue = '';
        }
    });
}

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

function showLoading(message = 'Loading...') {
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

// Refresh logs
function refreshLogs() {
    showToast('Refreshing logs...', 'info');
    viewLogs();
}

// Download logs
function downloadLogs() {
    showToast('Preparing logs for download...', 'info');
    downloadConfig();
}

// Show toast notification
function showToast(message, type = 'info') {
    const toastElement = document.getElementById('notificationToast');
    
    if (!toastElement) {
        // Fallback to creating toast if element doesn't exist
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'info'} border-0`;
        toast.setAttribute('role', 'alert');
        toast.style.cssText = 'position: fixed; bottom: 20px; right: 20px; z-index: 9999;';
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        document.body.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        toast.addEventListener('hidden.bs.toast', function() {
            document.body.removeChild(toast);
        });
        return;
    }
    
    const toastBody = document.getElementById('toastMessage');
    const toast = new bootstrap.Toast(toastElement);
    
    toastBody.textContent = message;
    
    toastElement.className = 'toast';
    if (type === 'success') {
        toastElement.classList.add('bg-success', 'text-white');
    } else if (type === 'error') {
        toastElement.classList.add('bg-danger', 'text-white');
    } else if (type === 'warning') {
        toastElement.classList.add('bg-warning');
    }
    
    toast.show();
}