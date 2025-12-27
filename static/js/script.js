const messagesDiv = document.getElementById("messages");
const form = document.getElementById("inputForm");
const input = document.getElementById("queryInput");
const themeBtn = document.getElementById("themeToggle");

let chatHistory = [];

/* ====== ТЕМА ====== */
function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
    themeBtn.textContent = theme === "dark" ? "☀️" : "🌙";
}

if (themeBtn) {
    const saved = localStorage.getItem("theme") || "light";
    applyTheme(saved);

    themeBtn.addEventListener("click", () => {
        const current = document.documentElement.getAttribute("data-theme");
        applyTheme(current === "dark" ? "light" : "dark");
    });
}

/* ====== ЧАТ ====== */
form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const text = input.value.trim();
    if (!text) return;

    const userMsg = document.createElement("div");
    userMsg.classList.add("message", "user");
    userMsg.innerText = text;
    messagesDiv.appendChild(userMsg);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;

    chatHistory.push({ role: "user", content: text });
    input.value = "";

    try {
        const resp = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ messages: chatHistory })
        });

        const data = await resp.json();

        const botMsg = document.createElement("div");
        botMsg.classList.add("message", "bot");
        botMsg.innerText = data.answer;
        messagesDiv.appendChild(botMsg);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;

        chatHistory.push({ role: "assistant", content: data.answer });

    } catch (err) {
        console.error("Error:", err);
        alert("Connection lost");
    }
});
