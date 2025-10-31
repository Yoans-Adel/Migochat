// Dashboard JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    // Auto-refresh dashboard every 30 seconds
    setInterval(function() {
        if (window.location.pathname === '/dashboard' || window.location.pathname === '/') {
            location.reload();
        }
    }, 30000);
    
    // Check WhatsApp status
    checkWhatsAppStatus();
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Check WhatsApp service status
async function checkWhatsAppStatus() {
    try {
        const response = await fetch('/api/whatsapp/status');
        const data = await response.json();
        
        const statusElement = document.getElementById('whatsappStatus');
        if (statusElement) {
            if (data.whatsapp_available) {
                statusElement.className = 'badge bg-success';
                statusElement.textContent = 'Active';
            } else {
                statusElement.className = 'badge bg-danger';
                statusElement.textContent = 'Inactive';
            }
        }
    } catch (error) {
        console.error('Error checking WhatsApp status:', error);
        const statusElement = document.getElementById('whatsappStatus');
        if (statusElement) {
            statusElement.className = 'badge bg-warning';
            statusElement.textContent = 'Unknown';
        }
    }
}

// Copy to clipboard function
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        // Show success message
        showToast('Copied to clipboard!', 'success');
    }).catch(function(err) {
        console.error('Could not copy text: ', err);
        showToast('Failed to copy to clipboard', 'error');
    });
}

// Show toast notification
function showToast(message, type = 'info') {
    // Create toast element
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
    
    // Add to page
    document.body.appendChild(toast);
    
    // Show toast
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove from DOM after hiding
    toast.addEventListener('hidden.bs.toast', function() {
        document.body.removeChild(toast);
    });
}

// Search functionality
function setupSearch(inputId, tableId) {
    const searchInput = document.getElementById(inputId);
    if (searchInput) {
        searchInput.addEventListener('keyup', function() {
            const filter = this.value.toLowerCase();
            const table = document.querySelector(tableId);
            const rows = table.getElementsByTagName('tr');
            
            for (let i = 1; i < rows.length; i++) {
                const row = rows[i];
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(filter) ? '' : 'none';
            }
        });
    }
}

// Initialize search on dashboard
document.addEventListener('DOMContentLoaded', function() {
    setupSearch('searchInput', '.table');
});
