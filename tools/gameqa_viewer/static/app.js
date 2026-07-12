const state = {
  games: [],
  game: null,
  samples: [],
  filtered: [],
  selectedIndex: 0,
  detail: null,
};

const els = {
  globalStats: document.querySelector("#globalStats"),
  themeToggle: document.querySelector("#themeToggle"),
  gameSelect: document.querySelector("#gameSelect"),
  taskFilter: document.querySelector("#taskFilter"),
  qaLevelFilter: document.querySelector("#qaLevelFilter"),
  plotLevelFilter: document.querySelector("#plotLevelFilter"),
  sampleSearch: document.querySelector("#sampleSearch"),
  gameNote: document.querySelector("#gameNote"),
  listCount: document.querySelector("#listCount"),
  resetFilters: document.querySelector("#resetFilters"),
  sampleList: document.querySelector("#sampleList"),
  sampleKicker: document.querySelector("#sampleKicker"),
  sampleTitle: document.querySelector("#sampleTitle"),
  prevButton: document.querySelector("#prevButton"),
  nextButton: document.querySelector("#nextButton"),
  navPosition: document.querySelector("#navPosition"),
  imageFrame: document.querySelector("#imageFrame"),
  sampleImage: document.querySelector("#sampleImage"),
  imagePlaceholder: document.querySelector("#imagePlaceholder"),
  imageName: document.querySelector("#imageName"),
  imageOpenLink: document.querySelector("#imageOpenLink"),
  copyImage: document.querySelector("#copyImage"),
  copyQuestion: document.querySelector("#copyQuestion"),
  metaStrip: document.querySelector("#metaStrip"),
  questionText: document.querySelector("#questionText"),
  optionsBlock: document.querySelector("#optionsBlock"),
  optionsList: document.querySelector("#optionsList"),
  answerText: document.querySelector("#answerText"),
  analysisBlock: document.querySelector("#analysisBlock"),
  analysisText: document.querySelector("#analysisText"),
  stateBlock: document.querySelector("#stateBlock"),
  stateJson: document.querySelector("#stateJson"),
  rawJson: document.querySelector("#rawJson"),
  copyState: document.querySelector("#copyState"),
  copyRaw: document.querySelector("#copyRaw"),
  lightbox: document.querySelector("#lightbox"),
  lightboxImage: document.querySelector("#lightboxImage"),
};

const QA_LEVEL_ORDER = { easy: 0, medium: 1, hard: 2 };
const HIGHLIGHT_LIMIT = 300000; // skip syntax highlighting for very large JSON

async function getJson(url) {
  const response = await fetch(url);
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error || `Request failed: ${url}`);
  }
  return payload;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderRichText(value) {
  const escaped = escapeHtml(value || "");
  return escaped
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/`([^`\n]+)`/g, "<code>$1</code>")
    .replace(/\n/g, "<br>");
}

function stringify(value) {
  if (value === null || value === undefined || value === "") {
    return "";
  }
  if (typeof value === "object") {
    return JSON.stringify(value, null, 2);
  }
  return String(value);
}

function highlightJson(text) {
  if (typeof text !== "string" || !text) return "";
  if (text.length > HIGHLIGHT_LIMIT) return escapeHtml(text);
  const re = /"(?:\\.|[^"\\])*"(\s*:)?|\b(?:true|false|null)\b|-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?/g;
  let out = "";
  let last = 0;
  let match;
  while ((match = re.exec(text))) {
    out += escapeHtml(text.slice(last, match.index));
    const token = match[0];
    if (token[0] === '"') {
      if (match[1]) {
        const key = token.slice(0, token.length - match[1].length);
        out += `<span class="j-key">${escapeHtml(key)}</span>${escapeHtml(match[1])}`;
      } else {
        out += `<span class="j-str">${escapeHtml(token)}</span>`;
      }
    } else if (token === "true" || token === "false") {
      out += `<span class="j-bool">${token}</span>`;
    } else if (token === "null") {
      out += `<span class="j-null">${token}</span>`;
    } else {
      out += `<span class="j-num">${token}</span>`;
    }
    last = match.index + token.length;
  }
  return out + escapeHtml(text.slice(last));
}

function option(label, value, selected = false) {
  const node = document.createElement("option");
  node.value = value;
  node.textContent = label;
  node.selected = selected;
  return node;
}

function fillSelect(select, items, selectedValue = "") {
  select.replaceChildren(...items.map((item) => option(item.label, item.value, item.value === selectedValue)));
}

function chip(label, value) {
  if (value === undefined || value === null || value === "") {
    return "";
  }
  return `<span class="chip"><b>${escapeHtml(label)}</b>${escapeHtml(value)}</span>`;
}

function taskKey(sample) {
  return [
    sample.question_id ?? "",
    sample.question_description ?? "",
    sample.qa_type ?? "",
    sample.qa_level ?? "",
  ].join("||");
}

function taskLabel(sample) {
  const desc = sample.question_description || `question ${sample.question_id ?? "?"}`;
  const tags = [sample.qa_level, sample.qa_type].filter(Boolean).join(" · ");
  return tags ? `${desc} (${tags})` : desc;
}

function taskSortValue(sample) {
  const numeric = Number(sample.question_id);
  return Number.isFinite(numeric) ? numeric : Number.POSITIVE_INFINITY;
}

function qaLevelSort(a, b) {
  const oa = QA_LEVEL_ORDER[a.toLowerCase()] ?? 99;
  const ob = QA_LEVEL_ORDER[b.toLowerCase()] ?? 99;
  return oa - ob || a.localeCompare(b);
}

async function init() {
  initTheme();
  const payload = await getJson("/api/games");
  state.games = payload.games;
  const totalSamples = state.games.reduce((sum, game) => sum + game.count, 0);
  els.globalStats.innerHTML = [
    `<span class="stat-pill">${state.games.length} games</span>`,
    `<span class="stat-pill">${totalSamples} samples</span>`,
  ].join("");

  fillSelect(
    els.gameSelect,
    state.games.map((game) => ({ label: `${game.name} (${game.count})`, value: game.id })),
  );

  const params = new URLSearchParams(location.search);
  const initialGame = params.get("game") || state.games[0]?.id;
  els.gameSelect.value = initialGame;
  await loadGame(initialGame, Number(params.get("sample") || 0));
}

async function loadGame(gameId, sampleIndex = 0) {
  state.game = state.games.find((game) => game.id === gameId);
  const payload = await getJson(`/api/games/${encodeURIComponent(gameId)}/samples`);
  state.samples = payload.samples;

  const taskMap = new Map();
  for (const sample of state.samples) {
    const key = taskKey(sample);
    if (!taskMap.has(key)) {
      taskMap.set(key, { label: taskLabel(sample), value: key, order: taskSortValue(sample) });
    }
  }
  const tasks = [...taskMap.values()].sort((a, b) => a.order - b.order || a.label.localeCompare(b.label));
  const qaLevels = [...new Set(state.samples.map((sample) => sample.qa_level).filter((value) => value !== null && value !== undefined))]
    .map(String)
    .sort(qaLevelSort);
  const plotLevels = [...new Set(state.samples.map((sample) => sample.plot_level).filter((value) => value !== null && value !== undefined))]
    .map(String)
    .sort(qaLevelSort);
  fillSelect(els.taskFilter, [{ label: "All tasks", value: "" }, ...tasks]);
  fillSelect(els.qaLevelFilter, [{ label: "All difficulties", value: "" }, ...qaLevels.map((value) => ({ label: value, value }))]);
  fillSelect(els.plotLevelFilter, [{ label: "All plots", value: "" }, ...plotLevels.map((value) => ({ label: value, value }))]);
  els.sampleSearch.value = "";

  renderGameNote();
  applyFilters();
  const target = state.samples.some((sample) => sample.index === sampleIndex) ? sampleIndex : state.filtered[0]?.index ?? 0;
  await selectSample(target);
}

function renderGameNote() {
  const game = state.game;
  const missing = [];
  if (game.image_missing) missing.push(`${game.image_missing} missing image${game.image_missing > 1 ? "s" : ""}`);
  if (game.state_missing) missing.push(`${game.state_missing} missing state${game.state_missing > 1 ? "s" : ""}`);
  const parts = [
    `<span class="note-path" title="${escapeHtml(game.data_path)}">${escapeHtml(game.data_path)}</span>`,
    `<span class="note-meta">${game.keys.length} fields</span>`,
  ];
  if (game.load_error) {
    parts.push(`<span class="note-warn">load error: ${escapeHtml(game.load_error)}</span>`);
  } else if (missing.length) {
    parts.push(`<span class="note-warn">⚠ ${escapeHtml(missing.join(", "))}</span>`);
  } else {
    parts.push(`<span class="note-ok">✓ all referenced files found</span>`);
  }
  els.gameNote.innerHTML = parts.join("");
}

function hasActiveFilters() {
  return Boolean(els.taskFilter.value || els.qaLevelFilter.value || els.plotLevelFilter.value || els.sampleSearch.value.trim());
}

function applyFilters() {
  const selectedTask = els.taskFilter.value;
  const qaLevel = els.qaLevelFilter.value;
  const plotLevel = els.plotLevelFilter.value;
  const query = els.sampleSearch.value.trim().toLowerCase();
  state.filtered = state.samples.filter((sample) => {
    if (selectedTask && taskKey(sample) !== selectedTask) return false;
    if (qaLevel && String(sample.qa_level) !== qaLevel) return false;
    if (plotLevel && String(sample.plot_level) !== plotLevel) return false;
    if (!query) return true;
    return [
      sample.data_id,
      sample.question_id,
      sample.question_description,
      sample.question_preview,
      sample.answer_preview,
      sample.qa_type,
      sample.qa_level,
      sample.plot_level,
    ]
      .join(" ")
      .toLowerCase()
      .includes(query);
  });

  els.listCount.textContent =
    state.filtered.length === state.samples.length
      ? `${state.samples.length} sample${state.samples.length === 1 ? "" : "s"}`
      : `${state.filtered.length} / ${state.samples.length} samples`;
  els.resetFilters.hidden = !hasActiveFilters();
  renderSampleList();
}

function renderSampleList() {
  if (!state.filtered.length) {
    els.sampleList.innerHTML = `<div class="empty-state">No matching samples</div>`;
    return;
  }

  els.sampleList.replaceChildren(
    ...state.filtered.map((sample) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = `sample-card${sample.index === state.selectedIndex ? " active" : ""}`;
      button.dataset.index = sample.index;
      button.innerHTML = `
        <div class="sample-title-row">
          <span class="sample-id">#${escapeHtml(sample.index)} · ${escapeHtml(sample.data_id ?? "sample")}</span>
          <span class="sample-answer">${escapeHtml(sample.answer_preview)}</span>
        </div>
        <p>${escapeHtml(sample.question_description || sample.question_preview)}</p>
        <div class="mini-tags">
          ${sample.qa_type ? `<span class="mini-tag tag-type">${escapeHtml(sample.qa_type)}</span>` : ""}
          ${sample.qa_level ? `<span class="mini-tag level-${escapeHtml(String(sample.qa_level).toLowerCase())}">${escapeHtml(sample.qa_level)}</span>` : ""}
          ${sample.plot_level ? `<span class="mini-tag tag-plot plot-${escapeHtml(String(sample.plot_level).toLowerCase())}">plot ${escapeHtml(sample.plot_level)}</span>` : ""}
        </div>
      `;
      button.addEventListener("click", () => selectSample(sample.index));
      return button;
    }),
  );
  scrollActiveCardIntoView();
}

function scrollActiveCardIntoView() {
  const active = els.sampleList.querySelector(".sample-card.active");
  if (!active) return;
  // Scroll only the list itself; scrollIntoView would also scroll
  // overflow-hidden ancestors and shift the whole sidebar/page.
  const list = els.sampleList;
  const listRect = list.getBoundingClientRect();
  const cardRect = active.getBoundingClientRect();
  if (cardRect.top < listRect.top) {
    list.scrollTop += cardRect.top - listRect.top;
  } else if (cardRect.bottom > listRect.bottom) {
    list.scrollTop += cardRect.bottom - listRect.bottom;
  }
}

async function selectSample(index) {
  state.selectedIndex = Number(index);
  let payload;
  try {
    payload = await getJson(`/api/games/${encodeURIComponent(state.game.id)}/samples/${state.selectedIndex}`);
  } catch (error) {
    els.sampleTitle.textContent = `Failed to load sample: ${error.message}`;
    return;
  }
  renderDetail(payload.sample);
  renderSampleList();

  const url = new URL(location.href);
  url.searchParams.set("game", state.game.id);
  url.searchParams.set("sample", String(state.selectedIndex));
  history.replaceState(null, "", url);
}

function renderDetail(sample) {
  state.detail = sample;
  els.sampleKicker.textContent = `${state.game.name} · sample ${sample.index}`;
  els.sampleTitle.textContent = sample.question_description || `Question ${sample.question_id ?? sample.index}`;

  if (sample.image_url) {
    els.sampleImage.src = sample.image_url;
    els.sampleImage.alt = `${state.game.name} ${sample.image || "sample image"}`;
    els.sampleImage.hidden = false;
    els.imagePlaceholder.hidden = true;
    els.imageFrame.classList.add("zoomable");
    els.imageName.textContent = sample.image || "";
    els.imageOpenLink.href = sample.image_url;
    els.imageOpenLink.hidden = false;
    els.copyImage.hidden = false;
  } else {
    els.sampleImage.removeAttribute("src");
    els.sampleImage.hidden = true;
    els.imagePlaceholder.hidden = false;
    els.imageFrame.classList.remove("zoomable");
    els.imageName.textContent = "";
    els.imageOpenLink.hidden = true;
    els.copyImage.hidden = true;
  }

  els.metaStrip.innerHTML = [
    chip("data_id", sample.data_id),
    chip("question_id", sample.question_id),
    chip("qa_type", sample.qa_type),
    chip("qa_level", sample.qa_level),
    chip("plot_level", sample.plot_level),
    chip("image", sample.image),
    chip("state", sample.state),
  ].join("");

  els.questionText.innerHTML = renderRichText(sample.question);

  const options = Array.isArray(sample.options) ? sample.options : [];
  const answerNumber = Number(sample.answer);
  const correctIndex =
    options.length && Number.isInteger(answerNumber) && answerNumber >= 1 && answerNumber <= options.length
      ? answerNumber - 1
      : -1;

  els.optionsBlock.hidden = options.length === 0;
  els.optionsList.replaceChildren(
    ...options.map((item, index) => {
      const li = document.createElement("li");
      li.textContent = stringify(item);
      if (index === correctIndex) {
        li.className = "correct";
        const badge = document.createElement("span");
        badge.className = "correct-badge";
        badge.textContent = "✓ answer";
        li.appendChild(badge);
      }
      return li;
    }),
  );

  let answerDisplay = stringify(sample.answer);
  if (correctIndex >= 0) {
    answerDisplay = `${answerDisplay}: ${stringify(options[correctIndex])}`;
  }
  els.answerText.textContent = answerDisplay;

  els.analysisBlock.hidden = !sample.analysis;
  els.analysisText.innerHTML = renderRichText(sample.analysis);

  if (sample.state_error) {
    els.stateJson.textContent = sample.state_error;
    els.stateBlock.dataset.text = sample.state_error;
  } else if (sample.state_content !== null && sample.state_content !== undefined) {
    const stateText = JSON.stringify(sample.state_content, null, 2);
    els.stateJson.innerHTML = highlightJson(stateText);
    els.stateBlock.dataset.text = stateText;
  } else {
    els.stateJson.textContent = "No state file for this sample";
    els.stateBlock.dataset.text = "";
  }
  const rawText = JSON.stringify(sample.raw, null, 2);
  els.rawJson.innerHTML = highlightJson(rawText);
  els.rawJson.dataset.text = rawText;

  const currentPosition = state.filtered.findIndex((item) => item.index === sample.index);
  els.navPosition.textContent = currentPosition >= 0 ? `${currentPosition + 1} / ${state.filtered.length}` : `– / ${state.filtered.length}`;
  els.prevButton.disabled = currentPosition <= 0;
  els.nextButton.disabled = currentPosition < 0 || currentPosition >= state.filtered.length - 1;
}

function stepSample(delta) {
  const position = state.filtered.findIndex((sample) => sample.index === state.selectedIndex);
  const next = state.filtered[position + delta];
  if (next) {
    selectSample(next.index);
  }
}

async function copyText(button, text) {
  if (!text) return;
  try {
    await navigator.clipboard.writeText(text);
  } catch {
    const helper = document.createElement("textarea");
    helper.value = text;
    document.body.appendChild(helper);
    helper.select();
    document.execCommand("copy");
    helper.remove();
  }
  const original = button.textContent;
  button.textContent = "Copied ✓";
  button.classList.add("copied");
  setTimeout(() => {
    button.textContent = original;
    button.classList.remove("copied");
  }, 1200);
}

async function copyImageToClipboard(button) {
  const url = state.detail?.image_url;
  if (!url) return;
  const original = button.textContent;
  try {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    let blob = await response.blob();
    if (blob.type !== "image/png") {
      // Clipboard API only accepts PNG for images; re-encode losslessly
      // from the decoded pixels (no quality parameter is involved for PNG).
      const bitmap = await createImageBitmap(blob);
      const canvas = document.createElement("canvas");
      canvas.width = bitmap.width;
      canvas.height = bitmap.height;
      canvas.getContext("2d").drawImage(bitmap, 0, 0);
      blob = await new Promise((resolve, reject) =>
        canvas.toBlob((result) => (result ? resolve(result) : reject(new Error("PNG encode failed"))), "image/png"),
      );
    }
    await navigator.clipboard.write([new ClipboardItem({ "image/png": blob })]);
    button.textContent = "Copied ✓";
    button.classList.add("copied");
  } catch (error) {
    button.textContent = "Copy failed";
    console.error("Copy image failed:", error);
  }
  setTimeout(() => {
    button.textContent = original;
    button.classList.remove("copied");
  }, 1400);
}

function openLightbox() {
  if (!state.detail?.image_url) return;
  els.lightboxImage.src = state.detail.image_url;
  els.lightbox.hidden = false;
  document.body.classList.add("no-scroll");
}

function closeLightbox() {
  if (els.lightbox.hidden) return;
  els.lightbox.hidden = true;
  document.body.classList.remove("no-scroll");
}

function initTheme() {
  const saved = localStorage.getItem("gameqa-theme");
  const preferred = saved || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  applyTheme(preferred);
}

function applyTheme(theme) {
  document.documentElement.dataset.theme = theme;
  els.themeToggle.textContent = theme === "dark" ? "☀" : "☾";
  localStorage.setItem("gameqa-theme", theme);
}

els.themeToggle.addEventListener("click", () => {
  applyTheme(document.documentElement.dataset.theme === "dark" ? "light" : "dark");
});

els.gameSelect.addEventListener("change", () => loadGame(els.gameSelect.value));

for (const select of [els.taskFilter, els.qaLevelFilter, els.plotLevelFilter]) {
  select.addEventListener("change", () => {
    applyFilters();
    if (!state.filtered.some((sample) => sample.index === state.selectedIndex) && state.filtered[0]) {
      selectSample(state.filtered[0].index);
    } else {
      renderSampleList();
      renderNavPosition();
    }
  });
}

els.sampleSearch.addEventListener("input", () => {
  applyFilters();
  if (!state.filtered.some((sample) => sample.index === state.selectedIndex) && state.filtered[0]) {
    selectSample(state.filtered[0].index);
  } else {
    renderNavPosition();
  }
});

function renderNavPosition() {
  const position = state.filtered.findIndex((sample) => sample.index === state.selectedIndex);
  els.navPosition.textContent = position >= 0 ? `${position + 1} / ${state.filtered.length}` : `– / ${state.filtered.length}`;
  els.prevButton.disabled = position <= 0;
  els.nextButton.disabled = position < 0 || position >= state.filtered.length - 1;
}

els.resetFilters.addEventListener("click", () => {
  els.taskFilter.value = "";
  els.qaLevelFilter.value = "";
  els.plotLevelFilter.value = "";
  els.sampleSearch.value = "";
  applyFilters();
  renderNavPosition();
});

els.prevButton.addEventListener("click", () => stepSample(-1));
els.nextButton.addEventListener("click", () => stepSample(1));

els.imageFrame.addEventListener("click", openLightbox);
els.lightbox.addEventListener("click", closeLightbox);

els.copyState.addEventListener("click", (event) => {
  event.preventDefault();
  event.stopPropagation();
  copyText(els.copyState, els.stateBlock.dataset.text || "");
});
els.copyRaw.addEventListener("click", (event) => {
  event.preventDefault();
  event.stopPropagation();
  copyText(els.copyRaw, els.rawJson.dataset.text || "");
});
els.copyQuestion.addEventListener("click", () => {
  copyText(els.copyQuestion, stringify(state.detail?.question) || "");
});
els.copyImage.addEventListener("click", () => copyImageToClipboard(els.copyImage));

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    closeLightbox();
    return;
  }
  const tag = event.target.tagName;
  if (tag === "INPUT" || tag === "SELECT" || tag === "TEXTAREA") return;
  if (event.key === "ArrowLeft") {
    event.preventDefault();
    stepSample(-1);
  } else if (event.key === "ArrowRight") {
    event.preventDefault();
    stepSample(1);
  } else if (event.key === "/") {
    event.preventDefault();
    els.sampleSearch.focus();
    els.sampleSearch.select();
  }
});

init().catch((error) => {
  document.body.innerHTML = `<main class="empty-state">${escapeHtml(error.message)}</main>`;
});
