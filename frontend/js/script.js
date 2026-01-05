const API_BASE_URL = 'http://localhost:8000/api/v1';

document.addEventListener('DOMContentLoaded', () => {
    // Initialize Theme
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-theme');
    }

    // Theme Toggle Handler
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            document.body.classList.toggle('dark-theme');
            const isDark = document.body.classList.contains('dark-theme');
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
            updateToggleIcon(isDark);
        });
        updateToggleIcon(document.body.classList.contains('dark-theme'));
    }

    // Current Page Detection
    const path = window.location.pathname;
    const page = path.split("/").pop();

    if (page === 'dashboard.html') {
        initDashboard();
    } else if (page === 'privacy.html') {
        initPrivacyControls();
    } else if (page === 'logs.html') {
        initLogs();
    } else if (page === 'alerts.html') {
        initAlerts();
    } else if (page === 'permissions.html') {
        initPermissions();
    }
});

function updateToggleIcon(isDark) {
    const btn = document.getElementById('themeToggle');
    if (btn) {
        btn.innerHTML = isDark ? '🌙' : '☀️';
    }
}

async function initPermissions() {
    const container = document.getElementById('appsContainer');
    if (!container) return;

    try {
        const response = await fetch(`${API_BASE_URL}/permissions/list`);
        if (response.ok) {
            const apps = await response.json();
            if (apps.length > 0) {
                // Keep the "System Services" static entry and append real apps
                apps.forEach(app => {
                    const div = document.createElement('div');
                    div.className = 'app-item';
                    
                    const badges = app.requested_permissions.map(p => 
                        `<span class="perm-allow">✔ ${p.replace('_', ' ')}</span>`
                    ).join(' ');

                    div.innerHTML = `
                        <div style="flex: 1;">
                            <h3 style="color: var(--color-prune-dark); margin-bottom: 0.5rem;">${app.app_name}</h3>
                            <div class="permission-badges">${badges}</div>
                        </div>
                        <div style="display: flex; gap: 0.5rem; align-items: center;">
                            <button class="btn btn-secondary revoke-btn" data-app="${app.app_id}" style="color: var(--color-danger); border-color: var(--color-danger); padding: 0.5rem 1rem;">Revoke</button>
                        </div>
                    `;
                    container.appendChild(div);
                });
            }
        }
    } catch (e) {
        console.warn("Backend offline, using static permission display");
    }

    container.addEventListener('click', async (e) => {
        if (e.target.classList.contains('revoke-btn')) {
            const appId = e.target.dataset.app;
            const appItem = e.target.closest('.app-item');
            if (confirm('Are you sure you want to revoke all permissions for this app?')) {
                try {
                    const response = await fetch(`${API_BASE_URL}/permissions/revoke-all?app_id=${appId}`, {
                        method: 'POST'
                    });
                    
                    if (response.ok) {
                        appItem.style.opacity = '0.3';
                        e.target.disabled = true;
                        e.target.innerText = 'Revoked';
                    } else {
                        alert('Failed to revoke permissions');
                    }
                } catch (err) {
                    console.error('Revoke error:', err);
                }
            }
        }
    });
}

async function initAlerts() {
    const container = document.getElementById('alertsContainer');
    if (!container) return;

    // Fetch recent threats from backend
    try {
        const response = await fetch(`${API_BASE_URL}/threats/recent`);
        if (response.ok) {
            const threats = await response.json();
            if (threats.length > 0) {
                container.innerHTML = ''; // Clear only if we have data
                threats.forEach(threat => {
                    const div = document.createElement('div');
                    div.className = 'alert-item';
                    if (threat.level === 'medium') div.style.borderLeftColor = '#FFC107';
                    
                    div.innerHTML = `
                        <div class="alert-header">
                            <h4 style="color: ${threat.level === 'critical' || threat.level === 'high' ? 'var(--color-danger)' : 'var(--color-warning)'};">${threat.threat_type.replace('_', ' ').toUpperCase()}</h4>
                            <span class="severity-tag severity-${threat.level}">${threat.level} Risk</span>
                        </div>
                        <p style="font-size: 1rem; opacity: 0.8;"><strong>App:</strong> ${threat.app_id || 'Unknown'}<br>${threat.description}</p>
                        <div class="alert-actions">
                            <button class="btn btn-primary" style="padding: 0.5rem 1rem; font-size: 0.9rem;">Mitigate Threat</button>
                        </div>
                    `;
                    container.appendChild(div);
                });
            }
        }
    } catch (e) {
        console.warn("Backend offline, using static alerts");
    }

    // Event delegation for dynamically added buttons
    container.addEventListener('click', (e) => {
        if (e.target.classList.contains('btn-primary')) {
            const btn = e.target;
            const alertItem = btn.closest('.alert-item');
            alertItem.style.opacity = '0.5';
            alertItem.style.pointerEvents = 'none';
            btn.innerText = 'Actioned';
            alert('Security action initiated: Threat Mitigated');
        }
    });
}

async function initLogs() {
    const container = document.getElementById('logsContainer');
    if (!container) return;

    const searchBar = document.querySelector('.search-bar');
    
    // Fetch logs from backend
    try {
        const response = await fetch(`${API_BASE_URL}/permissions/audit`);
        if (response.ok) {
            const logs = await response.json();
            if (logs.length > 0) {
                container.innerHTML = '';
                logs.forEach(log => {
                    const tr = document.createElement('tr');
                    tr.className = 'log-row';
                    const time = new Date(log.timestamp).toLocaleTimeString();
                    
                    tr.innerHTML = `
                        <td>${time}</td>
                        <td>${log.app_name}</td>
                        <td>${log.action.toUpperCase()}</td>
                        <td>${log.permission_type}</td>
                        <td><span class="status-${log.action === 'grant' ? 'allowed' : 'blocked'}">${log.action === 'grant' ? 'Granted' : 'Revoked'}</span></td>
                    `;
                    container.appendChild(tr);
                });
            }
        }
    } catch (e) {
        console.warn("Backend offline, using static logs");
    }

    if (searchBar) {
        searchBar.addEventListener('input', (e) => {
            const term = e.target.value.toLowerCase();
            const logRows = container.querySelectorAll('.log-row');
            logRows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(term) ? '' : 'none';
            });
        });
    }
}

// Neural Signal Simulation & Dashboard
async function initDashboard() {
    const canvas = document.getElementById('neuralChart');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    let width = canvas.width = canvas.offsetWidth;
    let height = canvas.height = canvas.offsetHeight;

    window.addEventListener('resize', () => {
        width = canvas.width = canvas.offsetWidth;
        height = canvas.height = canvas.offsetHeight;
    });

    let offset = 0;
    let backendBands = { alpha: 30, beta: 20, gamma: 10 };
    let intentInfo = { intent_type: 'neutral', confidence: 0.6, explanation: 'Analyzing...' };

    // Function to fetch live signal processing results
    async function updateBands() {
        try {
            // Simulate sending EEG data to backend
            const syntheticResp = await fetch(`${API_BASE_URL}/signal/synthetic`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ duration: 1.0, brain_state: Math.random() > 0.5 ? 'focused' : 'neutral' })
            });
            
            if (syntheticResp.ok) {
                const synthData = await syntheticResp.json();
                const processResp = await fetch(`${API_BASE_URL}/signal/process`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ channels: synthData.data.channels, sampling_rate: 256 })
                });
                
                if (processResp.ok) {
                    const result = await processResp.json();
                    backendBands = result.frequency_bands;
                    intentInfo = result.intent_classification;
                    updateIntentUI(intentInfo);
                }
            }
        } catch (e) {
            // Keep using default waves if backend is down
        }
    }

    function updateIntentUI(info) {
        const statusEl = document.getElementById('intentStatus');
        const explanationEl = document.getElementById('intentExplanation');
        const confidenceEl = document.getElementById('intentConfidence');
        
        if (statusEl) {
            statusEl.innerText = info.intent_type.toUpperCase();
            // Burgundy for subconscious (danger), Sour Lemon for intentional (focus)
            statusEl.style.color = info.intent_type === 'intentional' ? '#ECF4A0' : (info.intent_type === 'subconscious' ? '#7D0A4E' : 'var(--color-prune)');
        }
        if (explanationEl) explanationEl.innerText = info.explanation;
        if (confidenceEl) confidenceEl.innerText = (info.confidence * 100).toFixed(1) + '%';
    }

    // Sync Privacy and Permissions display
    async function syncSummary() {
        try {
            // Update Privacy Mode
            const privacyResp = await fetch(`${API_BASE_URL}/privacy/status`);
            if (privacyResp.ok) {
                const status = await privacyResp.json();
                const modeEl = document.getElementById('currentPrivacyMode');
                if (modeEl) {
                    const level = status.current_level;
                    modeEl.innerText = level <= 0.3 ? 'Strict' : (level >= 0.7 ? 'Performance' : 'Balanced');
                }
            }

            // Update Permissions Count
            const permsResp = await fetch(`${API_BASE_URL}/permissions/list`);
            if (permsResp.ok) {
                const apps = await permsResp.json();
                const countEl = document.getElementById('activePermsCount');
                if (countEl) {
                    // Count apps that actually have permissions
                    const activeApps = apps.filter(app => app.requested_permissions.length > 0);
                    countEl.innerText = activeApps.length;
                }
            }
        } catch(e) {}
    }

    // Update every 2 seconds for real-time feel
    setInterval(() => {
        updateBands();
        syncSummary();
    }, 2000);
    
    updateBands(); // Initial call
    syncSummary(); // Initial call

    function animate() {
        ctx.clearRect(0, 0, width, height);

        // Map backend band powers to visual amplitudes
        // Base amplitude + scaled power
        const alphaAmp = 20 + (backendBands.alpha || 0) * 0.5;
        const betaAmp = 15 + (backendBands.beta || 0) * 0.4;
        const gammaAmp = 10 + (backendBands.gamma || 0) * 0.8;

        drawWave(ctx, width, height, offset, 12, alphaAmp, '#4E0631'); 
        drawWave(ctx, width, height, offset * 1.5, 22, betaAmp, '#7D0A4E');
        drawWave(ctx, width, height, offset * 2, 8, gammaAmp, '#ECF4A0');

        offset += 0.05;
        requestAnimationFrame(animate);
    }
    animate();
}

function drawWave(ctx, w, h, offset, frequency, amplitude, color) {
    ctx.beginPath();
    ctx.strokeStyle = color;
    ctx.lineWidth = 2;

    for (let x = 0; x < w; x++) {
        const y = h / 2 + Math.sin((x / 50 + offset) * frequency / 5) * amplitude;
        ctx.lineTo(x, y);
    }
    ctx.stroke();
}

function initPrivacyControls() {
    const slider = document.getElementById('privacySlider');
    const noiseMeter = document.getElementById('noiseMeter');
    const riskLabel = document.getElementById('riskLabel');
    const statusText = document.getElementById('privacyStatus');

    if (!slider) return;

    const levels = {
        1: { name: 'Performance', noise: 'Low (~5%)', risk: 'High', color: '#F44336', apiVal: 0.9 },
        2: { name: 'Balanced', noise: 'Moderate (~15%)', risk: 'Medium', color: '#FFC107', apiVal: 0.5 },
        3: { name: 'Strict', noise: 'High (~25%)', risk: 'Low', color: '#4CAF50', apiVal: 0.1 }
    };

    async function updatePrivacy(val) {
        const level = levels[parseInt(val)];
        if (!level) return;

        statusText.innerText = level.name;
        noiseMeter.innerText = level.noise;
        riskLabel.innerText = level.risk;
        riskLabel.style.color = level.color;

        // Update backend
        try {
            await fetch(`${API_BASE_URL}/privacy/set-level`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ level: level.apiVal })
            });
        } catch (e) {
            console.warn("Backend offline, privacy level only updated locally");
        }
    }

    // Initialize - fetch current level from backend
    async function initSlider() {
        try {
            const response = await fetch(`${API_BASE_URL}/privacy/status`);
            if (response.ok) {
                const status = await response.json();
                const level = status.current_level;
                
                // Map API level back to slider value
                let sliderVal = 2; // Default Balanced
                if (level <= 0.3) sliderVal = 3; // Strict
                else if (level >= 0.7) sliderVal = 1; // Performance
                
                slider.value = sliderVal;
                updatePrivacy(sliderVal);
            }
        } catch (e) {
            updatePrivacy(slider.value);
        }
    }

    initSlider();

    slider.addEventListener('input', (e) => updatePrivacy(e.target.value));
    slider.addEventListener('change', (e) => updatePrivacy(e.target.value));
}


