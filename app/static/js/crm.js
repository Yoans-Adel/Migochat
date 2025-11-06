// CRM System - Unified Management for Leads, Users, and Bulk Operations
// State Management
const crmState = {
    leads: [],
    users: [],
    conversations: [],
    selectedItems: {
        leads: new Set(),
        users: new Set()
    },
    currentConversation: null,
    filters: {
        stage: '',
        customerType: '',
        search: ''
    }
};

// Initialize CRM
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 CRM System Initialized');
    
    // Load initial data
    loadStats();
    loadLeads();
    
    // Set up auto-refresh
    setInterval(() => {
        refreshAll();
    }, 30000); // Every 30 seconds
    
    // Set up tab event listeners
    document.querySelectorAll('button[data-bs-toggle="tab"]').forEach(tab => {
        tab.addEventListener('shown.bs.tab', function(e) {
            const target = e.target.getAttribute('data-bs-target');
            if (target === '#users') {
                loadUsers();
            } else if (target === '#conversations') {
                loadConversations();
            } else if (target === '#bulk') {
                updateBulkStats();
            }
        });
    });
    
    // Character counter for bulk messages
    const bulkMessage = document.getElementById('bulkMessage');
    if (bulkMessage) {
        bulkMessage.addEventListener('input', function() {
            document.getElementById('charCount').textContent = this.value.length;
        });
    }
    
    // Schedule checkbox
    const scheduleCheckbox = document.getElementById('scheduleMessage');
    if (scheduleCheckbox) {
        scheduleCheckbox.addEventListener('change', function() {
            document.getElementById('scheduleTime').classList.toggle('d-none', !this.checked);
        });
    }
});

// ============================================================
// Stats Functions
// ============================================================

async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        if (!response.ok) throw new Error('Failed to load stats');
        
        const data = await response.json();
        
        // Update stat cards
        document.getElementById('totalLeads').textContent = data.total_users || 0;
        document.getElementById('activeConversations').textContent = data.active_conversations || 0;
        document.getElementById('hotLeads').textContent = data.hot_leads || 0;
        document.getElementById('responseRate').textContent = `${data.response_rate || 0}%`;
        
        // Update change indicators
        updateChangeIndicator('leadsChange', data.leads_change || 0);
        updateChangeIndicator('conversationsChange', data.conversations_change || 0);
        updateChangeIndicator('hotLeadsChange', data.hot_leads_change || 0);
        updateChangeIndicator('responseRateChange', data.response_rate_change || 0);
        
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

function updateChangeIndicator(elementId, change) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const icon = change > 0 ? 'fa-arrow-up' : change < 0 ? 'fa-arrow-down' : 'fa-minus';
    const color = change > 0 ? 'text-success' : change < 0 ? 'text-danger' : 'text-muted';
    
    element.className = color;
    element.innerHTML = `<i class="fas ${icon} me-1"></i>${Math.abs(change)}% this week`;
}

// ============================================================
// Leads Functions
// ============================================================

async function loadLeads() {
    try {
        showLoading('leadsTableBody');
        
        const stage = document.getElementById('leadStageFilter')?.value || '';
        const customerType = document.getElementById('customerTypeFilter')?.value || '';
        
        const params = new URLSearchParams();
        if (stage) params.append('stage', stage);
        if (customerType) params.append('customer_type', customerType);
        
        const response = await fetch(`/api/leads?${params.toString()}`);
        if (!response.ok) throw new Error('Failed to load leads');
        
        const data = await response.json();
        crmState.leads = data.leads || [];
        
        // Update counts
        document.getElementById('leadsCount').textContent = crmState.leads.length;
        
        // Render leads table
        renderLeadsTable();
        
    } catch (error) {
        console.error('Error loading leads:', error);
        showError('leadsTableBody', 'Failed to load leads');
    }
}

function renderLeadsTable() {
    const tbody = document.getElementById('leadsTableBody');
    if (!tbody) return;
    
    if (crmState.leads.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center text-muted py-4">
                    <i class="fas fa-users fa-3x mb-3 d-block"></i>
                    No leads found
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = crmState.leads.map(lead => {
        const isSelected = crmState.selectedItems.leads.has(lead.psid);
        const stageColor = getStageColor(lead.lead_stage);
        const typeColor = getTypeColor(lead.customer_type);
        
        return `
            <tr class="${isSelected ? 'table-active' : ''}">
                <td>
                    <input type="checkbox" 
                           ${isSelected ? 'checked' : ''} 
                           onchange="toggleSelection('leads', '${lead.psid}', this.checked)">
                </td>
                <td>
                    <div class="d-flex align-items-center">
                        <img src="${lead.profile_pic || '/static/img/default-avatar.png'}" 
                             class="rounded-circle me-2" 
                             width="40" height="40"
                             onerror="this.src='/static/img/default-avatar.png'">
                        <div>
                            <strong>${lead.first_name || ''} ${lead.last_name || ''}</strong>
                            <br>
                            <small class="text-muted">${lead.psid}</small>
                        </div>
                    </div>
                </td>
                <td>
                    <div class="d-flex align-items-center">
                        <div class="progress me-2" style="width: 60px; height: 8px;">
                            <div class="progress-bar bg-${getScoreColor(lead.lead_score)}" 
                                 style="width: ${lead.lead_score || 0}%"></div>
                        </div>
                        <span class="badge bg-${getScoreColor(lead.lead_score)}">${lead.lead_score || 0}</span>
                    </div>
                </td>
                <td><span class="badge bg-${stageColor} lead-badge">${lead.lead_stage || 'NEW'}</span></td>
                <td><span class="badge bg-${typeColor} lead-badge">${lead.customer_type || 'POTENTIAL'}</span></td>
                <td>
                    <small class="text-muted">
                        ${lead.last_message_at ? formatDate(lead.last_message_at) : 'Never'}
                    </small>
                </td>
                <td>
                    <button class="btn btn-sm btn-primary action-btn me-1" 
                            onclick="viewUserDetail('${lead.psid}')"
                            title="View Details">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-success action-btn me-1" 
                            onclick="sendQuickMessage('${lead.psid}')"
                            title="Send Message">
                        <i class="fas fa-paper-plane"></i>
                    </button>
                    <button class="btn btn-sm btn-info action-btn" 
                            onclick="changeLeadStage('${lead.psid}')"
                            title="Change Stage">
                        <i class="fas fa-exchange-alt"></i>
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

// ============================================================
// Users Functions
// ============================================================

async function loadUsers() {
    try {
        showLoading('usersTableBody');
        
        const response = await fetch('/api/users');
        if (!response.ok) throw new Error('Failed to load users');
        
        const data = await response.json();
        crmState.users = data.users || [];
        
        // Update counts
        document.getElementById('usersCount').textContent = crmState.users.length;
        
        // Render users table
        renderUsersTable();
        
    } catch (error) {
        console.error('Error loading users:', error);
        showError('usersTableBody', 'Failed to load users');
    }
}

function renderUsersTable() {
    const tbody = document.getElementById('usersTableBody');
    if (!tbody) return;
    
    if (crmState.users.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center text-muted py-4">
                    <i class="fas fa-users fa-3x mb-3 d-block"></i>
                    No users found
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = crmState.users.map(user => {
        const isSelected = crmState.selectedItems.users.has(user.psid);
        const platform = user.platform || 'facebook';
        const platformIcon = platform === 'whatsapp' ? 'fa-whatsapp' : 'fa-facebook-messenger';
        const platformColor = platform === 'whatsapp' ? 'success' : 'primary';
        
        return `
            <tr class="${isSelected ? 'table-active' : ''}">
                <td>
                    <input type="checkbox" 
                           ${isSelected ? 'checked' : ''} 
                           onchange="toggleSelection('users', '${user.psid}', this.checked)">
                </td>
                <td>
                    <div class="d-flex align-items-center">
                        <img src="${user.profile_pic || '/static/img/default-avatar.png'}" 
                             class="rounded-circle me-2" 
                             width="40" height="40"
                             onerror="this.src='/static/img/default-avatar.png'">
                        <div>
                            <strong>${user.first_name || ''} ${user.last_name || ''}</strong>
                            <br>
                            <small class="text-muted">${user.psid}</small>
                        </div>
                    </div>
                </td>
                <td>
                    <span class="badge bg-${platformColor}">
                        <i class="fab ${platformIcon} me-1"></i>${platform}
                    </span>
                </td>
                <td>
                    <span class="badge bg-${user.is_active ? 'success' : 'secondary'}">
                        ${user.is_active ? 'Active' : 'Inactive'}
                    </span>
                </td>
                <td>${user.message_count || 0}</td>
                <td>
                    <small class="text-muted">
                        ${user.last_message_at ? formatDate(user.last_message_at) : 'Never'}
                    </small>
                </td>
                <td>
                    <button class="btn btn-sm btn-primary action-btn me-1" 
                            onclick="viewUserDetail('${user.psid}')">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-success action-btn" 
                            onclick="sendQuickMessage('${user.psid}')">
                        <i class="fas fa-paper-plane"></i>
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

// ============================================================
// Conversations Functions
// ============================================================

async function loadConversations() {
    try {
        const response = await fetch('/api/conversations');
        if (!response.ok) throw new Error('Failed to load conversations');
        
        const data = await response.json();
        crmState.conversations = data.conversations || [];
        
        // Update count
        document.getElementById('conversationsCount').textContent = crmState.conversations.length;
        
        // Render conversations list
        renderConversationsList();
        
    } catch (error) {
        console.error('Error loading conversations:', error);
    }
}

function renderConversationsList() {
    const list = document.getElementById('conversationsList');
    if (!list) return;
    
    if (crmState.conversations.length === 0) {
        list.innerHTML = `
            <div class="list-group-item text-center text-muted">
                <i class="fas fa-comments fa-2x mb-2 d-block"></i>
                No active conversations
            </div>
        `;
        return;
    }
    
    list.innerHTML = crmState.conversations.map(conv => `
        <a href="#" class="list-group-item list-group-item-action ${conv.psid === crmState.currentConversation?.psid ? 'active' : ''}" 
           onclick="loadConversation('${conv.psid}'); return false;">
            <div class="d-flex w-100 justify-content-between">
                <div class="d-flex align-items-center">
                    <img src="${conv.profile_pic || '/static/img/default-avatar.png'}" 
                         class="rounded-circle me-2" 
                         width="40" height="40">
                    <div>
                        <h6 class="mb-1">${conv.first_name || ''} ${conv.last_name || ''}</h6>
                        <small>${conv.last_message || 'No messages'}</small>
                    </div>
                </div>
                <small>${formatDate(conv.last_message_at)}</small>
            </div>
            ${conv.unread_count ? `<span class="badge bg-danger">${conv.unread_count}</span>` : ''}
        </a>
    `).join('');
}

async function loadConversation(psid) {
    try {
        const response = await fetch(`/api/messages?user_id=${psid}`);
        if (!response.ok) throw new Error('Failed to load conversation');
        
        const data = await response.json();
        crmState.currentConversation = { psid, messages: data.messages || [] };
        
        // Update header
        const user = crmState.conversations.find(c => c.psid === psid);
        if (user) {
            document.getElementById('conversationHeader').innerHTML = `
                <div class="d-flex align-items-center">
                    <img src="${user.profile_pic || '/static/img/default-avatar.png'}" 
                         class="rounded-circle me-2" 
                         width="40" height="40">
                    <div>
                        <h6 class="mb-0">${user.first_name || ''} ${user.last_name || ''}</h6>
                        <small class="text-muted">${user.psid}</small>
                    </div>
                </div>
            `;
        }
        
        // Show send button
        document.getElementById('sendMessageBtn').classList.remove('d-none');
        document.getElementById('messageComposer').classList.remove('d-none');
        
        // Render messages
        renderMessages();
        
    } catch (error) {
        console.error('Error loading conversation:', error);
        showToast('Failed to load conversation', 'error');
    }
}

function renderMessages() {
    const container = document.getElementById('messagesContainer');
    if (!container || !crmState.currentConversation) return;
    
    const messages = crmState.currentConversation.messages;
    
    if (messages.length === 0) {
        container.innerHTML = `
            <div class="text-center text-muted p-5">
                <i class="fas fa-comment-slash fa-3x mb-3"></i>
                <p>No messages yet</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = messages.map(msg => {
        const isOutgoing = msg.type === 'outgoing';
        const alignClass = isOutgoing ? 'text-end' : 'text-start';
        const bgClass = isOutgoing ? 'bg-primary text-white' : 'bg-light';
        
        return `
            <div class="${alignClass} mb-3">
                <div class="d-inline-block p-3 rounded ${bgClass}" style="max-width: 70%;">
                    ${msg.text}
                    <div class="small ${isOutgoing ? 'text-white-50' : 'text-muted'} mt-1">
                        ${formatTime(msg.timestamp)}
                    </div>
                </div>
            </div>
        `;
    }).join('');
    
    // Scroll to bottom
    container.scrollTop = container.scrollHeight;
}

// ============================================================
// Selection Functions
// ============================================================

function toggleSelection(type, id, checked) {
    if (checked) {
        crmState.selectedItems[type].add(id);
    } else {
        crmState.selectedItems[type].delete(id);
    }
    
    updateBulkActionsBar(type);
}

function toggleSelectAll(type, checked) {
    const items = type === 'leads' ? crmState.leads : crmState.users;
    
    if (checked) {
        items.forEach(item => crmState.selectedItems[type].add(item.psid));
    } else {
        crmState.selectedItems[type].clear();
    }
    
    // Re-render table
    if (type === 'leads') {
        renderLeadsTable();
    } else {
        renderUsersTable();
    }
    
    updateBulkActionsBar(type);
}

function updateBulkActionsBar(type) {
    const count = crmState.selectedItems[type].size;
    const bar = document.getElementById(`${type}ActionsBar`);
    const countSpan = document.getElementById(`selected${type.charAt(0).toUpperCase() + type.slice(1)}Count`);
    
    if (bar) {
        bar.classList.toggle('d-none', count === 0);
    }
    
    if (countSpan) {
        countSpan.textContent = count;
    }
}

function clearSelection(type) {
    crmState.selectedItems[type].clear();
    
    if (type === 'leads') {
        renderLeadsTable();
    } else {
        renderUsersTable();
    }
    
    updateBulkActionsBar(type);
}

// ============================================================
// Bulk Operations
// ============================================================

async function sendBulkMessage() {
    const audience = document.getElementById('bulkAudience')?.value;
    const message = document.getElementById('bulkMessage')?.value;
    const campaignName = document.getElementById('campaignName')?.value;
    
    if (!message) {
        showToast('Please enter a message', 'error');
        return;
    }
    
    if (!campaignName) {
        showToast('Please enter a campaign name', 'error');
        return;
    }
    
    if (!confirm(`Send message to ${audience} users?`)) {
        return;
    }
    
    try {
        showToast('Sending bulk message...', 'info');
        
        const response = await fetch('/api/messages/bulk', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                campaign_name: campaignName,
                audience: audience,
                message: message,
                scheduled: document.getElementById('scheduleMessage')?.checked || false,
                scheduled_time: document.getElementById('scheduleTime')?.value || null
            })
        });
        
        if (!response.ok) throw new Error('Failed to send bulk message');
        
        const data = await response.json();
        showToast(`✅ Message sent to ${data.sent_count} users`, 'success');
        
        // Clear form
        document.getElementById('bulkMessage').value = '';
        document.getElementById('campaignName').value = '';
        
    } catch (error) {
        console.error('Error sending bulk message:', error);
        showToast('❌ Failed to send bulk message', 'error');
    }
}

function updateBulkStats() {
    const audience = document.getElementById('bulkAudience')?.value || 'all';
    const message = document.getElementById('bulkMessage')?.value || '';
    
    let count = 0;
    if (audience === 'all') {
        count = crmState.users.length;
    } else if (audience === 'leads') {
        count = crmState.leads.length;
    } else if (audience === 'active') {
        count = crmState.users.filter(u => u.is_active).length;
    }
    
    document.getElementById('recipientsCount').textContent = count;
    document.getElementById('charCount').textContent = message.length;
    
    // Rough estimate: $0.005 per message
    const cost = (count * 0.005).toFixed(2);
    document.getElementById('estimatedCost').textContent = `$${cost}`;
}

// ============================================================
// User Detail Functions
// ============================================================

async function viewUserDetail(psid) {
    try {
        const response = await fetch(`/api/users/${psid}`);
        if (!response.ok) throw new Error('Failed to load user details');
        
        const user = await response.json();
        
        // Populate modal
        document.getElementById('userDetailTitle').textContent = `${user.first_name || ''} ${user.last_name || ''}`;
        document.getElementById('userDetailBody').innerHTML = `
            <div class="row">
                <div class="col-md-4 text-center">
                    <img src="${user.profile_pic || '/static/img/default-avatar.png'}" 
                         class="rounded-circle mb-3" 
                         width="120" height="120">
                    <h5>${user.first_name || ''} ${user.last_name || ''}</h5>
                    <p class="text-muted">${user.psid}</p>
                    <span class="badge bg-${user.is_active ? 'success' : 'secondary'} mb-2">
                        ${user.is_active ? 'Active' : 'Inactive'}
                    </span>
                </div>
                <div class="col-md-8">
                    <h6>Contact Information</h6>
                    <table class="table table-sm">
                        <tr>
                            <td><strong>Platform:</strong></td>
                            <td>${user.platform || 'Facebook'}</td>
                        </tr>
                        <tr>
                            <td><strong>Governorate:</strong></td>
                            <td>${user.governorate || 'Not set'}</td>
                        </tr>
                        <tr>
                            <td><strong>Lead Stage:</strong></td>
                            <td><span class="badge bg-${getStageColor(user.lead_stage)}">${user.lead_stage || 'NEW'}</span></td>
                        </tr>
                        <tr>
                            <td><strong>Customer Type:</strong></td>
                            <td><span class="badge bg-${getTypeColor(user.customer_type)}">${user.customer_type || 'POTENTIAL'}</span></td>
                        </tr>
                        <tr>
                            <td><strong>Lead Score:</strong></td>
                            <td>${user.lead_score || 0}</td>
                        </tr>
                        <tr>
                            <td><strong>Total Messages:</strong></td>
                            <td>${user.message_count || 0}</td>
                        </tr>
                        <tr>
                            <td><strong>Created:</strong></td>
                            <td>${formatDate(user.created_at)}</td>
                        </tr>
                        <tr>
                            <td><strong>Last Active:</strong></td>
                            <td>${user.last_message_at ? formatDate(user.last_message_at) : 'Never'}</td>
                        </tr>
                    </table>
                    
                    <div class="d-grid gap-2 mt-3">
                        <button class="btn btn-primary" onclick="sendQuickMessage('${user.psid}')">
                            <i class="fas fa-paper-plane me-2"></i>Send Message
                        </button>
                        <button class="btn btn-info" onclick="changeLeadStage('${user.psid}')">
                            <i class="fas fa-exchange-alt me-2"></i>Change Stage
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('userDetailModal'));
        modal.show();
        
    } catch (error) {
        console.error('Error loading user details:', error);
        showToast('Failed to load user details', 'error');
    }
}

// ============================================================
// Utility Functions
// ============================================================

function refreshAll() {
    loadStats();
    loadLeads();
    const activeTab = document.querySelector('.crm-tabs .nav-link.active');
    if (activeTab) {
        const target = activeTab.getAttribute('data-bs-target');
        if (target === '#users') loadUsers();
        if (target === '#conversations') loadConversations();
    }
    
    // Update sync time
    document.getElementById('syncTime').textContent = new Date().toLocaleTimeString();
}

function showLoading(tbodyId) {
    const tbody = document.getElementById(tbodyId);
    if (tbody) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center py-4">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </td>
            </tr>
        `;
    }
}

function showError(tbodyId, message) {
    const tbody = document.getElementById(tbodyId);
    if (tbody) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center text-danger py-4">
                    <i class="fas fa-exclamation-triangle fa-2x mb-2 d-block"></i>
                    ${message}
                </td>
            </tr>
        `;
    }
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('notificationToast');
    const toastBody = document.getElementById('toastMessage');
    
    if (toast && toastBody) {
        toastBody.textContent = message;
        
        toast.className = 'toast';
        if (type === 'success') {
            toast.classList.add('bg-success', 'text-white');
        } else if (type === 'error') {
            toast.classList.add('bg-danger', 'text-white');
        } else if (type === 'warning') {
            toast.classList.add('bg-warning');
        }
        
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
    }
}

function formatDate(dateString) {
    if (!dateString) return 'Never';
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);
    
    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    
    return date.toLocaleDateString();
}

function formatTime(timestamp) {
    if (!timestamp) return '';
    return new Date(timestamp).toLocaleTimeString();
}

function getStageColor(stage) {
    const colors = {
        'NEW': 'primary',
        'CONTACTED': 'info',
        'QUALIFIED': 'success',
        'NEGOTIATING': 'warning',
        'CONVERTED': 'success',
        'LOST': 'danger'
    };
    return colors[stage] || 'secondary';
}

function getTypeColor(type) {
    const colors = {
        'POTENTIAL': 'info',
        'ACTIVE': 'success',
        'VIP': 'warning',
        'CHURNED': 'danger'
    };
    return colors[type] || 'secondary';
}

function getScoreColor(score) {
    if (score >= 80) return 'success';
    if (score >= 50) return 'warning';
    return 'danger';
}

// Placeholder functions for future implementation
function sendQuickMessage(psid) {
    showToast('Quick message feature coming soon!', 'info');
}

function changeLeadStage(psid) {
    showToast('Change stage feature coming soon!', 'info');
}

function bulkChangeStage() {
    showToast('Bulk change stage feature coming soon!', 'info');
}

function bulkExport(type) {
    showToast('Export feature coming soon!', 'info');
}

function previewBulkMessage() {
    showToast('Preview feature coming soon!', 'info');
}

function loadTemplate() {
    const template = document.getElementById('messageTemplate')?.value;
    const messageBox = document.getElementById('bulkMessage');
    
    const templates = {
        'welcome': 'مرحباً {name}! 👋\nشكراً لتواصلك معنا. كيف يمكننا مساعدتك اليوم؟',
        'followup': 'مرحباً {name}! 😊\nنود متابعة طلبك السابق. هل لديك أي استفسارات؟',
        'promotion': '🎉 عرض خاص لك {name}!\nاحصل على خصم 20% على جميع المنتجات اليوم فقط!',
        'reminder': 'مرحباً {name}! ⏰\nنذكرك بموعدك القادم معنا.'
    };
    
    if (template && templates[template]) {
        messageBox.value = templates[template];
        updateBulkStats();
    }
}

async function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input?.value;
    
    if (!message || !crmState.currentConversation) {
        return;
    }
    
    try {
        const response = await fetch('/api/messages/send', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: crmState.currentConversation.psid,
                text: message,
                platform: 'facebook'
            })
        });
        
        if (!response.ok) throw new Error('Failed to send message');
        
        input.value = '';
        loadConversation(crmState.currentConversation.psid);
        showToast('✅ Message sent', 'success');
        
    } catch (error) {
        console.error('Error sending message:', error);
        showToast('❌ Failed to send message', 'error');
    }
}

function showMessageComposer() {
    document.getElementById('messageComposer').classList.toggle('d-none');
}
