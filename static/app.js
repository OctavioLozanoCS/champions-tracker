// State
let currentFormat = 'all';
let currentSessionId = null;
let allSessions = [];
let allMatches = [];
let allOppMatchups = [];
let allMyPerf = [];
let pollInterval = null;
let currentRoster = ["Floette", "Garchomp", "Incineroar", "Sinistcha", "Sneasler", "Kingambit"];
let selectedBrought = [];
let selectedOppTeam = [];
let captureStream = null;
let currentSavedScreenshot = null;
let appConfig = { provider: 'gemini', gemini_api_key: '', ollama_host: 'http://localhost:11434', ollama_model: 'moondream', auto_detect_on_snap: true };
let allPokemonNames = [];

// Helper: Safe Event Listener
function on(el, event, handler) {
  if (el) {
    el.addEventListener(event, handler);
  } else {
    console.warn(`[SafeEvent] Element not found for event: ${event}`);
  }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  console.log('[App] Initializing Pokemon Champions Tracker...');

  // Setup Event Listeners FIRST so buttons work immediately!
  setupEventListeners();

  // Load initial data asynchronously
  initData();

  // Auto-poll every 5 seconds
  pollInterval = setInterval(loadData, 5000);
});

async function initData() {
  try { await loadConfig(); } catch (e) { console.error('Config load error:', e); }
  try { await loadSessions(); } catch (e) { console.error('Sessions load error:', e); }
  try { await loadRoster(); } catch (e) { console.error('Roster load error:', e); }
  try { await loadPokemonDatalist(); } catch (e) { console.error('Pokedex load error:', e); }
  try { await loadData(); } catch (e) { console.error('Data load error:', e); }
}

function setupEventListeners() {
  const formatTabs = document.getElementById('formatTabs');
  const searchInput = document.getElementById('searchInput');
  const oppFilterInput = document.getElementById('oppFilterInput');
  const myFilterInput = document.getElementById('myFilterInput');
  const refreshBtn = document.getElementById('refreshBtn');
  const exportBtn = document.getElementById('exportBtn');

  const selectWindowBtn = document.getElementById('selectWindowBtn');
  const snapDirectBtn = document.getElementById('snapDirectBtn');
  const disconnectWindowBtn = document.getElementById('disconnectWindowBtn');

  const sessionSelect = document.getElementById('sessionSelect');
  const newSessionBtn = document.getElementById('newSessionBtn');
  const clearSessionBtn = document.getElementById('clearSessionBtn');
  const manageSessionsBtn = document.getElementById('manageSessionsBtn');

  const sessionManagerModal = document.getElementById('sessionManagerModal');
  const closeSessionManagerBtn = document.getElementById('closeSessionManagerBtn');
  const doneSessionManagerBtn = document.getElementById('doneSessionManagerBtn');
  const modalCreateSessionBtn = document.getElementById('modalCreateSessionBtn');

  const matchModal = document.getElementById('matchModal');
  const openModalBtn = document.getElementById('openModalBtn');
  const closeModalBtn = document.getElementById('closeModalBtn');
  const cancelModalBtn = document.getElementById('cancelModalBtn');
  const matchForm = document.getElementById('matchForm');
  const resultToggleBtns = document.querySelectorAll('.btn-toggle');
  const rosterChips = document.getElementById('rosterChips');
  const editRosterBtn = document.getElementById('editRosterBtn');

  const addOppBtn = document.getElementById('addOppBtn');
  const clearOppBtn = document.getElementById('clearOppBtn');
  const oppQuickInput = document.getElementById('oppQuickInput');
  const retryDetectBtn = document.getElementById('retryDetectBtn');

  const openSettingsBtn = document.getElementById('openSettingsBtn');
  const settingsModal = document.getElementById('settingsModal');
  const closeSettingsBtn = document.getElementById('closeSettingsBtn');
  const cancelSettingsBtn = document.getElementById('cancelSettingsBtn');
  const settingsForm = document.getElementById('settingsForm');
  const visionProvider = document.getElementById('visionProvider');

  // Format Tabs
  on(formatTabs, 'click', (e) => {
    if (e.target.classList.contains('tab')) {
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      e.target.classList.add('active');
      currentFormat = e.target.dataset.format;
      loadData();
    }
  });

  // Search & Filter
  on(searchInput, 'input', renderMatchHistory);
  on(oppFilterInput, 'input', renderOppTable);
  on(myFilterInput, 'input', renderMyTable);

  // Top Actions
  on(refreshBtn, 'click', () => { loadSessions(); loadData(); });
  on(exportBtn, 'click', exportData);

  // WINDOW & SNAP BUTTONS
  on(selectWindowBtn, 'click', handleSelectGameWindow);
  on(disconnectWindowBtn, 'click', disconnectGameWindow);
  on(snapDirectBtn, 'click', handleDirectSnap);

  // Global Hotkey (F8 or Shift+Space to Snap!)
  window.addEventListener('keydown', (e) => {
    if (e.key === 'F8' || (e.shiftKey && e.code === 'Space')) {
      if (document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA') {
        e.preventDefault();
        console.log('[Hotkey] Triggered snap via keyboard hotkey');
        handleDirectSnap();
      }
    }
  });

  // Global Clipboard Paste (Ctrl + V)
  window.addEventListener('paste', handleGlobalPaste);

  // Sessions Controls
  on(sessionSelect, 'change', handleSessionSelectChange);
  on(newSessionBtn, 'click', handleNewSession);
  on(clearSessionBtn, 'click', handleClearSession);
  on(manageSessionsBtn, 'click', openSessionManager);
  on(closeSessionManagerBtn, 'click', closeSessionManager);
  on(doneSessionManagerBtn, 'click', closeSessionManager);
  on(modalCreateSessionBtn, 'click', handleNewSession);
  on(sessionManagerModal, 'click', (e) => {
    if (e.target === sessionManagerModal) closeSessionManager();
  });

  // Match Modal Controls
  on(openModalBtn, 'click', () => openModal());
  on(closeModalBtn, 'click', closeModal);
  on(cancelModalBtn, 'click', closeModal);
  on(matchModal, 'click', (e) => {
    if (e.target === matchModal) closeModal();
  });

  // Settings Controls
  on(openSettingsBtn, 'click', openSettings);
  on(closeSettingsBtn, 'click', closeSettings);
  on(cancelSettingsBtn, 'click', closeSettings);
  on(settingsModal, 'click', (e) => {
    if (e.target === settingsModal) closeSettings();
  });
  on(visionProvider, 'change', updateSettingsProviderUI);
  on(settingsForm, 'submit', handleSaveSettings);

  // Result Toggle Buttons
  resultToggleBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      resultToggleBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const resInput = document.getElementById('matchResult');
      if (resInput) resInput.value = btn.dataset.result;
    });
  });

  // Roster Chip Clicks
  on(rosterChips, 'click', handleRosterChipClick);
  on(editRosterBtn, 'click', handleEditRoster);

  // Opponent Chips & Autocomplete
  on(addOppBtn, 'click', addOpponentFromInput);
  on(clearOppBtn, 'click', () => {
    selectedOppTeam = [];
    renderOppChips();
  });
  on(oppQuickInput, 'keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addOpponentFromInput();
    }
  });

  on(retryDetectBtn, 'click', () => {
    const previewImg = document.getElementById('previewImg');
    if (previewImg && previewImg.src) {
      triggerVisionAutoDetect(previewImg.src);
    }
  });

  on(matchForm, 'submit', handleFormSubmit);

  console.log('[App] All event listeners registered successfully.');
}

// -------------------------------------------------------------
// SEPARATE BUTTON 1: Select Game Window
// -------------------------------------------------------------
async function handleSelectGameWindow() {
  console.log('[Window] Opening window selector prompt...');
  try {
    const stream = await navigator.mediaDevices.getDisplayMedia({
      video: {
        displaySurface: "window",
        frameRate: { ideal: 30 }
      },
      audio: false
    });

    captureStream = stream;
    const captureVideo = document.getElementById('captureVideo');
    if (captureVideo) captureVideo.srcObject = stream;

    const track = stream.getVideoTracks()[0];
    const label = track.label || "Game Window";

    const selectWindowBtn = document.getElementById('selectWindowBtn');
    const windowBtnText = document.getElementById('windowBtnText');
    const windowActivePill = document.getElementById('windowActivePill');
    const windowActiveName = document.getElementById('windowActiveName');

    if (selectWindowBtn) selectWindowBtn.classList.add('linked');
    if (windowBtnText) windowBtnText.textContent = `🟢 Linked: ${label.length > 18 ? label.slice(0, 16) + '...' : label}`;
    if (windowActiveName) windowActiveName.textContent = `Linked: ${label}`;
    if (windowActivePill) windowActivePill.style.display = 'inline-flex';

    track.addEventListener('ended', disconnectGameWindow);
    console.log('[Window] Successfully linked window:', label);
  } catch (err) {
    if (err.name !== 'NotAllowedError') {
      alert('Could not link game window: ' + err.message);
    }
  }
}

function disconnectGameWindow() {
  if (captureStream) {
    captureStream.getTracks().forEach(t => t.stop());
    captureStream = null;
  }
  const captureVideo = document.getElementById('captureVideo');
  if (captureVideo) captureVideo.srcObject = null;

  const selectWindowBtn = document.getElementById('selectWindowBtn');
  const windowBtnText = document.getElementById('windowBtnText');
  const windowActivePill = document.getElementById('windowActivePill');

  if (selectWindowBtn) selectWindowBtn.classList.remove('linked');
  if (windowBtnText) windowBtnText.textContent = '🔗 Select Game Window';
  if (windowActivePill) windowActivePill.style.display = 'none';
  console.log('[Window] Disconnected');
}

// -------------------------------------------------------------
// SEPARATE BUTTON 2: Fast 1-Click Direct SNAP
// -------------------------------------------------------------
async function handleDirectSnap() {
  console.log('[Snap] Direct snap clicked...');
  const captureVideo = document.getElementById('captureVideo');

  if (!captureStream || !captureVideo || !captureVideo.srcObject) {
    const shouldLink = confirm("No game window is linked yet. Would you like to select your game window now?");
    if (shouldLink) {
      await handleSelectGameWindow();
      if (captureStream) {
        setTimeout(executeSnap, 400);
      }
    }
    return;
  }

  executeSnap();
}

async function executeSnap() {
  const captureVideo = document.getElementById('captureVideo');
  const captureCanvas = document.getElementById('captureCanvas');

  if (!captureVideo || !captureVideo.videoWidth) {
    alert('Video stream not ready yet. Please try again in a moment.');
    return;
  }

  captureCanvas.width = captureVideo.videoWidth;
  captureCanvas.height = captureVideo.videoHeight;
  const ctx = captureCanvas.getContext('2d');
  ctx.drawImage(captureVideo, 0, 0, captureCanvas.width, captureCanvas.height);

  const dataUrl = captureCanvas.toDataURL('image/png');
  console.log('[Snap] Captured frame from window, saving...');
  await uploadAndPreviewScreenshot(dataUrl);
}

// Global Clipboard Paste (Ctrl+V)
async function handleGlobalPaste(e) {
  const items = (e.clipboardData || e.originalEvent.clipboardData).items;
  for (let item of items) {
    if (item.type.indexOf('image') !== -1) {
      const blob = item.getAsFile();
      const reader = new FileReader();
      reader.onload = async (event) => {
        console.log('[Paste] Image pasted from clipboard, saving...');
        await uploadAndPreviewScreenshot(event.target.result);
      };
      reader.readAsDataURL(blob);
      e.preventDefault();
      break;
    }
  }
}

async function uploadAndPreviewScreenshot(dataUrl) {
  try {
    const res = await fetch('/api/save-screenshot', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ image: dataUrl })
    });

    if (res.ok) {
      const result = await res.json();
      currentSavedScreenshot = result;

      const previewImg = document.getElementById('previewImg');
      const previewFilename = document.getElementById('previewFilename');
      const modalScreenshotPreview = document.getElementById('modalScreenshotPreview');
      const matchSource = document.getElementById('matchSource');

      if (previewImg) previewImg.src = dataUrl;
      if (previewFilename) previewFilename.textContent = result.filename;
      if (modalScreenshotPreview) modalScreenshotPreview.style.display = 'flex';
      if (matchSource) matchSource.value = 'screenshot';

      openModal();

      if (appConfig.auto_detect_on_snap && appConfig.provider !== 'disabled') {
        triggerVisionAutoDetect(dataUrl);
      }
    }
  } catch (err) {
    console.error('Error saving screenshot:', err);
  }
}

// -------------------------------------------------------------
// Vision Auto-Detection
// -------------------------------------------------------------
async function triggerVisionAutoDetect(dataUrl) {
  const autoDetectBanner = document.getElementById('autoDetectBanner');
  const autoDetectText = document.getElementById('autoDetectText');
  if (autoDetectBanner) autoDetectBanner.style.display = 'flex';
  if (autoDetectText) autoDetectText.textContent = '⚡ Gemini Flash scanning opponent team & trainer name...';

  try {
    const res = await fetch('/api/auto-detect', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ image: dataUrl })
    });

    const result = await res.json();
    if (result.success && result.data) {
      const d = result.data;
      if (d.opponent_name) {
        const oppNameInput = document.getElementById('matchOpponent');
        if (oppNameInput) oppNameInput.value = d.opponent_name;
      }
      if (d.format) {
        const fmtInput = document.getElementById('matchFormat');
        if (fmtInput) fmtInput.value = d.format;
      }
      if (d.opponent_team && Array.isArray(d.opponent_team)) {
        selectedOppTeam = d.opponent_team;
        renderOppChips();
      }

      if (autoDetectText) {
        autoDetectText.textContent = `✓ Detected Opponent: ${d.opponent_name || 'Opponent'} & ${selectedOppTeam.length} Pokémon!`;
      }
      setTimeout(() => {
        if (autoDetectBanner) autoDetectBanner.style.display = 'none';
      }, 4000);
    } else {
      if (result.configured === false) {
        if (autoDetectText) {
          autoDetectText.innerHTML = `⚠️ ${result.message} <a href="#" id="openSettingsFromBanner" style="color:#60a5fa; text-decoration:underline; margin-left:4px;">Configure Now</a>`;
          document.getElementById('openSettingsFromBanner')?.addEventListener('click', (e) => {
            e.preventDefault();
            openSettings();
          });
        }
      } else {
        if (autoDetectText) autoDetectText.textContent = result.message || 'Vision scan could not parse screen.';
      }
    }
  } catch (err) {
    if (autoDetectText) autoDetectText.textContent = 'Vision detection error: ' + err.message;
  }
}

// -------------------------------------------------------------
// SESSIONS MANAGEMENT
// -------------------------------------------------------------
async function loadSessions() {
  try {
    const res = await fetch('/api/sessions');
    if (res.ok) {
      const data = await res.json();
      allSessions = data.sessions || [];
      if (!currentSessionId) {
        currentSessionId = data.active_id || (allSessions[0] ? allSessions[0].id : 1);
      }
      renderSessionDropdown();
    }
  } catch (err) {
    console.error('Failed to load sessions:', err);
  }
}

function renderSessionDropdown() {
  const sessionSelect = document.getElementById('sessionSelect');
  const sessionSummaryPill = document.getElementById('sessionSummaryPill');
  const sessionHistoryBadge = document.getElementById('sessionHistoryBadge');
  const kpiRecord = document.getElementById('kpiRecord');

  if (!sessionSelect) return;

  let html = allSessions.map(s => {
    const isCur = String(s.id) === String(currentSessionId);
    return `<option value="${s.id}" ${isCur ? 'selected' : ''}>${escapeHtml(s.name)} (${s.wins}W - ${s.losses}L)</option>`;
  }).join('');

  html += `<option value="all" ${currentSessionId === 'all' ? 'selected' : ''}>🌐 All Sessions (Lifetime)</option>`;
  sessionSelect.innerHTML = html;

  const curSession = allSessions.find(s => String(s.id) === String(currentSessionId));
  if (curSession) {
    if (sessionSummaryPill) sessionSummaryPill.textContent = `${curSession.name}: ${curSession.wins}W - ${curSession.losses}L (${curSession.win_rate}%)`;
    if (sessionHistoryBadge) sessionHistoryBadge.textContent = curSession.name;
  } else if (currentSessionId === 'all') {
    if (sessionSummaryPill) sessionSummaryPill.textContent = `Lifetime: ${kpiRecord ? kpiRecord.textContent : ''}`;
    if (sessionHistoryBadge) sessionHistoryBadge.textContent = 'Lifetime All Matches';
  }
}

async function handleSessionSelectChange(e) {
  currentSessionId = e.target.value;
  if (currentSessionId !== 'all') {
    await fetch('/api/sessions/active', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: currentSessionId })
    });
  }
  renderSessionDropdown();
  loadData();
}

async function handleNewSession() {
  const name = prompt("Enter a name for your new session (e.g. 'Session 2', 'Master Ball Climb', 'Tournament'):");
  if (!name || !name.trim()) return;

  try {
    const res = await fetch('/api/sessions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: name.trim() })
    });
    if (res.ok) {
      const data = await res.json();
      currentSessionId = data.id;
      await loadSessions();
      closeSessionManager();
      loadData();
    }
  } catch (err) {
    alert('Failed to create session');
  }
}

async function handleClearSession() {
  if (currentSessionId === 'all') {
    alert("Please select a specific session from the dropdown to clear.");
    return;
  }

  const curSession = allSessions.find(s => String(s.id) === String(currentSessionId));
  const sName = curSession ? curSession.name : `Session ${currentSessionId}`;

  const confirmed = confirm(`Are you sure you want to clear/delete all matches in "${sName}"?\n\nThis will reset the session to 0 matches.`);
  if (!confirmed) return;

  try {
    const res = await fetch('/api/sessions/clear', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: currentSessionId })
    });
    if (res.ok) {
      await loadSessions();
      loadData();
    }
  } catch (err) {
    alert('Failed to clear session matches');
  }
}

function openSessionManager() {
  renderSessionManagerTable();
  const sessionManagerModal = document.getElementById('sessionManagerModal');
  if (sessionManagerModal) sessionManagerModal.classList.add('open');
}

function closeSessionManager() {
  const sessionManagerModal = document.getElementById('sessionManagerModal');
  if (sessionManagerModal) sessionManagerModal.classList.remove('open');
}

function renderSessionManagerTable() {
  const sessionManagerBody = document.getElementById('sessionManagerBody');
  if (!sessionManagerBody) return;

  sessionManagerBody.innerHTML = allSessions.map(s => {
    const isActive = String(s.id) === String(currentSessionId);
    return `
      <tr>
        <td><strong>${escapeHtml(s.name)}</strong></td>
        <td>${s.wins}W - ${s.losses}L</td>
        <td>${s.win_rate}%</td>
        <td>${isActive ? '<span class="badge-saved">Active</span>' : '<span style="color:var(--text-muted); font-size:12px;">Archived</span>'}</td>
        <td>
          ${!isActive ? `<button class="btn btn-sm btn-secondary" onclick="activateSessionFromModal(${s.id})">Switch To</button>` : ''}
          <button class="btn btn-sm btn-danger" style="margin-left:4px;" onclick="deleteSessionFromModal(${s.id})">Delete</button>
        </td>
      </tr>
    `;
  }).join('');
}

window.activateSessionFromModal = async function(id) {
  currentSessionId = id;
  await fetch('/api/sessions/active', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id: id })
  });
  await loadSessions();
  closeSessionManager();
  loadData();
};

window.deleteSessionFromModal = async function(id) {
  if (allSessions.length <= 1) {
    alert("Cannot delete the only session. Create a new session first!");
    return;
  }
  if (!confirm(`Delete this session and all its match data permanently?`)) return;

  try {
    const res = await fetch(`/api/sessions/${id}`, { method: 'DELETE' });
    if (res.ok) {
      currentSessionId = null;
      await loadSessions();
      renderSessionManagerTable();
      loadData();
    }
  } catch (e) {
    alert('Failed to delete session');
  }
};

// -------------------------------------------------------------
// Pokémon Datalist & Fast Autocomplete
// -------------------------------------------------------------
async function loadPokemonDatalist() {
  try {
    const res = await fetch('/pokemon_list.json');
    if (res.ok) {
      allPokemonNames = await res.json();
      const pokemonDatalist = document.getElementById('pokemonDatalist');
      if (pokemonDatalist) {
        pokemonDatalist.innerHTML = allPokemonNames.slice(0, 300).map(p => `<option value="${escapeHtml(p)}">`).join('');
      }
    }
  } catch (e) {
    console.error(e);
  }
}

function renderOppChips() {
  const oppChips = document.getElementById('oppChips');
  const oppTeamInput = document.getElementById('oppTeamInput');

  if (oppChips) {
    oppChips.innerHTML = selectedOppTeam.map((p, idx) => `
      <span class="opp-chip">
        ${escapeHtml(p)}
        <span class="opp-chip-remove" onclick="removeOpponentChip(${idx})">&times;</span>
      </span>
    `).join('');
  }
  if (oppTeamInput) oppTeamInput.value = selectedOppTeam.join(', ');
}

window.removeOpponentChip = function(idx) {
  selectedOppTeam.splice(idx, 1);
  renderOppChips();
};

function addOpponentFromInput() {
  const oppQuickInput = document.getElementById('oppQuickInput');
  if (!oppQuickInput) return;
  const val = oppQuickInput.value.trim();
  if (!val) return;

  const formatted = val.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase()).join(' ');

  if (!selectedOppTeam.includes(formatted)) {
    if (selectedOppTeam.length >= 6) {
      selectedOppTeam.shift();
    }
    selectedOppTeam.push(formatted);
    renderOppChips();
  }

  oppQuickInput.value = '';
  oppQuickInput.focus();
}

// -------------------------------------------------------------
// Roster Management
// -------------------------------------------------------------
async function loadRoster() {
  try {
    const res = await fetch('/api/roster');
    if (res.ok) {
      currentRoster = await res.json();
    }
  } catch (e) {
    console.error(e);
  }
  renderRosterChips();
}

function renderRosterChips() {
  const rosterChips = document.getElementById('rosterChips');
  const myTeamInput = document.getElementById('myTeamInput');

  if (rosterChips) {
    rosterChips.innerHTML = currentRoster.map(p => {
      const isSelected = selectedBrought.includes(p);
      return `<div class="roster-chip ${isSelected ? 'selected' : ''}" data-pokemon="${escapeHtml(p)}">${escapeHtml(p)}</div>`;
    }).join('');
  }
  if (myTeamInput) myTeamInput.value = selectedBrought.join(', ');
}

function handleRosterChipClick(e) {
  const chip = e.target.closest('.roster-chip');
  if (!chip) return;
  const pName = chip.dataset.pokemon;

  if (selectedBrought.includes(pName)) {
    selectedBrought = selectedBrought.filter(p => p !== pName);
  } else {
    if (selectedBrought.length >= 4) {
      selectedBrought.shift();
    }
    selectedBrought.push(pName);
  }
  renderRosterChips();
}

async function handleEditRoster() {
  const currentStr = currentRoster.join(', ');
  const input = prompt('Enter your 6-Pokémon Roster (comma-separated):', currentStr);
  if (!input) return;

  const newRoster = input.split(',').map(s => s.trim()).filter(Boolean);
  if (newRoster.length === 0) return;

  try {
    const res = await fetch('/api/roster', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newRoster)
    });
    if (res.ok) {
      currentRoster = newRoster;
      selectedBrought = [];
      renderRosterChips();
    }
  } catch (err) {
    alert('Failed to update roster');
  }
}

// -------------------------------------------------------------
// Settings Management
// -------------------------------------------------------------
async function loadConfig() {
  try {
    const res = await fetch('/api/config');
    if (res.ok) {
      appConfig = await res.json();
      const visionProvider = document.getElementById('visionProvider');
      const geminiApiKey = document.getElementById('geminiApiKey');
      const ollamaHost = document.getElementById('ollamaHost');
      const ollamaModel = document.getElementById('ollamaModel');
      const autoDetectOnSnap = document.getElementById('autoDetectOnSnap');

      if (visionProvider) visionProvider.value = appConfig.provider || 'gemini';
      if (geminiApiKey) geminiApiKey.value = appConfig.gemini_api_key || '';
      if (ollamaHost) ollamaHost.value = appConfig.ollama_host || 'http://localhost:11434';
      if (ollamaModel) ollamaModel.value = appConfig.ollama_model || 'moondream';
      if (autoDetectOnSnap) autoDetectOnSnap.checked = appConfig.auto_detect_on_snap !== false;
      updateSettingsProviderUI();
    }
  } catch (e) {
    console.error(e);
  }
}

function updateSettingsProviderUI() {
  const visionProvider = document.getElementById('visionProvider');
  const geminiConfigGroup = document.getElementById('geminiConfigGroup');
  const ollamaConfigGroup = document.getElementById('ollamaConfigGroup');

  if (!visionProvider) return;
  const p = visionProvider.value;
  if (geminiConfigGroup) geminiConfigGroup.style.display = p === 'gemini' ? 'block' : 'none';
  if (ollamaConfigGroup) ollamaConfigGroup.style.display = p === 'ollama' ? 'block' : 'none';
}

function openSettings() {
  const settingsModal = document.getElementById('settingsModal');
  if (settingsModal) settingsModal.classList.add('open');
}

function closeSettings() {
  const settingsModal = document.getElementById('settingsModal');
  if (settingsModal) settingsModal.classList.remove('open');
}

async function handleSaveSettings(e) {
  e.preventDefault();
  const visionProvider = document.getElementById('visionProvider');
  const geminiApiKey = document.getElementById('geminiApiKey');
  const ollamaHost = document.getElementById('ollamaHost');
  const ollamaModel = document.getElementById('ollamaModel');
  const autoDetectOnSnap = document.getElementById('autoDetectOnSnap');

  const payload = {
    provider: visionProvider ? visionProvider.value : 'gemini',
    gemini_api_key: geminiApiKey ? geminiApiKey.value.trim() : '',
    ollama_host: ollamaHost ? ollamaHost.value.trim() : 'http://localhost:11434',
    ollama_model: ollamaModel ? ollamaModel.value.trim() : 'moondream',
    auto_detect_on_snap: autoDetectOnSnap ? autoDetectOnSnap.checked : true
  };

  try {
    const res = await fetch('/api/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (res.ok) {
      appConfig = payload;
      closeSettings();
      alert('Settings saved successfully!');
    }
  } catch (err) {
    alert('Failed to save settings: ' + err.message);
  }
}

// -------------------------------------------------------------
// Load Stats & Match History (Filtered by Session)
// -------------------------------------------------------------
async function loadData() {
  try {
    let queryParams = [];
    if (currentFormat !== 'all') {
      queryParams.push(`format=${encodeURIComponent(currentFormat)}`);
    }
    if (currentSessionId) {
      queryParams.push(`session_id=${encodeURIComponent(currentSessionId)}`);
    }
    const queryString = queryParams.length ? `?${queryParams.join('&')}` : '';

    const [statsRes, matchesRes] = await Promise.all([
      fetch(`/api/stats${queryString}`),
      fetch(`/api/matches${queryString}`)
    ]);

    if (!statsRes.ok || !matchesRes.ok) return;

    const stats = await statsRes.json();
    const matches = await matchesRes.json();

    allMatches = matches;
    allOppMatchups = stats.opp_matchups || [];
    allMyPerf = stats.my_performance || [];

    updateKPIs(stats);
    renderOppTable();
    renderMyTable();
    renderMatchHistory();
  } catch (err) {
    console.error('Failed to load data:', err);
  }
}

function updateKPIs(stats) {
  const kpiTotal = document.getElementById('kpiTotal');
  const kpiRecord = document.getElementById('kpiRecord');
  const kpiWinRate = document.getElementById('kpiWinRate');
  const winRateBar = document.getElementById('winRateBar');
  const kpiWins = document.getElementById('kpiWins');
  const kpiLosses = document.getElementById('kpiLosses');
  const kpiStreak = document.getElementById('kpiStreak');

  if (kpiTotal) kpiTotal.textContent = stats.total || 0;
  if (kpiRecord) kpiRecord.textContent = `${stats.wins || 0}W - ${stats.losses || 0}L`;
  if (kpiWinRate) kpiWinRate.textContent = `${stats.win_rate || 0.0}%`;
  if (winRateBar) winRateBar.style.width = `${Math.min(100, Math.max(0, stats.win_rate || 0))}%`;
  if (kpiWins) kpiWins.textContent = stats.wins || 0;
  if (kpiLosses) kpiLosses.textContent = stats.losses || 0;
  if (kpiStreak) {
    kpiStreak.textContent = stats.streak || '-';
    if (stats.streak && stats.streak.startsWith('W')) {
      kpiStreak.className = 'kpi-value text-win';
    } else if (stats.streak && stats.streak.startsWith('L')) {
      kpiStreak.className = 'kpi-value text-loss';
    } else {
      kpiStreak.className = 'kpi-value';
    }
  }
}

function renderOppTable() {
  const oppFilterInput = document.getElementById('oppFilterInput');
  const oppMatchupsBody = document.getElementById('oppMatchupsBody');
  if (!oppMatchupsBody) return;

  const query = oppFilterInput ? oppFilterInput.value.toLowerCase().trim() : '';
  const filtered = allOppMatchups.filter(m => m.pokemon.toLowerCase().includes(query));

  if (filtered.length === 0) {
    oppMatchupsBody.innerHTML = `<tr><td colspan="4" class="empty-state">${query ? 'No matching Pokémon found' : 'No opponent data yet in this session'}</td></tr>`;
    return;
  }

  oppMatchupsBody.innerHTML = filtered.map(item => {
    const rateColor = item.win_rate >= 60 ? 'text-win' : item.win_rate <= 40 ? 'text-loss' : 'text-accent';
    return `
      <tr>
        <td><strong>${escapeHtml(item.pokemon)}</strong></td>
        <td class="${rateColor}"><strong>${item.win_rate}%</strong></td>
        <td>${item.wins}W - ${item.losses}L</td>
        <td>${item.total}</td>
      </tr>
    `;
  }).join('');
}

function renderMyTable() {
  const myFilterInput = document.getElementById('myFilterInput');
  const myPerfBody = document.getElementById('myPerfBody');
  if (!myPerfBody) return;

  const query = myFilterInput ? myFilterInput.value.toLowerCase().trim() : '';
  const filtered = allMyPerf.filter(m => m.pokemon.toLowerCase().includes(query));

  if (filtered.length === 0) {
    myPerfBody.innerHTML = `<tr><td colspan="4" class="empty-state">${query ? 'No matching Pokémon found' : 'No team data yet in this session'}</td></tr>`;
    return;
  }

  myPerfBody.innerHTML = filtered.map(item => {
    const rateColor = item.win_rate >= 60 ? 'text-win' : item.win_rate <= 40 ? 'text-loss' : 'text-accent';
    return `
      <tr>
        <td><strong>${escapeHtml(item.pokemon)}</strong></td>
        <td class="${rateColor}"><strong>${item.win_rate}%</strong></td>
        <td>${item.wins}W - ${item.losses}L</td>
        <td>${item.total}</td>
      </tr>
    `;
  }).join('');
}

function renderMatchHistory() {
  const searchInput = document.getElementById('searchInput');
  const matchList = document.getElementById('matchList');
  if (!matchList) return;

  const query = searchInput ? searchInput.value.toLowerCase().trim() : '';
  const filtered = allMatches.filter(m => {
    if (!query) return true;
    const oppName = (m.opponent_name || '').toLowerCase();
    const myTeamStr = (m.my_team || []).join(' ').toLowerCase();
    const oppTeamStr = (m.opp_team || []).join(' ').toLowerCase();
    const notesStr = (m.notes || '').toLowerCase();
    return oppName.includes(query) || myTeamStr.includes(query) || oppTeamStr.includes(query) || notesStr.includes(query);
  });

  if (filtered.length === 0) {
    matchList.innerHTML = `<div class="empty-state">${query ? 'No battles match your search' : 'No battles logged in this session yet.'}</div>`;
    return;
  }

  matchList.innerHTML = filtered.map(m => {
    const resClass = m.result === 'WIN' ? 'win' : m.result === 'LOSS' ? 'loss' : 'draw';
    const sourceBadge = m.source === 'screenshot' 
      ? '<span style="font-size:10px; background:rgba(59,130,246,0.2); color:#60a5fa; padding:2px 6px; border-radius:4px; margin-left:6px;">📸 Vision/Screenshot</span>'
      : '';
    
    return `
      <div class="match-item">
        <div>
          <span class="result-badge ${resClass}">${m.result}</span>
          ${m.score ? `<div style="font-size:12px; font-weight:600; color:var(--text-muted); margin-top:4px; text-align:center;">${escapeHtml(m.score)}</div>` : ''}
        </div>

        <div class="match-meta-box">
          <div class="match-opp-name">${escapeHtml(m.opponent_name || 'Opponent')}${sourceBadge}</div>
          <div class="match-format-tag">${escapeHtml(m.format || 'Ranked')} ${m.tier ? `• ${escapeHtml(m.tier)}` : ''}</div>
          <div class="match-time">${escapeHtml(m.created_at || '')}</div>
        </div>

        <div>
          <div class="team-box-title">My Team:</div>
          <div>
            ${(m.my_team || []).map(p => `<span class="pokemon-tag my">${escapeHtml(p)}</span>`).join('')}
          </div>
          ${m.mvp ? `<div class="match-notes-pill">⭐ MVP: <strong>${escapeHtml(m.mvp)}</strong></div>` : ''}
        </div>

        <div>
          <div class="team-box-title">Opponent Team:</div>
          <div>
            ${(m.opp_team || []).map(p => `<span class="pokemon-tag opp">${escapeHtml(p)}</span>`).join('')}
          </div>
          ${m.notes ? `<div class="match-notes-pill">📝 ${escapeHtml(m.notes)}</div>` : ''}
        </div>

        <div class="match-actions">
          <button class="btn-icon" title="Delete Match" onclick="deleteMatch(${m.id})">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M10 11v6M14 11v6"/></svg>
          </button>
        </div>
      </div>
    `;
  }).join('');
}

// -------------------------------------------------------------
// Modal Controls
// -------------------------------------------------------------
function openModal() {
  const matchForm = document.getElementById('matchForm');
  const modalScreenshotPreview = document.getElementById('modalScreenshotPreview');
  const autoDetectBanner = document.getElementById('autoDetectBanner');
  const matchModal = document.getElementById('matchModal');
  const modalTitle = document.getElementById('modalTitle');
  const matchResultInput = document.getElementById('matchResult');
  const resultToggleBtns = document.querySelectorAll('.btn-toggle');

  if (!currentSavedScreenshot) {
    if (matchForm) matchForm.reset();
    const editMatchId = document.getElementById('editMatchId');
    if (editMatchId) editMatchId.value = '';
    if (modalScreenshotPreview) modalScreenshotPreview.style.display = 'none';
    if (autoDetectBanner) autoDetectBanner.style.display = 'none';
    selectedBrought = [];
    selectedOppTeam = [];
    renderRosterChips();
    renderOppChips();
  }
  
  if (modalTitle) modalTitle.textContent = 'Log New Battle';
  resultToggleBtns.forEach(b => b.classList.remove('active'));
  const winBtn = document.querySelector('.btn-toggle.win');
  if (winBtn) winBtn.classList.add('active');
  if (matchResultInput) matchResultInput.value = 'WIN';

  if (matchModal) matchModal.classList.add('open');
}

function closeModal() {
  const matchModal = document.getElementById('matchModal');
  const autoDetectBanner = document.getElementById('autoDetectBanner');
  if (matchModal) matchModal.classList.remove('open');
  currentSavedScreenshot = null;
  if (autoDetectBanner) autoDetectBanner.style.display = 'none';
}

async function handleFormSubmit(e) {
  e.preventDefault();
  
  const myTeamInput = document.getElementById('myTeamInput');
  const oppTeamInput = document.getElementById('oppTeamInput');
  const matchResultInput = document.getElementById('matchResult');
  const matchFormat = document.getElementById('matchFormat');
  const matchTier = document.getElementById('matchTier');
  const matchOpponent = document.getElementById('matchOpponent');
  const matchScore = document.getElementById('matchScore');
  const matchMvp = document.getElementById('matchMvp');
  const matchSource = document.getElementById('matchSource');
  const matchNotes = document.getElementById('matchNotes');

  const myTeam = selectedBrought.length > 0 
    ? selectedBrought 
    : (myTeamInput ? myTeamInput.value.split(',').map(s => s.trim()).filter(Boolean) : []);

  if (myTeam.length === 0) {
    alert('Please select or enter the Pokémon you brought!');
    return;
  }

  const oppTeam = selectedOppTeam.length > 0
    ? selectedOppTeam
    : (oppTeamInput ? oppTeamInput.value.split(',').map(s => s.trim()).filter(Boolean) : []);

  if (oppTeam.length === 0) {
    alert('Please specify the opponent Pokémon faced!');
    return;
  }

  const payload = {
    result: matchResultInput ? matchResultInput.value : 'WIN',
    format: matchFormat ? matchFormat.value : 'Ranked Doubles',
    tier: matchTier ? matchTier.value.trim() : '',
    opponent_name: matchOpponent ? matchOpponent.value.trim() : '',
    score: matchScore ? matchScore.value.trim() : '',
    my_team: myTeam,
    opp_team: oppTeam,
    mvp: matchMvp ? matchMvp.value.trim() : '',
    source: matchSource ? matchSource.value : 'manual',
    notes: matchNotes ? matchNotes.value.trim() : '',
    session_id: currentSessionId !== 'all' ? parseInt(currentSessionId) : null
  };

  try {
    const res = await fetch('/api/matches', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (res.ok) {
      closeModal();
      await loadSessions();
      loadData();
    } else {
      const err = await res.json();
      alert('Error saving match: ' + (err.error || 'Unknown error'));
    }
  } catch (err) {
    alert('Failed to connect to server: ' + err.message);
  }
}

async function deleteMatch(id) {
  if (!confirm(`Delete match #${id}?`)) return;

  try {
    const res = await fetch(`/api/matches/${id}`, { method: 'DELETE' });
    if (res.ok) {
      await loadSessions();
      loadData();
    }
  } catch (err) {
    alert('Failed to delete match');
  }
}

async function exportData() {
  try {
    const query = currentSessionId ? `?session_id=${encodeURIComponent(currentSessionId)}` : '';
    const res = await fetch(`/api/export${query}`);
    const data = await res.json();
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `pokemon_champions_matches_${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
  } catch (err) {
    alert('Export failed');
  }
}

function escapeHtml(text) {
  if (!text) return '';
  const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
  return String(text).replace(/[&<>"']/g, m => map[m]);
}
