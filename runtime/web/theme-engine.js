(function () {
  const STORAGE_KEY = "alex-theme-engine-choice";
  const root = document.documentElement;

  function applyTheme(themeName) {
    root.setAttribute("data-alex-theme", themeName || "dark-tech");
    try {
      localStorage.setItem(STORAGE_KEY, themeName || "dark-tech");
    } catch (_) {}
  }

  let saved = null;
  try {
    saved = localStorage.getItem(STORAGE_KEY);
  } catch (_) {}

  applyTheme(saved || root.getAttribute("data-alex-theme") || "dark-tech");
  window.AlexThemeEngine = { applyTheme };
})();
