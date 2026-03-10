// ==================== BASE PATH ====================
const BASE = window.location.pathname.replace(/\/$/, "");

// ==================== STATE ====================
let vocabList = [];
let flashcardDeck = [];
let flashcardIndex = 0;
let quizDeck = [];
let quizIndex = 0;
let quizScore = 0;
let quizAllCards = [];
let currentVietnameseWord = "";

// ==================== INIT ====================
document.addEventListener("DOMContentLoaded", () => {
    loadVersion();
    loadVocab();
    loadCategories();
    setupDragDrop();
});

// ==================== NAVIGATION ====================
function showPage(name, btn) {
    document.querySelectorAll(".page").forEach(p => p.classList.remove("active"));
    document.getElementById("page-" + name).classList.add("active");
    document.querySelectorAll(".nav-links button").forEach(b => b.classList.remove("active"));
    if (btn) btn.classList.add("active");
    document.getElementById("nav-links").classList.remove("open");

    if (name === "flashcards") startFlashcards();
    if (name === "quiz") startQuiz();
    if (name === "stats") loadStats();
    if (name === "vocab") { loadVocab(); loadCategories(); }
}

function toggleMenu() {
    document.getElementById("nav-links").classList.toggle("open");
}

document.addEventListener("click", (e) => {
    const nav = document.getElementById("nav-links");
    const hamburger = document.querySelector(".nav-hamburger");
    if (nav && nav.classList.contains("open") && !nav.contains(e.target) && !hamburger.contains(e.target)) {
        nav.classList.remove("open");
    }
});

// ==================== VERSION ====================
async function loadVersion() {
    try {
        const res = await fetch(BASE + "/api/version");
        const data = await res.json();
        document.getElementById("version-badge").textContent = `${data.name} v${data.version}`;
    } catch(e) {}
}

// ==================== TOAST ====================
function toast(msg) {
    const el = document.getElementById("toast");
    el.textContent = msg;
    el.classList.add("show");
    setTimeout(() => el.classList.remove("show"), 2500);
}

// ==================== VOCAB CRUD ====================
async function loadVocab() {
    const cat = document.getElementById("filter-category").value;
    const search = document.getElementById("search-input").value;
    const params = new URLSearchParams();
    if (cat) params.set("category", cat);
    if (search) params.set("search", search);

    try {
        const res = await fetch(BASE + "/api/vocab?" + params);
        vocabList = await res.json();
    } catch(e) { vocabList = []; }
    renderVocabList();
}

function renderVocabList() {
    const container = document.getElementById("vocab-list");
    if (!vocabList.length) {
        container.innerHTML = '<div class="empty-state"><div class="icon">&#x1F4D6;</div><p>Aucun vocabulaire. Ajoute tes premiers mots !</p></div>';
        return;
    }
    container.innerHTML = vocabList.map(v => {
        const vietAttr = escAttr(v.vietnamese);
        return `
        <div class="vocab-item">
            <div class="vocab-text">
                <div class="vocab-viet">${esc(v.vietnamese)}</div>
                <div class="vocab-french">${esc(v.french)}</div>
            </div>
            ${v.category ? `<span class="vocab-category">${esc(v.category)}</span>` : ""}
            <div class="vocab-actions">
                <button class="btn-icon" data-speak="${vietAttr}" title="Ecouter">
                    <svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02z"/></svg>
                </button>
                <button class="btn-icon" data-delete="${v.id}" title="Supprimer">
                    <svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>
                </button>
            </div>
        </div>`;
    }).join("");

    // Attach event listeners
    container.querySelectorAll("[data-speak]").forEach(btn => {
        btn.addEventListener("click", () => speak(btn.dataset.speak));
    });
    container.querySelectorAll("[data-delete]").forEach(btn => {
        btn.addEventListener("click", () => deleteVocab(btn.dataset.delete));
    });
}

async function addVocab(e) {
    e.preventDefault();
    const form = new FormData();
    form.set("vietnamese", document.getElementById("input-viet").value);
    form.set("french", document.getElementById("input-french").value);
    form.set("category", document.getElementById("input-category").value);

    await fetch(BASE + "/api/vocab", { method: "POST", body: form });
    document.getElementById("input-viet").value = "";
    document.getElementById("input-french").value = "";
    toast("Mot ajoute !");
    loadVocab();
    loadCategories();
}

async function deleteVocab(id) {
    if (!confirm("Supprimer ce mot ?")) return;
    await fetch(`${BASE}/api/vocab/${id}`, { method: "DELETE" });
    toast("Supprime");
    loadVocab();
}

// ==================== CATEGORIES ====================
async function loadCategories() {
    try {
        const res = await fetch(BASE + "/api/categories");
        const cats = await res.json();
        ["filter-category", "flash-category", "quiz-category"].forEach(id => {
            const sel = document.getElementById(id);
            const current = sel.value;
            sel.innerHTML = '<option value="">Toutes categories</option>' +
                cats.map(c => `<option value="${escAttr(c)}" ${c === current ? "selected" : ""}>${esc(c)}</option>`).join("");
        });
    } catch(e) {}
}

// ==================== TTS ====================
function speak(text) {
    currentVietnameseWord = text;
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "vi-VN";
    utterance.rate = 0.8;
    const voices = speechSynthesis.getVoices();
    const viVoice = voices.find(v => v.lang.startsWith("vi"));
    if (viVoice) utterance.voice = viVoice;
    speechSynthesis.cancel();
    speechSynthesis.speak(utterance);
}

function speakVietnamese() {
    if (currentVietnameseWord) speak(currentVietnameseWord);
}

speechSynthesis.onvoiceschanged = () => speechSynthesis.getVoices();

// ==================== FLASHCARDS ====================
async function startFlashcards() {
    const cat = document.getElementById("flash-category").value;
    const params = cat ? `?category=${encodeURIComponent(cat)}` : "";
    try {
        const res = await fetch(BASE + "/api/review" + params);
        flashcardDeck = await res.json();
    } catch(e) { flashcardDeck = []; }
    flashcardIndex = 0;

    if (!flashcardDeck.length) {
        document.getElementById("flashcard-area").style.display = "none";
        document.getElementById("flashcard-empty").style.display = "block";
        return;
    }
    document.getElementById("flashcard-area").style.display = "block";
    document.getElementById("flashcard-empty").style.display = "none";

    // Shuffle
    for (let i = flashcardDeck.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [flashcardDeck[i], flashcardDeck[j]] = [flashcardDeck[j], flashcardDeck[i]];
    }
    showFlashcard();
}

function showFlashcard() {
    if (flashcardIndex >= flashcardDeck.length) {
        flashcardIndex = 0;
        startFlashcards();
        return;
    }
    const card = flashcardDeck[flashcardIndex];
    currentVietnameseWord = card.vietnamese;
    document.getElementById("flash-front-word").textContent = card.vietnamese;
    document.getElementById("flash-back-word").textContent = card.french;
    document.getElementById("flash-back-hint").textContent = card.category || "";
    document.getElementById("flash-progress").textContent = `${flashcardIndex + 1} / ${flashcardDeck.length}`;
    document.getElementById("flashcard").classList.remove("flipped");
}

function flipCard() {
    document.getElementById("flashcard").classList.toggle("flipped");
}

async function reviewCard(correct) {
    const card = flashcardDeck[flashcardIndex];
    fetch(`${BASE}/api/review/${card.id}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ correct })
    });
    flashcardIndex++;
    showFlashcard();
}

// ==================== QUIZ ====================
async function startQuiz() {
    const cat = document.getElementById("quiz-category").value;
    const params = cat ? `?category=${encodeURIComponent(cat)}&limit=50` : "?limit=50";
    try {
        const res = await fetch(BASE + "/api/review" + params);
        quizAllCards = await res.json();
    } catch(e) { quizAllCards = []; }

    document.getElementById("quiz-result").style.display = "none";

    if (quizAllCards.length < 4) {
        document.getElementById("quiz-area").style.display = "none";
        document.getElementById("quiz-empty").style.display = "block";
        return;
    }
    document.getElementById("quiz-area").style.display = "block";
    document.getElementById("quiz-empty").style.display = "none";

    quizDeck = shuffle(quizAllCards).slice(0, 10);
    quizIndex = 0;
    quizScore = 0;
    showQuizQuestion();
}

function showQuizQuestion() {
    if (quizIndex >= quizDeck.length) {
        document.getElementById("quiz-area").style.display = "none";
        document.getElementById("quiz-result").style.display = "block";
        const pct = Math.round((quizScore / quizDeck.length) * 100);
        document.getElementById("quiz-result-text").textContent =
            `Score : ${quizScore} / ${quizDeck.length} (${pct}%)`;
        return;
    }

    const direction = document.getElementById("quiz-direction").value;
    const card = quizDeck[quizIndex];
    const isVietToFr = direction === "viet-to-fr";

    currentVietnameseWord = card.vietnamese;
    document.getElementById("quiz-progress").textContent = `Question ${quizIndex + 1} / ${quizDeck.length}`;
    document.getElementById("quiz-question").textContent = isVietToFr ? card.vietnamese : card.french;

    const correctAnswer = isVietToFr ? card.french : card.vietnamese;
    const pool = quizAllCards
        .filter(c => c.id !== card.id)
        .map(c => isVietToFr ? c.french : c.vietnamese);
    const wrongOptions = shuffle(pool).slice(0, 3);
    const options = shuffle([correctAnswer, ...wrongOptions]);

    const container = document.getElementById("quiz-options");
    container.innerHTML = options.map(opt =>
        `<button class="quiz-option" data-answer="${escAttr(opt)}">${esc(opt)}</button>`
    ).join("");

    // Attach click handlers
    container.querySelectorAll(".quiz-option").forEach(btn => {
        btn.addEventListener("click", () => answerQuiz(btn, correctAnswer));
    });

    document.getElementById("quiz-speak-btn").style.display = isVietToFr ? "inline-flex" : "none";
}

function answerQuiz(btn, correctAnswer) {
    const buttons = document.querySelectorAll(".quiz-option");
    const chosen = btn.dataset.answer;
    const isCorrect = chosen === correctAnswer;

    buttons.forEach(b => {
        b.disabled = true;
        b.style.pointerEvents = "none";
        if (b.dataset.answer === correctAnswer) b.classList.add("correct");
    });

    if (isCorrect) {
        quizScore++;
    } else {
        btn.classList.add("wrong");
    }

    const card = quizDeck[quizIndex];
    fetch(`${BASE}/api/review/${card.id}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ correct: isCorrect })
    });

    setTimeout(() => {
        quizIndex++;
        showQuizQuestion();
    }, 1200);
}

// ==================== OCR UPLOAD ====================
function setupDragDrop() {
    const zone = document.getElementById("upload-zone");
    if (!zone) return;
    zone.addEventListener("dragover", e => { e.preventDefault(); zone.classList.add("dragover"); });
    zone.addEventListener("dragleave", () => zone.classList.remove("dragover"));
    zone.addEventListener("drop", e => {
        e.preventDefault();
        zone.classList.remove("dragover");
        if (e.dataTransfer.files.length) processUpload(e.dataTransfer.files[0]);
    });
}

function handleUpload(e) {
    if (e.target.files.length) processUpload(e.target.files[0]);
}

async function processUpload(file) {
    document.getElementById("upload-loading").style.display = "block";
    document.getElementById("upload-zone").style.display = "none";
    document.getElementById("ocr-preview").classList.remove("visible");
    document.getElementById("upload-loading-text").textContent = "Analyse IA en cours...";

    const form = new FormData();
    form.append("file", file);

    try {
        const res = await fetch(BASE + "/api/ocr", { method: "POST", body: form });
        const data = await res.json();

        document.getElementById("ocr-raw").value = data.debug_raw || data.raw_text;
        let methodLabel = data.method === "ai" ? "Claude IA" : "Fallback";
        if (data.pages > 1) methodLabel += ` (${data.pages} chunks)`;
        document.getElementById("ocr-method").textContent = methodLabel;
        renderOcrEntries(data.entries);
        document.getElementById("ocr-preview").classList.add("visible");
    } catch (err) {
        toast("Erreur: " + err.message);
    }
    document.getElementById("upload-loading").style.display = "none";
    document.getElementById("upload-zone").style.display = "";
}

let ocrEntries = [];

function renderOcrEntries(entries) {
    ocrEntries = [...entries];
    const container = document.getElementById("ocr-entries");
    if (!entries.length) {
        container.innerHTML = '<p style="color:var(--text-muted);font-size:0.9rem;">Aucune paire detectee.</p>';
        return;
    }
    container.innerHTML = `<p style="color:var(--success);font-size:0.85rem;margin-bottom:0.6rem;font-weight:600;">${entries.length} mots detectes</p>` +
        entries.map((e, i) => `
        <div class="ocr-entry" data-index="${i}">
            <input type="text" value="${escAttr(e.vietnamese)}" data-field="vietnamese" placeholder="Vietnamien">
            <input type="text" value="${escAttr(e.french)}" data-field="french" placeholder="Francais">
            <input type="text" value="${escAttr(e.category || '')}" data-field="category" placeholder="Categorie">
            <button class="btn-icon ocr-delete" style="width:32px;height:32px;">
                <svg width="14" height="14" fill="currentColor" viewBox="0 0 24 24"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>
            </button>
        </div>
    `).join("");

    // Attach listeners
    container.querySelectorAll(".ocr-entry input").forEach(input => {
        input.addEventListener("change", () => {
            const idx = parseInt(input.closest(".ocr-entry").dataset.index);
            const field = input.dataset.field;
            if (ocrEntries[idx]) ocrEntries[idx][field] = input.value;
        });
    });
    container.querySelectorAll(".ocr-delete").forEach(btn => {
        btn.addEventListener("click", () => {
            const row = btn.closest(".ocr-entry");
            const idx = parseInt(row.dataset.index);
            ocrEntries[idx] = null;
            row.remove();
        });
    });
}

async function importOcrEntries() {
    const valid = ocrEntries.filter(e => e && e.vietnamese && e.french);
    if (!valid.length) { toast("Rien a importer"); return; }

    await fetch(BASE + "/api/vocab/bulk", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ entries: valid })
    });
    toast(`${valid.length} mots importes !`);
    resetUpload();
    loadVocab();
    loadCategories();
}

function resetUpload() {
    document.getElementById("ocr-preview").classList.remove("visible");
    document.getElementById("file-input").value = "";
    ocrEntries = [];
}

async function importManualText() {
    const text = document.getElementById("manual-text").value.trim();
    if (!text) return;

    const lines = text.split("\n").filter(l => l.trim());
    const entries = [];
    for (const line of lines) {
        for (const sep of ["=", ":", " - ", "\t", "   "]) {
            if (line.includes(sep)) {
                const parts = line.split(sep);
                if (parts.length >= 2 && parts[0].trim() && parts[1].trim()) {
                    entries.push({ vietnamese: parts[0].trim(), french: parts[1].trim() });
                    break;
                }
            }
        }
    }

    if (!entries.length) { toast("Aucune paire detectee"); return; }

    await fetch(BASE + "/api/vocab/bulk", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ entries })
    });
    document.getElementById("manual-text").value = "";
    toast(`${entries.length} mots importes !`);
    loadVocab();
    loadCategories();
}

// ==================== STATS ====================
async function loadStats() {
    try {
        const res = await fetch(BASE + "/api/stats");
        const data = await res.json();

        document.getElementById("stat-total").textContent = data.total_vocab;
        document.getElementById("stat-reviewed").textContent = data.reviewed;
        document.getElementById("stat-due").textContent = data.due_today;

        const renderList = (items, key) => items.length
            ? items.map(i => `<div class="vocab-item"><div class="vocab-text"><span class="vocab-viet">${esc(i.vietnamese)}</span> <span class="vocab-french">${esc(i.french)}</span></div><span style="color:var(--text-dim);font-size:0.85rem;font-weight:600;">${i[key]}x</span></div>`).join("")
            : '<p style="color:var(--text-dim);padding:1rem;font-size:0.9rem;">Pas encore de donnees</p>';

        document.getElementById("stat-top-correct").innerHTML = renderList(data.top_correct, "correct");
        document.getElementById("stat-top-incorrect").innerHTML = renderList(data.top_incorrect, "incorrect");
    } catch(e) {}
}

// ==================== UTILS ====================
function esc(str) {
    if (!str) return "";
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}

function escAttr(str) {
    if (!str) return "";
    return str.replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/'/g, "&#039;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function shuffle(arr) {
    const a = [...arr];
    for (let i = a.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
}
