(() => {
  const body = document.body;
  const screenDisplay = document.querySelector("[data-screen-time]");
  const languageDisplay = document.querySelector("[data-language-time]");
  let screenSeconds = Number(body.dataset.screenSeconds || 0);
  let languageSeconds = Number(body.dataset.languageSeconds || 0);
  let pendingSeconds = 0;
  let lastSent = 0;

  const formatTime = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const remainder = seconds % 60;
    if (hours) return `${hours}h ${String(minutes).padStart(2, "0")}m`;
    if (minutes) return `${minutes}m ${String(remainder).padStart(2, "0")}s`;
    return `${remainder}s`;
  };

  const sendTime = async () => {
    if (pendingSeconds <= 0) return;
    const seconds = Math.min(pendingSeconds, 45);
    pendingSeconds -= seconds;
    const payload = { seconds };
    if (body.dataset.language) payload.language = body.dataset.language;
    try {
      const response = await fetch("/api/time", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
        keepalive: true
      });
      if (!response.ok) throw new Error(`Time tracking failed (${response.status})`);
      const result = await response.json();
      screenSeconds = result.screen_seconds;
      if (body.dataset.language) languageSeconds = result.language_seconds;
      lastSent = Date.now();
    } catch (error) {
      pendingSeconds += seconds;
      console.error(error);
    }
  };

  window.setInterval(() => {
    if (document.visibilityState !== "visible") return;
    pendingSeconds += 1;
    screenSeconds += 1;
    if (body.dataset.language) languageSeconds += 1;
    if (screenDisplay) screenDisplay.textContent = formatTime(screenSeconds);
    if (languageDisplay) languageDisplay.textContent = formatTime(languageSeconds);
    if (pendingSeconds >= 15) sendTime();
  }, 1000);

  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "hidden" && pendingSeconds) sendTime();
  });
  window.addEventListener("pagehide", () => {
    if (pendingSeconds && navigator.sendBeacon) {
      const payload = { seconds: Math.min(pendingSeconds, 45) };
      if (body.dataset.language) payload.language = body.dataset.language;
      navigator.sendBeacon("/api/time", new Blob([JSON.stringify(payload)], { type: "application/json" }));
      pendingSeconds = 0;
    }
  });
})();
