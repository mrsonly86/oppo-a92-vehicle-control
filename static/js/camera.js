/**
 * Camera-specific JavaScript for OPPO A92 Vehicle Control System
 * Handles camera stream, detection overlay, and real-time video processing
 */

// Camera-specific variables
let cameraStream = null;
let detectionCanvas = null;
let detectionContext = null;
let streamActive = false;
let fpsCounter = 0;
let lastFpsUpdate = Date.now();

// Initialize camera page when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    if (window.location.pathname === '/camera') {
        initializeCameraPage();
    }
});

/**
 * Initialize camera page functionality
 */
function initializeCameraPage() {
    setupCameraStream();
    setupDetectionOverlay();
    setupCameraControls();
    checkCameraStatus();
    startFPSCounter();
}

/**
 * Setup camera stream display
 */
function setupCameraStream() {
    const cameraImg = document.getElementById('camera-stream');
    if (cameraImg) {
        cameraImg.addEventListener('load', function() {
            streamActive = true;
            updateStreamStatus('live');
            updateFPS();
        });
        
        cameraImg.addEventListener('error', function() {
            streamActive = false;
            updateStreamStatus('error');
            setTimeout(reconnectCamera, 5000); // Try to reconnect after 5 seconds
        });
    }
}

/**
 * Setup detection overlay canvas
 */
function setupDetectionOverlay() {
    const cameraContainer = document.querySelector('.position-relative');
    if (!cameraContainer) return;
    
    // Create canvas for detection overlay
    detectionCanvas = document.createElement('canvas');
    detectionCanvas.className = 'position-absolute top-0 start-0';
    detectionCanvas.style.pointerEvents = 'none';
    detectionCanvas.style.zIndex = '10';
    
    cameraContainer.appendChild(detectionCanvas);
    detectionContext = detectionCanvas.getContext('2d');
    
    // Update canvas size when image loads
    const cameraImg = document.getElementById('camera-stream');
    if (cameraImg) {
        cameraImg.addEventListener('load', updateCanvasSize);
        window.addEventListener('resize', updateCanvasSize);
    }
}

/**
 * Update canvas size to match camera image
 */
function updateCanvasSize() {
    const cameraImg = document.getElementById('camera-stream');
    if (cameraImg && detectionCanvas) {
        const rect = cameraImg.getBoundingClientRect();
        detectionCanvas.width = rect.width;
        detectionCanvas.height = rect.height;
        detectionCanvas.style.width = rect.width + 'px';
        detectionCanvas.style.height = rect.height + 'px';
    }
}

/**
 * Setup camera control buttons
 */
function setupCameraControls() {
    // Start processing button
    const startBtn = document.getElementById('start-processing');
    if (startBtn) {
        startBtn.addEventListener('click', function() {
            startAIProcessing();
        });
    }
    
    // Stop processing button
    const stopBtn = document.getElementById('stop-processing');
    if (stopBtn) {
        stopBtn.addEventListener('click', function() {
            stopAIProcessing();
        });
    }
    
    // Screenshot button
    const screenshotBtn = document.getElementById('take-screenshot');
    if (screenshotBtn) {
        screenshotBtn.addEventListener('click', function() {
            takeScreenshot();
        });
    }
    
    // Test connection button
    const testBtn = document.getElementById('test-connection');
    if (testBtn) {
        testBtn.addEventListener('click', function() {
            testCameraConnection();
        });
    }
}

/**
 * Start AI processing
 */
function startAIProcessing() {
    showAlert('Starting AI processing...', 'info');
    
    fetch('/api/camera/start', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'started' || data.status === 'already_running') {
                updateAIStatusBadge('Processing', 'success');
                showAlert('AI processing started successfully!', 'success');
                
                // Enable detection overlay
                enableDetectionOverlay();
            } else {
                showAlert('Failed to start AI processing', 'danger');
            }
        })
        .catch(error => {
            console.error('Error starting AI processing:', error);
            showAlert('Error starting AI processing', 'danger');
        });
}

/**
 * Stop AI processing
 */
function stopAIProcessing() {
    showAlert('Stopping AI processing...', 'warning');
    
    fetch('/api/camera/stop', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'stopped') {
                updateAIStatusBadge('Idle', 'warning');
                showAlert('AI processing stopped', 'warning');
                
                // Disable detection overlay
                disableDetectionOverlay();
            } else {
                showAlert('Failed to stop AI processing', 'danger');
            }
        })
        .catch(error => {
            console.error('Error stopping AI processing:', error);
            showAlert('Error stopping AI processing', 'danger');
        });
}

/**
 * Take screenshot of current camera view
 */
function takeScreenshot() {
    const cameraImg = document.getElementById('camera-stream');
    if (!cameraImg) return;
    
    // Create canvas to capture screenshot
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    
    canvas.width = cameraImg.naturalWidth || cameraImg.width;
    canvas.height = cameraImg.naturalHeight || cameraImg.height;
    
    // Draw image to canvas
    context.drawImage(cameraImg, 0, 0);
    
    // Create download link
    canvas.toBlob(function(blob) {
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `oppo-a92-screenshot-${new Date().toISOString().replace(/[:.]/g, '-')}.png`;
        link.click();
        
        URL.revokeObjectURL(url);
        showAlert('Screenshot saved successfully!', 'success');
    }, 'image/png');
}

/**
 * Test camera connection
 */
function testCameraConnection() {
    const ip = document.getElementById('camera-ip').value;
    const port = document.getElementById('camera-port').value;
    
    showAlert('Testing connection to OPPO A92...', 'info');
    
    fetch('/api/camera/test', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ ip, port })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showAlert(`Successfully connected to OPPO A92 at ${ip}:${port}`, 'success');
            updateCameraConnectionStatus('Connected');
        } else {
            showAlert(`Failed to connect to OPPO A92 at ${ip}:${port}`, 'danger');
            updateCameraConnectionStatus('Failed');
        }
    })
    .catch(error => {
        console.error('Error testing connection:', error);
        showAlert('Error testing camera connection', 'danger');
        updateCameraConnectionStatus('Error');
    });
}

/**
 * Check camera status
 */
function checkCameraStatus() {
    fetch('/api/camera/status')
        .then(response => response.json())
        .then(data => {
            updateCameraConnectionStatus(data.connected ? 'Connected' : 'Disconnected');
            updateAIStatusBadge(data.processing ? 'Processing' : 'Idle', 
                              data.processing ? 'success' : 'warning');
        })
        .catch(error => {
            console.error('Error checking camera status:', error);
            updateCameraConnectionStatus('Error');
        });
}

/**
 * Update camera connection status display
 */
function updateCameraConnectionStatus(status) {
    const statusElement = document.getElementById('camera-connection-status');
    if (statusElement) {
        statusElement.textContent = status;
        
        // Update color based on status
        statusElement.className = 'small text-muted';
        if (status === 'Connected') {
            statusElement.classList.add('text-success');
        } else if (status === 'Error' || status === 'Failed') {
            statusElement.classList.add('text-danger');
        } else {
            statusElement.classList.add('text-warning');
        }
    }
}

/**
 * Update AI status badge
 */
function updateAIStatusBadge(status, type) {
    const badge = document.getElementById('ai-status-badge');
    const text = document.getElementById('ai-status-text');
    
    if (badge && text) {
        text.textContent = status;
        badge.className = `badge bg-${type}`;
    }
}

/**
 * Update stream status indicator
 */
function updateStreamStatus(status) {
    const statusBadge = document.getElementById('stream-status');
    if (statusBadge) {
        switch (status) {
            case 'live':
                statusBadge.className = 'badge bg-success';
                statusBadge.innerHTML = '<i class="fas fa-circle me-1"></i>Live';
                break;
            case 'error':
                statusBadge.className = 'badge bg-danger';
                statusBadge.innerHTML = '<i class="fas fa-times me-1"></i>Error';
                break;
            case 'connecting':
                statusBadge.className = 'badge bg-warning';
                statusBadge.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Connecting';
                break;
        }
    }
}

/**
 * Enable detection overlay
 */
function enableDetectionOverlay() {
    if (detectionCanvas) {
        detectionCanvas.style.display = 'block';
    }
    
    // Show detection info
    const detectionInfo = document.getElementById('detection-info');
    if (detectionInfo) {
        detectionInfo.classList.remove('d-none');
    }
}

/**
 * Disable detection overlay
 */
function disableDetectionOverlay() {
    if (detectionCanvas && detectionContext) {
        detectionContext.clearRect(0, 0, detectionCanvas.width, detectionCanvas.height);
        detectionCanvas.style.display = 'none';
    }
    
    // Hide detection info
    const detectionInfo = document.getElementById('detection-info');
    if (detectionInfo) {
        detectionInfo.classList.add('d-none');
    }
}

/**
 * Draw detection boxes on overlay canvas
 */
function drawDetections(detections) {
    if (!detectionContext || !detectionCanvas) return;
    
    // Clear previous detections
    detectionContext.clearRect(0, 0, detectionCanvas.width, detectionCanvas.height);
    
    const vehicles = detections.vehicles || [];
    if (vehicles.length === 0) return;
    
    const cameraImg = document.getElementById('camera-stream');
    if (!cameraImg) return;
    
    const scaleX = detectionCanvas.width / cameraImg.naturalWidth;
    const scaleY = detectionCanvas.height / cameraImg.naturalHeight;
    
    vehicles.forEach(vehicle => {
        if (!vehicle.bbox) return;
        
        const [x1, y1, x2, y2] = vehicle.bbox;
        const scaledX1 = x1 * scaleX;
        const scaledY1 = y1 * scaleY;
        const scaledX2 = x2 * scaleX;
        const scaledY2 = y2 * scaleY;
        const width = scaledX2 - scaledX1;
        const height = scaledY2 - scaledY1;
        
        // Set colors based on vehicle type
        const colors = {
            'car': '#28a745',
            'motorcycle': '#007bff',
            'truck': '#ffc107',
            'bus': '#17a2b8'
        };
        const color = colors[vehicle.class] || '#6c757d';
        
        // Draw bounding box
        detectionContext.strokeStyle = color;
        detectionContext.lineWidth = 3;
        detectionContext.strokeRect(scaledX1, scaledY1, width, height);
        
        // Draw label background
        const label = `${vehicle.class}: ${(vehicle.confidence * 100).toFixed(0)}%`;
        if (vehicle.license_plate) {
            label += ` | ${vehicle.license_plate}`;
        }
        
        detectionContext.font = '14px Arial';
        const textWidth = detectionContext.measureText(label).width;
        
        detectionContext.fillStyle = color;
        detectionContext.fillRect(scaledX1, scaledY1 - 25, textWidth + 10, 25);
        
        // Draw label text
        detectionContext.fillStyle = 'white';
        detectionContext.fillText(label, scaledX1 + 5, scaledY1 - 5);
        
        // Draw authorization status if available
        if (vehicle.license_plate) {
            const authStatus = vehicle.authorized ? 'AUTHORIZED' : 'UNAUTHORIZED';
            const authColor = vehicle.authorized ? '#28a745' : '#dc3545';
            
            detectionContext.fillStyle = authColor;
            detectionContext.fillRect(scaledX2 - 100, scaledY1, 100, 20);
            
            detectionContext.fillStyle = 'white';
            detectionContext.font = '12px Arial';
            detectionContext.fillText(authStatus, scaledX2 - 95, scaledY1 + 15);
        }
    });
}

/**
 * Update detection statistics on camera page
 */
function updateCameraPageDetections(detections) {
    if (window.location.pathname !== '/camera') return;
    
    const vehicles = detections.vehicles || [];
    
    // Update detection counters
    updateElementText('vehicle-count', vehicles.length);
    updateElementText('plate-count', vehicles.filter(v => v.license_plate).length);
    updateElementText('authorized-count', vehicles.filter(v => v.authorized).length);
    updateElementText('unauthorized-count', vehicles.filter(v => !v.authorized && v.license_plate).length);
    
    // Draw detection overlay
    drawDetections(detections);
    
    // Update recent detections list
    updateRecentDetectionsList(vehicles);
}

/**
 * Update recent detections list
 */
function updateRecentDetectionsList(vehicles) {
    const container = document.getElementById('recent-detections');
    if (!container) return;
    
    if (vehicles.length === 0) {
        container.innerHTML = '<p class="text-muted text-center">No detections yet</p>';
        return;
    }
    
    const html = vehicles.map(vehicle => `
        <div class="d-flex align-items-center mb-2 p-2 bg-light rounded">
            <div class="flex-shrink-0">
                <i class="fas fa-${vehicle.class === 'car' ? 'car' : 'motorcycle'} text-primary"></i>
            </div>
            <div class="flex-grow-1 ms-2">
                <div class="fw-bold small">${vehicle.license_plate || 'No plate'}</div>
                <div class="text-muted" style="font-size: 0.75rem;">
                    ${vehicle.class} | ${(vehicle.confidence * 100).toFixed(0)}%
                    ${vehicle.driver_gender && vehicle.driver_gender !== 'unknown' ? ` | ${vehicle.driver_gender}` : ''}
                </div>
            </div>
            <div class="flex-shrink-0">
                <span class="badge ${vehicle.authorized ? 'bg-success' : 'bg-warning'}">
                    ${vehicle.authorized ? 'OK' : 'WARN'}
                </span>
            </div>
        </div>
    `).join('');
    
    container.innerHTML = html;
}

/**
 * Start FPS counter
 */
function startFPSCounter() {
    setInterval(() => {
        if (streamActive) {
            fpsCounter++;
        }
        
        // Update FPS display every second
        if (Date.now() - lastFpsUpdate > 1000) {
            updateElementText('fps-value', fpsCounter);
            fpsCounter = 0;
            lastFpsUpdate = Date.now();
        }
    }, 1000 / 30); // Check 30 times per second
}

/**
 * Update FPS counter
 */
function updateFPS() {
    fpsCounter++;
}

/**
 * Reconnect camera after error
 */
function reconnectCamera() {
    if (!streamActive) {
        updateStreamStatus('connecting');
        
        // Force reload of camera image
        const cameraImg = document.getElementById('camera-stream');
        if (cameraImg) {
            const src = cameraImg.src;
            cameraImg.src = '';
            cameraImg.src = src + '?t=' + Date.now();
        }
    }
}

/**
 * Handle WebSocket detection updates for camera page
 */
if (typeof socket !== 'undefined') {
    socket.on('detection_update', function(data) {
        if (window.location.pathname === '/camera') {
            updateCameraPageDetections(data.detections || {});
        }
    });
}

/**
 * Utility function to update element text
 */
function updateElementText(elementId, text) {
    const element = document.getElementById(elementId);
    if (element) element.textContent = text;
}

/**
 * Show alert (reuse from main.js or define locally)
 */
function showAlert(message, type = 'info') {
    if (window.VehicleControl && window.VehicleControl.showAlert) {
        window.VehicleControl.showAlert(message, type);
    } else {
        // Fallback alert
        console.log(`[${type.toUpperCase()}] ${message}`);
    }
}