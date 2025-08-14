/**
 * Main JavaScript for OPPO A92 Vehicle Control System
 * Handles WebSocket connections, real-time updates, and UI interactions
 */

// Global variables
let socket = null;
let isConnected = false;
let currentDetections = [];
let statisticsChart = null;
let performanceInterval = null;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeWebSocket();
    initializeSystemStatus();
    setupEventListeners();
    startPerformanceMonitoring();
});

/**
 * Initialize WebSocket connection for real-time updates
 */
function initializeWebSocket() {
    try {
        socket = io();
        
        socket.on('connect', function() {
            isConnected = true;
            updateConnectionStatus('connected');
            console.log('✅ WebSocket connected');
        });
        
        socket.on('disconnect', function() {
            isConnected = false;
            updateConnectionStatus('disconnected');
            console.log('❌ WebSocket disconnected');
        });
        
        socket.on('detection_update', function(data) {
            handleDetectionUpdate(data);
        });
        
        socket.on('notification', function(data) {
            showNotification(data);
        });
        
        socket.on('system_status', function(data) {
            updateSystemStatus(data);
        });
        
    } catch (error) {
        console.error('❌ Error initializing WebSocket:', error);
    }
}

/**
 * Initialize system status indicators
 */
function initializeSystemStatus() {
    // Check camera status
    fetch('/api/camera/status')
        .then(response => response.json())
        .then(data => {
            updateCameraStatus(data.connected ? 'connected' : 'disconnected');
        })
        .catch(error => {
            console.error('Error checking camera status:', error);
            updateCameraStatus('error');
        });
    
    // Check AI models status
    updateAIStatus('loading');
    
    // Simulate AI models loading
    setTimeout(() => {
        updateAIStatus('ready');
    }, 3000);
}

/**
 * Setup event listeners for UI interactions
 */
function setupEventListeners() {
    // Navigation active state
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            navLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
        });
    });
    
    // Alert close buttons
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('alert-close')) {
            e.target.closest('.alert').remove();
        }
    });
    
    // Modal cleanup on close
    document.addEventListener('hidden.bs.modal', function() {
        document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
            backdrop.remove();
        });
    });
}

/**
 * Start performance monitoring
 */
function startPerformanceMonitoring() {
    performanceInterval = setInterval(updatePerformanceMetrics, 5000);
}

/**
 * Update connection status indicator
 */
function updateConnectionStatus(status) {
    const indicator = document.getElementById('connection-status');
    if (indicator) {
        indicator.className = `status-indicator status-${status}`;
    }
}

/**
 * Update camera status
 */
function updateCameraStatus(status) {
    const statusElement = document.getElementById('camera-status');
    const statusText = document.getElementById('camera-status-text');
    
    if (statusElement && statusText) {
        statusElement.className = 'fas fa-circle me-1';
        
        switch (status) {
            case 'connected':
                statusElement.classList.add('text-success');
                statusText.textContent = 'Camera Online';
                break;
            case 'disconnected':
                statusElement.classList.add('text-danger');
                statusText.textContent = 'Camera Offline';
                break;
            case 'error':
                statusElement.classList.add('text-warning');
                statusText.textContent = 'Camera Error';
                break;
            default:
                statusElement.classList.add('text-secondary');
                statusText.textContent = 'Camera Unknown';
        }
    }
}

/**
 * Update AI processing status
 */
function updateAIStatus(status) {
    const statusElement = document.getElementById('ai-status');
    const statusText = document.getElementById('ai-status-text');
    
    if (statusElement && statusText) {
        statusElement.className = 'fas fa-circle me-1';
        
        switch (status) {
            case 'ready':
                statusElement.classList.add('text-success');
                statusText.textContent = 'AI Ready';
                break;
            case 'processing':
                statusElement.classList.add('text-primary');
                statusText.textContent = 'AI Processing';
                break;
            case 'loading':
                statusElement.classList.add('text-warning');
                statusText.textContent = 'AI Loading';
                break;
            case 'error':
                statusElement.classList.add('text-danger');
                statusText.textContent = 'AI Error';
                break;
            default:
                statusElement.classList.add('text-secondary');
                statusText.textContent = 'AI Unknown';
        }
    }
}

/**
 * Handle detection updates from WebSocket
 */
function handleDetectionUpdate(data) {
    currentDetections = data.detections || [];
    
    // Update detection counters
    updateDetectionCounters(currentDetections);
    
    // Update recent activity if on dashboard
    if (window.location.pathname === '/' || window.location.pathname === '/dashboard') {
        updateRecentActivity(data);
    }
    
    // Update camera page if active
    if (window.location.pathname === '/camera') {
        updateCameraPageDetections(currentDetections);
    }
}

/**
 * Update detection counters
 */
function updateDetectionCounters(detections) {
    const vehicles = detections.vehicles || [];
    
    // Count vehicles by type
    const carCount = vehicles.filter(v => v.class === 'car').length;
    const motorcycleCount = vehicles.filter(v => v.class === 'motorcycle').length;
    const totalCount = vehicles.length;
    
    // Update counters if elements exist
    updateElementText('car-count', carCount);
    updateElementText('motorcycle-count', motorcycleCount);
    updateElementText('vehicle-count', totalCount);
    
    // Update plates read count
    const platesRead = vehicles.filter(v => v.license_plate).length;
    updateElementText('plate-count', platesRead);
    
    // Update authorized/unauthorized counts
    const authorizedCount = vehicles.filter(v => v.authorized).length;
    const unauthorizedCount = totalCount - authorizedCount;
    updateElementText('authorized-count', authorizedCount);
    updateElementText('unauthorized-count', unauthorizedCount);
}

/**
 * Update recent activity section
 */
function updateRecentActivity(data) {
    const container = document.getElementById('recent-activity');
    if (!container) return;
    
    const vehicles = data.detections.vehicles || [];
    
    vehicles.forEach(vehicle => {
        if (vehicle.license_plate) {
            addActivityItem(container, {
                license_plate: vehicle.license_plate,
                vehicle_type: vehicle.class,
                authorized: vehicle.authorized || false,
                timestamp: new Date().toLocaleTimeString(),
                driver_gender: vehicle.driver_gender || 'unknown'
            });
        }
    });
}

/**
 * Add activity item to recent activity
 */
function addActivityItem(container, activity) {
    const existingItems = container.querySelectorAll('.activity-item');
    
    // Check if item already exists
    const exists = Array.from(existingItems).some(item => 
        item.dataset.plate === activity.license_plate
    );
    
    if (exists) return;
    
    const activityItem = document.createElement('div');
    activityItem.className = 'd-flex align-items-center mb-3 activity-item';
    activityItem.dataset.plate = activity.license_plate;
    
    activityItem.innerHTML = `
        <div class="flex-shrink-0">
            <i class="fas fa-${activity.authorized ? 'check-circle text-success' : 'exclamation-triangle text-warning'}"></i>
        </div>
        <div class="flex-grow-1 ms-3">
            <div class="fw-bold">${activity.license_plate}</div>
            <div class="small text-muted">
                ${activity.vehicle_type} | ${activity.timestamp}
                ${activity.driver_gender !== 'unknown' ? ` | ${activity.driver_gender}` : ''}
            </div>
        </div>
    `;
    
    // Add to top of container
    container.insertBefore(activityItem, container.firstChild);
    
    // Keep only last 10 items
    const items = container.querySelectorAll('.activity-item');
    if (items.length > 10) {
        items[items.length - 1].remove();
    }
}

/**
 * Update performance metrics
 */
function updatePerformanceMetrics() {
    // Simulate performance data (in real implementation, get from API)
    const metrics = {
        cpu: Math.random() * 30 + 40, // 40-70%
        memory: Math.random() * 0.4 + 1.0, // 1.0-1.4GB
        temperature: Math.random() * 8 + 30, // 30-38°C
        battery: Math.max(20, 100 - (Date.now() / 1000 % 3600) / 36), // Slow drain
        fps: Math.random() * 4 + 8 // 8-12 FPS
    };
    
    // Update CPU usage
    updateProgressBar('cpu-usage', metrics.cpu, 100, `${Math.round(metrics.cpu)}%`);
    
    // Update memory usage
    const memoryPercent = (metrics.memory / 1.5) * 100;
    updateProgressBar('memory-usage', memoryPercent, 100, `${metrics.memory.toFixed(1)}GB / 1.5GB`);
    
    // Update temperature
    const tempPercent = (metrics.temperature / 50) * 100;
    updateProgressBar('temperature', tempPercent, 100, `${Math.round(metrics.temperature)}°C`);
    
    // Update battery
    updateProgressBar('battery', metrics.battery, 100, `${Math.round(metrics.battery)}%`);
    
    // Update FPS counter
    updateElementText('fps-counter', Math.round(metrics.fps));
    updateElementText('fps-value', Math.round(metrics.fps));
}

/**
 * Update progress bar element
 */
function updateProgressBar(elementId, value, max, text) {
    const textElement = document.getElementById(`${elementId}-text`);
    const barElement = document.getElementById(`${elementId}-bar`);
    
    if (textElement) textElement.textContent = text;
    if (barElement) {
        const percentage = (value / max) * 100;
        barElement.style.width = `${percentage}%`;
        
        // Update color based on value
        barElement.className = 'progress-bar';
        if (percentage > 80) {
            barElement.classList.add('bg-danger');
        } else if (percentage > 60) {
            barElement.classList.add('bg-warning');
        } else {
            barElement.classList.add('bg-success');
        }
    }
}

/**
 * Update element text content
 */
function updateElementText(elementId, text) {
    const element = document.getElementById(elementId);
    if (element) element.textContent = text;
}

/**
 * Show notification alert
 */
function showNotification(data) {
    showAlert(data.message, data.type || 'info', data.title);
}

/**
 * Show alert message
 */
function showAlert(message, type = 'info', title = null) {
    const alertContainer = document.getElementById('alert-container');
    if (!alertContainer) return;
    
    const alertId = 'alert-' + Date.now();
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" id="${alertId}" role="alert">
            ${title ? `<strong>${title}:</strong> ` : ''}${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    alertContainer.insertAdjacentHTML('beforeend', alertHtml);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        const alert = document.getElementById(alertId);
        if (alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }
    }, 5000);
}

/**
 * Format timestamp for display
 */
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleTimeString();
}

/**
 * Format number with thousand separators
 */
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

/**
 * Debounce function for performance optimization
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Initialize camera controls (if on camera page)
 */
function initializeCameraControls() {
    const startBtn = document.getElementById('start-processing');
    const stopBtn = document.getElementById('stop-processing');
    
    if (startBtn) {
        startBtn.addEventListener('click', function() {
            startProcessing();
        });
    }
    
    if (stopBtn) {
        stopBtn.addEventListener('click', function() {
            stopProcessing();
        });
    }
}

/**
 * Start AI processing
 */
function startProcessing() {
    fetch('/api/camera/start', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'started' || data.status === 'already_running') {
                updateAIStatus('processing');
                showAlert('AI processing started', 'success');
            } else {
                showAlert('Failed to start AI processing', 'danger');
            }
        })
        .catch(error => {
            console.error('Error starting processing:', error);
            showAlert('Error starting AI processing', 'danger');
        });
}

/**
 * Stop AI processing
 */
function stopProcessing() {
    fetch('/api/camera/stop', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'stopped') {
                updateAIStatus('ready');
                showAlert('AI processing stopped', 'warning');
            } else {
                showAlert('Failed to stop AI processing', 'danger');
            }
        })
        .catch(error => {
            console.error('Error stopping processing:', error);
            showAlert('Error stopping AI processing', 'danger');
        });
}

/**
 * Update system status from WebSocket
 */
function updateSystemStatus(data) {
    if (data.camera_status) {
        updateCameraStatus(data.camera_status);
    }
    
    if (data.ai_status) {
        updateAIStatus(data.ai_status);
    }
    
    if (data.performance) {
        updatePerformanceMetrics(data.performance);
    }
}

/**
 * Check if device is mobile (OPPO A92 optimization)
 */
function isMobile() {
    return window.innerWidth <= 768;
}

/**
 * Optimize for mobile display
 */
function optimizeForMobile() {
    if (isMobile()) {
        // Reduce update frequency on mobile
        if (performanceInterval) {
            clearInterval(performanceInterval);
            performanceInterval = setInterval(updatePerformanceMetrics, 10000); // 10s instead of 5s
        }
        
        // Reduce animation complexity
        document.body.classList.add('mobile-optimized');
    }
}

// Initialize mobile optimization
window.addEventListener('resize', debounce(optimizeForMobile, 250));
optimizeForMobile();

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (performanceInterval) {
        clearInterval(performanceInterval);
    }
    
    if (socket) {
        socket.disconnect();
    }
});

// Export functions for use in other scripts
window.VehicleControl = {
    showAlert,
    updateDetectionCounters,
    formatTimestamp,
    formatNumber,
    initializeCameraControls,
    startProcessing,
    stopProcessing
};