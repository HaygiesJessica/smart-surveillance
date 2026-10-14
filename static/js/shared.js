/* Shared UI helpers. No framework, injected HTML, or synthetic monitoring data. */
"use strict";

window.SecurityUI = (() => {
  const byId = id => document.getElementById(id);

  const text = (id, value) => {
    const element = byId(id);
    if (element) element.textContent = value ?? "—";
  };

  const errors = new Map();

  function reportError(scope, message) {
    if (message) errors.set(scope, message);
    else errors.delete(scope);

    const element = byId("request-error");
    element.hidden = errors.size === 0;
    element.textContent = [...errors.values()].join(" ");
  }

  async function api(path, options = {}) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 8000);

    try {
      const response = await fetch(path, {
        cache: "no-store",
        ...options,
        signal: controller.signal,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.message || data.error || `Request failed (${response.status})`
        );
      }

      return data;
    } finally {
      clearTimeout(timer);
    }
  }

  function tone(element, value, level = "neutral") {
    if (!element) return;
    element.textContent = value;
    element.className = `device-state ${level}`;
  }

  function updateMode(status) {
    text(
      "mode-label",
      status.simulation_mode ? "Simulation mode" : "Hardware mode"
    );

    text(
      "mode-note",
      status.simulation_mode
        ? "Simulated sensors & captures"
        : "Physical devices configured"
    );

    const connection = byId("connection");
    connection.replaceChildren();

    const dot = document.createElement("span");
    dot.className = "status-dot success";

    connection.append(dot, document.createTextNode("Service connected"));
  }

  function disconnected() {
    const element = byId("connection");
    element.replaceChildren();

    const dot = document.createElement("span");
    dot.className = "status-dot warning";

    element.append(
      dot,
      document.createTextNode("Service unavailable · stale data")
    );

    text("mode-label", "Status unavailable");
    text("mode-note", "Last reported values may be stale");
  }

  function imageUrl(filename) {
    return `/static/captures/${encodeURIComponent(filename)}`;
  }

  function preview(url) {
    byId("modal-image").src = url;

    if (!byId("image-modal").open) {
      byId("image-modal").showModal();
    }
  }

  function tableMessage(body, message) {
    const row = document.createElement("tr");
    const cell = document.createElement("td");

    cell.colSpan = 5;
    cell.className = "table-message";
    cell.textContent = message;

    row.append(cell);
    body.replaceChildren(row);
  }

  function eventRows(body, events) {
    const fragment = document.createDocumentFragment();

    if (!events.length) {
      const row = document.createElement("tr");
      const cell = document.createElement("td");

      cell.colSpan = 5;
      cell.className = "table-message";
      cell.textContent = "No recorded events match this view.";

      row.append(cell);
      fragment.append(row);
    }

    for (const event of events) {
      const row = document.createElement("tr");

      const values = [
        `#${String(event.id).padStart(3, "0")}`,
        event.detected_at || "Unknown time",
        event.event_type || "Not recorded",
        event.alarm_status || "Not recorded",
      ];

      values.forEach((value, index) => {
        const cell = document.createElement("td");

        if (index === 2 || index === 3) {
          const badge = document.createElement("span");
          badge.className = `tag ${index === 2 ? "amber" : "neutral"}`;
          badge.textContent = value;
          cell.append(badge);
        } else {
          cell.textContent = value;
        }

        row.append(cell);
      });

      const imageCell = document.createElement("td");

      if (event.image) {
        const button = document.createElement("button");
        button.className = "thumbnail-button";
        button.setAttribute(
          "aria-label",
          `Preview capture for event ${event.id}`
        );

        const image = document.createElement("img");
        image.src = imageUrl(event.image);
        image.alt = `Capture for event ${event.id}`;
        image.loading = "lazy";
        image.width = 72;
        image.height = 44;

        image.addEventListener("error", () => {
          button.disabled = true;
          button.textContent = "Unavailable";
        });

        button.append(image);
        button.addEventListener("click", () => preview(imageUrl(event.image)));
        imageCell.append(button);
      } else {
        imageCell.textContent = "No image";
      }

      row.append(imageCell);
      fragment.append(row);
    }

    body.replaceChildren(fragment);
  }

  function nav() {
    const section =
      document.body.dataset.page === "history"
        ? "history"
        : location.hash.slice(1) || "overview";

    document.querySelectorAll("[data-section]").forEach(link => {
      const active = link.dataset.section === section;

      link.classList.toggle("active", active);

      if (active) link.setAttribute("aria-current", "location");
      else link.removeAttribute("aria-current");
    });
  }

  byId("close-preview").addEventListener("click", () => {
    byId("image-modal").close();
  });

  byId("image-modal").addEventListener("click", event => {
    if (event.target === byId("image-modal")) {
      byId("image-modal").close();
    }
  });

  byId("modal-image").addEventListener("error", () => {
    reportError("preview", "This capture could not be loaded.");
  });

  byId("image-modal").addEventListener("close", () => {
    reportError("preview", null);
  });

  window.addEventListener("hashchange", nav);
  nav();

  return {
    tableMessage,
    byId,
    text,
    api,
    tone,
    updateMode,
    disconnected,
    imageUrl,
    preview,
    eventRows,
    reportError,
  };
})();