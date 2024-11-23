// Global state
let timerInterval = null;
let displayEnabled = true;
let currentMode = 'timer';
let timerRunning = false;

// Initialize when document loads
document.addEventListener('DOMContentLoaded', () => {
    updateStatus();
    loadPresets();
    // Update status every 2 seconds
    setInterval(updateStatus, 2000);
});

// Status Updates
async function updateStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        // Update scores
        document.getElementById('homeScore').textContent = data.scores.home;
        document.getElementById('awayScore').textContent = data.scores.away;
        
        // Update timer display
        updateTimerDisplay(data.game_time);
        
        // Update system status
        updateSystemStatus(data);
        
        // Update display mode
        updateDisplayMode(data.display_mode);
        
        // Update power status
        updatePowerStatus(data.power);
        
        // Update display power state
        updateDisplayPower(data.display_enabled);
        
        timerRunning = !data.timer_paused;
        updateTimerButtons();
        
    } catch (error) {
        console.error('Status update failed:', error);
    }
}

// Score Control
async function updateScore(team, change) {
    const scoreElement = document.getElementById(team + 'Score');
    const currentScore = parseInt(scoreElement.textContent);
    const newScore = Math.max(0, Math.min(19, currentScore + change));
    
    try {
        await fetch('/api/score', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                team: team,
                score: newScore
            })
        });
    } catch (error) {
        console.error('Score update failed:', error);
    }
}

// Timer Control
async function startTimer() {
    try {
        await fetch('/api/timer/resume', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
        timerRunning = true;
        updateTimerButtons();
    } catch (error) {
        console.error('Timer start failed:', error);
    }
}

async function stopTimer() {
    try {
        await fetch('/api/timer/pause', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
        timerRunning = false;
        updateTimerButtons();
    } catch (error) {
        console.error('Timer stop failed:', error);
    }
}

async function setTimer() {
    const minutes = document.getElementById('timerInput').value;
    try {
        await fetch('/api/timer', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({minutes: parseInt(minutes)})
        });
    } catch (error) {
        console.error('Timer set failed:', error);
    }
}

function updateTimerDisplay(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    document.getElementById('timerDisplay').textContent = 
        `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
}

function updateTimerButtons() {
    const startBtn = document.getElementById('startTimerBtn');
    const stopBtn = document.getElementById('stopTimerBtn');
    
    if (timerRunning) {
        startBtn.classList.add('bg-gray-500');
        startBtn.classList.remove('bg-green-500');
        stopBtn.classList.add('bg-red-500');
        stopBtn.classList.remove('bg-gray-500');
    } else {
        startBtn.classList.add('bg-green-500');
        startBtn.classList.remove('bg-gray-500');
        stopBtn.classList.add('bg-gray-500');
        stopBtn.classList.remove('bg-red-500');
    }
}

// Display Mode Control
async function setDisplayMode(mode) {
    try {
        await fetch('/api/display/mode', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({mode: mode})
        });
        currentMode = mode;
        updateDisplayModeButtons();
    } catch (error) {
        console.error('Display mode change failed:', error);
    }
}

function updateDisplayMode(mode) {
    currentMode = mode;
    updateDisplayModeButtons();
    document.getElementById('displayMode').textContent = mode;
}

function updateDisplayModeButtons() {
    const modes = ['timer', 'text', 'time'];
    modes.forEach(mode => {
        const btn = document.getElementById(`${mode}ModeBtn`);
        if (mode === currentMode) {
            btn.classList.add('bg-blue-500', 'text-white');
            btn.classList.remove('bg-gray-200');
        } else {
            btn.classList.add('bg-gray-200');
            btn.classList.remove('bg-blue-500', 'text-white');
        }
    });
}

// Message Control
async function loadPresets() {
    try {
        const response = await fetch('/api/messages/presets');
        const data = await response.json();
        const select = document.getElementById('presetSelect');
        
        select.innerHTML = '<option value="">Select a preset message...</option>';
        data.default.forEach((msg, index) => {
            const option = document.createElement('option');
            option.value = index;
            option.textContent = msg;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Loading presets failed:', error);
    }
}

async function displaySelected() {
    const select = document.getElementById('presetSelect');
    if (select.value !== '') {
        const message = select.options[select.selectedIndex].text;
        await displayMessage(message);
    }
}

async function displayCustom() {
    const input = document.getElementById('customMessage');
    if (input.value.trim()) {
        await displayMessage(input.value.trim());
    }
}

async function displayMessage(message) {
    try {
        await fetch('/api/display/text', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({text: message})
        });
        setDisplayMode('text');
    } catch (error) {
        console.error('Message display failed:', error);
    }
}

async function clearMessage() {
    await displayMessage('');
    document.getElementById('customMessage').value = '';
    document.getElementById('presetSelect').selectedIndex = 0;
}

// Power Control
async function toggleDisplay() {
    displayEnabled = !displayEnabled;
    try {
        await fetch('/api/display/power', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({enabled: displayEnabled})
        });
        updateDisplayPower(displayEnabled);
    } catch (error) {
        console.error('Display toggle failed:', error);
    }
}

function updateDisplayPower(enabled) {
    const btn = document.getElementById('displayPowerBtn');
    const status = document.getElementById('displayStatus');
    
    if (enabled) {
        btn.textContent = 'ON';
        btn.classList.add('bg-green-500');
        btn.classList.remove('bg-red-500');
        status.textContent = 'Display Active';
        status.classList.add('text-green-500');
        status.classList.remove('text-red-500');
    } else {
        btn.textContent = 'OFF';
        btn.classList.add('bg-red-500');
        btn.classList.remove('bg-green-500');
        status.textContent = 'Display Off';
        status.classList.add('text-red-500');
        status.classList.remove('text-green-500');
    }
}

// System Status Updates
function updateSystemStatus(data) {
    // Update temperatures
    document.getElementById('systemTemp').textContent = 
        data.system.cpu_temp?.toFixed(1) || '--';
    document.getElementById('panelTemp').textContent = 
        data.scoreboard.temperatures?.electronics?.toFixed(1) || '--';
    
    // Update brightness
    document.getElementById('brightnessLevel').textContent = 
        data.scoreboard.brightness;
    
    // Update network status
    document.getElementById('wifiStatus').textContent = 
        data.system.wifi_connected ? 'Connected' : 'Disconnected';
    document.getElementById('clientCount').textContent = 
        data.system.connected_clients || '0';
}

function updatePowerStatus(power) {
    // Update battery level
    document.getElementById('batteryLevel').textContent = 
        power.battery_level;
    
    // Update panel voltage
    document.getElementById('panelVoltage').textContent = 
        power.panel_power.voltage.toFixed(1);
    
    // Update status colors based on levels
    const batteryElement = document.getElementById('batteryLevel');
    if (power.battery_level < 20) {
        batteryElement.classList.add('text-red-500');
    } else if (power.battery_level < 50) {
        batteryElement.classList.add('text-yellow-500');
    } else {
        batteryElement.classList.remove('text-red-500', 'text-yellow-500');
    }
}

// Two Minute Warning Handler
function handleTwoMinWarning(show) {
    const warningElement = document.getElementById('twoMinWarning');
    if (show) {
        warningElement.classList.remove('hidden');
        playWarningSound();
    } else {
        warningElement.classList.add('hidden');
    }
}

function playWarningSound() {
    const audio = new Audio('/static/sounds/warning.mp3');
    audio.play().catch(e => console.log('Warning sound playback failed'));
}
