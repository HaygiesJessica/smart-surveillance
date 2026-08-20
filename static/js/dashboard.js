async function loadStatus() {
    try {
        const response = await fetch("/api/status");
        const data = await response.json();

        document.getElementById("motion-count").textContent =
            data.motion_count;

        document.getElementById("last-detection").textContent =
            data.last_detection || "No detection yet";

        document.getElementById("system-status").textContent =
            data.system_status;

        document.getElementById("alarm-status").textContent =
            data.alarm;

        const latestImage = document.getElementById("latest-image");
        const cameraPlaceholder =
            document.getElementById("camera-placeholder");

        const latestDetectionTitle =
            document.getElementById("latest-detection-title");

        const latestDetectionText =
            document.getElementById("latest-detection-text");


        if (data.latest_image) {

            latestImage.src =
                `/static/captures/${data.latest_image}?t=${Date.now()}`;

            latestImage.style.display = "block";

            cameraPlaceholder.style.display = "none";

            latestDetectionTitle.textContent =
                "Motion Detected";

            latestDetectionText.textContent =
                `Detected on ${data.last_detection}`;

        }

    } catch (error) {
        console.error("Error loading system status:", error);
    }
}


async function simulateMotion() {
    try {
        const response = await fetch("/api/detection", {
            method: "POST"
        });

        const data = await response.json();

        if (data.success) {
            alert("Motion detected!");

            loadStatus();
        }

    } catch (error) {
        console.error("Error simulating motion:", error);
    }
}


loadStatus();

setInterval(loadStatus, 2000);