// Dashboard JavaScript functionality
const API_BASE_URL = 'http://localhost:8000/api/v1/demo';
const API_BASE = API_BASE_URL; // Alias for document functions

// Dashboard state
let currentSection = 'dashboard';

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    checkSystemHealth();
    loadDashboardStats();
    loadCandidates();
    loadJobs();
    loadApplications();
});

// System health check
async function checkSystemHealth() {
    try {
        const response = await fetch('http://localhost:8000/health');
        const data = await response.json();
        if (data.status === 'healthy') {
            document.getElementById('system-status').textContent = 'Online';
            document.getElementById('system-status').className = 'text-green-600 font-medium';
        }
    } catch (error) {
        document.getElementById('system-status').textContent = 'Offline';
        document.getElementById('system-status').className = 'text-red-600 font-medium';
    }
}

// Load dashboard statistics
async function loadDashboardStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/stats`);
        if (response.ok) {
            const stats = await response.json();
            document.getElementById('total-candidates').textContent = stats.total_candidates.toString();
            document.getElementById('active-jobs').textContent = stats.active_jobs.toString();
            document.getElementById('total-applications').textContent = stats.total_applications.toString();
            document.getElementById('scheduled-interviews').textContent = (stats.scheduled_interviews || 0).toString();
            document.getElementById('active-panels').textContent = (stats.active_panels || 0).toString();
        } else {
            // Fallback to 0 if API fails
            document.getElementById('total-candidates').textContent = '0';
            document.getElementById('active-jobs').textContent = '0';
            document.getElementById('total-applications').textContent = '0';
            document.getElementById('scheduled-interviews').textContent = '0';
            document.getElementById('active-panels').textContent = '0';
        }
    } catch (error) {
        console.error('Error loading dashboard stats:', error);
        // Fallback to 0 if API fails
        document.getElementById('total-candidates').textContent = '0';
        document.getElementById('active-jobs').textContent = '0';
        document.getElementById('total-applications').textContent = '0';
        document.getElementById('scheduled-interviews').textContent = '0';
        document.getElementById('active-panels').textContent = '0';
    }
}

// Section navigation
function showSection(sectionName) {
    // Hide all sections
    const sections = document.querySelectorAll('.dashboard-content');
    sections.forEach(section => section.classList.add('hidden'));
    
    // Show selected section
    document.getElementById(`${sectionName}-section`).classList.remove('hidden');
    currentSection = sectionName;
    
    // Load section data
    if (sectionName === 'candidates') {
        loadCandidates();
    } else if (sectionName === 'jobs') {
        loadJobs();
    } else if (sectionName === 'applications') {
        loadApplications();
    } else if (sectionName === 'interviews') {
        showInterviewTab('panels');
    }
}

// Load candidates
async function loadCandidates() {
    const candidatesList = document.getElementById('candidates-list');
    
    try {
        const response = await fetch(`${API_BASE_URL}/candidates`);
        if (response.ok) {
            const candidates = await response.json();
            if (candidates.length === 0) {
                candidatesList.innerHTML = `
                    <div class="text-center py-8">
                        <i class="fas fa-user-friends text-4xl text-gray-300 mb-4"></i>
                        <h3 class="text-lg font-medium text-gray-500 mb-2">No Candidates Yet</h3>
                        <p class="text-gray-400 mb-4">Add your first candidate to get started with AI-powered recruitment</p>
                        <button onclick="showAddCandidateModal()" class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition-all">
                            <i class="fas fa-plus"></i> Add First Candidate
                        </button>
                    </div>
                `;
            } else {
                renderCandidates(candidates);
            }
        } else {
            candidatesList.innerHTML = `
                <div class="text-center py-8">
                    <i class="fas fa-exclamation-triangle text-4xl text-red-300 mb-4"></i>
                    <h3 class="text-lg font-medium text-red-500 mb-2">Error Loading Candidates</h3>
                    <p class="text-gray-400">Please try refreshing the page</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading candidates:', error);
        candidatesList.innerHTML = `
            <div class="text-center py-8">
                <i class="fas fa-exclamation-triangle text-4xl text-red-300 mb-4"></i>
                <h3 class="text-lg font-medium text-red-500 mb-2">Error Loading Candidates</h3>
                <p class="text-gray-400">Please check your connection and try again</p>
            </div>
        `;
    }
}

// Load jobs
async function loadJobs() {
    const jobsList = document.getElementById('jobs-list');
    
    try {
        const response = await fetch(`${API_BASE_URL}/jobs`);
        if (response.ok) {
            const jobs = await response.json();
            if (jobs.length === 0) {
                jobsList.innerHTML = `
                    <div class="text-center py-8">
                        <i class="fas fa-briefcase text-4xl text-gray-300 mb-4"></i>
                        <h3 class="text-lg font-medium text-gray-500 mb-2">No Job Postings</h3>
                        <p class="text-gray-400 mb-4">Create your first job posting to start recruiting</p>
                        <button onclick="showAddJobModal()" class="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg transition-all">
                            <i class="fas fa-plus"></i> Create First Job
                        </button>
                    </div>
                `;
            } else {
                renderJobs(jobs);
            }
        } else {
            jobsList.innerHTML = `
                <div class="text-center py-8">
                    <i class="fas fa-exclamation-triangle text-4xl text-red-300 mb-4"></i>
                    <h3 class="text-lg font-medium text-red-500 mb-2">Error Loading Jobs</h3>
                    <p class="text-gray-400">Please try refreshing the page</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading jobs:', error);
        jobsList.innerHTML = `
            <div class="text-center py-8">
                <i class="fas fa-exclamation-triangle text-4xl text-red-300 mb-4"></i>
                <h3 class="text-lg font-medium text-red-500 mb-2">Error Loading Jobs</h3>
                <p class="text-gray-400">Please check your connection and try again</p>
            </div>
        `;
    }
}

// Render candidates list
function renderCandidates(candidates) {
    const candidatesList = document.getElementById('candidates-list');
    candidatesList.innerHTML = candidates.map(candidate => `
        <div class="bg-white rounded-lg shadow-sm p-6 mb-4">
            <div class="flex items-start justify-between">
                <div class="flex items-center">
                    <div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                        <i class="fas fa-user text-blue-600"></i>
                    </div>
                    <div class="ml-4">
                        <h3 class="text-lg font-medium text-gray-900">${candidate.full_name}</h3>
                        <p class="text-gray-600">${candidate.email}</p>
                        ${candidate.current_position ? `<p class="text-sm text-gray-500">${candidate.current_position}</p>` : ''}
                    </div>
                </div>
                <div class="flex space-x-2">
                    <button onclick="viewCandidate('${candidate.id}')" class="px-3 py-1 bg-blue-50 text-blue-600 rounded-lg text-sm hover:bg-blue-100">
                        <i class="fas fa-eye"></i> View
                    </button>
                    <button onclick="showCandidateDocuments('${candidate.id}', '${candidate.full_name}')" class="px-3 py-1 bg-cyan-50 text-cyan-600 rounded-lg text-sm hover:bg-cyan-100">
                        <i class="fas fa-folder-open"></i> Documents
                    </button>
                    <button onclick="editCandidate('${candidate.id}')" class="px-3 py-1 bg-green-50 text-green-600 rounded-lg text-sm hover:bg-green-100">
                        <i class="fas fa-edit"></i> Edit
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

// Render jobs list
function renderJobs(jobs) {
    const jobsList = document.getElementById('jobs-list');
    jobsList.innerHTML = jobs.map(job => `
        <div class="bg-white rounded-lg shadow-sm p-6 mb-4">
            <div class="flex items-start justify-between">
                <div>
                    <h3 class="text-lg font-medium text-gray-900">${job.title}</h3>
                    <p class="text-gray-600 mb-2">${job.department} • ${job.location}</p>
                    <p class="text-sm text-gray-500">${job.employment_type}</p>
                    <div class="mt-2">
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            Active
                        </span>
                    </div>
                </div>
                <div class="flex space-x-2">
                    <button onclick="viewJob('${job.id}')" class="px-3 py-1 bg-blue-50 text-blue-600 rounded-lg text-sm hover:bg-blue-100">
                        <i class="fas fa-eye"></i> View
                    </button>
                    <button onclick="editJob('${job.id}')" class="px-3 py-1 bg-green-50 text-green-600 rounded-lg text-sm hover:bg-green-100">
                        <i class="fas fa-edit"></i> Edit
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

// Load applications
async function loadApplications() {
    const applicationsList = document.getElementById('applications-list');
    applicationsList.innerHTML = `
        <div class="text-center py-8">
            <i class="fas fa-clipboard-list text-4xl text-gray-300 mb-4"></i>
            <h3 class="text-lg font-medium text-gray-500 mb-2">No Applications</h3>
            <p class="text-gray-400">Applications will appear here once candidates apply for jobs</p>
        </div>
    `;
}

// Modal functions
function showAddCandidateModal() {
    document.getElementById('add-candidate-modal').classList.remove('hidden');
    document.getElementById('add-candidate-modal').classList.add('flex');
}

function showAddJobModal() {
    document.getElementById('add-job-modal').classList.remove('hidden');
    document.getElementById('add-job-modal').classList.add('flex');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.add('hidden');
    document.getElementById(modalId).classList.remove('flex');
}

// Form handlers
document.getElementById('candidate-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = new FormData();
    formData.append('full_name', document.getElementById('candidate-name').value);
    formData.append('email', document.getElementById('candidate-email').value);
    formData.append('phone', document.getElementById('candidate-phone').value);
    
    const resumeFile = document.getElementById('candidate-resume').files[0];
    if (resumeFile) {
        formData.append('resume', resumeFile);
    }
    
    try {
        showNotification('Adding candidate...', 'info');
        
        const response = await fetch(`${API_BASE_URL}/candidates`, {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const result = await response.json();
            showNotification('Candidate added successfully! 🎉', 'success');
            closeModal('add-candidate-modal');
            document.getElementById('candidate-form').reset();
            loadCandidates();
            updateStats();
        } else {
            const error = await response.json();
            showNotification(`Failed to add candidate: ${error.detail}`, 'error');
        }
        
    } catch (error) {
        console.error('Error adding candidate:', error);
        showNotification('Failed to add candidate. Please try again.', 'error');
    }
});

document.getElementById('job-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const jobData = {
        title: document.getElementById('job-title').value,
        description: document.getElementById('job-description').value,
        department: document.getElementById('job-department').value,
        location: document.getElementById('job-location').value,
        employment_type: document.getElementById('job-type').value,
        experience_level: 'mid' // Default value
    };
    
    try {
        showNotification('Creating job...', 'info');
        
        const response = await fetch(`${API_BASE_URL}/jobs`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(jobData)
        });
        
        if (response.ok) {
            const result = await response.json();
            showNotification('Job created successfully! 🚀', 'success');
            closeModal('add-job-modal');
            document.getElementById('job-form').reset();
            loadJobs();
            updateStats();
        } else {
            const error = await response.json();
            showNotification(`Failed to create job: ${error.detail}`, 'error');
        }
        
    } catch (error) {
        console.error('Error creating job:', error);
        showNotification('Failed to create job. Please try again.', 'error');
    }
});

// Edit form handlers
document.getElementById('edit-candidate-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const candidateId = document.getElementById('edit-candidate-id').value;
    const candidateData = {
        full_name: document.getElementById('edit-candidate-name').value,
        email: document.getElementById('edit-candidate-email').value,
        phone: document.getElementById('edit-candidate-phone').value,
        current_position: document.getElementById('edit-candidate-position').value,
        current_company: document.getElementById('edit-candidate-company').value,
        experience_years: parseInt(document.getElementById('edit-candidate-experience').value) || 0
    };
    
    try {
        showNotification('Updating candidate...', 'info');
        
        const response = await fetch(`${API_BASE_URL}/candidates/${candidateId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(candidateData)
        });
        
        if (response.ok) {
            const result = await response.json();
            showNotification('Candidate updated successfully! ✅', 'success');
            closeModal('edit-candidate-modal');
            loadCandidates();
        } else {
            const error = await response.json();
            showNotification(`Failed to update candidate: ${error.detail}`, 'error');
        }
        
    } catch (error) {
        console.error('Error updating candidate:', error);
        showNotification('Failed to update candidate. Please try again.', 'error');
    }
});

document.getElementById('edit-job-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const jobId = document.getElementById('edit-job-id').value;
    const jobData = {
        title: document.getElementById('edit-job-title').value,
        description: document.getElementById('edit-job-description').value,
        requirements: document.getElementById('edit-job-requirements').value,
        department: document.getElementById('edit-job-department').value,
        location: document.getElementById('edit-job-location').value,
        job_type: document.getElementById('edit-job-type').value,
        experience_level: document.getElementById('edit-job-level').value
    };
    
    try {
        showNotification('Updating job...', 'info');
        
        const response = await fetch(`${API_BASE_URL}/jobs/${jobId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(jobData)
        });
        
        if (response.ok) {
            const result = await response.json();
            showNotification('Job updated successfully! ✅', 'success');
            closeModal('edit-job-modal');
            loadJobs();
        } else {
            const error = await response.json();
            showNotification(`Failed to update job: ${error.detail}`, 'error');
        }
        
    } catch (error) {
        console.error('Error updating job:', error);
        showNotification('Failed to update job. Please try again.', 'error');
    }
});

// Notification system
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    const colors = {
        success: 'bg-green-500',
        error: 'bg-red-500',
        info: 'bg-blue-500'
    };
    
    notification.className = `fixed top-4 right-4 ${colors[type]} text-white px-6 py-3 rounded-lg shadow-lg z-50 transform transition-all duration-300 translate-x-full`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.classList.remove('translate-x-full');
    }, 100);
    
    // Auto remove
    setTimeout(() => {
        notification.classList.add('translate-x-full');
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Update statistics after actions
function updateStats() {
    loadDashboardStats();
}

// Logout function
function logout() {
    showNotification('Logging out...', 'info');
    setTimeout(() => {
        window.location.href = 'login.html';
    }, 1000);
}

// API Demo Functions
async function testAPI() {
    try {
        const response = await fetch('http://localhost:8000/health');
        const data = await response.json();
        showNotification('API Connection Successful! ✅', 'success');
        return data;
    } catch (error) {
        showNotification('API Connection Failed - Please start the backend server', 'error');
        console.error('API Error:', error);
    }
}

// Auto-refresh system status
setInterval(checkSystemHealth, 30000); // Check every 30 seconds

// View and Edit Functions
async function viewCandidate(candidateId) {
    try {
        const response = await fetch(`${API_BASE_URL}/candidates/${candidateId}`);
        if (response.ok) {
            const candidate = await response.json();
            showCandidateDetailsModal(candidate);
        } else {
            showNotification('Could not load candidate details', 'error');
        }
    } catch (error) {
        console.error('Error viewing candidate:', error);
        showNotification('Error loading candidate details', 'error');
    }
}

async function editCandidate(candidateId) {
    try {
        const response = await fetch(`${API_BASE_URL}/candidates/${candidateId}`);
        if (response.ok) {
            const candidate = await response.json();
            showEditCandidateModal(candidate);
        } else {
            showNotification('Could not load candidate for editing', 'error');
        }
    } catch (error) {
        console.error('Error loading candidate for edit:', error);
        showNotification('Error loading candidate for editing', 'error');
    }
}

async function viewJob(jobId) {
    try {
        const response = await fetch(`${API_BASE_URL}/jobs/${jobId}`);
        if (response.ok) {
            const job = await response.json();
            showJobDetailsModal(job);
        } else {
            showNotification('Could not load job details', 'error');
        }
    } catch (error) {
        console.error('Error viewing job:', error);
        showNotification('Error loading job details', 'error');
    }
}

async function editJob(jobId) {
    try {
        const response = await fetch(`${API_BASE_URL}/jobs/${jobId}`);
        if (response.ok) {
            const job = await response.json();
            showEditJobModal(job);
        } else {
            showNotification('Could not load job for editing', 'error');
        }
    } catch (error) {
        console.error('Error loading job for edit:', error);
        showNotification('Error loading job for editing', 'error');
    }
}

// Modal display functions
function showCandidateDetailsModal(candidate) {
    // Populate the view modal with candidate details
    const content = document.getElementById('candidate-details-content');
    content.innerHTML = `
        <div class="grid grid-cols-2 gap-4">
            <div>
                <label class="block text-sm font-medium text-gray-700">Full Name</label>
                <p class="mt-1 text-sm text-gray-900">${candidate.full_name || candidate.name || 'N/A'}</p>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700">Email</label>
                <p class="mt-1 text-sm text-gray-900">${candidate.email || 'N/A'}</p>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700">Phone</label>
                <p class="mt-1 text-sm text-gray-900">${candidate.phone || 'N/A'}</p>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700">Experience</label>
                <p class="mt-1 text-sm text-gray-900">${candidate.experience_years || 0} years</p>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700">Current Position</label>
                <p class="mt-1 text-sm text-gray-900">${candidate.current_position || 'N/A'}</p>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700">Current Company</label>
                <p class="mt-1 text-sm text-gray-900">${candidate.current_company || 'N/A'}</p>
            </div>
        </div>
        <div class="mt-4">
            <label class="block text-sm font-medium text-gray-700">Status</label>
            <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(candidate.status)} mt-1">
                ${candidate.status || 'N/A'}
            </span>
        </div>
    `;
    
    showModal('view-candidate-modal');
}

function showEditCandidateModal(candidate) {
    // Populate the edit form with candidate data
    document.getElementById('edit-candidate-id').value = candidate.id;
    document.getElementById('edit-candidate-name').value = candidate.full_name || candidate.name || '';
    document.getElementById('edit-candidate-email').value = candidate.email || '';
    document.getElementById('edit-candidate-phone').value = candidate.phone || '';
    document.getElementById('edit-candidate-position').value = candidate.current_position || '';
    document.getElementById('edit-candidate-company').value = candidate.current_company || '';
    document.getElementById('edit-candidate-experience').value = candidate.experience_years || '';
    
    showModal('edit-candidate-modal');
}

function showJobDetailsModal(job) {
    // Populate the view modal with job details
    const content = document.getElementById('job-details-content');
    content.innerHTML = `
        <div class="grid grid-cols-2 gap-4">
            <div>
                <label class="block text-sm font-medium text-gray-700">Job Title</label>
                <p class="mt-1 text-sm text-gray-900">${job.title || 'N/A'}</p>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700">Department</label>
                <p class="mt-1 text-sm text-gray-900">${job.department || 'N/A'}</p>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700">Location</label>
                <p class="mt-1 text-sm text-gray-900">${job.location || 'N/A'}</p>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700">Job Type</label>
                <p class="mt-1 text-sm text-gray-900">${job.job_type || 'N/A'}</p>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700">Experience Level</label>
                <p class="mt-1 text-sm text-gray-900">${job.experience_level || 'N/A'}</p>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700">Status</label>
                <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(job.status)} mt-1">
                    ${job.status || 'N/A'}
                </span>
            </div>
        </div>
        <div class="mt-4">
            <label class="block text-sm font-medium text-gray-700">Description</label>
            <p class="mt-1 text-sm text-gray-900 whitespace-pre-wrap">${job.description || 'N/A'}</p>
        </div>
        <div class="mt-4">
            <label class="block text-sm font-medium text-gray-700">Requirements</label>
            <p class="mt-1 text-sm text-gray-900 whitespace-pre-wrap">${job.requirements || 'N/A'}</p>
        </div>
    `;
    
    showModal('view-job-modal');
}

function showEditJobModal(job) {
    // Populate the edit form with job data
    document.getElementById('edit-job-id').value = job.id;
    document.getElementById('edit-job-title').value = job.title || '';
    document.getElementById('edit-job-description').value = job.description || '';
    document.getElementById('edit-job-requirements').value = job.requirements || '';
    document.getElementById('edit-job-department').value = job.department || '';
    document.getElementById('edit-job-location').value = job.location || '';
    document.getElementById('edit-job-type').value = job.job_type || '';
    document.getElementById('edit-job-level').value = job.experience_level || '';
    
    showModal('edit-job-modal');
}

// Helper function to get status color classes
function getStatusColor(status) {
    const statusColors = {
        'Active': 'bg-green-100 text-green-800',
        'open': 'bg-green-100 text-green-800',
        'Interviewing': 'bg-blue-100 text-blue-800',
        'interviewing': 'bg-blue-100 text-blue-800',
        'Offered': 'bg-purple-100 text-purple-800',
        'offered': 'bg-purple-100 text-purple-800',
        'Hired': 'bg-green-100 text-green-800',
        'hired': 'bg-green-100 text-green-800',
        'Rejected': 'bg-red-100 text-red-800',
        'rejected': 'bg-red-100 text-red-800',
        'Closed': 'bg-gray-100 text-gray-800',
        'closed': 'bg-gray-100 text-gray-800',
        'Paused': 'bg-yellow-100 text-yellow-800',
        'paused': 'bg-yellow-100 text-yellow-800',
        'scheduled': 'bg-blue-100 text-blue-800',
        'in_progress': 'bg-yellow-100 text-yellow-800',
        'completed': 'bg-green-100 text-green-800',
        'cancelled': 'bg-red-100 text-red-800',
        'available': 'bg-green-100 text-green-800',
        'booked': 'bg-blue-100 text-blue-800',
        'blocked': 'bg-gray-100 text-gray-800',
        'past': 'bg-gray-100 text-gray-800'
    };
    return statusColors[status] || 'bg-gray-100 text-gray-800';
}

// Helper function to show modal
function showModal(modalId) {
    document.getElementById(modalId).classList.remove('hidden');
    document.getElementById(modalId).classList.add('flex');
}

// ==================== INTERVIEW MANAGEMENT ====================

// Interview tab navigation
function showInterviewTab(tabName) {
    // Update tab styles
    document.querySelectorAll('.interview-tab').forEach(tab => {
        tab.classList.remove('text-indigo-600', 'border-b-2', 'border-indigo-600', 'bg-indigo-50');
        tab.classList.add('text-gray-500');
    });
    
    const activeTab = document.getElementById(`tab-${tabName}`);
    activeTab.classList.add('text-indigo-600', 'border-b-2', 'border-indigo-600', 'bg-indigo-50');
    activeTab.classList.remove('text-gray-500');
    
    // Hide all content sections
    document.querySelectorAll('.interview-content').forEach(content => {
        content.classList.add('hidden');
    });
    
    // Show selected content
    document.getElementById(`${tabName}-content`).classList.remove('hidden');
    
    // Load data for the tab
    if (tabName === 'panels') {
        loadPanels();
    } else if (tabName === 'slots') {
        loadSlots();
    } else if (tabName === 'scheduled') {
        loadInterviews();
    }
}

// ==================== PANEL FUNCTIONS ====================

let interviewerCount = 0;

async function loadPanels() {
    const panelsList = document.getElementById('panels-list');
    
    try {
        const response = await fetch(`${API_BASE_URL}/panels`);
        if (response.ok) {
            const panels = await response.json();
            if (panels.length === 0) {
                panelsList.innerHTML = `
                    <div class="text-center py-8">
                        <i class="fas fa-users-cog text-4xl text-gray-300 mb-4"></i>
                        <h3 class="text-lg font-medium text-gray-500 mb-2">No Interview Panels</h3>
                        <p class="text-gray-400 mb-4">Create your first interview panel to start scheduling interviews</p>
                        <button onclick="showAddPanelModal()" class="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2 rounded-lg transition-all">
                            <i class="fas fa-plus"></i> Create First Panel
                        </button>
                    </div>
                `;
            } else {
                renderPanels(panels);
            }
        } else {
            panelsList.innerHTML = `
                <div class="text-center py-8">
                    <i class="fas fa-exclamation-triangle text-4xl text-red-300 mb-4"></i>
                    <h3 class="text-lg font-medium text-red-500 mb-2">Error Loading Panels</h3>
                    <p class="text-gray-400">Please try refreshing the page</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading panels:', error);
        panelsList.innerHTML = `
            <div class="text-center py-8">
                <i class="fas fa-exclamation-triangle text-4xl text-red-300 mb-4"></i>
                <h3 class="text-lg font-medium text-red-500 mb-2">Error Loading Panels</h3>
                <p class="text-gray-400">Please check your connection</p>
            </div>
        `;
    }
    
    // Populate panel dropdowns
    populatePanelDropdowns();
}

function renderPanels(panels) {
    const panelsList = document.getElementById('panels-list');
    
    const levelLabels = {
        'screening': 'Screening',
        'technical_1': 'Technical Round 1',
        'technical_2': 'Technical Round 2',
        'managerial': 'Managerial',
        'hr': 'HR',
        'final': 'Final'
    };
    
    panelsList.innerHTML = panels.map(panel => `
        <div class="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-all">
            <div class="flex items-start justify-between">
                <div>
                    <h3 class="text-lg font-medium text-gray-900">${panel.name}</h3>
                    <div class="flex items-center space-x-4 mt-2">
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">
                            ${levelLabels[panel.level] || panel.level}
                        </span>
                        ${panel.department ? `<span class="text-sm text-gray-500">${panel.department}</span>` : ''}
                    </div>
                    <div class="flex items-center space-x-4 mt-3 text-sm text-gray-600">
                        <span><i class="fas fa-users mr-1"></i> ${(panel.interviewers || []).length} Interviewers</span>
                        <span><i class="fas fa-clock mr-1"></i> ${panel.interview_duration_minutes} min</span>
                        <span><i class="fas fa-calendar-day mr-1"></i> Max ${panel.max_interviews_per_day}/day</span>
                    </div>
                    ${panel.skills_evaluated && panel.skills_evaluated.length > 0 ? `
                        <div class="mt-3 flex flex-wrap gap-1">
                            ${panel.skills_evaluated.map(skill => `
                                <span class="inline-flex items-center px-2 py-0.5 rounded text-xs bg-gray-100 text-gray-700">${skill}</span>
                            `).join('')}
                        </div>
                    ` : ''}
                </div>
                <div class="flex space-x-2">
                    <button onclick="viewPanel('${panel.id}')" class="px-3 py-1 bg-indigo-50 text-indigo-600 rounded-lg text-sm hover:bg-indigo-100">
                        <i class="fas fa-eye"></i> View
                    </button>
                    <button onclick="deletePanel('${panel.id}')" class="px-3 py-1 bg-red-50 text-red-600 rounded-lg text-sm hover:bg-red-100">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

function showAddPanelModal() {
    interviewerCount = 0;
    document.getElementById('interviewers-list').innerHTML = '';
    document.getElementById('panel-form').reset();
    showModal('add-panel-modal');
    // Add initial interviewer row
    addInterviewerRow();
}

function addInterviewerRow() {
    interviewerCount++;
    const container = document.getElementById('interviewers-list');
    const row = document.createElement('div');
    row.id = `interviewer-row-${interviewerCount}`;
    row.className = 'flex items-center space-x-2 p-2 bg-gray-50 rounded';
    row.innerHTML = `
        <input type="text" placeholder="Name" class="flex-1 border border-gray-300 rounded px-3 py-1 text-sm interviewer-name" required>
        <input type="email" placeholder="Email" class="flex-1 border border-gray-300 rounded px-3 py-1 text-sm interviewer-email" required>
        <input type="text" placeholder="Role" class="flex-1 border border-gray-300 rounded px-3 py-1 text-sm interviewer-role">
        <label class="flex items-center text-sm">
            <input type="checkbox" class="mr-1 interviewer-lead"> Lead
        </label>
        <button type="button" onclick="removeInterviewerRow(${interviewerCount})" class="text-red-500 hover:text-red-700">
            <i class="fas fa-times"></i>
        </button>
    `;
    container.appendChild(row);
}

function removeInterviewerRow(id) {
    const row = document.getElementById(`interviewer-row-${id}`);
    if (row) {
        row.remove();
    }
}

// Panel form handler
document.getElementById('panel-form')?.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    // Collect interviewers data
    const interviewers = [];
    document.querySelectorAll('#interviewers-list > div').forEach(row => {
        const name = row.querySelector('.interviewer-name').value;
        const email = row.querySelector('.interviewer-email').value;
        if (name && email) {
            interviewers.push({
                name: name,
                email: email,
                role: row.querySelector('.interviewer-role').value || null,
                is_lead: row.querySelector('.interviewer-lead').checked
            });
        }
    });
    
    const skills = document.getElementById('panel-skills').value
        .split(',')
        .map(s => s.trim())
        .filter(s => s);
    
    const panelData = {
        name: document.getElementById('panel-name').value,
        level: document.getElementById('panel-level').value,
        department: document.getElementById('panel-department').value || null,
        description: document.getElementById('panel-description').value || null,
        max_interviews_per_day: parseInt(document.getElementById('panel-max-interviews').value) || 5,
        interview_duration_minutes: parseInt(document.getElementById('panel-duration').value) || 60,
        buffer_minutes: parseInt(document.getElementById('panel-buffer').value) || 15,
        interviewers: interviewers,
        skills_evaluated: skills
    };
    
    try {
        showNotification('Creating panel...', 'info');
        
        const response = await fetch(`${API_BASE_URL}/panels`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(panelData)
        });
        
        if (response.ok) {
            showNotification('Panel created successfully! 🎯', 'success');
            closeModal('add-panel-modal');
            loadPanels();
        } else {
            const error = await response.json();
            showNotification(`Failed to create panel: ${error.detail}`, 'error');
        }
    } catch (error) {
        console.error('Error creating panel:', error);
        showNotification('Failed to create panel', 'error');
    }
});

async function viewPanel(panelId) {
    try {
        const response = await fetch(`${API_BASE_URL}/panels/${panelId}`);
        if (response.ok) {
            const panel = await response.json();
            showPanelDetailsModal(panel);
        } else {
            showNotification('Could not load panel details', 'error');
        }
    } catch (error) {
        console.error('Error viewing panel:', error);
        showNotification('Error loading panel details', 'error');
    }
}

function showPanelDetailsModal(panel) {
    const levelLabels = {
        'screening': 'Screening',
        'technical_1': 'Technical Round 1',
        'technical_2': 'Technical Round 2',
        'managerial': 'Managerial',
        'hr': 'HR',
        'final': 'Final'
    };
    
    const content = document.getElementById('panel-details-content');
    content.innerHTML = `
        <div class="grid grid-cols-2 gap-4">
            <div>
                <label class="block text-sm font-medium text-gray-700">Panel Name</label>
                <p class="mt-1 text-sm text-gray-900">${panel.name}</p>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700">Level</label>
                <p class="mt-1 text-sm text-gray-900">${levelLabels[panel.level] || panel.level}</p>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700">Department</label>
                <p class="mt-1 text-sm text-gray-900">${panel.department || 'N/A'}</p>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700">Duration</label>
                <p class="mt-1 text-sm text-gray-900">${panel.interview_duration_minutes} minutes</p>
            </div>
        </div>
        
        <div class="mt-6">
            <label class="block text-sm font-medium text-gray-700 mb-2">Panel Members</label>
            <div class="space-y-2">
                ${(panel.interviewers || []).map(i => `
                    <div class="flex items-center p-3 bg-gray-50 rounded-lg">
                        <div class="w-10 h-10 bg-indigo-100 rounded-full flex items-center justify-center mr-3">
                            <i class="fas fa-user text-indigo-600"></i>
                        </div>
                        <div>
                            <p class="font-medium text-gray-900">${i.name} ${i.is_lead ? '<span class="text-xs bg-yellow-100 text-yellow-800 px-2 py-0.5 rounded-full ml-2">Lead</span>' : ''}</p>
                            <p class="text-sm text-gray-500">${i.email}${i.role ? ` • ${i.role}` : ''}</p>
                        </div>
                    </div>
                `).join('') || '<p class="text-gray-500 text-sm">No interviewers assigned</p>'}
            </div>
        </div>
        
        ${panel.skills_evaluated && panel.skills_evaluated.length > 0 ? `
            <div class="mt-6">
                <label class="block text-sm font-medium text-gray-700 mb-2">Skills Evaluated</label>
                <div class="flex flex-wrap gap-2">
                    ${panel.skills_evaluated.map(skill => `
                        <span class="inline-flex items-center px-3 py-1 rounded-full text-sm bg-indigo-100 text-indigo-800">${skill}</span>
                    `).join('')}
                </div>
            </div>
        ` : ''}
    `;
    
    showModal('view-panel-modal');
}

async function deletePanel(panelId) {
    if (!confirm('Are you sure you want to delete this panel?')) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/panels/${panelId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showNotification('Panel deleted successfully', 'success');
            loadPanels();
        } else {
            showNotification('Failed to delete panel', 'error');
        }
    } catch (error) {
        console.error('Error deleting panel:', error);
        showNotification('Error deleting panel', 'error');
    }
}

// ==================== SLOT FUNCTIONS ====================

async function loadSlots() {
    const slotsList = document.getElementById('slots-list');
    
    // Build query params from filters
    const params = new URLSearchParams();
    const panelFilter = document.getElementById('slot-panel-filter')?.value;
    const statusFilter = document.getElementById('slot-status-filter')?.value;
    const dateFrom = document.getElementById('slot-date-from')?.value;
    const dateTo = document.getElementById('slot-date-to')?.value;
    
    if (panelFilter) params.append('panel_id', panelFilter);
    if (statusFilter) params.append('status_filter', statusFilter);
    if (dateFrom) params.append('date_from', dateFrom);
    if (dateTo) params.append('date_to', dateTo);
    
    try {
        const response = await fetch(`${API_BASE_URL}/slots?${params}`);
        if (response.ok) {
            const slots = await response.json();
            if (slots.length === 0) {
                slotsList.innerHTML = `
                    <div class="text-center py-8">
                        <i class="fas fa-clock text-4xl text-gray-300 mb-4"></i>
                        <h3 class="text-lg font-medium text-gray-500 mb-2">No Interview Slots</h3>
                        <p class="text-gray-400 mb-4">Create slots for panels to schedule interviews</p>
                    </div>
                `;
            } else {
                renderSlots(slots);
            }
        } else {
            slotsList.innerHTML = `
                <div class="text-center py-8">
                    <i class="fas fa-exclamation-triangle text-4xl text-red-300 mb-4"></i>
                    <h3 class="text-lg font-medium text-red-500 mb-2">Error Loading Slots</h3>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading slots:', error);
    }
}

function renderSlots(slots) {
    const slotsList = document.getElementById('slots-list');
    
    // Group slots by date
    const groupedSlots = {};
    slots.forEach(slot => {
        const date = slot.date ? slot.date.split('T')[0] : 'Unknown';
        if (!groupedSlots[date]) {
            groupedSlots[date] = [];
        }
        groupedSlots[date].push(slot);
    });
    
    let html = '';
    Object.keys(groupedSlots).sort().forEach(date => {
        html += `
            <div class="mb-6">
                <h3 class="text-lg font-semibold text-gray-800 mb-3">${formatDate(date)}</h3>
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    ${groupedSlots[date].map(slot => `
                        <div class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-all">
                            <div class="flex justify-between items-start">
                                <div>
                                    <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${getStatusColor(slot.status)}">
                                        ${slot.status}
                                    </span>
                                    <p class="text-lg font-medium mt-2">${formatTime(slot.start_time)} - ${formatTime(slot.end_time)}</p>
                                    ${slot.notes ? `<p class="text-sm text-gray-500 mt-1">${slot.notes}</p>` : ''}
                                </div>
                                <div class="flex space-x-1">
                                    ${slot.status === 'available' ? `
                                        <button onclick="blockSlot('${slot.id}')" class="p-1 text-gray-400 hover:text-gray-600" title="Block">
                                            <i class="fas fa-ban"></i>
                                        </button>
                                        <button onclick="deleteSlot('${slot.id}')" class="p-1 text-red-400 hover:text-red-600" title="Delete">
                                            <i class="fas fa-trash"></i>
                                        </button>
                                    ` : ''}
                                    ${slot.status === 'blocked' ? `
                                        <button onclick="unblockSlot('${slot.id}')" class="p-1 text-green-400 hover:text-green-600" title="Unblock">
                                            <i class="fas fa-check"></i>
                                        </button>
                                    ` : ''}
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    });
    
    slotsList.innerHTML = html;
}

function showAddSlotModal() {
    document.getElementById('slot-form').reset();
    populateSlotPanelDropdown('slot-panel');
    showModal('add-slot-modal');
}

function showBulkSlotModal() {
    document.getElementById('bulk-slot-form').reset();
    populateSlotPanelDropdown('bulk-slot-panel');
    showModal('bulk-slot-modal');
}

async function populatePanelDropdowns() {
    try {
        const response = await fetch(`${API_BASE_URL}/panels`);
        if (response.ok) {
            const panels = await response.json();
            
            // Populate filter dropdown
            const filterDropdown = document.getElementById('slot-panel-filter');
            if (filterDropdown) {
                filterDropdown.innerHTML = '<option value="">All Panels</option>' +
                    panels.map(p => `<option value="${p.id}">${p.name}</option>`).join('');
            }
        }
    } catch (error) {
        console.error('Error populating panel dropdowns:', error);
    }
}

async function populateSlotPanelDropdown(elementId) {
    try {
        const response = await fetch(`${API_BASE_URL}/panels`);
        if (response.ok) {
            const panels = await response.json();
            const dropdown = document.getElementById(elementId);
            if (dropdown) {
                dropdown.innerHTML = '<option value="">Select Panel</option>' +
                    panels.map(p => `<option value="${p.id}">${p.name} (${p.level})</option>`).join('');
            }
        }
    } catch (error) {
        console.error('Error populating panel dropdown:', error);
    }
}

// Slot form handler
document.getElementById('slot-form')?.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const date = document.getElementById('slot-date').value;
    const startTime = document.getElementById('slot-start').value;
    const endTime = document.getElementById('slot-end').value;
    
    const slotData = {
        panel_id: document.getElementById('slot-panel').value,
        date: `${date}T00:00:00`,
        start_time: `${date}T${startTime}:00`,
        end_time: `${date}T${endTime}:00`,
        notes: document.getElementById('slot-notes').value || null
    };
    
    try {
        showNotification('Adding slot...', 'info');
        
        const response = await fetch(`${API_BASE_URL}/slots`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(slotData)
        });
        
        if (response.ok) {
            showNotification('Slot added successfully! ⏰', 'success');
            closeModal('add-slot-modal');
            loadSlots();
        } else {
            const error = await response.json();
            showNotification(`Failed to add slot: ${error.detail}`, 'error');
        }
    } catch (error) {
        console.error('Error adding slot:', error);
        showNotification('Failed to add slot', 'error');
    }
});

// Bulk slot form handler
document.getElementById('bulk-slot-form')?.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const dateFrom = new Date(document.getElementById('bulk-date-from').value);
    const dateTo = new Date(document.getElementById('bulk-date-to').value);
    
    // Generate dates array
    const dates = [];
    let currentDate = new Date(dateFrom);
    while (currentDate <= dateTo) {
        // Skip weekends (optional)
        if (currentDate.getDay() !== 0 && currentDate.getDay() !== 6) {
            dates.push(currentDate.toISOString().split('T')[0]);
        }
        currentDate.setDate(currentDate.getDate() + 1);
    }
    
    const bulkData = {
        panel_id: document.getElementById('bulk-slot-panel').value,
        dates: dates,
        start_hour: parseInt(document.getElementById('bulk-start-hour').value),
        end_hour: parseInt(document.getElementById('bulk-end-hour').value),
        slot_duration_minutes: parseInt(document.getElementById('bulk-duration').value),
        break_minutes: parseInt(document.getElementById('bulk-break').value)
    };
    
    try {
        showNotification('Generating slots...', 'info');
        
        const response = await fetch(`${API_BASE_URL}/slots/bulk`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(bulkData)
        });
        
        if (response.ok) {
            const result = await response.json();
            showNotification(`${result.slots_created} slots created! 📅`, 'success');
            closeModal('bulk-slot-modal');
            loadSlots();
        } else {
            const error = await response.json();
            showNotification(`Failed to generate slots: ${error.detail}`, 'error');
        }
    } catch (error) {
        console.error('Error generating slots:', error);
        showNotification('Failed to generate slots', 'error');
    }
});

async function blockSlot(slotId) {
    try {
        const response = await fetch(`${API_BASE_URL}/slots/${slotId}/status?new_status=blocked`, {
            method: 'PUT'
        });
        if (response.ok) {
            showNotification('Slot blocked', 'success');
            loadSlots();
        }
    } catch (error) {
        showNotification('Error blocking slot', 'error');
    }
}

async function unblockSlot(slotId) {
    try {
        const response = await fetch(`${API_BASE_URL}/slots/${slotId}/status?new_status=available`, {
            method: 'PUT'
        });
        if (response.ok) {
            showNotification('Slot unblocked', 'success');
            loadSlots();
        }
    } catch (error) {
        showNotification('Error unblocking slot', 'error');
    }
}

async function deleteSlot(slotId) {
    if (!confirm('Delete this slot?')) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/slots/${slotId}`, {
            method: 'DELETE'
        });
        if (response.ok) {
            showNotification('Slot deleted', 'success');
            loadSlots();
        }
    } catch (error) {
        showNotification('Error deleting slot', 'error');
    }
}

// ==================== INTERVIEW SCHEDULING FUNCTIONS ====================

async function loadInterviews() {
    const interviewsList = document.getElementById('interviews-list');
    
    const params = new URLSearchParams();
    const levelFilter = document.getElementById('interview-level-filter')?.value;
    const statusFilter = document.getElementById('interview-status-filter')?.value;
    
    if (levelFilter) params.append('level', levelFilter);
    if (statusFilter) params.append('status_filter', statusFilter);
    
    try {
        const response = await fetch(`${API_BASE_URL}/interviews?${params}`);
        if (response.ok) {
            const interviews = await response.json();
            if (interviews.length === 0) {
                interviewsList.innerHTML = `
                    <div class="text-center py-8">
                        <i class="fas fa-calendar-check text-4xl text-gray-300 mb-4"></i>
                        <h3 class="text-lg font-medium text-gray-500 mb-2">No Scheduled Interviews</h3>
                        <p class="text-gray-400 mb-4">Schedule your first interview to get started</p>
                        <button onclick="showScheduleInterviewModal()" class="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg transition-all">
                            <i class="fas fa-calendar-plus"></i> Schedule Interview
                        </button>
                    </div>
                `;
            } else {
                renderInterviews(interviews);
            }
        }
    } catch (error) {
        console.error('Error loading interviews:', error);
    }
}

function renderInterviews(interviews) {
    const interviewsList = document.getElementById('interviews-list');
    
    const levelLabels = {
        'screening': 'Screening',
        'technical_1': 'Technical Round 1',
        'technical_2': 'Technical Round 2',
        'managerial': 'Managerial',
        'hr': 'HR',
        'final': 'Final'
    };
    
    interviewsList.innerHTML = interviews.map(interview => `
        <div class="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-all">
            <div class="flex items-start justify-between">
                <div>
                    <div class="flex items-center space-x-3">
                        <h3 class="text-lg font-medium text-gray-900">${interview.candidate_name}</h3>
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(interview.status)}">
                            ${interview.status}
                        </span>
                    </div>
                    <p class="text-gray-600 mt-1">For: ${interview.job_title}</p>
                    <div class="flex items-center space-x-4 mt-3 text-sm text-gray-600">
                        <span><i class="fas fa-layer-group mr-1"></i> ${levelLabels[interview.level] || interview.level} (Round ${interview.round_number})</span>
                        <span><i class="fas fa-users mr-1"></i> ${interview.panel_name}</span>
                    </div>
                    <div class="flex items-center space-x-4 mt-2 text-sm text-gray-600">
                        <span><i class="fas fa-calendar mr-1"></i> ${formatDate(interview.scheduled_date)}</span>
                        <span><i class="fas fa-clock mr-1"></i> ${formatTime(interview.scheduled_start)} - ${formatTime(interview.scheduled_end)}</span>
                        <span><i class="fas fa-${interview.interview_mode === 'video' ? 'video' : interview.interview_mode === 'phone' ? 'phone' : 'building'} mr-1"></i> ${interview.interview_mode}</span>
                    </div>
                    ${interview.overall_score ? `
                        <div class="mt-2">
                            <span class="text-sm font-medium">Score: ${interview.overall_score.toFixed(1)}/10</span>
                            ${interview.recommendation ? `<span class="ml-2 text-sm text-gray-500">• ${interview.recommendation}</span>` : ''}
                        </div>
                    ` : ''}
                </div>
                <div class="flex flex-col space-y-2">
                    <button onclick="viewInterview('${interview.id}')" class="px-3 py-1 bg-blue-50 text-blue-600 rounded-lg text-sm hover:bg-blue-100">
                        <i class="fas fa-eye"></i> View
                    </button>
                    ${interview.status === 'scheduled' ? `
                        <button onclick="addFeedback('${interview.id}')" class="px-3 py-1 bg-purple-50 text-purple-600 rounded-lg text-sm hover:bg-purple-100">
                            <i class="fas fa-comment"></i> Feedback
                        </button>
                        <button onclick="completeInterview('${interview.id}')" class="px-3 py-1 bg-green-50 text-green-600 rounded-lg text-sm hover:bg-green-100">
                            <i class="fas fa-check"></i> Complete
                        </button>
                        <button onclick="cancelInterview('${interview.id}')" class="px-3 py-1 bg-red-50 text-red-600 rounded-lg text-sm hover:bg-red-100">
                            <i class="fas fa-times"></i> Cancel
                        </button>
                    ` : ''}
                </div>
            </div>
        </div>
    `).join('');
}

async function showScheduleInterviewModal() {
    document.getElementById('schedule-interview-form').reset();
    
    // Populate dropdowns
    await Promise.all([
        populateCandidateDropdown(),
        populateJobDropdown(),
        populateInterviewPanelDropdown()
    ]);
    
    showModal('schedule-interview-modal');
}

async function populateCandidateDropdown() {
    try {
        const response = await fetch(`${API_BASE_URL}/candidates`);
        if (response.ok) {
            const candidates = await response.json();
            const dropdown = document.getElementById('interview-candidate');
            dropdown.innerHTML = '<option value="">Select Candidate</option>' +
                candidates.map(c => `<option value="${c.id}">${c.full_name} (${c.email})</option>`).join('');
        }
    } catch (error) {
        console.error('Error loading candidates:', error);
    }
}

async function populateJobDropdown() {
    try {
        const response = await fetch(`${API_BASE_URL}/jobs`);
        if (response.ok) {
            const jobs = await response.json();
            const dropdown = document.getElementById('interview-job');
            dropdown.innerHTML = '<option value="">Select Job</option>' +
                jobs.map(j => `<option value="${j.id}">${j.title} (${j.department})</option>`).join('');
        }
    } catch (error) {
        console.error('Error loading jobs:', error);
    }
}

async function populateInterviewPanelDropdown() {
    try {
        const response = await fetch(`${API_BASE_URL}/panels`);
        if (response.ok) {
            const panels = await response.json();
            const dropdown = document.getElementById('interview-panel');
            dropdown.innerHTML = '<option value="">Select Panel</option>' +
                panels.map(p => `<option value="${p.id}">${p.name} (${p.level})</option>`).join('');
        }
    } catch (error) {
        console.error('Error loading panels:', error);
    }
}

async function loadPanelSlots() {
    const panelId = document.getElementById('interview-panel').value;
    const slotSection = document.getElementById('available-slots-section');
    const slotDropdown = document.getElementById('interview-slot');
    
    if (!panelId) {
        slotSection.classList.add('hidden');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/slots?panel_id=${panelId}&status_filter=available`);
        if (response.ok) {
            const slots = await response.json();
            if (slots.length > 0) {
                slotSection.classList.remove('hidden');
                slotDropdown.innerHTML = '<option value="">Select Available Slot (Optional)</option>' +
                    slots.map(s => `<option value="${s.id}">${formatDate(s.date)} ${formatTime(s.start_time)} - ${formatTime(s.end_time)}</option>`).join('');
            } else {
                slotSection.classList.add('hidden');
            }
        }
    } catch (error) {
        console.error('Error loading panel slots:', error);
    }
}

// Schedule interview form handler
document.getElementById('schedule-interview-form')?.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const slotId = document.getElementById('interview-slot').value;
    const date = document.getElementById('interview-date').value;
    const startTime = document.getElementById('interview-start').value;
    const endTime = document.getElementById('interview-end').value;
    
    // Validate that either slot is selected or manual date/time is provided
    if (!slotId && (!date || !startTime || !endTime)) {
        showNotification('Please select a slot or provide date and time', 'error');
        return;
    }
    
    const interviewData = {
        candidate_id: document.getElementById('interview-candidate').value,
        job_id: document.getElementById('interview-job').value,
        panel_id: document.getElementById('interview-panel').value,
        level: document.getElementById('interview-level').value,
        round_number: 1,
        scheduled_date: date ? `${date}T00:00:00` : null,
        scheduled_start: date && startTime ? `${date}T${startTime}:00` : null,
        scheduled_end: date && endTime ? `${date}T${endTime}:00` : null,
        interview_mode: document.getElementById('interview-mode').value,
        meeting_link: document.getElementById('interview-meeting-link').value || null,
        location: document.getElementById('interview-location').value || null
    };
    
    if (slotId) {
        interviewData.slot_id = slotId;
        // Get slot details if using slot
        try {
            const slotResponse = await fetch(`${API_BASE_URL}/slots/${slotId}`);
            if (slotResponse.ok) {
                const slot = await slotResponse.json();
                interviewData.scheduled_date = slot.date;
                interviewData.scheduled_start = slot.start_time;
                interviewData.scheduled_end = slot.end_time;
            }
        } catch (error) {
            console.error('Error getting slot details:', error);
        }
    }
    
    try {
        showNotification('Scheduling interview...', 'info');
        
        const response = await fetch(`${API_BASE_URL}/interviews`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(interviewData)
        });
        
        if (response.ok) {
            showNotification('Interview scheduled successfully! 📅', 'success');
            closeModal('schedule-interview-modal');
            loadInterviews();
        } else {
            const error = await response.json();
            showNotification(`Failed to schedule interview: ${error.detail}`, 'error');
        }
    } catch (error) {
        console.error('Error scheduling interview:', error);
        showNotification('Failed to schedule interview', 'error');
    }
});

async function viewInterview(interviewId) {
    try {
        const response = await fetch(`${API_BASE_URL}/interviews/${interviewId}`);
        if (response.ok) {
            const interview = await response.json();
            showInterviewDetailsModal(interview);
        } else {
            showNotification('Could not load interview details', 'error');
        }
    } catch (error) {
        console.error('Error viewing interview:', error);
        showNotification('Error loading interview details', 'error');
    }
}

function showInterviewDetailsModal(interview) {
    const levelLabels = {
        'screening': 'Screening',
        'technical_1': 'Technical Round 1',
        'technical_2': 'Technical Round 2',
        'managerial': 'Managerial',
        'hr': 'HR',
        'final': 'Final'
    };
    
    const content = document.getElementById('interview-details-content');
    content.innerHTML = `
        <div class="grid grid-cols-2 gap-6">
            <div class="col-span-2 bg-gray-50 rounded-lg p-4">
                <div class="flex items-center justify-between">
                    <div>
                        <h3 class="text-lg font-semibold">${interview.candidate?.name || 'Unknown'}</h3>
                        <p class="text-sm text-gray-600">${interview.candidate?.email || ''}</p>
                    </div>
                    <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(interview.status)}">
                        ${interview.status}
                    </span>
                </div>
            </div>
            
            <div>
                <label class="block text-sm font-medium text-gray-700">Job Position</label>
                <p class="mt-1 text-sm text-gray-900">${interview.job?.title || 'N/A'}</p>
                <p class="text-xs text-gray-500">${interview.job?.department || ''}</p>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700">Interview Level</label>
                <p class="mt-1 text-sm text-gray-900">${levelLabels[interview.level] || interview.level} (Round ${interview.round_number})</p>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700">Panel</label>
                <p class="mt-1 text-sm text-gray-900">${interview.panel?.name || 'N/A'}</p>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700">Mode</label>
                <p class="mt-1 text-sm text-gray-900">${interview.interview_mode}</p>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700">Date & Time</label>
                <p class="mt-1 text-sm text-gray-900">${formatDate(interview.scheduled_date)}</p>
                <p class="text-xs text-gray-500">${formatTime(interview.scheduled_start)} - ${formatTime(interview.scheduled_end)}</p>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700">${interview.interview_mode === 'video' ? 'Meeting Link' : 'Location'}</label>
                <p class="mt-1 text-sm text-gray-900">${interview.meeting_link || interview.location || 'N/A'}</p>
            </div>
        </div>
        
        ${interview.overall_score ? `
            <div class="mt-6 bg-blue-50 rounded-lg p-4">
                <h4 class="font-semibold text-blue-900">Overall Assessment</h4>
                <div class="mt-2 flex items-center space-x-4">
                    <span class="text-2xl font-bold text-blue-600">${interview.overall_score.toFixed(1)}/10</span>
                    ${interview.recommendation ? `<span class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">${interview.recommendation}</span>` : ''}
                </div>
            </div>
        ` : ''}
        
        ${(interview.panel?.interviewers || []).length > 0 ? `
            <div class="mt-6">
                <h4 class="font-semibold text-gray-900 mb-3">Panel Members</h4>
                <div class="grid grid-cols-2 gap-3">
                    ${interview.panel.interviewers.map(i => `
                        <div class="flex items-center p-3 bg-gray-50 rounded-lg">
                            <div class="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center mr-3">
                                <i class="fas fa-user text-indigo-600 text-sm"></i>
                            </div>
                            <div>
                                <p class="font-medium text-sm">${i.name}</p>
                                <p class="text-xs text-gray-500">${i.role || 'Interviewer'}</p>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        ` : ''}
        
        ${(interview.feedbacks || []).length > 0 ? `
            <div class="mt-6">
                <h4 class="font-semibold text-gray-900 mb-3">Feedback</h4>
                <div class="space-y-3">
                    ${interview.feedbacks.map(f => `
                        <div class="border border-gray-200 rounded-lg p-4">
                            <div class="flex justify-between items-start">
                                <div>
                                    <p class="font-medium">${f.interviewer_name}</p>
                                    <p class="text-xs text-gray-500">${f.interviewer_role || ''}</p>
                                </div>
                                <span class="text-lg font-bold text-blue-600">${f.overall_score}/10</span>
                            </div>
                            ${f.strengths ? `<p class="mt-2 text-sm"><strong>Strengths:</strong> ${f.strengths}</p>` : ''}
                            ${f.weaknesses ? `<p class="mt-1 text-sm"><strong>Areas to improve:</strong> ${f.weaknesses}</p>` : ''}
                            ${f.comments ? `<p class="mt-1 text-sm text-gray-600">${f.comments}</p>` : ''}
                            <span class="inline-block mt-2 px-2 py-0.5 bg-gray-100 text-gray-700 text-xs rounded">${f.recommendation || 'No recommendation'}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        ` : ''}
    `;
    
    showModal('view-interview-modal');
}

function addFeedback(interviewId) {
    document.getElementById('feedback-interview-id').value = interviewId;
    document.getElementById('feedback-form').reset();
    document.getElementById('feedback-interview-id').value = interviewId; // Re-set after reset
    showModal('add-feedback-modal');
}

// Feedback form handler
document.getElementById('feedback-form')?.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const interviewId = document.getElementById('feedback-interview-id').value;
    const feedbackData = {
        interviewer_id: crypto.randomUUID(),
        interviewer_name: document.getElementById('feedback-interviewer-name').value,
        interviewer_role: document.getElementById('feedback-interviewer-role').value || null,
        overall_score: parseFloat(document.getElementById('feedback-score').value),
        strengths: document.getElementById('feedback-strengths').value || null,
        weaknesses: document.getElementById('feedback-weaknesses').value || null,
        comments: document.getElementById('feedback-comments').value || null,
        recommendation: document.getElementById('feedback-recommendation').value
    };
    
    try {
        showNotification('Submitting feedback...', 'info');
        
        const response = await fetch(`${API_BASE_URL}/interviews/${interviewId}/feedback`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(feedbackData)
        });
        
        if (response.ok) {
            showNotification('Feedback submitted successfully! 💬', 'success');
            closeModal('add-feedback-modal');
            loadInterviews();
        } else {
            const error = await response.json();
            showNotification(`Failed to submit feedback: ${error.detail}`, 'error');
        }
    } catch (error) {
        console.error('Error submitting feedback:', error);
        showNotification('Failed to submit feedback', 'error');
    }
});

async function completeInterview(interviewId) {
    const recommendation = prompt('Enter recommendation (proceed, reject, hold, hire):');
    
    if (!recommendation) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/interviews/${interviewId}/complete?recommendation=${recommendation}`, {
            method: 'PUT'
        });
        
        if (response.ok) {
            showNotification('Interview marked as completed! ✅', 'success');
            loadInterviews();
        } else {
            showNotification('Failed to complete interview', 'error');
        }
    } catch (error) {
        console.error('Error completing interview:', error);
        showNotification('Error completing interview', 'error');
    }
}

async function cancelInterview(interviewId) {
    const reason = prompt('Enter cancellation reason (optional):');
    
    try {
        const url = reason 
            ? `${API_BASE_URL}/interviews/${interviewId}/cancel?reason=${encodeURIComponent(reason)}`
            : `${API_BASE_URL}/interviews/${interviewId}/cancel`;
            
        const response = await fetch(url, { method: 'PUT' });
        
        if (response.ok) {
            showNotification('Interview cancelled', 'success');
            loadInterviews();
        } else {
            showNotification('Failed to cancel interview', 'error');
        }
    } catch (error) {
        console.error('Error cancelling interview:', error);
        showNotification('Error cancelling interview', 'error');
    }
}

// ==================== UTILITY FUNCTIONS ====================

function formatDate(dateStr) {
    if (!dateStr) return 'N/A';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' });
}

function formatTime(timeStr) {
    if (!timeStr) return 'N/A';
    const date = new Date(timeStr);
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    if (e.ctrlKey && e.key === '1') {
        e.preventDefault();
        showSection('candidates');
    } else if (e.ctrlKey && e.key === '2') {
        e.preventDefault();
        showSection('jobs');
    } else if (e.ctrlKey && e.key === '3') {
        e.preventDefault();
        showSection('interviews');
    } else if (e.ctrlKey && e.key === '4') {
        e.preventDefault();
        showSection('applications');
    }
});

// Add some demo data for visualization
function addDemoData() {
    // This would populate the dashboard with sample data for demonstration
    console.log('Demo data would be added here');
}

// =============================================================================
// DOCUMENT MANAGEMENT FUNCTIONS
// =============================================================================

// Store current candidate ID for document operations
let currentDocumentCandidateId = null;
let currentDocumentCandidateName = null;
let candidateDocumentsCache = [];

// Show candidate documents modal
async function showCandidateDocuments(candidateId, candidateName) {
    currentDocumentCandidateId = candidateId;
    currentDocumentCandidateName = candidateName;
    
    document.getElementById('candidate-docs-info').innerHTML = `
        <span class="font-semibold">${candidateName}</span>
    `;
    
    // Show modal
    document.getElementById('candidate-documents-modal').classList.remove('hidden');
    document.getElementById('candidate-documents-modal').classList.add('flex');
    
    // Load documents
    await loadCandidateDocuments(candidateId);
}

// Load documents for a candidate
async function loadCandidateDocuments(candidateId) {
    const docsList = document.getElementById('candidate-documents-list');
    docsList.innerHTML = '<div class="text-center py-8"><i class="fas fa-spinner fa-spin text-2xl text-gray-400"></i></div>';
    
    try {
        const response = await fetch(`${API_BASE}/candidates/${candidateId}/documents`);
        if (!response.ok) throw new Error('Failed to load documents');
        
        const documents = await response.json();
        candidateDocumentsCache = documents;
        
        renderCandidateDocuments(documents);
    } catch (error) {
        console.error('Error loading documents:', error);
        docsList.innerHTML = `
            <div class="text-center py-8">
                <i class="fas fa-exclamation-circle text-4xl text-red-300 mb-4"></i>
                <h3 class="text-lg font-medium text-gray-500">Error Loading Documents</h3>
                <p class="text-gray-400">${error.message}</p>
            </div>
        `;
    }
}

// Render candidate documents list
function renderCandidateDocuments(documents) {
    const docsList = document.getElementById('candidate-documents-list');
    
    if (documents.length === 0) {
        docsList.innerHTML = `
            <div class="text-center py-8">
                <i class="fas fa-folder-open text-4xl text-gray-300 mb-4"></i>
                <h3 class="text-lg font-medium text-gray-500 mb-2">No Documents</h3>
                <p class="text-gray-400">Upload documents to get started</p>
            </div>
        `;
        return;
    }
    
    const typeIcons = {
        'resume': 'fa-file-alt',
        'cover_letter': 'fa-envelope-open-text',
        'identity_proof': 'fa-id-card',
        'address_proof': 'fa-home',
        'education_certificate': 'fa-graduation-cap',
        'marksheet': 'fa-scroll',
        'degree_certificate': 'fa-certificate',
        'experience_letter': 'fa-briefcase',
        'relieving_letter': 'fa-file-contract',
        'salary_slip': 'fa-money-bill-wave',
        'offer_letter': 'fa-file-signature',
        'portfolio': 'fa-images',
        'certification': 'fa-award',
        'reference_letter': 'fa-user-tie',
        'background_check': 'fa-search',
        'medical_certificate': 'fa-notes-medical',
        'other': 'fa-file'
    };
    
    const statusColors = {
        'pending': 'bg-yellow-100 text-yellow-800',
        'verified': 'bg-green-100 text-green-800',
        'rejected': 'bg-red-100 text-red-800',
        'under_review': 'bg-blue-100 text-blue-800',
        'expired': 'bg-gray-100 text-gray-800'
    };
    
    docsList.innerHTML = documents.map(doc => `
        <div class="bg-gray-50 rounded-lg p-4 hover:bg-gray-100 transition-all">
            <div class="flex items-start justify-between">
                <div class="flex items-start">
                    <div class="w-12 h-12 bg-cyan-100 rounded-lg flex items-center justify-center mr-4">
                        <i class="fas ${typeIcons[doc.document_type] || 'fa-file'} text-cyan-600 text-xl"></i>
                    </div>
                    <div>
                        <h4 class="font-semibold text-gray-900">${doc.title}</h4>
                        <p class="text-sm text-gray-500">${formatDocumentType(doc.document_type)}${doc.document_subtype ? ' - ' + doc.document_subtype : ''}</p>
                        <div class="flex items-center gap-3 mt-2 text-xs text-gray-500">
                            <span><i class="fas fa-file mr-1"></i>${doc.original_filename}</span>
                            <span><i class="fas fa-hdd mr-1"></i>${doc.file_size}</span>
                            ${doc.is_expired ? '<span class="text-red-500"><i class="fas fa-exclamation-triangle mr-1"></i>Expired</span>' : ''}
                        </div>
                        ${doc.institution_name ? `<p class="text-xs text-gray-500 mt-1"><i class="fas fa-university mr-1"></i>${doc.institution_name}${doc.year_of_passing ? ' (' + doc.year_of_passing + ')' : ''}</p>` : ''}
                        ${doc.company_name ? `<p class="text-xs text-gray-500 mt-1"><i class="fas fa-building mr-1"></i>${doc.company_name}${doc.designation ? ' - ' + doc.designation : ''}</p>` : ''}
                    </div>
                </div>
                <div class="flex flex-col items-end gap-2">
                    <span class="px-2 py-1 rounded-full text-xs font-medium ${statusColors[doc.status] || 'bg-gray-100 text-gray-800'}">
                        ${doc.status.charAt(0).toUpperCase() + doc.status.slice(1)}
                    </span>
                    <div class="flex gap-1">
                        <button onclick="viewDocument('${doc.id}')" class="p-2 text-blue-600 hover:bg-blue-50 rounded" title="View Details">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button onclick="downloadDocument('${doc.id}', '${doc.original_filename}')" class="p-2 text-green-600 hover:bg-green-50 rounded" title="Download">
                            <i class="fas fa-download"></i>
                        </button>
                        <button onclick="previewDocument('${doc.id}', '${doc.mime_type}')" class="p-2 text-purple-600 hover:bg-purple-50 rounded" title="Preview">
                            <i class="fas fa-external-link-alt"></i>
                        </button>
                        <button onclick="showVerifyDocumentModal('${doc.id}')" class="p-2 text-orange-600 hover:bg-orange-50 rounded" title="Verify">
                            <i class="fas fa-check-circle"></i>
                        </button>
                        <button onclick="deleteDocument('${doc.id}')" class="p-2 text-red-600 hover:bg-red-50 rounded" title="Delete">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

// Filter candidate documents
function filterCandidateDocuments() {
    const typeFilter = document.getElementById('doc-type-filter').value;
    const statusFilter = document.getElementById('doc-status-filter').value;
    
    let filtered = candidateDocumentsCache;
    
    if (typeFilter) {
        filtered = filtered.filter(d => d.document_type === typeFilter);
    }
    if (statusFilter) {
        filtered = filtered.filter(d => d.status === statusFilter);
    }
    
    renderCandidateDocuments(filtered);
}

// Format document type for display
function formatDocumentType(type) {
    const typeLabels = {
        'resume': 'Resume/CV',
        'cover_letter': 'Cover Letter',
        'identity_proof': 'Identity Proof',
        'address_proof': 'Address Proof',
        'education_certificate': 'Education Certificate',
        'marksheet': 'Marksheet',
        'degree_certificate': 'Degree Certificate',
        'experience_letter': 'Experience Letter',
        'relieving_letter': 'Relieving Letter',
        'salary_slip': 'Salary Slip',
        'offer_letter': 'Offer Letter',
        'portfolio': 'Portfolio',
        'certification': 'Certification',
        'reference_letter': 'Reference Letter',
        'background_check': 'Background Check',
        'medical_certificate': 'Medical Certificate',
        'other': 'Other'
    };
    return typeLabels[type] || type;
}

// Show upload document modal
function showUploadDocumentModal() {
    document.getElementById('doc-candidate-id').value = currentDocumentCandidateId;
    document.getElementById('upload-document-modal').classList.remove('hidden');
    document.getElementById('upload-document-modal').classList.add('flex');
    
    // Reset form
    document.getElementById('document-upload-form').reset();
    document.getElementById('doc-identity-fields').classList.add('hidden');
    document.getElementById('doc-education-fields').classList.add('hidden');
    document.getElementById('doc-experience-fields').classList.add('hidden');
}

// Handle document type change - show/hide conditional fields
document.addEventListener('DOMContentLoaded', function() {
    const docTypeSelect = document.getElementById('doc-type');
    if (docTypeSelect) {
        docTypeSelect.addEventListener('change', function() {
            const type = this.value;
            
            // Hide all conditional fields first
            document.getElementById('doc-identity-fields').classList.add('hidden');
            document.getElementById('doc-education-fields').classList.add('hidden');
            document.getElementById('doc-experience-fields').classList.add('hidden');
            
            // Show relevant fields based on type
            if (['identity_proof', 'address_proof'].includes(type)) {
                document.getElementById('doc-identity-fields').classList.remove('hidden');
            } else if (['education_certificate', 'marksheet', 'degree_certificate'].includes(type)) {
                document.getElementById('doc-education-fields').classList.remove('hidden');
            } else if (['experience_letter', 'relieving_letter', 'salary_slip', 'offer_letter'].includes(type)) {
                document.getElementById('doc-experience-fields').classList.remove('hidden');
            }
        });
    }
    
    // Verification status change handler
    const verifyStatus = document.getElementById('verify-status');
    if (verifyStatus) {
        verifyStatus.addEventListener('change', function() {
            const rejectionField = document.getElementById('rejection-reason-field');
            if (this.value === 'rejected') {
                rejectionField.classList.remove('hidden');
            } else {
                rejectionField.classList.add('hidden');
            }
        });
    }
});

// Handle document upload form submission
document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('document-upload-form');
    if (uploadForm) {
        uploadForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const candidateId = document.getElementById('doc-candidate-id').value;
            const formData = new FormData();
            
            formData.append('document_type', document.getElementById('doc-type').value);
            formData.append('title', document.getElementById('doc-title').value);
            formData.append('file', document.getElementById('doc-file').files[0]);
            
            // Optional fields
            if (document.getElementById('doc-subtype').value) {
                formData.append('document_subtype', document.getElementById('doc-subtype').value);
            }
            if (document.getElementById('doc-description').value) {
                formData.append('description', document.getElementById('doc-description').value);
            }
            if (document.getElementById('doc-access').value) {
                formData.append('access_level', document.getElementById('doc-access').value);
            }
            if (document.getElementById('doc-tags').value) {
                formData.append('tags', document.getElementById('doc-tags').value);
            }
            
            // Identity document fields
            if (document.getElementById('doc-number').value) {
                formData.append('document_number', document.getElementById('doc-number').value);
            }
            if (document.getElementById('doc-issuing-authority').value) {
                formData.append('issuing_authority', document.getElementById('doc-issuing-authority').value);
            }
            if (document.getElementById('doc-issue-date').value) {
                formData.append('issue_date', document.getElementById('doc-issue-date').value);
            }
            if (document.getElementById('doc-expiry-date').value) {
                formData.append('expiry_date', document.getElementById('doc-expiry-date').value);
            }
            
            // Education document fields
            if (document.getElementById('doc-institution').value) {
                formData.append('institution_name', document.getElementById('doc-institution').value);
            }
            if (document.getElementById('doc-year').value) {
                formData.append('year_of_passing', document.getElementById('doc-year').value);
            }
            if (document.getElementById('doc-grade').value) {
                formData.append('grade_percentage', document.getElementById('doc-grade').value);
            }
            
            // Experience document fields
            if (document.getElementById('doc-company').value) {
                formData.append('company_name', document.getElementById('doc-company').value);
            }
            if (document.getElementById('doc-designation').value) {
                formData.append('designation', document.getElementById('doc-designation').value);
            }
            if (document.getElementById('doc-period-from').value) {
                formData.append('period_from', document.getElementById('doc-period-from').value);
            }
            if (document.getElementById('doc-period-to').value) {
                formData.append('period_to', document.getElementById('doc-period-to').value);
            }
            
            try {
                const response = await fetch(`${API_BASE}/candidates/${candidateId}/documents`, {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    showNotification('Document uploaded successfully!', 'success');
                    closeModal('upload-document-modal');
                    await loadCandidateDocuments(candidateId);
                } else {
                    throw new Error(result.detail || 'Failed to upload document');
                }
            } catch (error) {
                console.error('Error uploading document:', error);
                showNotification('Error uploading document: ' + error.message, 'error');
            }
        });
    }
});

// View document details
async function viewDocument(documentId) {
    try {
        const response = await fetch(`${API_BASE}/documents/${documentId}`);
        if (!response.ok) throw new Error('Failed to load document details');
        
        const doc = await response.json();
        
        document.getElementById('document-details-content').innerHTML = `
            <div class="grid grid-cols-2 gap-4">
                <div class="col-span-2 bg-cyan-50 p-4 rounded-lg">
                    <h3 class="font-semibold text-cyan-800 mb-2">${doc.title}</h3>
                    <p class="text-sm text-cyan-600">${formatDocumentType(doc.document_type)}${doc.document_subtype ? ' - ' + doc.document_subtype : ''}</p>
                </div>
                
                <div class="space-y-2">
                    <p class="text-sm"><span class="font-medium text-gray-600">Candidate:</span> ${doc.candidate_name}</p>
                    <p class="text-sm"><span class="font-medium text-gray-600">Original File:</span> ${doc.original_filename}</p>
                    <p class="text-sm"><span class="font-medium text-gray-600">File Size:</span> ${doc.file_size}</p>
                    <p class="text-sm"><span class="font-medium text-gray-600">Type:</span> ${doc.mime_type}</p>
                </div>
                
                <div class="space-y-2">
                    <p class="text-sm"><span class="font-medium text-gray-600">Status:</span> 
                        <span class="px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(doc.status)}">${doc.status}</span>
                    </p>
                    <p class="text-sm"><span class="font-medium text-gray-600">Access Level:</span> ${doc.access_level}</p>
                    <p class="text-sm"><span class="font-medium text-gray-600">Downloads:</span> ${doc.download_count}</p>
                    <p class="text-sm"><span class="font-medium text-gray-600">Uploaded:</span> ${formatDate(doc.created_at)}</p>
                </div>
                
                ${doc.description ? `<div class="col-span-2"><p class="text-sm"><span class="font-medium text-gray-600">Description:</span> ${doc.description}</p></div>` : ''}
                
                ${doc.document_number ? `
                <div class="col-span-2 bg-blue-50 p-4 rounded-lg">
                    <h4 class="font-medium text-blue-800 mb-2">Document Details</h4>
                    <div class="grid grid-cols-2 gap-2 text-sm">
                        <p><span class="text-gray-600">Number:</span> ${doc.document_number}</p>
                        ${doc.issuing_authority ? `<p><span class="text-gray-600">Issuing Authority:</span> ${doc.issuing_authority}</p>` : ''}
                        ${doc.issue_date ? `<p><span class="text-gray-600">Issue Date:</span> ${formatDate(doc.issue_date)}</p>` : ''}
                        ${doc.expiry_date ? `<p><span class="text-gray-600">Expiry Date:</span> ${formatDate(doc.expiry_date)} ${doc.is_expired ? '<span class="text-red-500">(Expired)</span>' : ''}</p>` : ''}
                    </div>
                </div>
                ` : ''}
                
                ${doc.institution_name ? `
                <div class="col-span-2 bg-green-50 p-4 rounded-lg">
                    <h4 class="font-medium text-green-800 mb-2">Education Details</h4>
                    <div class="grid grid-cols-2 gap-2 text-sm">
                        <p><span class="text-gray-600">Institution:</span> ${doc.institution_name}</p>
                        ${doc.year_of_passing ? `<p><span class="text-gray-600">Year:</span> ${doc.year_of_passing}</p>` : ''}
                        ${doc.grade_percentage ? `<p><span class="text-gray-600">Grade:</span> ${doc.grade_percentage}</p>` : ''}
                    </div>
                </div>
                ` : ''}
                
                ${doc.company_name ? `
                <div class="col-span-2 bg-purple-50 p-4 rounded-lg">
                    <h4 class="font-medium text-purple-800 mb-2">Employment Details</h4>
                    <div class="grid grid-cols-2 gap-2 text-sm">
                        <p><span class="text-gray-600">Company:</span> ${doc.company_name}</p>
                        ${doc.designation ? `<p><span class="text-gray-600">Designation:</span> ${doc.designation}</p>` : ''}
                        ${doc.period_from ? `<p><span class="text-gray-600">From:</span> ${formatDate(doc.period_from)}</p>` : ''}
                        ${doc.period_to ? `<p><span class="text-gray-600">To:</span> ${formatDate(doc.period_to)}</p>` : ''}
                    </div>
                </div>
                ` : ''}
                
                ${doc.verification_notes || doc.verified_by ? `
                <div class="col-span-2 bg-yellow-50 p-4 rounded-lg">
                    <h4 class="font-medium text-yellow-800 mb-2">Verification Info</h4>
                    <div class="text-sm">
                        ${doc.verified_by ? `<p><span class="text-gray-600">Verified By:</span> ${doc.verified_by}</p>` : ''}
                        ${doc.verified_at ? `<p><span class="text-gray-600">Verified At:</span> ${formatDate(doc.verified_at)}</p>` : ''}
                        ${doc.verification_notes ? `<p><span class="text-gray-600">Notes:</span> ${doc.verification_notes}</p>` : ''}
                        ${doc.rejection_reason ? `<p class="text-red-600"><span class="text-gray-600">Rejection Reason:</span> ${doc.rejection_reason}</p>` : ''}
                    </div>
                </div>
                ` : ''}
                
                <div class="col-span-2 flex gap-3 pt-4">
                    <button onclick="downloadDocument('${doc.id}', '${doc.original_filename}')" class="flex-1 bg-green-600 hover:bg-green-700 text-white py-2 rounded-lg transition-all">
                        <i class="fas fa-download mr-2"></i>Download
                    </button>
                    <button onclick="previewDocument('${doc.id}', '${doc.mime_type}')" class="flex-1 bg-purple-600 hover:bg-purple-700 text-white py-2 rounded-lg transition-all">
                        <i class="fas fa-external-link-alt mr-2"></i>Preview
                    </button>
                </div>
            </div>
        `;
        
        document.getElementById('view-document-modal').classList.remove('hidden');
        document.getElementById('view-document-modal').classList.add('flex');
        
    } catch (error) {
        console.error('Error loading document details:', error);
        showNotification('Error loading document details', 'error');
    }
}

// Get status color class
function getStatusColor(status) {
    const colors = {
        'pending': 'bg-yellow-100 text-yellow-800',
        'verified': 'bg-green-100 text-green-800',
        'rejected': 'bg-red-100 text-red-800',
        'under_review': 'bg-blue-100 text-blue-800',
        'expired': 'bg-gray-100 text-gray-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
}

// Download document
async function downloadDocument(documentId, filename) {
    try {
        const response = await fetch(`${API_BASE}/documents/${documentId}/download`);
        if (!response.ok) throw new Error('Failed to download document');
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        showNotification('Document downloaded successfully', 'success');
    } catch (error) {
        console.error('Error downloading document:', error);
        showNotification('Error downloading document', 'error');
    }
}

// Preview document in new tab
function previewDocument(documentId, mimeType) {
    window.open(`${API_BASE}/documents/${documentId}/view`, '_blank');
}

// Show verify document modal
function showVerifyDocumentModal(documentId) {
    document.getElementById('verify-doc-id').value = documentId;
    document.getElementById('verify-document-form').reset();
    document.getElementById('rejection-reason-field').classList.add('hidden');
    
    document.getElementById('verify-document-modal').classList.remove('hidden');
    document.getElementById('verify-document-modal').classList.add('flex');
}

// Handle verify document form submission
document.addEventListener('DOMContentLoaded', function() {
    const verifyForm = document.getElementById('verify-document-form');
    if (verifyForm) {
        verifyForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const documentId = document.getElementById('verify-doc-id').value;
            const formData = new FormData();
            formData.append('status', document.getElementById('verify-status').value);
            
            if (document.getElementById('verify-notes').value) {
                formData.append('notes', document.getElementById('verify-notes').value);
            }
            if (document.getElementById('verify-rejection-reason').value) {
                formData.append('rejection_reason', document.getElementById('verify-rejection-reason').value);
            }
            
            try {
                const response = await fetch(`${API_BASE}/documents/${documentId}/verify`, {
                    method: 'PUT',
                    body: formData
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    showNotification('Document verification updated!', 'success');
                    closeModal('verify-document-modal');
                    await loadCandidateDocuments(currentDocumentCandidateId);
                } else {
                    throw new Error(result.detail || 'Failed to update verification');
                }
            } catch (error) {
                console.error('Error updating verification:', error);
                showNotification('Error updating verification: ' + error.message, 'error');
            }
        });
    }
});

// Delete document
async function deleteDocument(documentId) {
    if (!confirm('Are you sure you want to delete this document? This action cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/documents/${documentId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showNotification('Document deleted successfully', 'success');
            await loadCandidateDocuments(currentDocumentCandidateId);
        } else {
            const result = await response.json();
            throw new Error(result.detail || 'Failed to delete document');
        }
    } catch (error) {
        console.error('Error deleting document:', error);
        showNotification('Error deleting document: ' + error.message, 'error');
    }
}

// Get interview documents (for panel use)
async function getInterviewDocuments(interviewId) {
    try {
        const response = await fetch(`${API_BASE}/interviews/${interviewId}/documents`);
        if (!response.ok) throw new Error('Failed to load interview documents');
        
        return await response.json();
    } catch (error) {
        console.error('Error loading interview documents:', error);
        return null;
    }
}

// Wrapper function to trigger document upload form submission
function uploadDocument() {
    const form = document.getElementById('document-upload-form');
    if (form) {
        form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
    }
}

// Wrapper function to trigger verify document form submission
function verifyDocument() {
    const form = document.getElementById('verify-document-form');
    if (form) {
        form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
    }
}

// Export functions to window for onclick handlers
window.showCandidateDocuments = showCandidateDocuments;
window.loadCandidateDocuments = loadCandidateDocuments;
window.showUploadDocumentModal = showUploadDocumentModal;
window.uploadDocument = uploadDocument;
window.viewDocument = viewDocument;
window.downloadDocument = downloadDocument;
window.deleteDocument = deleteDocument;
window.showVerifyDocumentModal = showVerifyDocumentModal;
window.verifyDocument = verifyDocument;
window.getInterviewDocuments = getInterviewDocuments;
window.filterCandidateDocuments = filterCandidateDocuments;

// Export dashboard functionality for external use
window.dashboard = {
    showSection,
    loadCandidates,
    loadJobs,
    loadApplications,
    loadPanels,
    loadSlots,
    loadInterviews,
    showNotification,
    testAPI,
    showCandidateDocuments,
    loadCandidateDocuments
};