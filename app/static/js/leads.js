// Leads page JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    // Setup search functionality
    setupSearch('searchInput', '#leadsTable');
    
    // Auto-refresh leads every 60 seconds
    setInterval(function() {
        if (window.location.pathname === '/dashboard/leads') {
            location.reload();
        }
    }, 60000);
});

// Filter leads based on selected criteria
function filterLeads() {
    const stageFilter = document.getElementById('stageFilter').value;
    const typeFilter = document.getElementById('typeFilter').value;
    const scoreFilter = document.getElementById('scoreFilter').value;
    const searchInput = document.getElementById('searchInput').value.toLowerCase();
    
    const rows = document.querySelectorAll('#leadsTable tbody tr');
    let visibleCount = 0;
    
    rows.forEach(row => {
        const stage = row.getAttribute('data-stage');
        const type = row.getAttribute('data-type');
        const score = parseInt(row.getAttribute('data-score'));
        const text = row.textContent.toLowerCase();
        
        let show = true;
        
        // Stage filter
        if (stageFilter && stage !== stageFilter) {
            show = false;
        }
        
        // Type filter
        if (typeFilter && type !== typeFilter) {
            show = false;
        }
        
        // Score filter
        if (scoreFilter && score < parseInt(scoreFilter)) {
            show = false;
        }
        
        // Search filter
        if (searchInput && !text.includes(searchInput)) {
            show = false;
        }
        
        row.style.display = show ? '' : 'none';
        if (show) visibleCount++;
    });
    
    // Update lead count
    document.getElementById('leadCount').textContent = `${visibleCount} leads`;
}

// View lead profile
async function viewLeadProfile(psid) {
    try {
        const response = await fetch(`/api/users/${psid}`);
        const data = await response.json();
        
        if (data.user) {
            const content = document.getElementById('leadProfileContent');
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
                                <strong>Lead Stage:</strong><br>
                                ${data.user.lead_stage ? `<span class="badge bg-primary">${data.user.lead_stage}</span>` : 'Not set'}
                            </div>
                            <div class="col-sm-6">
                                <strong>Customer Type:</strong><br>
                                ${data.user.customer_type ? `<span class="badge bg-info">${data.user.customer_type}</span>` : 'Not set'}
                            </div>
                        </div>
                        <div class="row mb-3">
                            <div class="col-sm-6">
                                <strong>Customer Label:</strong><br>
                                ${data.user.customer_label ? `<span class="badge bg-success">${data.user.customer_label}</span>` : 'Not set'}
                            </div>
                            <div class="col-sm-6">
                                <strong>Lead Score:</strong><br>
                                <div class="progress" style="width: 100px;">
                                    <div class="progress-bar" role="progressbar" style="width: ${data.user.lead_score || 0}%">
                                        ${data.user.lead_score || 0}
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="row mb-3">
                            <div class="col-sm-6">
                                <strong>Joined:</strong><br>
                                <small>${new Date(data.user.created_at).toLocaleDateString()}</small>
                            </div>
                            <div class="col-sm-6">
                                <strong>Last Activity:</strong><br>
                                <small>${data.user.last_message_at ? new Date(data.user.last_message_at).toLocaleString() : 'Never'}</small>
                            </div>
                        </div>
                        ${data.activities && data.activities.length > 0 ? `
                            <div class="mb-3">
                                <strong>Recent Activities:</strong>
                                <div class="mt-2" style="max-height: 200px; overflow-y: auto;">
                                    ${data.activities.slice(0, 10).map(activity => `
                                        <div class="border-bottom pb-2 mb-2">
                                            <div class="d-flex justify-content-between">
                                                <span class="badge ${activity.automated ? 'bg-success' : 'bg-primary'}">${activity.activity_type}</span>
                                                <small class="text-muted">${new Date(activity.timestamp).toLocaleString()}</small>
                                            </div>
                                            <div class="mt-1">
                                                <strong>${activity.old_value || 'None'}</strong> → <strong>${activity.new_value}</strong>
                                                <br>
                                                <small class="text-muted">${activity.reason}</small>
                                            </div>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        ` : ''}
                    </div>
                </div>
            `;
            
            const modal = new bootstrap.Modal(document.getElementById('leadProfileModal'));
            modal.show();
        } else {
            showToast('Failed to load lead profile', 'error');
        }
    } catch (error) {
        console.error('Error loading lead profile:', error);
        showToast('Error loading lead profile', 'error');
    }
}

// Edit lead
async function editLead(psid) {
    try {
        const response = await fetch(`/api/users/${psid}`);
        const data = await response.json();
        
        if (data.user) {
            document.getElementById('editLeadId').value = psid;
            document.getElementById('editFirstName').value = data.user.first_name || '';
            document.getElementById('editLastName').value = data.user.last_name || '';
            document.getElementById('editLeadStage').value = data.user.lead_stage || 'Intake';
            document.getElementById('editCustomerType').value = data.user.customer_type || '';
            document.getElementById('editCustomerLabel').value = data.user.customer_label || '';
            
            const modal = new bootstrap.Modal(document.getElementById('editLeadModal'));
            modal.show();
        } else {
            showToast('Failed to load lead data', 'error');
        }
    } catch (error) {
        console.error('Error loading lead data:', error);
        showToast('Error loading lead data', 'error');
    }
}

// Save lead changes
async function saveLeadChanges() {
    const psid = document.getElementById('editLeadId').value;
    const firstName = document.getElementById('editFirstName').value;
    const lastName = document.getElementById('editLastName').value;
    const leadStage = document.getElementById('editLeadStage').value;
    const customerType = document.getElementById('editCustomerType').value;
    const customerLabel = document.getElementById('editCustomerLabel').value;
    
    try {
        const response = await fetch(`/api/users/${psid}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                first_name: firstName,
                last_name: lastName,
                lead_stage: leadStage,
                customer_type: customerType,
                customer_label: customerLabel
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('Lead updated successfully!', 'success');
            const modal = bootstrap.Modal.getInstance(document.getElementById('editLeadModal'));
            modal.hide();
            // Refresh the page to show updated data
            setTimeout(() => location.reload(), 1000);
        } else {
            showToast('Failed to update lead', 'error');
        }
    } catch (error) {
        console.error('Error updating lead:', error);
        showToast('Error updating lead', 'error');
    }
}

// Send message to lead
function sendMessageToLead(psid) {
    // Redirect to messages page with pre-filled recipient
    window.location.href = `/dashboard/messages?recipient=${psid}`;
}

// Refresh leads
function refreshLeads() {
    location.reload();
}

// Execute bulk action
async function executeBulkAction() {
    const action = document.getElementById('bulkAction').value;
    const targetLeads = document.querySelector('input[name="targetLeads"]:checked').value;
    
    try {
        showToast('Executing bulk action...', 'info');
        
        // Get leads based on target
        let leads = [];
        if (targetLeads === 'all') {
            const response = await fetch('/api/leads');
            const data = await response.json();
            leads = data.leads;
        } else {
            // Get filtered leads (simplified - in real implementation, you'd pass filter criteria)
            const response = await fetch('/api/leads');
            const data = await response.json();
            leads = data.leads;
        }
        
        if (leads.length === 0) {
            showToast('No leads found for bulk action', 'warning');
            return;
        }
        
        // Execute action based on type
        let successCount = 0;
        let errorCount = 0;
        
        for (const lead of leads) {
            try {
                if (action === 'send_message') {
                    const messageText = document.getElementById('bulkMessageText').value;
                    const response = await fetch('/api/messages/send', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            recipient_id: lead.psid,
                            message_text: messageText
                        })
                    });
                    
                    const result = await response.json();
                    if (result.success) {
                        successCount++;
                    } else {
                        errorCount++;
                    }
                } else if (action === 'update_stage') {
                    const newStage = document.getElementById('bulkStageValue').value;
                    const response = await fetch(`/api/users/${lead.psid}`, {
                        method: 'PUT',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            lead_stage: newStage
                        })
                    });
                    
                    const result = await response.json();
                    if (result.success) {
                        successCount++;
                    } else {
                        errorCount++;
                    }
                }
                
                // Add small delay between actions
                await new Promise(resolve => setTimeout(resolve, 100));
            } catch (error) {
                errorCount++;
            }
        }
        
        showToast(`Bulk action completed! Success: ${successCount}, Errors: ${errorCount}`, 'success');
        
        // Close modal and refresh
        const modal = bootstrap.Modal.getInstance(document.getElementById('bulkActionModal'));
        modal.hide();
        setTimeout(() => location.reload(), 1000);
        
    } catch (error) {
        console.error('Error executing bulk action:', error);
        showToast('Error executing bulk action', 'error');
    }
}

// Setup bulk action form based on selected action
document.addEventListener('DOMContentLoaded', function() {
    const bulkActionSelect = document.getElementById('bulkAction');
    const bulkActionValue = document.getElementById('bulkActionValue');
    
    bulkActionSelect.addEventListener('change', function() {
        const action = this.value;
        
        if (action === 'update_stage') {
            bulkActionValue.innerHTML = `
                <label for="bulkStageValue" class="form-label">New Stage</label>
                <select class="form-select" id="bulkStageValue">
                    <option value="Intake">Intake</option>
                    <option value="Qualified">Qualified</option>
                    <option value="In-Progress">In-Progress</option>
                    <option value="Converted">Converted</option>
                </select>
            `;
        } else if (action === 'update_type') {
            bulkActionValue.innerHTML = `
                <label for="bulkTypeValue" class="form-label">New Customer Type</label>
                <select class="form-select" id="bulkTypeValue">
                    <option value="عميل الندرة">عميل الندرة</option>
                    <option value="عميل العاطفة">عميل العاطفة</option>
                    <option value="عميل القيمة">عميل القيمة</option>
                    <option value="عميل الولاء">عميل الولاء</option>
                    <option value="عميل المنطق">عميل المنطق</option>
                    <option value="عميل التوفير">عميل التوفير</option>
                    <option value="عميل التردد">عميل التردد</option>
                </select>
            `;
        } else if (action === 'send_message') {
            bulkActionValue.innerHTML = `
                <label for="bulkMessageText" class="form-label">Message</label>
                <textarea class="form-control" id="bulkMessageText" rows="4" placeholder="Enter your message..." required></textarea>
            `;
        }
    });
});

// Include common functions
function setupSearch(inputId, tableId) {
    const searchInput = document.getElementById(inputId);
    if (searchInput) {
        searchInput.addEventListener('keyup', function() {
            filterLeads(); // Use the filter function instead of basic search
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
