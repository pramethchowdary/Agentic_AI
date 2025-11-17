let selectedToken = null;

// Check cooldown status from backend before selecting
async function checkCooldown(num) {
  try {
    const response = await fetch(`/check_token?token=${num}`);
    if (!response.ok) return null;
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error checking cooldown:", error);
    return null;
  }
}

// Token selection handler
async function selectToken(num) {
  const status = await checkCooldown(num);

  // If still cooling down
  if (status && status.remaining_seconds > 0) {
    const mins = Math.floor(status.remaining_seconds / 60);
    const secs = status.remaining_seconds % 60;
    document.getElementById("cooldownMessage").textContent =
      `⏳ Token ${num} is cooling down. Try again in ${mins}m ${secs}s.`;
    return; // stop user from selecting
  }

  // Safe to select
  selectedToken = num;
  document.getElementById("selectedToken").value = num;
  document.getElementById("cooldownMessage").textContent =
    `✅ Token ${num} selected. Ready for use.`;

  // Update button UI
  document.querySelectorAll(".token-btn").forEach(btn => {
    btn.classList.remove("active");
  });
  document.getElementById(`token${num}`).classList.add("active");
}

document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.getElementById("themeToggle");

  toggle.addEventListener("click", () => {
    document.body.classList.toggle("dark");
    toggle.textContent = document.body.classList.contains("dark")
      ? "☀️ Light Mode"
      : "🌙 Dark Mode";
  });

  // ✅ No more markTokenUsed here.
  // Backend handles cooldown only after successful extraction.
});
