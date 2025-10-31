// Users page JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    // Setup search functionality
    setupSearch('userSearchInput', '.table');
    
    // Auto-refresh users every 60 seconds
    setInterval(function() {
        if (window.location.pathname === '/dashboard/users') {
            location.reload();
        }
    }, 60000);
});

// View user profile
async function viewUserProfile(psid) {
    try {
        const response = await fetch(`/api/users/${psid}`);
        const data = await response.json();
        
        if (data.user && data.messages) {
            const content = document.getElementById('userProfileContent');
            content.innerHTML = `
                <div class="row">
                    <div class="col-md-4">
                        <div class="text-center">
                            ${data.user.profile_pic ? 
                                `<img src="${data.user.profile_pic}" class="rounded-circle mb-3" width="100" height="100" alt="Profile">` :
                                `<div class="bg-secondary rounded-circle mb-3 mx-auto d-flex align-items-center justify-content-center" style="width: 100px; height: 100px;">
                                    <i class="fas fa-user fa-3x text-white"></i>
                                </div>`
                            }
                            <h5>${data.user.first_name || 'Unknown'} ${data.user.last_name || ''}</h5>
                            <p class="text-muted">${data.user.psid}</p>
                        </div>
                    </div>
                    <div class="col-md-8">
                        <div class="row mb-3">
                            <div class="col-sm-6">
                                <strong>Location:</strong><br>
                                ${data.user.governorate ? `<span class="badge bg-info">${data.user.governorate}</span>` : 'Not set'}
                            </div>
                            <div class="col-sm-6">
                                <strong>Status:</strong><br>
                                <span class="badge ${data.user.is_active ? 'bg-success' : 'bg-secondary'}">
                                    ${data.user.is_active ? 'Active' : 'Inactive'}
                                </span>
                            </div>
                        </div>
                        <div class="row mb-3">
                            <div class="col-sm-6">
                                <strong>Joined:</strong><br>
                                <small>${new Date(data.user.created_at).toLocaleDateString()}</small>
                            </div>
                            <div class="col-sm-6">
                                <strong>Last Message:</strong><br>
                                <small>${data.user.last_message_at ? new Date(data.user.last_message_at).toLocaleString() : 'Never'}</small>
                            </div>
                        </div>
                        <div class="mb-3">
                            <strong>Recent Messages (${data.messages.length}):</strong>
                            <div class="mt-2" style="max-height: 200px; overflow-y: auto;">
                                ${data.messages.slice(0, 10).map(msg => `
                                    <div class="border-bottom pb-2 mb-2">
                                        <div class="d-flex justify-content-between">
                                            <span class="badge ${msg.direction === 'inbound' ? 'bg-primary' : 'bg-success'}">${msg.direction}</span>
                                            <small class="text-muted">${new Date(msg.timestamp).toLocaleString()}</small>
                                        </div>
                                        <div class="mt-1">${msg.message_text}</div>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            const modal = new bootstrap.Modal(document.getElementById('userProfileModal'));
            modal.show();
        } else {
            showToast('Failed to load user profile', 'error');
        }
    } catch (error) {
        console.error('Error loading user profile:', error);
        showToast('Error loading user profile', 'error');
    }
}

// Edit user
async function editUser(psid) {
    try {
        const response = await fetch(`/api/users/${psid}`);
        const data = await response.json();
        
        if (data.user) {
            document.getElementById('editUserId').value = psid;
            document.getElementById('editFirstName').value = data.user.first_name || '';
            document.getElementById('editLastName').value = data.user.last_name || '';
            document.getElementById('editGovernorate').value = data.user.governorate || '';
            
            const modal = new bootstrap.Modal(document.getElementById('editUserModal'));
            modal.show();
        } else {
            showToast('Failed to load user data', 'error');
        }
    } catch (error) {
        console.error('Error loading user data:', error);
        showToast('Error loading user data', 'error');
    }
}

// Save user changes
async function saveUserChanges() {
    const psid = document.getElementById('editUserId').value;
    const firstName = document.getElementById('editFirstName').value;
    const lastName = document.getElementById('editLastName').value;
    const governorate = document.getElementById('editGovernorate').value;
    
    try {
        const response = await fetch(`/api/users/${psid}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                first_name: firstName,
                last_name: lastName,
                governorate: governorate
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('User updated successfully!', 'success');
            const modal = bootstrap.Modal.getInstance(document.getElementById('editUserModal'));
            modal.hide();
            // Refresh the page to show updated data
            setTimeout(() => location.reload(), 1000);
        } else {
            showToast('Failed to update user', 'error');
        }
    } catch (error) {
        console.error('Error updating user:', error);
        showToast('Error updating user', 'error');
    }
}

// Send message to user
function sendMessageToUser(psid) {
    // Redirect to messages page with pre-filled recipient
    window.location.href = `/dashboard/messages?recipient=${psid}`;
}

// Send bulk message
async function sendBulkMessage() {
    const messageText = document.getElementById('bulkMessageText').value;
    const targetUsers = document.querySelector('input[name="targetUsers"]:checked').value;
    
    if (!messageText) {
        showToast('Please enter a message', 'error');
        return;
    }
    
    try {
        // Get users list
        const usersResponse = await fetch('/api/users');
        const usersData = await usersResponse.json();
        
        let targetUserList = usersData.users;
        
        if (targetUsers === 'active') {
            // Filter active users (last 7 days)
            const weekAgo = new Date();
            weekAgo.setDate(weekAgo.getDate() - 7);
            targetUserList = usersData.users.filter(user => 
                user.last_message_at && new Date(user.last_message_at) >= weekAgo
            );
        }
        
        if (targetUserList.length === 0) {
            showToast('No users found for bulk message', 'warning');
            return;
        }
        
        // Send messages to all target users
        let successCount = 0;
        let errorCount = 0;
        
        for (const user of targetUserList) {
            try {
                const response = await fetch('/api/messages/send', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        recipient_id: user.psid,
                        message_text: messageText
                    })
                });
                
                const result = await response.json();
                if (result.success) {
                    successCount++;
                } else {
                    errorCount++;
                }
            } catch (error) {
                errorCount++;
            }
            
            // Add small delay between messages to avoid rate limiting
            await new Promise(resolve => setTimeout(resolve, 100));
        }
        
        showToast(`Bulk message sent! Success: ${successCount}, Errors: ${errorCount}`, 'success');
        
        // Close modal and reset form
        const modal = bootstrap.Modal.getInstance(document.getElementById('bulkMessageModal'));
        modal.hide();
        document.getElementById('bulkMessageForm').reset();
        
    } catch (error) {
        console.error('Error sending bulk message:', error);
        showToast('Error sending bulk message', 'error');
    }
}

// Refresh users
function refreshUsers() {
    location.reload();
}

// Include common functions
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
