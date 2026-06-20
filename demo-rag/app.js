const input = document.getElementById("documentInput");
const result = document.getElementById("fileResult");
const themeSelect = document.getElementById("themeSelect");
const themeCommand = document.getElementById("themeCommand");

const savedTheme = localStorage.getItem("alex-rag-theme") || "dark-tech";
document.body.dataset.theme = savedTheme;
themeSelect.value = savedTheme;
themeCommand.textContent = `python3 scripts/applica_tema_formazione.py ${savedTheme}`;

themeSelect.addEventListener("change", () => {
  const theme = themeSelect.value;
  document.body.dataset.theme = theme;
  localStorage.setItem("alex-rag-theme", theme);
  themeCommand.textContent = `python3 scripts/applica_tema_formazione.py ${theme}`;
});

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

input.addEventListener("change", () => {
  const file = input.files && input.files[0];

  if (!file) {
    result.textContent = "Nessun documento selezionato.";
    return;
  }

  const safeName = file.name.replace(/[^a-zA-Z0-9._-]/g, "_");
  const title = file.name.replace(/\.[^.]+$/, "");
  const command = `cp ~/Downloads/${safeName} rag/documenti/${safeName}\npython3 scripts/pipeline_formazione_completa.py rag/documenti/${safeName} --titolo "${title}"`;

  result.innerHTML = `
    <strong>Documento selezionato:</strong> ${file.name}<br>
    <strong>Dimensione:</strong> ${formatBytes(file.size)}<br>
    <strong>Tipo:</strong> ${file.type || "non dichiarato"}<br><br>
    <strong>Comando consigliato:</strong>
    <pre class="code-box">${command}</pre>
  `;

  const lowerName = file.name.toLowerCase();
  const canPreview =
    lowerName.endsWith(".txt") ||
    lowerName.endsWith(".md") ||
    lowerName.endsWith(".json") ||
    lowerName.endsWith(".csv");

  if (canPreview) {
    const reader = new FileReader();
    reader.onload = () => {
      const preview = String(reader.result || "").slice(0, 900);
      const escaped = preview.replace(/[<>&]/g, ch => ({"<":"&lt;", ">":"&gt;", "&":"&amp;"}[ch]));
      result.innerHTML += `<strong>Anteprima locale:</strong><pre class="code-box">${escaped}</pre>`;
    };
    reader.readAsText(file);
  }
});
