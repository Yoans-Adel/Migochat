// Messages page JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    // Setup search functionality
    setupSearch('searchInput', '.table');
    
    // Auto-refresh conversations every 60 seconds
    setInterval(function() {
        if (window.location.pathname === '/dashboard/messages') {
            location.reload();
        }
    }, 60000);
});

// Send message function
async function sendMessage() {
    const recipientId = document.getElementById('recipientId').value;
    const messageText = document.getElementById('messageText').value;
    
    if (!recipientId || !messageText) {
        showToast('Please fill in all fields', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/messages/send', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                recipient_id: recipientId,
                message_text: messageText
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('Message sent successfully!', 'success');
            // Close modal and reset form
            const modal = bootstrap.Modal.getInstance(document.getElementById('sendMessageModal'));
            modal.hide();
            document.getElementById('sendMessageForm').reset();
        } else {
            showToast('Failed to send message', 'error');
        }
    } catch (error) {
        console.error('Error sending message:', error);
        showToast('Error sending message', 'error');
    }
}

// Send message to specific user
function sendMessageToUser(psid) {
    document.getElementById('recipientId').value = psid;
    const modal = new bootstrap.Modal(document.getElementById('sendMessageModal'));
    modal.show();
}

// View conversation
async function viewConversation(psid) {
    try {
        const response = await fetch(`/api/users/${psid}`);
        const data = await response.json();
        
        if (data.user && data.messages) {
            const content = document.getElementById('conversationContent');
            content.innerHTML = `
                <div class="mb-3">
                    <div class="d-flex align-items-center">
                        ${data.user.profile_pic ? 
                            `<img src="${data.user.profile_pic}" class="rounded-circle me-2" width="40" height="40" alt="Profile">` :
                            `<div class="bg-secondary rounded-circle me-2 d-flex align-items-center justify-content-center" style="width: 40px; height: 40px;">
                                <i class="fas fa-user text-white"></i>
                            </div>`
                        }
                        <div>
                            <h6 class="mb-0">${data.user.first_name || 'Unknown'} ${data.user.last_name || ''}</h6>
                            <small class="text-muted">${data.user.psid}</small>
                        </div>
                    </div>
                </div>
                <div class="conversation-messages" style="max-height: 400px; overflow-y: auto;">
                    ${data.messages.map(msg => `
                        <div class="message-item mb-3 ${msg.direction === 'inbound' ? 'text-start' : 'text-end'}">
                            <div class="message-bubble ${msg.direction === 'inbound' ? 'bg-light' : 'bg-primary text-white'} p-2 rounded" style="max-width: 70%; display: inline-block;">
                                <div class="message-text">${msg.message_text}</div>
                                <div class="message-meta mt-1">
                                    <small class="${msg.direction === 'inbound' ? 'text-muted' : 'text-white-50'}">
                                        ${new Date(msg.timestamp).toLocaleString()}
                                        ${msg.direction === 'outbound' ? ` • ${msg.status}` : ''}
                                    </small>
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
            
            const modal = new bootstrap.Modal(document.getElementById('viewConversationModal'));
            modal.show();
        } else {
            showToast('Failed to load conversation', 'error');
        }
    } catch (error) {
        console.error('Error loading conversation:', error);
        showToast('Error loading conversation', 'error');
    }
}

// Include dashboard functions
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
