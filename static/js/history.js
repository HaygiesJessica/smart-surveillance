// History page logic: loads the summary stats and the full event table
// from the Flask API. Uses the same /api/stats and /api/detections
// endpoints as before - only the way the results are displayed changed.

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

async function loadStats() {
    try {
        const response = await fetch("/api/stats");

        if (!response.ok) {
            throw new Error("Failed to load statistics");
        }

        const stats = await response.json();

        document.getElementById("total-events").textContent = stats.total_events;
        document.getElementById("today-events").textContent = stats.today_events;

        document.getElementById("last-detection-time").textContent =
            stats.latest_event ? formatTimeOnly(stats.latest_event.detected_at) : "—";

    } catch (error) {
        console.error("Error loading statistics:", error);
    }
}


async function loadDetectionHistory() {
    const historyBody = document.getElementById("history-body");
    const tableScroll = document.getElementById("table-scroll");
    const emptyState = document.getElementById("empty-state");

    try {
        const response = await fetch("/api/detections");

        if (!response.ok) {
            throw new Error("Failed to load detection history");
        }

        const detections = await response.json();

        if (detections.length === 0) {
            historyBody.innerHTML = "";
            tableScroll.hidden = true;
            emptyState.hidden = false;
            return;
        }

        tableScroll.hidden = false;
        emptyState.hidden = true;
        historyBody.innerHTML = "";

        detections.forEach(detection => {

            let imageContent = `
                <span class="no-image">No Image</span>
            `;

            if (detection.image) {
                imageContent = `
                    <img
                        src="/static/captures/${detection.image}"
                        class="history-image"
                        alt="Captured photo for event #${detection.id}"
                        onclick="openImagePreview('/static/captures/${detection.image}')">
                `;
            }

            const eventType = (detection.event_type || "Motion Detected").toUpperCase();
            const alarmStatus = (detection.alarm_status || "Activated").toUpperCase();

            const row = document.createElement("tr");

            row.innerHTML = `
                <td>#${String(detection.id).padStart(3, "0")}</td>

                <td>${formatDetectedAt(detection.detected_at)}</td>

                <td><span class="badge badge-motion">${eventType}</span></td>

                <td>${imageContent}</td>

                <td><span class="badge badge-alarm">${alarmStatus}</span></td>
            `;

            historyBody.appendChild(row);
        });

    } catch (error) {
        console.error(
            "Error loading detection history:",
            error
        );

        tableScroll.hidden = false;
        emptyState.hidden = true;

        historyBody.innerHTML = `
            <tr>
                <td colspan="5" class="table-message">
                    Error loading detection history.
                </td>
            </tr>
        `;
    }
}


// Reuses the exact same simulation endpoint as the dashboard button.
// Since this page doesn't show the live PIR/camera/LED/buzzer state,
// the user is sent to the dashboard to watch the sequence happen.
async function simulateMotionFromHistory() {
    const button = document.getElementById("empty-simulate-btn");

    if (button) {
        button.disabled = true;
        button.textContent = "Starting...";
    }

    try {
        await fetch("/api/simulate-motion", { method: "POST" });
    } catch (error) {
        console.error("Error simulating motion:", error);
    }

    window.location.href = "/";
}


loadStats();
loadDetectionHistory();

setInterval(loadStats, 3000);
setInterval(loadDetectionHistory, 3000);

function openImagePreview(imageSource) {

    const modal =
        document.getElementById("image-modal");

    const modalImage =
        document.getElementById("modal-image");

    modalImage.src = imageSource;

    modal.classList.add("show");
}


function closeImagePreview() {

    const modal =
        document.getElementById("image-modal");

    modal.classList.remove("show");
}
