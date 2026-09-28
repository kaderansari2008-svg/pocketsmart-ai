/**
 * PocketSmart AI: Interactive Frontend Application
 * Architecture: Vanilla ES6+ Modular Client
 */

// Application State
const state = {
  summary: null,
  transactions: [],
  goals: [],
  subscriptions: [],
  affordabilityHistory: [],
  currentTab: 'dashboard',
  speechRecognition: null,
  isListening: false,
  lastEvaluatedPurchase: null,
  geminiApiKey: localStorage.getItem('pocketsmart_gemini_key') || ''
};

// DOM Elements
const elements = {
  // Navigation
  tabButtons: document.querySelectorAll('.tab-btn'),
  tabPanes: document.querySelectorAll('.tab-pane'),
  themeToggleBtn: document.getElementById('themeToggleBtn'),
  themeMoonIcon: document.getElementById('themeMoonIcon'),
  headerHealthPill: document.getElementById('headerHealthPill'),
  headerHealthText: document.getElementById('headerHealthText'),
  resetDemoBtn: document.getElementById('resetDemoBtn'),

  // Metrics
  statIncome: document.getElementById('statIncome'),
  statExpenses: document.getElementById('statExpenses'),
  statSurplus: document.getElementById('statSurplus'),
  statSavingsRate: document.getElementById('statSavingsRate'),
  statBurnRate: document.getElementById('statBurnRate'),
  statDaysLeft: document.getElementById('statDaysLeft'),

  // 50/30/20 Rule
  ruleAdherenceBadge: document.getElementById('ruleAdherenceBadge'),
  needsSpentText: document.getElementById('needsSpentText'),
  needsTargetText: document.getElementById('needsTargetText'),
  needsProgressBar: document.getElementById('needsProgressBar'),
  needsStatusMsg: document.getElementById('needsStatusMsg'),
  wantsSpentText: document.getElementById('wantsSpentText'),
  wantsTargetText: document.getElementById('wantsTargetText'),
  wantsProgressBar: document.getElementById('wantsProgressBar'),
  wantsStatusMsg: document.getElementById('wantsStatusMsg'),
  savingsSpentText: document.getElementById('savingsSpentText'),
  savingsTargetText: document.getElementById('savingsTargetText'),
  savingsProgressBar: document.getElementById('savingsProgressBar'),
  savingsStatusMsg: document.getElementById('savingsStatusMsg'),

  // Velocity & Insight
  categoryListContainer: document.getElementById('categoryListContainer'),
  velocityProjectedSpend: document.getElementById('velocityProjectedSpend'),
  velocityProjectedSurplus: document.getElementById('velocityProjectedSurplus'),
  dashboardAiInsightText: document.getElementById('dashboardAiInsightText'),

  // "Can I Afford This?"
  affordabilityForm: document.getElementById('affordabilityForm'),
  affordItemName: document.getElementById('affordItemName'),
  affordPrice: document.getElementById('affordPrice'),
  affordCategory: document.getElementById('affordCategory'),
  affordUrgency: document.getElementById('affordUrgency'),
  affordInstallments: document.getElementById('affordInstallments'),
  evalPlaceholder: document.getElementById('evalPlaceholder'),
  evalContent: document.getElementById('evalContent'),
  evalVerdictPill: document.getElementById('evalVerdictPill'),
  evalScoreValue: document.getElementById('evalScoreValue'),
  evalHeadline: document.getElementById('evalHeadline'),
  evalGaugeFill: document.getElementById('evalGaugeFill'),
  evalReasonsList: document.getElementById('evalReasonsList'),
  evalRecsList: document.getElementById('evalRecsList'),
  logApprovedPurchaseBtn: document.getElementById('logApprovedPurchaseBtn'),
  createGoalFromEvalBtn: document.getElementById('createGoalFromEvalBtn'),
  affordHistoryTbody: document.getElementById('affordHistoryTbody'),

  // AI Advisor
  chatMessages: document.getElementById('chatMessages'),
  chatForm: document.getElementById('chatForm'),
  chatInput: document.getElementById('chatInput'),
  geminiApiKeyInput: document.getElementById('geminiApiKeyInput'),
  saveApiKeyBtn: document.getElementById('saveApiKeyBtn'),

  // Transactions
  txTableBody: document.getElementById('txTableBody'),
  txSearchInput: document.getElementById('txSearchInput'),
  txTypeFilter: document.getElementById('txTypeFilter'),
  openAddTxBtn: document.getElementById('openAddTxBtn'),
  addTxFromTabBtn: document.getElementById('addTxFromTabBtn'),

  // Modals
  addTxModal: document.getElementById('addTxModal'),
  closeAddTxModalBtn: document.getElementById('closeAddTxModalBtn'),
  cancelAddTxBtn: document.getElementById('cancelAddTxBtn'),
  manualTxForm: document.getElementById('manualTxForm'),
  nlTxInput: document.getElementById('nlTxInput'),
  parseNlBtn: document.getElementById('parseNlBtn'),
  txDate: document.getElementById('txDate'),
  txAmount: document.getElementById('txAmount'),
  txType: document.getElementById('txType'),
  txCategory: document.getElementById('txCategory'),
  txMerchant: document.getElementById('txMerchant'),
  txNote: document.getElementById('txNote'),
  txPaymentMethod: document.getElementById('txPaymentMethod'),

  // Voice Modal
  voiceInputBtn: document.getElementById('voiceInputBtn'),
  voiceModal: document.getElementById('voiceModal'),
  closeVoiceModalBtn: document.getElementById('closeVoiceModalBtn'),
  voiceStatusText: document.getElementById('voiceStatusText'),
  voiceTranscriptBox: document.getElementById('voiceTranscriptBox'),
  stopVoiceBtn: document.getElementById('stopVoiceBtn'),
  processVoiceBtn: document.getElementById('processVoiceBtn'),

  // Goals & Subs
  goalsListContainer: document.getElementById('goalsListContainer'),
  subListContainer: document.getElementById('subListContainer'),
  annualLeakValue: document.getElementById('annualLeakValue'),
  openNewGoalModalBtn: document.getElementById('openNewGoalModalBtn'),
  openNewSubModalBtn: document.getElementById('openNewSubModalBtn'),
  newGoalModal: document.getElementById('newGoalModal'),
  closeGoalModalBtn: document.getElementById('closeGoalModalBtn'),
  cancelGoalBtn: document.getElementById('cancelGoalBtn'),
  newGoalForm: document.getElementById('newGoalForm'),
  newSubModal: document.getElementById('newSubModal'),
  closeSubModalBtn: document.getElementById('closeSubModalBtn'),
  cancelSubBtn: document.getElementById('cancelSubBtn'),
  newSubForm: document.getElementById('newSubForm'),

  // Toast
  toastContainer: document.getElementById('toastContainer')
};

// ==========================================================================
// Toast Notification Utility
// ==========================================================================
function showToast(message, type = 'success') {
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  
  const icon = type === 'success' ? '✓' : (type === 'error' ? '✕' : 'ℹ');
  toast.innerHTML = `<strong>${icon}</strong> <span>${message}</span>`;
  
  elements.toastContainer.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 3200);
}

// ==========================================================================
// API Helpers
// ==========================================================================
async function apiGet(endpoint) {
  try {
    const res = await fetch(endpoint);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error(`API GET error on ${endpoint}:`, err);
    showToast(`Error connecting to server: ${err.message}`, 'error');
    return null;
  }
}

async function apiPost(endpoint, data) {
  try {
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error(`API POST error on ${endpoint}:`, err);
    showToast(`Action failed: ${err.message}`, 'error');
    return null;
  }
}

async function apiDelete(endpoint) {
  try {
    const res = await fetch(endpoint, { method: 'DELETE' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error(`API DELETE error on ${endpoint}:`, err);
    showToast(`Delete failed: ${err.message}`, 'error');
    return null;
  }
}

// ==========================================================================
// App Initialization & Tab Navigation
// ==========================================================================
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initTabs();
  initModals();
  initVoiceRecognition();
  initChatPromptChips();
  initQuickSampleEvaluations();
  
  // Set default date for transactions
  if (elements.txDate) {
    elements.txDate.value = new Date().toISOString().split('T')[0];
  }
  
  // Load saved API key
  if (state.geminiApiKey && elements.geminiApiKeyInput) {
    elements.geminiApiKeyInput.value = state.geminiApiKey;
  }

  // Load all initial data
  refreshAllData();
});

function initTabs() {
  elements.tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const tabId = btn.getAttribute('data-tab');
      switchTab(tabId);
    });
  });
}

function switchTab(tabId) {
  state.currentTab = tabId;
  elements.tabButtons.forEach(b => {
    b.classList.toggle('active', b.getAttribute('data-tab') === tabId);
  });
  elements.tabPanes.forEach(p => {
    p.classList.toggle('active', p.id === `tab-${tabId}`);
  });

  // Tab specific refreshes
  if (tabId === 'transactions') {
    renderTransactionsTable();
  } else if (tabId === 'affordability') {
    fetchAffordabilityHistory();
  } else if (tabId === 'goals-subs') {
    fetchGoalsAndSubscriptions();
  }
}

function initTheme() {
  const savedTheme = localStorage.getItem('pocketsmart_theme') || 'dark';
  document.documentElement.setAttribute('data-theme', savedTheme);
  updateThemeIcon(savedTheme);

  elements.themeToggleBtn.addEventListener('click', () => {
    const current = document.documentElement.getAttribute('data-theme') || 'dark';
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('pocketsmart_theme', next);
    updateThemeIcon(next);
  });
}

function updateThemeIcon(theme) {
  if (theme === 'light') {
    elements.themeMoonIcon.innerHTML = `
      <circle cx="12" cy="12" r="5"></circle>
      <line x1="12" y1="1" x2="12" y2="3"></line>
      <line x1="12" y1="21" x2="12" y2="23"></line>
      <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
      <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
      <line x1="1" y1="12" x2="3" y2="12"></line>
      <line x1="21" y1="12" x2="23" y2="12"></line>
      <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
      <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
    `;
  } else {
    elements.themeMoonIcon.innerHTML = `<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"></path>`;
  }
}

// ==========================================================================
// Data Fetching & UI Rendering
// ==========================================================================
async function refreshAllData() {
  await Promise.all([
    fetchSummary(),
    fetchTransactions(),
    fetchAffordabilityHistory(),
    fetchGoalsAndSubscriptions()
  ]);
}

async function fetchSummary() {
  const data = await apiGet('/api/summary');
  if (!data) return;
  state.summary = data;

  // 1. Metric Cards
  elements.statIncome.textContent = `$${data.effective_income.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
  elements.statExpenses.textContent = `$${data.total_expenses.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
  elements.statSurplus.textContent = `$${data.net_savings.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
  elements.statSavingsRate.textContent = `${data.savings_rate_pct}%`;
  elements.statBurnRate.textContent = `Daily burn: $${data.daily_burn_rate}/day`;
  elements.statDaysLeft.textContent = `${data.days_remaining} days left in billing cycle`;

  // 2. Health Pill
  elements.headerHealthText.textContent = `Health: ${data.health_score}/100 (${data.health_status})`;
  if (data.health_score < 60) {
    elements.headerHealthPill.style.color = '#f59e0b';
    elements.headerHealthPill.style.borderColor = 'rgba(245, 158, 11, 0.3)';
  } else {
    elements.headerHealthPill.style.color = '#10b981';
    elements.headerHealthPill.style.borderColor = 'rgba(16, 185, 129, 0.3)';
  }

  // 3. 50/30/20 Rule Bars
  const ftt = data.fifty_thirty_twenty;
  
  // Needs
  elements.needsSpentText.textContent = `$${ftt.needs.spent.toLocaleString()}`;
  elements.needsTargetText.textContent = `/ $${ftt.needs.target_amount.toLocaleString()} (${ftt.needs.actual_pct}%)`;
  elements.needsProgressBar.style.width = `${Math.min(100, (ftt.needs.spent / Math.max(1, ftt.needs.target_amount)) * 100)}%`;
  elements.needsStatusMsg.textContent = ftt.needs.actual_pct <= 52 
    ? '✅ Well within 50% target envelope' 
    : `⚠️ Exceeding by ${(ftt.needs.actual_pct - 50).toFixed(1)}% of income`;

  // Wants
  elements.wantsSpentText.textContent = `$${ftt.wants.spent.toLocaleString()}`;
  elements.wantsTargetText.textContent = `/ $${ftt.wants.target_amount.toLocaleString()} (${ftt.wants.actual_pct}%)`;
  elements.wantsProgressBar.style.width = `${Math.min(100, (ftt.wants.spent / Math.max(1, ftt.wants.target_amount)) * 100)}%`;
  elements.wantsStatusMsg.textContent = ftt.wants.actual_pct <= 30
    ? '✅ Lifestyle spending is well disciplined'
    : `⚠️ Discretionary over by ${(ftt.wants.actual_pct - 30).toFixed(1)}%`;

  // Savings
  elements.savingsSpentText.textContent = `$${ftt.savings.spent.toLocaleString()}`;
  elements.savingsTargetText.textContent = `/ $${ftt.savings.target_amount.toLocaleString()} (${ftt.savings.actual_pct}%)`;
  elements.savingsProgressBar.style.width = `${Math.min(100, (ftt.savings.spent / Math.max(1, ftt.savings.target_amount)) * 100)}%`;
  elements.savingsStatusMsg.textContent = ftt.savings.actual_pct >= 18
    ? '✅ Wealth building goal achieved'
    : `💡 Save $${(ftt.savings.target_amount - ftt.savings.spent).toFixed(0)} more to hit 20%`;

  const isAdherent = ftt.needs.actual_pct <= 55 && ftt.wants.actual_pct <= 35;
  elements.ruleAdherenceBadge.textContent = isAdherent ? 'Healthy Distribution' : 'Needs Optimization';
  elements.ruleAdherenceBadge.className = isAdherent ? 'rule-benchmark-badge' : 'rule-benchmark-badge text-amber';

  // 4. Categories Breakdown
  renderCategoryBreakdown(data.category_spending);

  // 5. Velocity Card
  elements.velocityProjectedSpend.textContent = `$${data.projected_monthly_spend.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
  const projectedSurplus = data.effective_income - data.projected_monthly_spend;
  elements.velocityProjectedSurplus.textContent = `$${projectedSurplus.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
  elements.velocityProjectedSurplus.className = projectedSurplus >= 0 ? 'value text-emerald' : 'value text-red';

  // 6. AI Insight Text
  generateInsightText(data);
}

function renderCategoryBreakdown(categories) {
  elements.categoryListContainer.innerHTML = '';
  const entries = Object.entries(categories);

  entries.forEach(([name, c]) => {
    const row = document.createElement('div');
    row.className = 'category-row';

    const pct = Math.min(100, c.percent_used);
    const isOver = c.spent > c.budget && c.budget > 0;
    const progressColor = isOver ? '#f43f5e' : (c.color || '#6366f1');

    row.innerHTML = `
      <div class="cat-info-row">
        <span class="cat-name-tag">
          <span class="cat-dot" style="background: ${c.color}"></span>
          ${name}
        </span>
        <span class="cat-numbers">
          <strong>$${c.spent.toFixed(2)}</strong> / $${c.budget.toFixed(2)}
          <span style="color: ${isOver ? '#f43f5e' : '#94a3b8'}; margin-left: 6px;">(${c.percent_used}%)</span>
        </span>
      </div>
      <div class="cat-progress-track">
        <div class="cat-progress-fill" style="width: ${pct}%; background: ${progressColor}"></div>
      </div>
    `;
    elements.categoryListContainer.appendChild(row);
  });
}

function generateInsightText(summary) {
  const over = Object.entries(summary.category_spending).filter(([_, c]) => c.spent > c.budget && c.budget > 0);
  if (over.length > 0) {
    const catNames = over.map(([name]) => name).join(', ');
    elements.dashboardAiInsightText.innerHTML = `
      ⚠️ <strong>Attention:</strong> You have exceeded monthly caps in <strong>${catNames}</strong>. 
      Your current projected run-rate is <strong>$${summary.daily_burn_rate}/day</strong>. 
      Recommend pausing non-essential discretionary purchases for the next <strong>${summary.days_remaining} days</strong> to preserve your $${summary.net_savings.toFixed(2)} cash reserve.
    `;
  } else {
    elements.dashboardAiInsightText.innerHTML = `
      ✨ <strong>Strong Fiscal Discipline:</strong> All primary budget categories are currently within allocated envelopes. 
      Your net projected surplus is <strong>$${(summary.effective_income - summary.projected_monthly_spend).toFixed(2)}</strong>. 
      Great time to fund your high-yield emergency buffer or invest in long-term goals!
    `;
  }
}

// ==========================================================================
// "CAN I AFFORD THIS?" AI RECOMMENDATION ENGINE
// ==========================================================================
elements.affordabilityForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const payload = {
    item_name: elements.affordItemName.value.trim(),
    price: parseFloat(elements.affordPrice.value),
    category: elements.affordCategory.value,
    urgency: elements.affordUrgency.value,
    installments: parseInt(elements.affordInstallments.value)
  };

  const btn = document.getElementById('runAffordabilityBtn');
  btn.disabled = true;
  btn.innerHTML = `<span>Evaluating with PocketSmart AI...</span>`;

  const result = await apiPost('/api/affordability', payload);
  btn.disabled = false;
  btn.innerHTML = `
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3Z"/></svg>
    <span>Run PocketSmart AI Evaluation</span>
  `;

  if (result) {
    state.lastEvaluatedPurchase = payload;
    renderAffordabilityResult(result);
    fetchAffordabilityHistory();
    showToast(`PocketSmart verdict: ${result.verdict}`, 'info');
  }
});

function renderAffordabilityResult(res) {
  elements.evalPlaceholder.classList.add('hidden');
  elements.evalContent.classList.remove('hidden');

  // Verdict Pill
  elements.evalVerdictPill.textContent = res.verdict;
  elements.evalVerdictPill.className = `verdict-pill verdict-${res.verdict_badge}`;
  elements.evalScoreValue.textContent = `${res.score} / 100`;
  elements.evalHeadline.textContent = res.summary_sentence;

  // Gauge
  elements.evalGaugeFill.style.width = `${res.score}%`;

  // Reasons list
  elements.evalReasonsList.innerHTML = res.reasons.map(r => `<li>${r}</li>`).join('');

  // Recommendations & Alternatives
  const allTips = [...res.recommendations, ...res.alternatives];
  elements.evalRecsList.innerHTML = allTips.map(t => `<li>${t}</li>`).join('');

  // Button actions
  elements.logApprovedPurchaseBtn.onclick = () => {
    openLogModalWithPrefill({
      amount: res.monthly_cost,
      category: res.category,
      merchant: res.item_name,
      note: `Evaluated purchase (${res.verdict})`
    });
  };

  elements.createGoalFromEvalBtn.onclick = () => {
    openGoalModalWithPrefill(res.item_name, res.price);
  };
}

async function fetchAffordabilityHistory() {
  const data = await apiGet('/api/affordability/history');
  if (!data || !data.history) return;
  state.affordabilityHistory = data.history;

  if (data.history.length === 0) {
    elements.affordHistoryTbody.innerHTML = `<tr><td colspan="6" class="text-center py-4 text-muted">No evaluations yet. Test a purchase above!</td></tr>`;
    return;
  }

  elements.affordHistoryTbody.innerHTML = data.history.map(h => {
    const badgeClass = h.verdict.toLowerCase().includes('safe') ? 'verdict-safe' : 
                      (h.verdict.toLowerCase().includes('caution') ? 'verdict-caution' : 'verdict-danger');
    return `
      <tr>
        <td><strong>${escapeHtml(h.item_name)}</strong></td>
        <td>$${parseFloat(h.price).toFixed(2)}</td>
        <td><span class="badge-tag" style="background: rgba(99, 102, 241, 0.15); color: #818cf8;">${escapeHtml(h.category)}</span></td>
        <td><span class="verdict-pill ${badgeClass}" style="font-size: 0.7rem; padding: 0.15rem 0.6rem;">${escapeHtml(h.verdict)}</span></td>
        <td><strong>${h.affordability_score}/100</strong></td>
        <td><small class="text-muted">${h.created_at.split(' ')[0]}</small></td>
      </tr>
    `;
  }).join('');
}

function initQuickSampleEvaluations() {
  document.querySelectorAll('.btn-sample-eval').forEach(btn => {
    btn.addEventListener('click', () => {
      elements.affordItemName.value = btn.getAttribute('data-item');
      elements.affordPrice.value = btn.getAttribute('data-price');
      elements.affordCategory.value = btn.getAttribute('data-cat');
      elements.affordUrgency.value = 'nice_to_have';
      elements.affordabilityForm.dispatchEvent(new Event('submit'));
    });
  });
}

// ==========================================================================
// TRANSACTIONS LEDGER
// ==========================================================================
async function fetchTransactions() {
  const data = await apiGet('/api/transactions');
  if (!data || !data.transactions) return;
  state.transactions = data.transactions;
  renderTransactionsTable();
}

function renderTransactionsTable() {
  const search = elements.txSearchInput.value.toLowerCase().trim();
  const typeFilter = elements.txTypeFilter.value;

  const filtered = state.transactions.filter(t => {
    const matchesSearch = !search || 
      (t.merchant && t.merchant.toLowerCase().includes(search)) || 
      (t.note && t.note.toLowerCase().includes(search)) ||
      (t.category && t.category.toLowerCase().includes(search));
    const matchesType = typeFilter === 'all' || t.type === typeFilter;
    return matchesSearch && matchesType;
  });

  if (filtered.length === 0) {
    elements.txTableBody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-muted">No transactions found matching your criteria.</td></tr>`;
    return;
  }

  elements.txTableBody.innerHTML = filtered.map(t => {
    const isIncome = t.type === 'income';
    const amountClass = isIncome ? 'amount-income' : 'amount-expense';
    const prefix = isIncome ? '+' : '-';
    
    return `
      <tr>
        <td>${t.date}</td>
        <td><strong>${escapeHtml(t.merchant || 'General')}</strong><br><small class="text-muted">${escapeHtml(t.note || '')}</small></td>
        <td><span class="badge-tag" style="background: rgba(99, 102, 241, 0.12); color: #818cf8;">${escapeHtml(t.category)}</span></td>
        <td><small class="text-muted">${escapeHtml(t.payment_method || 'Card')}</small></td>
        <td><span class="badge-tag" style="background: ${isIncome ? 'rgba(16, 185, 129, 0.15)' : 'rgba(255, 255, 255, 0.08)'}; color: ${isIncome ? '#10b981' : '#94a3b8'}">${t.type.toUpperCase()}</span></td>
        <td class="tx-amount ${amountClass}">${prefix}$${parseFloat(t.amount).toFixed(2)}</td>
        <td>
          <button class="btn-del-tx" onclick="deleteTransaction(${t.id})" title="Delete transaction">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>
          </button>
        </td>
      </tr>
    `;
  }).join('');
}

elements.txSearchInput.addEventListener('input', renderTransactionsTable);
elements.txTypeFilter.addEventListener('change', renderTransactionsTable);

async function deleteTransaction(id) {
  if (!confirm('Are you sure you want to remove this transaction?')) return;
  const res = await apiDelete(`/api/transactions/${id}`);
  if (res && res.success) {
    showToast('Transaction removed');
    refreshAllData();
  }
}

// ==========================================================================
// MODALS & NATURAL LANGUAGE LOGGING
// ==========================================================================
function initModals() {
  const openModal = (m) => m.showModal();
  const closeModal = (m) => m.close();

  // Add Transaction Modal
  elements.openAddTxBtn.addEventListener('click', () => openModal(elements.addTxModal));
  elements.addTxFromTabBtn.addEventListener('click', () => openModal(elements.addTxModal));
  elements.closeAddTxModalBtn.addEventListener('click', () => closeModal(elements.addTxModal));
  elements.cancelAddTxBtn.addEventListener('click', () => closeModal(elements.addTxModal));

  // Natural Language Parser
  elements.parseNlBtn.addEventListener('click', async () => {
    const text = elements.nlTxInput.value.trim();
    if (!text) return;
    
    elements.parseNlBtn.disabled = true;
    elements.parseNlBtn.textContent = 'Parsing...';
    
    const parsed = await apiPost('/api/parse-nl', { text });
    elements.parseNlBtn.disabled = false;
    elements.parseNlBtn.textContent = 'Parse';

    if (parsed) {
      if (parsed.amount > 0) elements.txAmount.value = parsed.amount;
      if (parsed.type) elements.txType.value = parsed.type;
      if (parsed.category) elements.txCategory.value = parsed.category;
      if (parsed.merchant) elements.txMerchant.value = parsed.merchant;
      if (parsed.date) elements.txDate.value = parsed.date;
      if (parsed.note) elements.txNote.value = parsed.note;
      showToast('Extracted transaction details!', 'info');
    }
  });

  // Manual Form Submission
  elements.manualTxForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
      type: elements.txType.value,
      amount: parseFloat(elements.txAmount.value),
      category: elements.txCategory.value,
      merchant: elements.txMerchant.value.trim(),
      date: elements.txDate.value,
      payment_method: elements.txPaymentMethod.value,
      note: elements.txNote.value.trim()
    };

    const res = await apiPost('/api/transactions', payload);
    if (res && res.success) {
      closeModal(elements.addTxModal);
      elements.manualTxForm.reset();
      elements.nlTxInput.value = '';
      elements.txDate.value = new Date().toISOString().split('T')[0];
      showToast('Transaction recorded successfully!');
      refreshAllData();
    }
  });

  // Goals Modal
  elements.openNewGoalModalBtn.addEventListener('click', () => openModal(elements.newGoalModal));
  elements.closeGoalModalBtn.addEventListener('click', () => closeModal(elements.newGoalModal));
  elements.cancelGoalBtn.addEventListener('click', () => closeModal(elements.newGoalModal));
  
  elements.newGoalForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
      name: document.getElementById('goalName').value.trim(),
      target_amount: parseFloat(document.getElementById('goalTarget').value),
      current_amount: parseFloat(document.getElementById('goalCurrent').value || 0),
      target_date: document.getElementById('goalDate').value
    };
    const res = await apiPost('/api/savings-goals', payload);
    if (res && res.success) {
      closeModal(elements.newGoalModal);
      elements.newGoalForm.reset();
      showToast('New savings goal created!');
      fetchGoalsAndSubscriptions();
    }
  });

  // Subscriptions Modal
  elements.openNewSubModalBtn.addEventListener('click', () => openModal(elements.newSubModal));
  elements.closeSubModalBtn.addEventListener('click', () => closeModal(elements.newSubModal));
  elements.cancelSubBtn.addEventListener('click', () => closeModal(elements.newSubModal));
  
  elements.newSubForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
      name: document.getElementById('subName').value.trim(),
      cost: parseFloat(document.getElementById('subCost').value),
      billing_cycle: document.getElementById('subCycle').value,
      category: document.getElementById('subCategory').value
    };
    const res = await apiPost('/api/subscriptions', payload);
    if (res && res.success) {
      closeModal(elements.newSubModal);
      elements.newSubForm.reset();
      showToast('Subscription tracked!');
      fetchGoalsAndSubscriptions();
    }
  });

  // Reset Demo Data
  elements.resetDemoBtn.addEventListener('click', async () => {
    if (!confirm('Reset all categories, budgets, and transactions back to the default sample dataset?')) return;
    const res = await apiPost('/api/reset-data', {});
    if (res && res.success) {
      showToast('Demo data restored successfully!');
      refreshAllData();
    }
  });
}

function openLogModalWithPrefill(data) {
  elements.addTxModal.showModal();
  if (data.amount) elements.txAmount.value = data.amount;
  if (data.category) elements.txCategory.value = data.category;
  if (data.merchant) elements.txMerchant.value = data.merchant;
  if (data.note) elements.txNote.value = data.note;
}

function openGoalModalWithPrefill(name, target) {
  elements.newGoalModal.showModal();
  document.getElementById('goalName').value = name;
  document.getElementById('goalTarget').value = target;
  document.getElementById('goalCurrent').value = 0;
}

// ==========================================================================
// VOICE INPUT WITH WEB SPEECH API
// ==========================================================================
function initVoiceRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  elements.voiceInputBtn.addEventListener('click', () => {
    if (!SpeechRecognition) {
      showToast('Voice Recognition is not supported in this browser. Please use text input.', 'error');
      return;
    }

    elements.voiceModal.showModal();
    startListening();
  });

  elements.closeVoiceModalBtn.addEventListener('click', () => {
    stopListening();
    elements.voiceModal.close();
  });

  elements.stopVoiceBtn.addEventListener('click', () => {
    stopListening();
  });

  elements.processVoiceBtn.addEventListener('click', async () => {
    const text = elements.voiceTranscriptBox.textContent.replace(/"/g, '').trim();
    if (!text || text === 'Listening... Speak now') {
      showToast('No speech detected. Please speak into the mic.', 'error');
      return;
    }
    stopListening();
    elements.voiceModal.close();

    // Directly parse and open log modal
    const parsed = await apiPost('/api/parse-nl', { text });
    if (parsed) {
      openLogModalWithPrefill(parsed);
      showToast('Speech parsed! Review & confirm transaction.', 'info');
    }
  });

  function startListening() {
    state.recognition = new SpeechRecognition();
    state.recognition.continuous = true;
    state.recognition.interimResults = true;
    state.recognition.lang = 'en-US';

    elements.voiceStatusText.textContent = 'Listening... Speak now';
    elements.voiceTranscriptBox.textContent = 'Listening for speech...';

    state.recognition.onresult = (event) => {
      let finalTranscript = '';
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript;
        } else {
          finalTranscript += event.results[i][0].transcript;
        }
      }
      elements.voiceTranscriptBox.textContent = `"${finalTranscript}"`;
    };

    state.recognition.onerror = (event) => {
      console.warn('Speech recognition error:', event.error);
      elements.voiceStatusText.textContent = `Error: ${event.error}`;
    };

    state.recognition.start();
  }

  function stopListening() {
    if (state.recognition) {
      state.recognition.stop();
      elements.voiceStatusText.textContent = 'Ready to process';
    }
  }
}

// ==========================================================================
// GOALS & SUBSCRIPTIONS
// ==========================================================================
async function fetchGoalsAndSubscriptions() {
  const [goalsData, subsData] = await Promise.all([
    apiGet('/api/savings-goals'),
    apiGet('/api/subscriptions')
  ]);

  // Render Goals
  if (goalsData && goalsData.goals) {
    state.goals = goalsData.goals;
    if (state.goals.length === 0) {
      elements.goalsListContainer.innerHTML = `<div class="text-center py-4 text-muted">No savings goals created yet.</div>`;
    } else {
      elements.goalsListContainer.innerHTML = state.goals.map(g => {
        const pct = Math.min(100, Math.round((g.current_amount / Math.max(1, g.target_amount)) * 100));
        return `
          <div class="goal-card">
            <div class="goal-card-top">
              <div class="goal-name-wrap">
                <span class="goal-icon-badge">🎯</span>
                <div>
                  ${escapeHtml(g.name)}
                  ${g.target_date ? `<br><small class="text-muted">Target: ${g.target_date}</small>` : ''}
                </div>
              </div>
              <div class="goal-stats">
                $${g.current_amount.toFixed(0)} / $${g.target_amount.toFixed(0)} (${pct}%)
              </div>
            </div>
            <div class="progress-track">
              <div class="progress-fill fill-savings" style="width: ${pct}%"></div>
            </div>
            <div class="goal-actions">
              <button class="btn btn-secondary btn-sm" onclick="contributeToGoal(${g.id}, 50)">+$50</button>
              <button class="btn btn-secondary btn-sm" onclick="contributeToGoal(${g.id}, 100)">+$100</button>
              <button class="btn btn-ghost btn-sm" onclick="contributeToGoal(${g.id}, -50)">-$50</button>
            </div>
          </div>
        `;
      }).join('');
    }
  }

  // Render Subscriptions
  if (subsData && subsData.subscriptions) {
    state.subscriptions = subsData.subscriptions;
    elements.annualLeakValue.textContent = `$${subsData.annual_leakage.toLocaleString('en-US', { minimumFractionDigits: 2 })} / year`;

    if (state.subscriptions.length === 0) {
      elements.subListContainer.innerHTML = `<div class="text-center py-4 text-muted">No recurring subscriptions added.</div>`;
    } else {
      elements.subListContainer.innerHTML = state.subscriptions.map(s => {
        const costStr = s.billing_cycle === 'monthly' ? `$${s.cost.toFixed(2)}/mo` : `$${s.cost.toFixed(2)}/yr`;
        const isReview = s.status === 'review';
        return `
          <div class="sub-card" style="${isReview ? 'border-color: rgba(245, 158, 11, 0.4);' : ''}">
            <div class="sub-card-top">
              <div class="sub-name-wrap">
                <span>${isReview ? '⚠️' : '💳'}</span>
                <div>
                  ${escapeHtml(s.name)}
                  <br><small class="text-muted">${escapeHtml(s.category)} ${isReview ? '• Flagged as Unused' : ''}</small>
                </div>
              </div>
              <div class="tx-amount text-red">${costStr}</div>
            </div>
            <div class="goal-actions" style="justify-content: flex-end;">
              <button class="btn btn-ghost btn-sm text-red" onclick="deleteSubscription(${s.id})">Cancel Sub</button>
            </div>
          </div>
        `;
      }).join('');
    }
  }
}

async function contributeToGoal(goalId, amount) {
  const res = await apiPost(`/api/savings-goals/${goalId}/contribute`, { amount });
  if (res && res.success) {
    showToast(`Updated savings goal by ${amount >= 0 ? '+' : ''}$${amount}!`);
    fetchGoalsAndSubscriptions();
  }
}

async function deleteSubscription(subId) {
  if (!confirm('Remove this subscription tracking?')) return;
  const res = await apiDelete(`/api/subscriptions/${subId}`);
  if (res && res.success) {
    showToast('Subscription removed');
    fetchGoalsAndSubscriptions();
  }
}

// ==========================================================================
// AI ADVISOR CHAT
// ==========================================================================
function initChatPromptChips() {
  document.querySelectorAll('.chip, .prompt-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const q = chip.getAttribute('data-chat') || chip.getAttribute('data-query');
      if (q) {
        switchTab('advisor');
        elements.chatInput.value = q;
        elements.chatForm.dispatchEvent(new Event('submit'));
      }
    });
  });

  elements.saveApiKeyBtn.addEventListener('click', () => {
    const key = elements.geminiApiKeyInput.value.trim();
    state.geminiApiKey = key;
    localStorage.setItem('pocketsmart_gemini_key', key);
    showToast(key ? 'Gemini API Key saved for enhanced responses!' : 'Cleared API Key, using Built-in Engine', 'info');
  });
}

elements.chatForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const message = elements.chatInput.value.trim();
  if (!message) return;

  // Add User Message to Chat
  appendChatMessage(message, 'user');
  elements.chatInput.value = '';

  // Add Loading Indicator
  const loadingId = appendChatLoading();

  const response = await apiPost('/api/chat', {
    message,
    api_key: state.geminiApiKey
  });

  removeChatLoading(loadingId);

  if (response && response.reply) {
    appendChatMessage(response.reply, 'ai', response.engine);
  } else {
    appendChatMessage("I am having trouble analyzing your request right now. Please try again.", 'ai');
  }
});

function appendChatMessage(text, sender, engine = null) {
  const msg = document.createElement('div');
  msg.className = `chat-msg ${sender}-msg`;

  const bubble = document.createElement('div');
  bubble.className = 'msg-bubble';

  if (sender === 'ai') {
    // Render simple markdown headers, bold, bullets
    let formatted = text
      .replace(/### (.*?)\n/g, '<h4 style="margin: 0.4rem 0; font-size: 0.95rem; font-weight: 700;">$1</h4>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\* (.*?)\n/g, '<li style="margin-left: 1.2rem;">$1</li>')
      .replace(/\n\n/g, '<br><br>');
      
    bubble.innerHTML = formatted;
    if (engine) {
      const engineTag = document.createElement('div');
      engineTag.style.cssText = 'font-size: 0.65rem; color: #94a3b8; margin-top: 0.5rem; text-align: right;';
      engineTag.textContent = `Generated via ${engine}`;
      bubble.appendChild(engineTag);
    }
  } else {
    bubble.textContent = text;
  }

  msg.appendChild(bubble);
  elements.chatMessages.appendChild(msg);
  elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
}

function appendChatLoading() {
  const id = `loading-${Date.now()}`;
  const msg = document.createElement('div');
  msg.className = 'chat-msg ai-msg';
  msg.id = id;
  msg.innerHTML = `
    <div class="msg-bubble" style="color: var(--text-muted); font-style: italic;">
      ✨ PocketSmart AI is computing financial scenarios...
    </div>
  `;
  elements.chatMessages.appendChild(msg);
  elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
  return id;
}

function removeChatLoading(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
