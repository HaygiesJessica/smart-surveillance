"use strict";

(() => {
  const U = window.SecurityUI;
  const pageSize = 20;

  let events = [];
  let page = 1;
  let key = "";
  let loading = false;
  let timer;

  function render() {
    const query = U.byId("event-search").value.trim().toLowerCase();
    const date = U.byId("event-date").value;
    const alarm = U.byId("alarm-filter").value;

    const filtered = events.filter(event =>
      (
        !query ||
        [
          event.id,
          `#${String(event.id).padStart(3, "0")}`,
          event.detected_at,
          event.event_type,
          event.alarm_status,
        ].join(" ").toLowerCase().includes(query)
      ) &&
      (!date || (event.detected_at || "").slice(0, 10) === date) &&
      (!alarm || event.alarm_status === alarm)
    );

    const pages = Math.max(1, Math.ceil(filtered.length / pageSize));
    page = Math.min(page, pages);

    U.eventRows(
      U.byId("history-body"),
      filtered.slice((page - 1) * pageSize, page * pageSize)
    );

    U.text(
      "results-count",
      `${filtered.length} matching event${
        filtered.length === 1 ? "" : "s"
      } · ${events.length} recorded`
    );

    U.text("page-label", `Page ${page} of ${pages}`);
    U.byId("previous-page").disabled = page === 1;
    U.byId("next-page").disabled = page === pages;
  }

  function alarms() {
    const select = U.byId("alarm-filter");
    const selected = select.value;

    const all = document.createElement("option");
    all.value = "";
    all.textContent = "All statuses";

    select.replaceChildren(all);

    [...new Set(events.map(event => event.alarm_status).filter(Boolean))]
      .sort()
      .forEach(value => {
        const option = document.createElement("option");
        option.value = value;
        option.textContent = value;
        select.append(option);
      });

    select.value = [...select.options].some(
      option => option.value === selected
    ) ? selected : "";
  }

  async function refresh() {
    if (loading) return;

    loading = true;
    U.byId("refresh-btn").disabled = true;

    try {
      const [stats, records, status] = await Promise.all([
        U.api("/api/stats"),
        U.api("/api/detections"),
        U.api("/api/status"),
      ]);

      U.updateMode(status);
      U.text("total-events", stats.total_events);
      U.text("today-events", stats.today_events);

      U.text(
        "last-detection",
        stats.latest_event?.detected_at || "No detections"
      );

      const newKey = JSON.stringify(records);

      if (newKey !== key) {
        events = records;
        key = newKey;
        alarms();
        render();
      }

      U.reportError("history", null);
    } catch (error) {
      U.disconnected();

      U.reportError(
        "history",
        `History could not be updated. ${error.message}`
      );

      if (!key) {
        U.text(
          "results-count",
          "History unavailable. Use Refresh to retry."
        );

        U.tableMessage(
          U.byId("history-body"),
          "Event history is unavailable. Use Refresh to retry."
        );
      }
    } finally {
      loading = false;
      U.byId("refresh-btn").disabled = false;
    }
  }

  ["event-search", "event-date", "alarm-filter"].forEach(id => {
    U.byId(id).addEventListener("input", () => {
      page = 1;
      render();
    });
  });

  U.byId("clear-filters").addEventListener("click", () => {
    ["event-search", "event-date", "alarm-filter"].forEach(id => {
      U.byId(id).value = "";
    });

    page = 1;
    render();
  });

  U.byId("previous-page").addEventListener("click", () => {
    page--;
    render();
  });

  U.byId("next-page").addEventListener("click", () => {
    page++;
    render();
  });

  U.byId("refresh-btn").addEventListener("click", refresh);

  async function poll() {
    clearTimeout(timer);

    if (!document.hidden) {
      await refresh();
    }

    timer = setTimeout(poll, 15000);
  }

  poll();
})();