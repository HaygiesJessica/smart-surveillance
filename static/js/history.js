async function loadDetectionHistory() {
    try {
        const response = await fetch("/api/detections");

        if (!response.ok) {
            throw new Error("Failed to load detection history");
        }

        const detections = await response.json();

        const historyBody =
            document.getElementById("history-body");

        historyBody.innerHTML = "";

        if (detections.length === 0) {
            historyBody.innerHTML = `
                <tr>
                    <td colspan="4" class="empty-history">
                        No motion events recorded yet.
                    </td>
                </tr>
            `;

            return;
        }

        detections.forEach(detection => {

            let imageContent = `
                <span class="no-image">
                    No Image
                </span>
            `;

            if (detection.image) {
                imageContent = `
                    <img
                        src="/static/captures/${detection.image}"
                        class="history-image"
                        alt="Detection ${detection.id}"
                        onclick="openImagePreview('/static/captures/${detection.image}')">
                        `;
                }

            const row = document.createElement("tr");

            row.innerHTML = `
                <td>#${detection.id}</td>

                <td>
                    ${imageContent}
                </td>

                <td>${detection.detected_at}</td>

                <td>
                    <span class="detected-badge">
                        Motion Detected
                    </span>
                </td>
            `;

            historyBody.appendChild(row);
        });

    } catch (error) {
        console.error(
            "Error loading detection history:",
            error
        );

        const historyBody =
            document.getElementById("history-body");

        historyBody.innerHTML = `
            <tr>
                <td colspan="4" class="empty-history">
                    Error loading detection history.
                </td>
            </tr>
        `;
    }
}


loadDetectionHistory();

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