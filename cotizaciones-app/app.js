/* ==========================================================================
   COTIZACIONES CDE - APPLICATION LOGIC (V1)
   ========================================================================== */

const REFRESH_INTERVAL_SECONDS = 15;
let countdownRemaining = REFRESH_INTERVAL_SECONDS;
let countdownTimer = null;
let systemUpdateTimer = null;
let lastSystemRetrieveTime = null;
let isFetching = false;

// Formatters
function formatPYG(val) {
  if (val === null || val === undefined || isNaN(val) || val === 0) return "--";
  return Math.round(val).toLocaleString('es-PY').replace(/,/g, '.');
}

function formatDecimal(val, decimals = 2) {
  if (val === null || val === undefined || isNaN(val) || val === 0) return "--";
  return Number(val).toLocaleString('es-PY', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  });
}

function formatTimestampDisplay(tsStr) {
  if (!tsStr) return "--:--:--";
  try {
    // If ISO string
    if (tsStr.includes('T')) {
      const d = new Date(tsStr);
      return d.toLocaleTimeString('es-PY', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    }
    return tsStr;
  } catch (e) {
    return tsStr;
  }
}

// DOM Elements
const cardsContainer = document.getElementById('cardsContainer');
const countdownNumberEl = document.getElementById('countdownNumber');
const btnRefresh = document.getElementById('btnRefresh');
const refreshBtnText = document.getElementById('refreshBtnText');
const globalSystemStatusEl = document.getElementById('globalSystemStatus');

// House Icons & Titles Mapping
const HOUSE_METADATA = {
  "Bonanza": { icon: "🏦", title: "BONANZA", branch: "Casa Matriz" },
  "Cambios Chaco": { icon: "🏦", title: "CAMBIOS CHACO", branch: "Sucursal Adrián Jara" },
  "Cambios Alberdi": { icon: "🏦", title: "CAMBIOS ALBERDI", branch: "Ciudad del Este" },
  "La Moneda": { icon: "🏦", title: "LA MONEDA", branch: "Casa Matriz" }
};

// Fetch rates from Backend API
async function fetchRates() {
  if (isFetching) return;
  isFetching = true;

  // UI updating state
  btnRefresh.classList.add('loading');
  refreshBtnText.textContent = "Actualizando...";

  try {
    const response = await fetch('/api/rates', {
      cache: 'no-store',
      headers: { 'Accept': 'application/json' }
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    lastSystemRetrieveTime = new Date();
    renderCards(data);

    refreshBtnText.textContent = "Actualizado";
    setTimeout(() => {
      refreshBtnText.textContent = "ACTUALIZAR AHORA";
    }, 1500);

  } catch (error) {
    console.error("Error fetching rates:", error);
    refreshBtnText.textContent = "Error de conexión";
    setTimeout(() => {
      refreshBtnText.textContent = "ACTUALIZAR AHORA";
    }, 2000);
  } finally {
    isFetching = false;
    btnRefresh.classList.remove('loading');
    resetCountdown();
    updateGlobalSystemStatus();
  }
}

// Render Exchange Cards
function renderCards(housesData) {
  if (!housesData || !Array.isArray(housesData)) return;

  cardsContainer.innerHTML = '';

  housesData.forEach((house) => {
    const meta = HOUSE_METADATA[house.source] || { icon: "🏦", title: house.source.toUpperCase(), branch: house.branch };
    
    const cardEl = document.createElement('article');
    cardEl.className = 'exchange-card';

    // Status logic
    let statusClass = "status-ok";
    let statusText = "🟢 ACTUALIZADO";

    if (house.status !== "ok") {
      statusClass = "status-error";
      statusText = "🔴 SIN CONEXIÓN";
    }

    cardEl.classList.add(statusClass);

    const retrievedTimeFormatted = house.retrievedAt ? formatTimestampDisplay(house.retrievedAt) : "--:--:--";
    const sourceTimeFormatted = house.sourceUpdatedAt ? house.sourceUpdatedAt : "--:--:--";

    if (house.status === "error") {
      cardEl.innerHTML = `
        <div class="card-header">
          <div class="house-info">
            <span class="house-title">${meta.icon} ${meta.title}</span>
            <span class="house-branch">${meta.branch}</span>
          </div>
          <span class="badge-status ${statusClass}">${statusText}</span>
        </div>
        <div class="card-error-msg">
          <p>🔴 SIN CONEXIÓN</p>
          <p style="font-size: 0.8rem; opacity: 0.8; margin-top: 0.3rem;">No fue posible obtener la cotización.</p>
        </div>
        <div class="card-footer">
          <div class="footer-ts">
            <span class="footer-ts-label">Consultado:</span>
            <span class="footer-ts-val">${retrievedTimeFormatted}</span>
          </div>
        </div>
      `;
    } else {
      // Rates Formatting
      const usdPygBuy = formatPYG(house.usd_pyg?.buy);
      const usdPygSell = formatPYG(house.usd_pyg?.sell);

      const brlPygBuy = formatPYG(house.brl_pyg?.buy);
      const brlPygSell = formatPYG(house.brl_pyg?.sell);

      const usdBrlBuy = formatDecimal(house.usd_brl?.buy, 2);
      const usdBrlSell = formatDecimal(house.usd_brl?.sell, 2);

      cardEl.innerHTML = `
        <div class="card-header">
          <div class="house-info">
            <span class="house-title">${meta.icon} ${meta.title}</span>
            <span class="house-branch">${meta.branch}</span>
          </div>
          <span class="badge-status ${statusClass}">${statusText}</span>
        </div>

        <div class="rates-grid">
          
          <!-- USD / PYG -->
          <div class="pair-block">
            <div class="pair-header">
              <span class="pair-title">USD / PYG (Dólar → Guaraní)</span>
            </div>
            <div class="pair-values">
              <div class="rate-box">
                <span class="rate-label">Compra</span>
                <span class="rate-value ${usdPygBuy === '--' ? 'unavailable' : ''}">${usdPygBuy}</span>
              </div>
              <div class="rate-box">
                <span class="rate-label">Venta</span>
                <span class="rate-value ${usdPygSell === '--' ? 'unavailable' : ''}">${usdPygSell}</span>
              </div>
            </div>
          </div>

          <!-- BRL / PYG -->
          <div class="pair-block">
            <div class="pair-header">
              <span class="pair-title">BRL / PYG (Real → Guaraní)</span>
            </div>
            <div class="pair-values">
              <div class="rate-box">
                <span class="rate-label">Compra</span>
                <span class="rate-value ${brlPygBuy === '--' ? 'unavailable' : ''}">${brlPygBuy}</span>
              </div>
              <div class="rate-box">
                <span class="rate-label">Venta</span>
                <span class="rate-value ${brlPygSell === '--' ? 'unavailable' : ''}">${brlPygSell}</span>
              </div>
            </div>
          </div>

          <!-- USD / BRL -->
          <div class="pair-block">
            <div class="pair-header">
              <span class="pair-title">USD / BRL (Dólar → Real)</span>
            </div>
            <div class="pair-values">
              <div class="rate-box">
                <span class="rate-label">Compra</span>
                <span class="rate-value ${usdBrlBuy === '--' ? 'unavailable' : ''}">${usdBrlBuy}</span>
              </div>
              <div class="rate-box">
                <span class="rate-label">Venta</span>
                <span class="rate-value ${usdBrlSell === '--' ? 'unavailable' : ''}">${usdBrlSell}</span>
              </div>
            </div>
          </div>

        </div>

        <div class="card-footer">
          <div class="footer-ts">
            <span class="footer-ts-label">● Fuente actualizada:</span>
            <span class="footer-ts-val">${sourceTimeFormatted}</span>
          </div>
          <div class="footer-ts">
            <span class="footer-ts-label">Consultado:</span>
            <span class="footer-ts-val">${retrievedTimeFormatted}</span>
          </div>
        </div>
      `;
    }

    cardsContainer.appendChild(cardEl);
  });
}

// Countdown timer loop (15 seconds)
function startCountdown() {
  if (countdownTimer) clearInterval(countdownTimer);
  
  countdownTimer = setInterval(() => {
    countdownRemaining--;
    if (countdownRemaining <= 0) {
      countdownRemaining = REFRESH_INTERVAL_SECONDS;
      fetchRates();
    }
    countdownNumberEl.textContent = countdownRemaining;
  }, 1000);
}

function resetCountdown() {
  countdownRemaining = REFRESH_INTERVAL_SECONDS;
  countdownNumberEl.textContent = countdownRemaining;
}

// Global System Status Counter
function updateGlobalSystemStatus() {
  if (!lastSystemRetrieveTime) {
    globalSystemStatusEl.textContent = "Cargando datos...";
    return;
  }
  const secondsElapsed = Math.floor((new Date() - lastSystemRetrieveTime) / 1000);
  if (secondsElapsed < 5) {
    globalSystemStatusEl.textContent = "Sistema actualizado hace un momento";
  } else {
    globalSystemStatusEl.textContent = `Sistema actualizado hace ${secondsElapsed} s`;
  }
}

function startSystemUpdateTimer() {
  if (systemUpdateTimer) clearInterval(systemUpdateTimer);
  systemUpdateTimer = setInterval(updateGlobalSystemStatus, 2000);
}

// Setup Event Listeners
btnRefresh.addEventListener('click', () => {
  fetchRates();
});

// PWA Service Worker Registration
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('./sw.js')
      .then(reg => console.log('PWA ServiceWorker registrado:', reg.scope))
      .catch(err => console.log('ServiceWorker falló:', err));
  });
}

// Initial Kickoff
document.addEventListener('DOMContentLoaded', () => {
  fetchRates();
  startCountdown();
  startSystemUpdateTimer();
});
