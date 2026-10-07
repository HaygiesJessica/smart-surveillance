// Dashboard logic: Polls the Flask API for the current hardware state
// and updates the page so the MONITORING -> MOTION DETECTED -> CAPTURING
// -> ALARM ACTIVE -> EVENT SAVED -> MONITORING sequence is visible.

const STATE_INFO = {
    "MONITORING": {
        cardClass: "state-monitoring",
        dot: "success",
        hint: "System armed. Waiting for PIR sensor trigger...",
    },
    "MOTION DETECTED": {
        cardClass: "state-motion",
        dot: "warning",
        hint: "PIR sensor triggered. Initializing camera...",
    },
    "CAPTURING": {
        cardClass: "state-capturing",
        dot: "info",
        hint: "Capturing image from webcam...",
    },
    "ALARM ACTIVE": {
        cardClass: "state-alarm",
        dot: "danger",
        hint: "Intruder detected! LED and Buzzer active.",
    },
    "EVENT SAVED": {
        cardClass: "state-saved",
        dot: "success",
        hint: "Event logged to database.",
    },
};

const MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
];

function formatDetectedAt(raw) {
    if (!raw) return "";
    const match = raw.match(/^(\d{4})-(\d{2})-(\d{2}) (\d{2}:\d{2}:\d{2} (?:AM|PM))$/);
    if (!match) return raw;
    const [, year, month, day, time] = match;
    const monthName = MONTH_NAMES[parseInt(month, 10) - 1];
    return `${monthName} ${parseInt(day, 10)}, ${year} — ${time}`;
}

function formatTimeOnly(raw) {
    if (!raw) return "—";
    const match = raw.match(/(\d{2}:\d{2}:\d{2} (?:AM|PM))$/);
    return match ? match[1] : raw;
}

function setDot(elementId, variant) {
    const element = document.getElementById(elementId);
    if (element) {
        element.className = "status-dot " + variant;
    }
}

async function loadStatus() {
    try {
        const response = await fetch("/api/status");
        const data = await response.json();

        // --- Big "System Status" card ---
        const info = STATE_INFO[data.state] || STATE_INFO["MONITORING"];

        document.getElementById("status-hero").className =
            "status-hero " + info.cardClass;

        document.getElementById("status-hero-text").textContent = data.state;
        document.getElementById("status-hero-hint").textContent =
            data.error || info.hint;

        setDot("status-hero-dot", info.dot);

        // --- PIR Motion Sensor card ---
        const motionDetected = data.motion_sensor === "Motion Detected";
        document.getElementById("pir-text").textContent = motionDetected ? "MOTION DETECTED" : "NO MOTION";
        setDot("pir-dot", motionDetected ? "warning" : "success");

        // --- Camera card ---
        const capturing = data.camera_status !== "Ready";
        document.getElementById("camera-text").textContent = data.camera_status.toUpperCase();
        setDot("camera-dot", capturing ? "info" : "success");

        // --- LED Alarm card ---
        document.getElementById("led-text").textContent = data.led ? "ON" : "OFF";
        setDot("led-dot", data.led ? "danger" : "neutral");

        // --- Buzzer card ---
        document.getElementById("buzzer-text").textContent = data.buzzer ? "ON" : "OFF";
        setDot("buzzer-dot", data.buzzer ? "danger" : "neutral");

        // --- Latest capture image ---
        const captureImage = document.getElementById("capture-image");
        const capturePlaceholder = document.getElementById("capture-placeholder");

        if (data.latest_image) {
            captureImage.src = `/static/captures/${data.latest_image}?t=${Date.now()}`;
            captureImage.hidden = false;
            capturePlaceholder.hidden = true;
        }

    } catch (error) {
        console.error("Error loading system status:", error);
    }
}

async function loadStats() {
    try {
        const response = await fetch("/api/stats");
        const stats = await response.json();

        document.getElementById("total-events").textContent = stats.total_events;
        document.getElementById("today-events").textContent = stats.today_events;
        document.getElementById("last-detection-time").textContent =
            stats.latest_event ? formatTimeOnly(stats.latest_event.detected_at) : "—";

        if (stats.latest_event) {
            const event = stats.latest_event;
            document.getElementById("capture-event-id").textContent = `Event #${String(event.id).padStart(3, "0")}`;
            document.getElementById("capture-time").textContent = formatDetectedAt(event.detected_at);
            document.getElementById("capture-alarm-badge").textContent = (event.alarm_status || "Activated").toUpperCase();
            document.getElementById("capture-info").hidden = false;
        }
    } catch (error) {
        console.error("Error loading stats:", error);
    }
}

function openImagePreview() {
    const captureImage = document.getElementById("capture-image");
    if (!captureImage || captureImage.hidden || !captureImage.src) return;
    document.getElementById("modal-image").src = captureImage.src;
    document.getElementById("image-modal").classList.add("show");
}

function closeImagePreview() {
    document.getElementById("image-modal").classList.remove("show");
}

// Initialize polling
loadStatus();
loadStats();
setInterval(loadStatus, 500);
setInterval(loadStats, 2000);