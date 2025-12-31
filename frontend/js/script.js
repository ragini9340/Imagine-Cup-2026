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
    }
} else if (page === 'logs.html') {
    initLogs();
} else if (page === 'alerts.html') {
    initAlerts();
}
});

function initAlerts() {
const actionButtons = document.querySelectorAll('.alert-actions .btn-primary');
actionButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        const alertItem = btn.closest('.alert-item');
        alertItem.style.opacity = '0.5';
        alertItem.style.pointerEvents = 'none';
        btn.innerText = 'Actioned';
        alert('Security action initiated: Access ' + (btn.innerText.toLowerCase().includes('revoke') ? 'Revoked' : 'Blocked'));
    });
});
}

function initLogs() {
const searchBar = document.querySelector('.search-bar');
const logRows = document.querySelectorAll('.log-row');

if (!searchBar) return;

searchBar.addEventListener('input', (e) => {
    const term = e.target.value.toLowerCase();
    logRows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(term) ? '' : 'none';
    });
});
}
});

function updateToggleIcon(isDark) {
    const btn = document.getElementById('themeToggle');
    if (btn) {
        btn.innerHTML = isDark ? '🌙' : '☀️';
    }
}

// Mock Data for Neural Signals
function initDashboard() {
    const canvas = document.getElementById('neuralChart');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    let width = canvas.width = canvas.offsetWidth;
    let height = canvas.height = canvas.offsetHeight;

    // Handle resize
    window.addEventListener('resize', () => {
        width = canvas.width = canvas.offsetWidth;
        height = canvas.height = canvas.offsetHeight;
    });

    let offset = 0;

    function animate() {
        ctx.clearRect(0, 0, width, height);

        // Draw Alpha, Beta, Gamma simulated waves
        drawWave(ctx, width, height, offset, 10, 50, '#4E0631'); // Alpha (Burgundy Rose)
        drawWave(ctx, width, height, offset * 1.5, 20, 30, '#7D0A4E'); // Beta (Lighter Burgundy)
        drawWave(ctx, width, height, offset * 2, 5, 20, '#ECF4A0'); // Gamma (Sour Lemon)

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
        1: { name: 'Performance', noise: 'Low (~5%)', risk: 'High', color: '#F44336' },
        2: { name: 'Balanced', noise: 'Moderate (~15%)', risk: 'Medium', color: '#FFC107' },
        3: { name: 'Strict', noise: 'High (~25%)', risk: 'Low', color: '#4CAF50' }
    };

    function updatePrivacy(val) {
        const level = levels[parseInt(val)];
        if (!level) return;

        statusText.innerText = level.name;
        noiseMeter.innerText = level.noise;
        riskLabel.innerText = level.risk;
        riskLabel.style.color = level.color;
    }

    // Initialize
    updatePrivacy(slider.value);

    slider.addEventListener('input', (e) => updatePrivacy(e.target.value));
    slider.addEventListener('change', (e) => updatePrivacy(e.target.value));

}

