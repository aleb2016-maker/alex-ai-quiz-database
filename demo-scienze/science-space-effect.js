(function () {
  if (window.__scienceSpaceEffectInstalledV2) {
    return;
  }

  window.__scienceSpaceEffectInstalledV2 = true;

  const symbols = ["⭐", "✨", "🌟", "🪐", "☄️", "🔭"];
  let lastEffectTime = 0;

  function randomBetween(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
  }

  function colorLooksGreen(rgbText) {
    const match = String(rgbText || "").match(/\d+/g);

    if (!match || match.length < 3) {
      return false;
    }

    const red = Number(match[0]);
    const green = Number(match[1]);
    const blue = Number(match[2]);

    return green > red + 35 && green > blue + 10;
  }

  function colorLooksRed(rgbText) {
    const match = String(rgbText || "").match(/\d+/g);

    if (!match || match.length < 3) {
      return false;
    }

    const red = Number(match[0]);
    const green = Number(match[1]);
    const blue = Number(match[2]);

    return red > green + 35 && red > blue + 20;
  }

  function classLooksCorrect(element) {
    const className = String(element.className || "").toLowerCase();

    return (
      className.includes("correct") ||
      className.includes("corretto") ||
      className.includes("corretta") ||
      className.includes("giusta") ||
      className.includes("right")
    );
  }

  function classLooksWrong(element) {
    const className = String(element.className || "").toLowerCase();

    return (
      className.includes("wrong") ||
      className.includes("errata") ||
      className.includes("sbagliata") ||
      className.includes("incorrect")
    );
  }

  function elementLooksCorrect(element) {
    const style = window.getComputedStyle(element);

    const backgroundIsGreen = colorLooksGreen(style.backgroundColor);
    const borderIsGreen = colorLooksGreen(style.borderColor);
    const textIsGreen = colorLooksGreen(style.color);

    const backgroundIsRed = colorLooksRed(style.backgroundColor);
    const borderIsRed = colorLooksRed(style.borderColor);
    const textIsRed = colorLooksRed(style.color);

    if (classLooksWrong(element) || backgroundIsRed || borderIsRed || textIsRed) {
      return false;
    }

    if (classLooksCorrect(element) || backgroundIsGreen || borderIsGreen || textIsGreen) {
      return true;
    }

    return false;
  }

  function launchScienceSpaceEffect(target) {
    const now = Date.now();

    if (now - lastEffectTime < 750) {
      return;
    }

    lastEffectTime = now;

    const rect = target.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;

    target.classList.add("science-correct-glow");

    setTimeout(function () {
      target.classList.remove("science-correct-glow");
    }, 950);

    for (let i = 0; i < 34; i++) {
      const element = document.createElement("span");
      const symbol = symbols[randomBetween(0, symbols.length - 1)];

      element.className = "science-space-object";
      element.textContent = symbol;

      const angle = (Math.PI * 2 * i) / 34;
      const distance = randomBetween(95, 260);

      const dx = Math.cos(angle) * distance + randomBetween(-35, 35);
      const dy = Math.sin(angle) * distance + randomBetween(-35, 35);

      element.style.setProperty("--x", centerX + "px");
      element.style.setProperty("--y", centerY + "px");
      element.style.setProperty("--dx", dx + "px");
      element.style.setProperty("--dy", dy + "px");
      element.style.setProperty("--rot", randomBetween(-320, 320) + "deg");
      element.style.setProperty("--size", randomBetween(18, 36) + "px");

      document.body.appendChild(element);

      setTimeout(function () {
        element.remove();
      }, 1450);
    }
  }

  document.addEventListener("click", function (event) {
    const clicked = event.target.closest(
      "button, .option, .answer, .risposta, [role='button'], label, li, div"
    );

    if (!clicked) {
      return;
    }

    setTimeout(function () {
      if (elementLooksCorrect(clicked)) {
        launchScienceSpaceEffect(clicked);
      }
    }, 260);
  }, true);
})();
