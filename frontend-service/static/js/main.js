(function () {
  "use strict";

  const estimateForm = document.getElementById("estimate-form");
  const estimateResult = document.getElementById("estimate-result");
  const submitBtn = document.getElementById("submit-estimate");
  const btnText = submitBtn.querySelector(".btn-text");
  const btnSpinner = submitBtn.querySelector(".btn-spinner");

  const chatPanel = document.getElementById("chat-panel");
  const chatOverlay = document.getElementById("chat-overlay");
  const chatMessages = document.getElementById("chat-messages");
  const chatSuggestions = document.getElementById("chat-suggestions");
  const chatForm = document.getElementById("chat-form");
  const chatInput = document.getElementById("chat-input");

  document.getElementById("open-chat").addEventListener("click", openChat);
  document.getElementById("close-chat").addEventListener("click", closeChat);
  chatOverlay.addEventListener("click", closeChat);

  function openChat() {
    chatPanel.classList.add("open");
    chatPanel.setAttribute("aria-hidden", "false");
    chatOverlay.classList.remove("hidden");
    chatInput.focus();
  }

  function closeChat() {
    chatPanel.classList.remove("open");
    chatPanel.setAttribute("aria-hidden", "true");
    chatOverlay.classList.add("hidden");
  }

  function setLoading(loading) {
    submitBtn.disabled = loading;
    btnText.classList.toggle("hidden", loading);
    btnSpinner.classList.toggle("hidden", !loading);
  }

  function formatCurrency(amount, currency) {
    const symbol = currency === "INR" ? "₹" : "$";
    return symbol + Number(amount).toLocaleString(undefined, { minimumFractionDigits: 2 });
  }

  estimateForm.addEventListener("submit", async function (e) {
    e.preventDefault();
    setLoading(true);

    const payload = {
      name: document.getElementById("name").value.trim(),
      email: document.getElementById("email").value.trim(),
      event_type: document.getElementById("event_type").value,
      budget: parseFloat(document.getElementById("budget").value),
      budget_currency: document.getElementById("budget_currency").value,
      location: document.getElementById("location").value.trim(),
      special_requirements: document.getElementById("special_requirements").value.trim() || null,
    };

    try {
      const response = await fetch("/api/proxy/estimate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to generate estimate");
      }

      renderEstimate(data);
      estimateResult.classList.remove("hidden");
      estimateResult.scrollIntoView({ behavior: "smooth", block: "nearest" });
    } catch (err) {
      alert("Error: " + err.message);
    } finally {
      setLoading(false);
    }
  });

  function renderEstimate(data) {
    document.getElementById("result-tier").textContent = data.BudgetTier + " tier";
    document.getElementById("result-total").textContent = formatCurrency(
      data.TotalEstimatedCost,
      data.Currency
    );

    const breakdownEl = document.getElementById("result-breakdown");
    breakdownEl.innerHTML = "";
    Object.entries(data.EstimatedCostBreakdowns).forEach(function ([label, value]) {
      const item = document.createElement("div");
      item.className = "breakdown-item";
      item.innerHTML = "<span>" + label + "</span><strong>" + formatCurrency(value, data.Currency) + "</strong>";
      breakdownEl.appendChild(item);
    });

    const timelineEl = document.getElementById("result-timeline");
    timelineEl.innerHTML = "<h4>Suggested Timeline</h4><ol></ol>";
    const ol = timelineEl.querySelector("ol");
    data.SuggestedTimelinePlan.forEach(function (step) {
      const li = document.createElement("li");
      li.textContent = step;
      ol.appendChild(li);
    });

    document.getElementById("result-plan").textContent = data.GeneratedPlanText;
  }

  function appendMessage(text, role) {
    const div = document.createElement("div");
    div.className = "chat-msg " + role;
    div.textContent = text;
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function renderSuggestions(suggestions) {
    chatSuggestions.innerHTML = "";
    if (!suggestions || !suggestions.length) return;
    suggestions.forEach(function (s) {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.textContent = s;
      btn.addEventListener("click", function () {
        chatInput.value = s;
        chatForm.dispatchEvent(new Event("submit"));
      });
      chatSuggestions.appendChild(btn);
    });
  }

  chatForm.addEventListener("submit", async function (e) {
    e.preventDefault();
    const message = chatInput.value.trim();
    if (!message) return;

    appendMessage(message, "user");
    chatInput.value = "";
    chatSuggestions.innerHTML = "";

    try {
      const response = await fetch("/api/proxy/chatbot", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: message }),
      });
      const data = await response.json();
      appendMessage(data.reply || "Sorry, I couldn't process that.", "bot");
      renderSuggestions(data.suggestions);
    } catch (err) {
      appendMessage("Sorry, the assistant is temporarily unavailable.", "bot");
    }
  });
})();
