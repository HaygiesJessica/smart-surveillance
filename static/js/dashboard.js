// Dashboard logic: polls the Flask API for the current simulation state
// and updates the page so the MONITORING -> MOTION DETECTED -> CAPTURING
// -> ALARM ACTIVE -> EVENT SAVED -> MONITORING sequence is visible.
//
// This file only reads from and writes to the DOM - it does not change
// how the backend works. It still calls the same two endpoints as
// before: GET /api/status (live state) and POST /api/simulate-motion
// (the "PIR sensor" button), plus GET /api/stats for the event totals.

let isBusy = false;

// How each system state should look on screen: which CSS class to put
// on the big status card, which color the status dot should be, and a
// short hint sentence describing what's happening.
const STATE_INFO = {
    "MONITORING": {
        cardClass: "state-monitoring",
        dot: "success",
        hint: "All sensors normal. Waiting for motion.",
    },
    "MOTION DETECTED": {
        cardClass: "state-motion",
        dot: "warning",
        hint: "PIR sensor triggered. Getting the camera ready...",
    },
    "CAPTURING": {
        cardClass: "state-capturing",
        dot: "info",
        hint: "Camera is capturing an image...",
    },
    "ALARM ACTIVE": {
        cardClass: "state-alarm",
        dot: "danger",
        hint: "LED and buzzer are active.",
    },
    "EVENT SAVED": {
        cardClass: "state-saved",
        dot: "success",
        hint: "Event saved to the database.",
    },
};

const MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
];

// The backend stores timestamps like "2026-09-10 11:41:53 AM".
// This turns that into "September 10, 2026 - 11:41:53 AM".
function formatDetectedAt(raw) {
    if (!raw) return "";

    const match = raw.match(/^(\d{4})-(\d{2})-(\d{2}) (\d{2}:\d{2}:\d{2} (?:AM|PM))$/);
    if (!match) return raw;

    const [, year, month, day, time] = match;
    const monthName = MONTH_NAMES[parseInt(month, 10) - 1];

    return `${monthName} ${parseInt(day, 10)}, ${year} — ${time}`;
}

// Pulls just the "11:41:53 AM" part out, for the compact stat card.
function formatTimeOnly(raw) {
    if (!raw) return "—";

    const match = raw.match(/(\d{2}:\d{2}:\d{2} (?:AM|PM))$/);
    return match ? match[1] : raw;
}

// Small helper so every status dot is set the same way:
// <span class="status-dot <variant>"></span>
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

        isBusy = data.busy;

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

        document.getElementById("pir-text").textContent =
            motionDetected ? "MOTION DETECTED" : "NO MOTION";

        setDot("pir-dot", motionDetected ? "warning" : "success");

        // --- Camera card ---
        const capturing = data.camera_status !== "Ready";

        document.getElementById("camera-text").textContent =
            data.camera_status.toUpperCase();

        setDot("camera-dot", capturing ? "info" : "success");

        // --- LED Alarm card ---
        document.getElementById("led-text").textContent =
            data.led ? "ON" : "OFF";

        setDot("led-dot", data.led ? "danger" : "neutral");

        // --- Buzzer card ---
        document.getElementById("buzzer-text").textContent =
            data.buzzer ? "ON" : "OFF";

        setDot("buzzer-dot", data.buzzer ? "danger" : "neutral");

        // --- Latest capture image ---
        // This appears as soon as the camera takes the photo, even
        // before the event finishes saving.
        const captureImage = document.getElementById("capture-image");
        const capturePlaceholder = document.getElementById("capture-placeholder");

        if (data.latest_image) {
            captureImage.src =
                `/static/captures/${data.latest_image}?t=${Date.now()}`;

            captureImage.hidden = false;
            capturePlaceholder.hidden = true;
        }

        updateSimulateButton();

    } catch (error) {
        console.error("Error loading system status:", error);
    }
}

// Loads the event totals and the details of the most recent saved
// event (used to fill in "Event #___", the timestamp and the alarm
// badge under the latest capture image).
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

            document.getElementById("capture-event-id").textContent =
                `Event #${String(event.id).padStart(3, "0")}`;

            document.getElementById("capture-time").textContent =
                formatDetectedAt(event.detected_at);

            document.getElementById("capture-alarm-badge").textContent =
                (event.alarm_status || "Activated").toUpperCase();

            document.getElementById("capture-info").hidden = false;
        }

    } catch (error) {
        console.error("Error loading stats:", error);
    }
}

// Disables the button and shows "Processing..." while an event is
// running, so a second click cannot start a second detection sequence.
function updateSimulateButton() {
    const button = document.getElementById("simulate-btn");
    if (!button) return;

    button.disabled = isBusy;
    button.textContent = isBusy ? "Processing..." : "Simulate Motion";
}

async function simulateMotion() {
    if (isBusy) {
        return;
    }

    try {
        const response = await fetch("/api/simulate-motion", {
            method: "POST"
        });

        const data = await response.json();

        if (!data.success) {
            // e.g. "System is already processing an event."
            console.log(data.message);
        }

        // Refresh right away so the UI starts updating immediately
        // instead of waiting for the next poll.
        loadStatus();

    } catch (error) {
        console.error("Error simulating motion:", error);
    }
}

// Opens the "View Image" modal with a larger look at the current
// latest capture. Purely a display feature - it reuses whatever image
// is already loaded in the Latest Capture panel, no extra API call.
function openImagePreview() {
    const captureImage = document.getElementById("capture-image");

    if (!captureImage || captureImage.hidden || !captureImage.src) {
        return;
    }

    document.getElementById("modal-image").src = captureImage.src;
    document.getElementById("image-modal").classList.add("show");
}

function closeImagePreview() {
    document.getElementById("image-modal").classList.remove("show");
}

loadStatus();
loadStats();

// Poll fairly often so the MOTION DETECTED / CAPTURING / ALARM ACTIVE
// states are actually visible as they happen, not just the end result.
setInterval(loadStatus, 500);
setInterval(loadStats, 2000);
