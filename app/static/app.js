/**
 * Liga Predictor — Frontend Application Logic
 *
 * Handles:
 * - API communication with FastAPI backend
 * - Dynamic rendering of simulation results
 * - Slider controls and input validation
 * - Loading states and error handling
 * - Staggered animations for result cards
 */

// ============================================
// State
// ============================================
let isSimulating = false;
let appInfo = null;

// ============================================
// DOM References
// ============================================
const jornadaSlider = document.getElementById("jornada-slider");
const jornadaValue = document.getElementById("jornada-value");
const simulacoesSlider = document.getElementById("simulacoes-slider");
const simulacoesValue = document.getElementById("simulacoes-value");
const btnSimulate = document.getElementById("btn-simulate");
const btnText = document.getElementById("btn-text");
const loadingOverlay = document.getElementById("loading-overlay");
const loadingText = document.getElementById("loading-text");
const resultsSection = document.getElementById("results");
const errorBox = document.getElementById("error-box");

// ============================================
// Initialization
// ============================================
document.addEventListener("DOMContentLoaded", async () => {
    setupSliders();
    await fetchAppInfo();
});

async function fetchAppInfo() {
    try {
        const res = await fetch("/api/info");
        if (!res.ok) throw new Error("Falha ao obter informações");
        appInfo = await res.json();

        // Update slider ranges based on actual data
        if (appInfo.jornada_min && appInfo.jornada_max) {
            jornadaSlider.min = appInfo.jornada_min;
            jornadaSlider.max = appInfo.jornada_max;
            document.getElementById("jornada-min-label").textContent = appInfo.jornada_min;
            document.getElementById("jornada-max-label").textContent = appInfo.jornada_max;
        }

        // Update info badges
        const infoEl = document.getElementById("info-epoca");
        if (infoEl) infoEl.textContent = appInfo.epoca_teste;

        const featEl = document.getElementById("info-features");
        if (featEl) featEl.textContent = appInfo.features_utilizadas;

    } catch (err) {
        console.warn("Could not fetch app info:", err);
    }
}


// ============================================
// Slider Controls
// ============================================
function setupSliders() {
    jornadaSlider.addEventListener("input", () => {
        jornadaValue.textContent = jornadaSlider.value;
    });

    simulacoesSlider.addEventListener("input", () => {
        const val = parseInt(simulacoesSlider.value);
        simulacoesValue.textContent = formatNumber(val);
    });
}

function formatNumber(n) {
    return n.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
}


// ============================================
// Simulation
// ============================================
async function runSimulation() {
    if (isSimulating) return;
    isSimulating = true;

    // UI: loading state
    btnSimulate.disabled = true;
    btnSimulate.classList.add("loading");
    btnText.textContent = "A Simular...";
    loadingOverlay.classList.add("active");
    resultsSection.classList.remove("active");
    errorBox.classList.remove("active");

    // Loading messages
    const messages = [
        "A treinar o modelo Random Forest...",
        "A calcular probabilidades de cada jogo...",
        "A executar simulações Monte Carlo...",
        "A compilar classificações finais...",
        "Quase lá..."
    ];
    let msgIdx = 0;
    const msgInterval = setInterval(() => {
        msgIdx = (msgIdx + 1) % messages.length;
        loadingText.textContent = messages[msgIdx];
    }, 2000);

    const jornada = parseInt(jornadaSlider.value);
    const numSim = parseInt(simulacoesSlider.value);

    try {
        const res = await fetch("/api/simulate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                jornada: jornada,
                num_simulacoes: numSim
            })
        });

        if (!res.ok) {
            const errData = await res.json();
            throw new Error(errData.detail || "Erro desconhecido na simulação");
        }

        const data = await res.json();
        renderResults(data);

    } catch (err) {
        showError(err.message);
    } finally {
        clearInterval(msgInterval);
        isSimulating = false;
        btnSimulate.disabled = false;
        btnSimulate.classList.remove("loading");
        btnText.textContent = "Simular Campeonato";
        loadingOverlay.classList.remove("active");
    }
}


// ============================================
// Render Results
// ============================================
function renderResults(data) {
    // Update meta tags
    document.getElementById("meta-tempo").textContent = data.tempo_execucao + "s";
    document.getElementById("meta-sims").textContent = formatNumber(data.num_simulacoes);
    document.getElementById("meta-jogos").textContent = data.jogos_futuros;
    document.getElementById("meta-jornadas").textContent = data.jornadas_simuladas;

    // Feature Decay Banner
    renderDecayBanner(data.feature_decay);

    // Big 3 cards
    renderBig3(data);

    // Full probability table
    renderProbTable(data.probabilidades_titulo);

    // Feature Importance (pass decay info for rolling tags)
    renderFeatureImportance(data.feature_importance, data.feature_decay);

    // Standings table
    renderStandings(data.tabela_real, data.jornada);

    // Next matches
    renderMatches(data.proximos_jogos);

    // Show results with animation
    resultsSection.classList.add("active");

    // Trigger staggered animations
    requestAnimationFrame(() => {
        document.querySelectorAll(".stagger-in").forEach((el, i) => {
            el.style.animationDelay = `${i * 100}ms`;
        });
    });
}

function renderBig3(data) {
    const big3Teams = [
        { key: "Sporting CP", cssClass: "sporting", id: "card-sporting" },
        { key: "Benfica", cssClass: "benfica", id: "card-benfica" },
        { key: "Porto", cssClass: "porto", id: "card-porto" }
    ];

    // Sort by probability to assign rank
    const probs = data.probabilidades_titulo;
    const sorted = Object.entries(probs).sort((a, b) => b[1] - a[1]);
    const rankMap = {};
    sorted.forEach(([team], i) => { rankMap[team] = i + 1; });

    big3Teams.forEach(({ key, id }) => {
        const card = document.getElementById(id);
        if (!card) return;

        const prob = probs[key] || 0;
        const rank = rankMap[key] || "-";
        const pts = data.tabela_real[key] || 0;

        card.querySelector(".big3__rank").textContent =
            rank <= 3 ? `#${rank} mais provável` : `#${rank}º posição`;
        card.querySelector(".big3__prob").textContent = prob.toFixed(1) + "%";
        card.querySelector(".big3__pts").textContent = `${pts} pts acumulados`;
    });
}

function renderProbTable(probs) {
    const container = document.getElementById("prob-table-body");
    container.innerHTML = "";

    const sorted = Object.entries(probs).sort((a, b) => b[1] - a[1]);
    const maxProb = sorted.length > 0 ? sorted[0][1] : 100;

    sorted.forEach(([team, prob], i) => {
        if (prob <= 0) return; // Only show teams with > 0% chance

        const row = document.createElement("div");
        row.className = "prob-table__row stagger-in";
        row.style.animationDelay = `${(i + 3) * 80}ms`;

        const barWidth = maxProb > 0 ? (prob / maxProb) * 100 : 0;

        row.innerHTML = `
            <div class="prob-table__pos">${i + 1}</div>
            <div class="prob-table__team">${team}</div>
            <div class="prob-table__bar-container">
                <div class="prob-table__bar" style="width: 0%;" data-width="${barWidth}"></div>
            </div>
            <div class="prob-table__pct">${prob.toFixed(1)}%</div>
        `;

        container.appendChild(row);
    });

    // Animate bars after a short delay
    setTimeout(() => {
        document.querySelectorAll(".prob-table__bar").forEach(bar => {
            bar.style.width = bar.dataset.width + "%";
        });
    }, 300);
}

function renderDecayBanner(decay) {
    const banner = document.getElementById("decay-banner");
    const badge = document.getElementById("decay-badge");
    const subtitle = document.getElementById("feature-subtitle");

    if (!decay) {
        banner.classList.remove("active", "decay-banner--warning", "decay-banner--ok");
        if (badge) badge.textContent = "";
        return;
    }

    if (decay.ativo) {
        banner.classList.add("active", "decay-banner--warning");
        banner.classList.remove("decay-banner--ok");

        document.getElementById("decay-title").textContent = "Feature Decay Ativo";
        document.getElementById("decay-desc").textContent = decay.descricao;

        // Animate the confidence meter
        const fill = document.getElementById("decay-meter-fill");
        const valueEl = document.getElementById("decay-meter-value");
        valueEl.textContent = decay.fator_confianca + "%";
        setTimeout(() => {
            fill.style.width = decay.fator_confianca + "%";
        }, 300);

        // Badge next to feature importance title
        if (badge) {
            badge.textContent = `Decay ${decay.fator_confianca}%`;
            badge.classList.add("active");
        }

        // Update subtitle
        if (subtitle) {
            subtitle.textContent =
                `⚠ Jornada ${decay.jogos_na_epoca + 1}: rolling features reduzidas a ${decay.fator_confianca}% — ` +
                `o modelo apoia-se mais em Elo, xG e histórico da época anterior.`;
        }
    } else {
        banner.classList.add("active", "decay-banner--ok");
        banner.classList.remove("decay-banner--warning");

        document.getElementById("decay-title").textContent = "Dados Completos";
        document.getElementById("decay-desc").textContent = decay.descricao;

        const fill = document.getElementById("decay-meter-fill");
        const valueEl = document.getElementById("decay-meter-value");
        valueEl.textContent = "100%";
        setTimeout(() => {
            fill.style.width = "100%";
        }, 300);

        if (badge) {
            badge.textContent = "";
            badge.classList.remove("active");
        }

        if (subtitle) {
            subtitle.textContent =
                "As 15 features que mais influenciaram as previsões do Random Forest nesta simulação.";
        }
    }
}

// Rolling features list (must match backend ROLLING_FEATURES)
const ROLLING_FEATURE_KEYS = [
    "Casa_Form_Pts5", "Casa_Form_GM5", "Casa_Form_GS5",
    "Visitante_Form_Pts5", "Visitante_Form_GM5", "Visitante_Form_GS5",
    "Casa_Form_Empates5", "Visitante_Form_Empates5",
    "Casa_BTTS_Rate_5J", "Visitante_BTTS_Rate_5J",
    "Casa_CleanSheet_Rate_5J", "Visitante_CleanSheet_Rate_5J",
    "Casa_Rolling5_Remates", "Visitante_Rolling5_Remates",
    "Casa_Rolling5_RematesAlvo", "Visitante_Rolling5_RematesAlvo",
    "Casa_Rolling5_Cantos", "Visitante_Rolling5_Cantos",
];

function renderFeatureImportance(features, decay) {
    const container = document.getElementById("feature-importance-container");
    container.innerHTML = "";

    if (!features || features.length === 0) {
        container.innerHTML = '<p style="color: var(--text-muted)">Sem dados de importância de features.</p>';
        return;
    }

    const maxImportance = features[0].importancia;
    const decayActive = decay && decay.ativo;

    features.forEach((feat, i) => {
        const row = document.createElement("div");
        row.className = "feat-row stagger-in";
        row.style.animationDelay = `${(i + 5) * 60}ms`;

        const barWidth = maxImportance > 0 ? (feat.importancia / maxImportance) * 100 : 0;

        // Color interpolation: gold for top → green for bottom
        const hue = 45 - (i / (features.length - 1)) * (45 - 160);  // gold(45) → green(160)
        const saturation = 85 - (i / features.length) * 20;
        const lightness = 55 + (i / features.length) * 5;
        const barColor = `hsl(${hue}, ${saturation}%, ${lightness}%)`;

        // Check if this feature is a rolling feature (affected by decay)
        const isRolling = ROLLING_FEATURE_KEYS.includes(feat.feature);
        const rollingTag = (isRolling && decayActive)
            ? `<span class="feat-row__tag feat-row__tag--decay">↓ ${decay.fator_confianca}%</span>`
            : (isRolling ? '<span class="feat-row__tag feat-row__tag--rolling">ROLLING</span>' : '');

        row.innerHTML = `
            <div class="feat-row__rank">${i + 1}</div>
            <div class="feat-row__info">
                <div class="feat-row__label">${feat.label} ${rollingTag}</div>
                <div class="feat-row__bar-track">
                    <div class="feat-row__bar-fill" style="width: 0%; background: ${barColor};" data-width="${barWidth}"></div>
                </div>
            </div>
            <div class="feat-row__pct">${feat.importancia.toFixed(1)}%</div>
        `;

        container.appendChild(row);
    });

    // Animate bars
    setTimeout(() => {
        document.querySelectorAll(".feat-row__bar-fill").forEach(bar => {
            bar.style.width = bar.dataset.width + "%";
        });
    }, 400);
}

function renderStandings(tabela, jornada) {
    const container = document.getElementById("standings-body");
    const title = document.getElementById("standings-title-jornada");
    container.innerHTML = "";

    if (title) title.textContent = `(antes da Jornada ${jornada})`;

    const sorted = Object.entries(tabela).sort((a, b) => b[1] - a[1]);

    sorted.forEach(([team, pts], i) => {
        const row = document.createElement("div");
        row.className = "standings__row stagger-in";
        row.style.animationDelay = `${(i + 3) * 60}ms`;

        row.innerHTML = `
            <div class="standings__pos">${i + 1}</div>
            <div class="standings__team">${team}</div>
            <div class="standings__pts">${pts}</div>
        `;

        container.appendChild(row);
    });
}

function renderMatches(matches) {
    const container = document.getElementById("matches-container");
    container.innerHTML = "";

    if (!matches || matches.length === 0) {
        container.innerHTML = '<p style="color: var(--text-muted)">Sem jogos para mostrar.</p>';
        return;
    }

    matches.forEach((match, i) => {
        const card = document.createElement("div");
        card.className = "match-card stagger-in";
        card.style.animationDelay = `${(i + 5) * 100}ms`;

        card.innerHTML = `
            <div class="match-card__jornada">Jornada ${match.jornada}</div>
            <div class="match-card__teams">
                <span>${match.casa}</span>
                <span class="match-card__vs">vs</span>
                <span>${match.fora}</span>
            </div>
            <div class="match-card__probs">
                <div class="match-card__prob-bar match-card__prob-bar--home" style="width: ${match.prob_casa}%"></div>
                <div class="match-card__prob-bar match-card__prob-bar--draw" style="width: ${match.prob_empate}%"></div>
                <div class="match-card__prob-bar match-card__prob-bar--away" style="width: ${match.prob_fora}%"></div>
            </div>
            <div class="match-card__prob-labels">
                <span>${match.prob_casa}%</span>
                <span>${match.prob_empate}%</span>
                <span>${match.prob_fora}%</span>
            </div>
        `;

        container.appendChild(card);
    });
}


// ============================================
// Error Handling
// ============================================
function showError(message) {
    errorBox.textContent = "⚠ " + message;
    errorBox.classList.add("active");
}
