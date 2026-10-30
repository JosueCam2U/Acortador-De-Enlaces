const API_BASE = "http://localhost:8000";

const form = document.getElementById("shortenForm");
const input = document.getElementById("urlInput");
const submitButton = document.getElementById("submitButton");
const message = document.getElementById("message");
const resultSection = document.getElementById("resultSection");
const resultLink = document.getElementById("resultLink");
const copyButton = document.getElementById("copyButton");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  message.textContent = "";
  message.classList.remove("success");
  resultSection.hidden = true;
  submitButton.disabled = true;
  submitButton.textContent = "Generando...";

  try {
    const response = await fetch(`${API_BASE}/shorten`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ original_url: input.value.trim() }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => null);
      throw new Error(error?.detail || "No se pudo generar el enlace corto.");
    }

    const data = await response.json();
    resultLink.href = data.short_url;
    resultLink.textContent = data.short_url;
    resultSection.hidden = false;
    message.textContent = "Enlace creado correctamente.";
    message.classList.add("success");
  } catch (error) {
    message.textContent =
      error instanceof TypeError
        ? "No se pudo conectar con el servidor. Verifica que el backend esté activo."
        : error.message;
  } finally {
    submitButton.disabled = false;
    submitButton.textContent = "Acortar enlace";
  }
});

copyButton.addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(resultLink.href);
    copyButton.textContent = "Copiado";
    window.setTimeout(() => {
      copyButton.textContent = "Copiar";
    }, 1800);
  } catch {
    message.textContent = "No se pudo copiar. Selecciona y copia el enlace manualmente.";
    message.classList.remove("success");
  }
});
