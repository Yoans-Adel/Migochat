// Settings page JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    // Auto-refresh settings every 60 seconds
    setInterval(function() {
        if (window.location.pathname === '/dashboard/settings') {
            location.reload();
        }
    }, 60000);
    
    // Check WhatsApp status
    checkWhatsAppStatus();
});

// Check WhatsApp service status
async function checkWhatsAppStatus() {
    try {
        const response = await fetch('/api/whatsapp/status');
        const data = await response.json();
        
        const statusElements = [
            document.getElementById('whatsappStatusBadge'),
            document.getElementById('whatsappSystemStatus')
        ];
        
        statusElements.forEach(element => {
            if (element) {
                if (data.whatsapp_available) {
                    element.className = 'badge bg-success';
                    element.textContent = 'Active';
                } else {
                    element.className = 'badge bg-danger';
                    element.textContent = 'Inactive';
                }
            }
        });
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
    }
}

// Toggle password visibility
function togglePasswordField(inputId) {
    const input = document.getElementById(inputId);
    if (!input) {
        console.error(`Input with ID ${inputId} not found`);
        return;
    }
    
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

// Copy to clipboard function
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showToast('Copied to clipboard!', 'success');
    }).catch(function(err) {
        console.error('Could not copy text: ', err);
        showToast('Failed to copy to clipboard', 'error');
    });
}

// Refresh logs
function refreshLogs() {
    showToast('Refreshing logs...', 'info');
    // In a real implementation, this would fetch log data from the server
    setTimeout(() => {
        showToast('Logs refreshed!', 'success');
    }, 1000);
}

// Download logs
function downloadLogs() {
    showToast('Preparing logs for download...', 'info');
    // In a real implementation, this would generate and download log files
    setTimeout(() => {
        showToast('Log download started!', 'success');
    }, 1000);
}

// Test webhook connection
async function testWebhook() {
    try {
        showToast('Testing webhook connection...', 'info');
        
        const response = await fetch('/webhook', {
            method: 'GET',
            headers: {
                'hub.mode': 'subscribe',
                'hub.verify_token': 'your_verify_token_here',
                'hub.challenge': 'test_challenge'
            }
        });
        
        if (response.ok) {
            showToast('Webhook test successful!', 'success');
        } else {
            showToast('Webhook test failed', 'error');
        }
    } catch (error) {
        console.error('Error testing webhook:', error);
        showToast('Error testing webhook', 'error');
    }
}

// Show toast notification
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    document.body.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', function() {
        document.body.removeChild(toast);
    });
}

// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});
