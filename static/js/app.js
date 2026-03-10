// ==================== STATE ====================
let vocabList = [];
let flashcardDeck = [];
let flashcardIndex = 0;
let quizDeck = [];
let quizIndex = 0;
let quizScore = 0;
let currentVietnameseWord = "";

// ==================== INIT ====================
document.addEventListener("DOMContentLoaded", () => {
    loadVersion();
    loadVocab();
    loadCategories();
    setupDragDrop();
});

// ==================== NAVIGATION ====================
function showPage(name) {
    document.querySelectorAll(".page").forEach(p => p.classList.remove("active"));
    document.getElementById("page-" + name).classList.add("active");
    document.querySelectorAll(".nav-links button").forEach(b => b.classList.remove("active"));
    event.target.classList.add("active");

    if (name === "flashcards") startFlashcards();
    if (name === "quiz") startQuiz();
    if (name === "stats") loadStats();
    if (name === "vocab") { loadVocab(); loadCategories(); }
}

// ==================== VERSION ====================
async function loadVersion() {
    const res = await fetch("/api/version");
    const data = await res.json();
    document.getElementById("version-badge").textContent = `${data.name} v${data.version}`;
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

    const res = await fetch("/api/vocab?" + params);
    vocabList = await res.json();
    renderVocabList();
}

function renderVocabList() {
    const container = document.getElementById("vocab-list");
    if (!vocabList.length) {
        container.innerHTML = `<div class="empty-state"><div class="icon">&#x1F4D6;</div><p>Aucun vocabulaire. Ajoute tes premiers mots !</p></div>`;
        return;
    }
    container.innerHTML = vocabList.map(v => `
        <div class="vocab-item" id="vocab-${v.id}">
            <div class="vocab-text">
                <div class="vocab-viet">${esc(v.vietnamese)}</div>
                <div class="vocab-french">${esc(v.french)}</div>
            </div>
            ${v.category ? `<span class="vocab-category">${esc(v.category)}</span>` : ""}
            <div class="vocab-actions">
                <button class="btn-icon" onclick="speak('${esc(v.vietnamese)}')" title="Ecouter">
                    <svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02z"/></svg>
                </button>
                <button class="btn-icon" onclick="deleteVocab(${v.id})" title="Supprimer">
                    <svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>
                </button>
            </div>
        </div>
    `).join("");
}

async function addVocab(e) {
    e.preventDefault();
    const form = new FormData();
    form.set("vietnamese", document.getElementById("input-viet").value);
    form.set("french", document.getElementById("input-french").value);
    form.set("category", document.getElementById("input-category").value);

    await fetch("/api/vocab", { method: "POST", body: form });
    document.getElementById("input-viet").value = "";
    document.getElementById("input-french").value = "";
    toast("Mot ajoute !");
    loadVocab();
    loadCategories();
}

async function deleteVocab(id) {
    if (!confirm("Supprimer ce mot ?")) return;
    await fetch(`/api/vocab/${id}`, { method: "DELETE" });
    toast("Supprime");
    loadVocab();
}

// ==================== CATEGORIES ====================
async function loadCategories() {
    const res = await fetch("/api/categories");
    const cats = await res.json();
    const selectors = ["filter-category", "flash-category", "quiz-category"];
    selectors.forEach(id => {
        const sel = document.getElementById(id);
        const current = sel.value;
        sel.innerHTML = `<option value="">Toutes categories</option>` +
            cats.map(c => `<option value="${esc(c)}" ${c === current ? "selected" : ""}>${esc(c)}</option>`).join("");
    });
}

// ==================== TTS ====================
function speak(text) {
    currentVietnameseWord = text;
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "vi-VN";
    utterance.rate = 0.8;

    // Try to find Vietnamese voice
    const voices = speechSynthesis.getVoices();
    const viVoice = voices.find(v => v.lang.startsWith("vi"));
    if (viVoice) utterance.voice = viVoice;

    speechSynthesis.cancel();
    speechSynthesis.speak(utterance);
}

function speakVietnamese() {
    if (currentVietnameseWord) speak(currentVietnameseWord);
}

// Load voices
speechSynthesis.onvoiceschanged = () => speechSynthesis.getVoices();

// ==================== FLASHCARDS ====================
async function startFlashcards() {
    const cat = document.getElementById("flash-category").value;
    const params = cat ? `?category=${encodeURIComponent(cat)}` : "";
    const res = await fetch("/api/review" + params);
    flashcardDeck = await res.json();
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
    await fetch(`/api/review/${card.id}`, {
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
    const res = await fetch("/api/review" + params);
    const allCards = await res.json();

    document.getElementById("quiz-result").style.display = "none";

    if (allCards.length < 4) {
        document.getElementById("quiz-area").style.display = "none";
        document.getElementById("quiz-empty").style.display = "block";
        return;
    }
    document.getElementById("quiz-area").style.display = "block";
    document.getElementById("quiz-empty").style.display = "none";

    // Pick 10 questions max
    quizDeck = shuffle(allCards).slice(0, 10);
    quizIndex = 0;
    quizScore = 0;
    showQuizQuestion(allCards);
}

function showQuizQuestion(allCards) {
    if (quizIndex >= quizDeck.length) {
        document.getElementById("quiz-area").style.display = "none";
        document.getElementById("quiz-result").style.display = "block";
        document.getElementById("quiz-result-text").textContent =
            `Score : ${quizScore} / ${quizDeck.length}`;
        return;
    }

    const direction = document.getElementById("quiz-direction").value;
    const card = quizDeck[quizIndex];
    const isVietToFr = direction === "viet-to-fr";

    currentVietnameseWord = card.vietnamese;
    document.getElementById("quiz-progress").textContent = `Question ${quizIndex + 1} / ${quizDeck.length}`;
    document.getElementById("quiz-question").textContent = isVietToFr ? card.vietnamese : card.french;

    // Generate wrong options from pool
    const correctAnswer = isVietToFr ? card.french : card.vietnamese;
    const pool = allCards
        .filter(c => c.id !== card.id)
        .map(c => isVietToFr ? c.french : c.vietnamese);
    const wrongOptions = shuffle(pool).slice(0, 3);
    const options = shuffle([correctAnswer, ...wrongOptions]);

    const container = document.getElementById("quiz-options");
    container.innerHTML = options.map(opt => `
        <button class="quiz-option" onclick="answerQuiz(this, '${esc(correctAnswer)}')">
            ${esc(opt)}
        </button>
    `).join("");

    // Show/hide speak button based on direction
    document.getElementById("quiz-speak-btn").style.display = isVietToFr ? "inline-flex" : "none";
}

function answerQuiz(btn, correct) {
    const buttons = document.querySelectorAll(".quiz-option");
    const chosen = btn.textContent.trim();
    const isCorrect = chosen === correct;

    buttons.forEach(b => {
        b.disabled = true;
        b.style.pointerEvents = "none";
        if (b.textContent.trim() === correct) b.classList.add("correct");
    });

    if (isCorrect) {
        quizScore++;
    } else {
        btn.classList.add("wrong");
    }

    // Submit review
    const card = quizDeck[quizIndex];
    fetch(`/api/review/${card.id}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ correct: isCorrect })
    });

    // Auto next after delay
    setTimeout(() => {
        quizIndex++;
        // Re-fetch all cards for options pool
        fetch("/api/review?limit=50").then(r => r.json()).then(allCards => {
            if (allCards.length < 4) allCards = vocabList; // fallback
            showQuizQuestion(allCards);
        });
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
    document.getElementById("ocr-preview").classList.remove("visible");

    const form = new FormData();
    form.append("file", file);

    try {
        const res = await fetch("/api/ocr", { method: "POST", body: form });
        const data = await res.json();

        document.getElementById("ocr-raw").value = data.raw_text;
        renderOcrEntries(data.entries);
        document.getElementById("ocr-preview").classList.add("visible");
    } catch (err) {
        toast("Erreur OCR: " + err.message);
    }
    document.getElementById("upload-loading").style.display = "none";
}

let ocrEntries = [];

function renderOcrEntries(entries) {
    ocrEntries = entries;
    const container = document.getElementById("ocr-entries");
    if (!entries.length) {
        container.innerHTML = `<p style="color:var(--text-muted)">Aucune paire detectee. Verifie le format du texte.</p>`;
        return;
    }
    container.innerHTML = entries.map((e, i) => `
        <div class="ocr-entry">
            <input type="text" value="${esc(e.vietnamese)}" onchange="ocrEntries[${i}].vietnamese=this.value">
            <input type="text" value="${esc(e.french)}" onchange="ocrEntries[${i}].french=this.value">
            <button class="btn-icon" onclick="this.parentElement.remove();ocrEntries[${i}]=null;">
                <svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>
            </button>
        </div>
    `).join("");
}

async function importOcrEntries() {
    const valid = ocrEntries.filter(e => e && e.vietnamese && e.french);
    if (!valid.length) { toast("Rien a importer"); return; }

    await fetch("/api/vocab/bulk", {
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

    await fetch("/api/vocab/bulk", {
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
    const res = await fetch("/api/stats");
    const data = await res.json();

    document.getElementById("stat-total").textContent = data.total_vocab;
    document.getElementById("stat-reviewed").textContent = data.reviewed;
    document.getElementById("stat-due").textContent = data.due_today;

    const renderList = (items, key) => items.length
        ? items.map(i => `<div class="vocab-item"><div class="vocab-text"><span class="vocab-viet">${esc(i.vietnamese)}</span> <span class="vocab-french">${esc(i.french)}</span></div><span style="color:var(--text-muted)">${i[key]}x</span></div>`).join("")
        : `<p style="color:var(--text-muted);padding:1rem;">Pas encore de donnees</p>`;

    document.getElementById("stat-top-correct").innerHTML = renderList(data.top_correct, "correct");
    document.getElementById("stat-top-incorrect").innerHTML = renderList(data.top_incorrect, "incorrect");
}

// ==================== UTILS ====================
function esc(str) {
    if (!str) return "";
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
              .replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}

function shuffle(arr) {
    const a = [...arr];
    for (let i = a.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
}
