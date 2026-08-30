const $ = (id) => document.getElementById(id);
const input = $("input");
const analyzeBtn = $("analyze");
const sampleBtn = $("sample");
const status = $("status");
const results = $("results");
const externalTools = $("external-tools");
const suisiannLink = $("suisiann-link");

const fields = {
  tailo: "Tai-lo原",
  poj: "POJ原",
  segmentation: "分詞",
  sandhi: "變調",
  tailoSandhi: "Tai-lo變調",
  pojSandhi: "POJ變調",
};

let currentLanguage = "ko";

function setLanguage(lang, save = false) {
  const t = translations[lang];
  if (!t) return;

  currentLanguage = lang;
  document.documentElement.lang = lang;
  document.title = t.title;

  const metaDescription = document.querySelector('meta[name="description"]');

  if (metaDescription) {
    metaDescription.content = t.description;
  }

  document.querySelectorAll("[data-i18n]").forEach((element) => {
    const key = element.dataset.i18n;
    if (t[key] !== undefined) {
      element.textContent = t[key];
    }
  });

  document.querySelectorAll("[data-i18n-aria-label]").forEach((element) => {
    const key = element.dataset.i18nAriaLabel;
    if (t[key] !== undefined) {
      element.setAttribute("aria-label", t[key]);
    }
  });

  document.querySelectorAll("[data-lang]").forEach((button) => {
    button.classList.toggle("active", button.dataset.lang === lang);
  });

  if (save) {
    localStorage.setItem("language", lang);
  }
}

document.querySelectorAll("[data-lang]").forEach((button) => {
  button.addEventListener("click", () => {
    setLanguage(button.dataset.lang, true);
  });
});

const savedLanguage = localStorage.getItem("language");

if (savedLanguage && translations[savedLanguage]) {
  setLanguage(savedLanguage);
} else {
  const browserLanguage = navigator.language.toLowerCase();

  if (browserLanguage.startsWith("ko")) {
    setLanguage("ko");
  } else if (browserLanguage.startsWith("zh")) {
    setLanguage("zh-TW");
  } else {
    setLanguage("en");
  }
}

async function runAnalysis() {
  const text = input.value.trim();
  const t = translations[currentLanguage];

  if (!text) {
    status.textContent = t.emptyInput;
    input.focus();
    return;
  }

  analyzeBtn.disabled = true;
  status.textContent = t.analyzing;
  results.classList.add("hidden");

  try {
    const response = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    const data = await response.json();
    if (!response.ok || !data.ok) throw new Error(t.analysisFailed);

    const r = data.result;
    Object.entries(fields).forEach(([elementId, key]) => {
      $(elementId).textContent = r[key] ?? "";
    });
    results.classList.remove("hidden");
    suisiannLink.href =
      "https://suisiann.ithuan.tw/%E8%AC%9B/" + encodeURIComponent(text);
    externalTools.classList.remove("hidden");
    status.textContent = "";
  } catch (err) {
    status.textContent = err.message;
  } finally {
    analyzeBtn.disabled = false;
  }
}

analyzeBtn.addEventListener("click", runAnalysis);
sampleBtn.addEventListener("click", () => {
  input.value = "人生的無奈,咱嘛是愛忍耐";
  input.focus();
});
input.addEventListener("keydown", (event) => {
  if ((event.ctrlKey || event.metaKey) && event.key === "Enter") runAnalysis();
});

suisiannLink.addEventListener("click", (event) => {
  const isDesktop = window.matchMedia("(min-width: 768px)").matches;

  // 모바일에서는 HTML의 target="_blank" 동작 그대로 사용
  if (!isDesktop) return;

  event.preventDefault();

  const popup = window.open(
    suisiannLink.href,
    "suisiann-player",
    "width=630,height=790,resizable=yes,scrollbars=yes",
  );

  if (popup) {
    popup.focus();
  }
});

$("license-open").addEventListener("click", () =>
  $("license-dialog").showModal(),
);
$("license-close").addEventListener("click", () => $("license-dialog").close());
$("license-dialog").addEventListener("click", (event) => {
  if (event.target === $("license-dialog")) $("license-dialog").close();
});

$("usage-open").addEventListener("click", () => $("usage-dialog").showModal());

$("usage-close").addEventListener("click", () => $("usage-dialog").close());

$("usage-dialog").addEventListener("click", (event) => {
  if (event.target === $("usage-dialog")) $("usage-dialog").close();
});

document.querySelectorAll(".copy").forEach((button) => {
  button.addEventListener("click", async () => {
    const target = $(button.dataset.copy);
    await navigator.clipboard.writeText(target.textContent);
    const old = button.textContent;
    button.textContent = translations[currentLanguage].copied;
    setTimeout(() => (button.textContent = old), 800);
  });
});
