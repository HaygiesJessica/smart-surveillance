"use strict";

(() => {
  const U = window.SecurityUI;

  let status = null;
  let recordsAt = 0;
  let lastBusy = false;
  let recordsKey = "";
  let captureKey = "";
  let pending = false;
  let timer;

  const button = U.byId("simulate-btn");

  const hints = {
    MONITORING: "Waiting for motion activity.",
    "MOTION DETECTED": "Motion detected. Preparing capture.",
    CAPTURING: "Creating a still image capture.",
    "ALARM ACTIVE": "LED and buzzer alarm active.",
    "EVENT SAVED": "Detection recorded in event history.",
  };

  function renderStatus(data) {
    status = data;
    U.updateMode(data);

    button.hidden = !data.simulation_mode;
    button.disabled = Boolean(data.busy) || pending;
    button.textContent = data.busy
      ? "Processing motion…"
      : "＋ Simulate motion";

    const motion = data.motion_sensor === "Motion Detected";

    const level =
      data.error || data.led || data.buzzer
        ? "danger"
        : data.busy
          ? "warning"
          : "success";

    U.text("system-state", data.state);
    U.text(
      "system-hint",
      data.error || hints[data.state] || "Reported monitoring state"
    );

    U.byId("system-dot").className = `status-dot ${level}`;
    U.byId("system-status").className = `system-status ${level}`;

    U.text("camera-stat", data.camera_status);
    U.text(
      "camera-stat-note",
      data.simulation_mode
        ? "Simulated capture source"
        : "Connection unverified"
    );

    U.text("motion-stat", data.motion_sensor);

    U.tone(
      U.byId("pir-state"),
      data.motion_sensor,
      motion ? "warning" : "success"
    );

    U.tone(
      U.byId("camera-state"),
      data.camera_status,
      data.camera_status === "Ready" ? "success" : "warning"
    );

    U.tone(
      U.byId("led-state"),
      data.led ? "On" : "Off",
      data.led ? "danger" : "neutral"
    );

    U.tone(
      U.byId("buzzer-state"),
      data.buzzer ? "On" : "Off",
      data.buzzer ? "danger" : "neutral"
    );

    U.text(
      "camera-label",
      data.simulation_mode ? "SIMULATED" : "STILL CAPTURE"
    );

    U.text(
      "camera-connection",
      data.simulation_mode
        ? "Simulation mode uses generated placeholder captures. No live video is streamed."
        : "Camera connection is not verified by the status API. Captures may use a placeholder if the webcam fails."
    );

    U.text(
      "settings-mode",
      data.simulation_mode ? "Simulation" : "Hardware"
    );

    U.text(
      "settings-source",
      data.simulation_mode
        ? "Generated simulation image"
        : "Webcam with placeholder fallback"
    );
  }

  function renderCapture(event) {
    const key = event ? `${event.id}:${event.image}` : "";

    if (key === captureKey) return;
    captureKey = key;

    U.byId("capture-placeholder").querySelector("h3").textContent =
      "No capture available";

    U.byId("capture-placeholder").querySelector("p").textContent =
      "A captured image will appear after a motion event.";

    const image = U.byId("capture-image");
    const placeholder = U.byId("capture-placeholder");

    image.hidden = true;
    placeholder.hidden = false;
    U.byId("enlarge-btn").disabled = true;

    U.text(
      "capture-caption",
      event
        ? `Event #${String(event.id).padStart(3, "0")}`
        : "No recorded capture"
    );

    U.text("capture-time", event?.detected_at || "—");

    if (event?.image) {
      image.onload = () => {
        image.hidden = false;
        placeholder.hidden = true;
        U.byId("enlarge-btn").disabled = false;
      };

      image.onerror = () => {
        image.hidden = true;
        placeholder.hidden = false;
        U.byId("enlarge-btn").disabled = true;

        placeholder.querySelector("h3").textContent = "Capture unavailable";
        placeholder.querySelector("p").textContent =
          "The recorded image could not be loaded.";
      };

      image.src = U.imageUrl(event.image);
    }
  }

  function chart(events, serverDate) {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(serverDate || "")) {
      U.text(
        "analytics-note",
        "The monitoring server did not provide a date. Daily analytics are unavailable."
      );
      return;
    }

    const dates = [];
    const today = new Date(`${serverDate}T12:00:00Z`);

    for (let ago = 6; ago >= 0; ago--) {
      const day = new Date(today);
      day.setUTCDate(day.getUTCDate() - ago);

      dates.push({
        date: day.toISOString().slice(0, 10),
        label: day.toLocaleDateString("en", {
          weekday: "short",
          timeZone: "UTC",
        }),
        count: 0,
      });
    }

    const counts = new Map(dates.map(day => [day.date, day]));
    let unknown = 0;

    for (const event of events) {
      const date = (event.detected_at || "").slice(0, 10);

      if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) {
        unknown++;
        continue;
      }

      if (counts.has(date)) counts.get(date).count++;
    }

    const max = Math.max(1, ...dates.map(day => day.count));
    const fragment = document.createDocumentFragment();

    for (const day of dates) {
      const column = document.createElement("div");
      column.className = "chart-column";
      column.setAttribute(
        "aria-label",
        `${day.date}: ${day.count} events`
      );

      const value = document.createElement("strong");
      value.textContent = day.count;

      const track = document.createElement("div");
      track.className = "chart-track";

      const bar = document.createElement("div");
      bar.className = "chart-bar";
      bar.style.height = `${(100 * day.count) / max}%`;

      track.append(bar);

      const label = document.createElement("span");
      label.textContent = day.label;

      const date = document.createElement("small");
      date.textContent = day.date.slice(5);

      column.append(value, track, label, date);
      fragment.append(column);
    }

    U.byId("daily-chart").replaceChildren(fragment);

    U.text(
      "week-total",
      dates.reduce((sum, day) => sum + day.count, 0)
    );

    U.text(
      "analytics-note",
      `Period ending ${serverDate}. Counts include recorded events only.${
        unknown ? ` ${unknown} undated records excluded.` : ""
      }`
    );
  }

  async function refreshRecords() {
    try {
      const [stats, events] = await Promise.all([
        U.api("/api/stats"),
        U.api("/api/detections"),
      ]);

      U.text("total-events", stats.total_events);
      U.text("today-events", stats.today_events);

      const key = JSON.stringify([stats.server_date, events]);

      if (key !== recordsKey) {
        U.eventRows(U.byId("alerts-body"), events.slice(0, 5));
        U.text("alert-count", Math.min(events.length, 5));

        chart(events, stats.server_date);
        recordsKey = key;
      }

      // Match the capture image, event ID and timestamp to persisted history.
      renderCapture(stats.latest_event);
      U.reportError("records", null);
      recordsAt = Date.now();
    } catch (error) {
      if (!recordsKey) {
        U.tableMessage(
          U.byId("alerts-body"),
          "Recorded events are unavailable. Reconnecting…"
        );

        U.text(
          "analytics-note",
          "Event data is unavailable. Reconnecting…"
        );
      }

      U.reportError(
        "records",
        `Event data unavailable; displayed records may be stale. ${error.message}`
      );

      recordsAt = Date.now();
    }
  }

  async function poll() {
    clearTimeout(timer);

    if (!document.hidden) {
      try {
        const data = await U.api("/api/status");

        renderStatus(data);
        U.reportError("status", null);

        if (
          !recordsAt ||
          Date.now() - recordsAt >= 15000 ||
          (lastBusy && !data.busy) ||
          data.state === "EVENT SAVED"
        ) {
          await refreshRecords();
        }

        lastBusy = data.busy;
      } catch (error) {
        U.disconnected();
        button.disabled = true;

        U.byId("system-status").className = "system-status warning";
        U.byId("system-dot").className = "status-dot warning";

        U.text("system-state", "Service unavailable");
        U.text(
          "system-hint",
          "Last reported device values may be stale. Reconnecting…"
        );

        U.reportError(
          "status",
          `Cannot update monitoring status. ${error.message}`
        );
      }
    }

    timer = setTimeout(poll, status?.busy ? 1000 : 3000);
  }

  button.addEventListener("click", async () => {
    if (pending || !status?.simulation_mode || status.busy) return;

    pending = true;
    button.disabled = true;

    try {
      const result = await U.api("/api/simulate-motion", {
        method: "POST",
      });

      if (!result.success) {
        throw new Error(
          result.message || "Motion request was not accepted."
        );
      }

      U.reportError("simulation", null);
      status.busy = true;
      button.textContent = "Processing motion…";
    } catch (error) {
      U.reportError("simulation", error.message);
    } finally {
      pending = false;
      button.disabled = Boolean(status?.busy);
    }
  });

  U.byId("enlarge-btn").addEventListener("click", () => {
    U.preview(U.byId("capture-image").src);
  });

  document.addEventListener("visibilitychange", () => {
    if (!document.hidden) recordsAt = 0;
  });

  poll();
})();