// Novice AI Playground — Bugatti-styled SPA
(function () {
  'use strict';

  const API = '/api';

  // State
  let userName = '';
  let history = JSON.parse(localStorage.getItem('nai_history') || '[]');

  // DOM helpers
  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => document.querySelectorAll(sel);

  function showScreen(id) {
    $$('.screen').forEach((s) => s.classList.remove('active'));
    $('#screen-' + id).classList.add('active');
  }

  function setLoading(on) {
    $('#loading').classList.toggle('hidden', !on);
  }

  function persistHistory() {
    localStorage.setItem('nai_history', JSON.stringify(history));
  }

  // API calls
  async function callGemini(prompt, mode) {
    const res = await fetch(API, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt, mode }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ error: 'Server error' }));
      throw new Error(err.error || `HTTP ${res.status}`);
    }
    return res.json();
  }

  // Landing
  $('#name-form').addEventListener('submit', (e) => {
    e.preventDefault();
    userName = $('#name-input').value.trim();
    if (!userName) return;
    $('#user-name').textContent = userName.toUpperCase();
    showScreen('main');
  });

  // Menu navigation
  $$('.menu-card').forEach((card) => {
    card.addEventListener('click', () => {
      const target = card.dataset.target;
      if (target === 'history') {
        renderHistory();
        showScreen('history');
      } else if (target === 'clear') {
        if (confirm('Delete all saved history?')) {
          history = [];
          persistHistory();
          alert('History cleared.');
        }
      } else {
        showScreen(target);
      }
    });
  });

  // Back buttons
  $$('.back-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      const back = btn.dataset.back;
      if (back === 'main') showScreen('main');
    });
  });

  // Text generation
  $('#text-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const prompt = $('#text-input').value.trim();
    if (!prompt) return;
    setLoading(true);
    try {
      const data = await callGemini(prompt, 'text');
      $('#text-output').textContent = data.text || '(no response)';
      $('#text-result').classList.remove('hidden');
      // Save to history
      history.unshift({
        type: 'text',
        prompt,
        response: data.text,
        model: data.model,
        ts: new Date().toISOString(),
      });
      persistHistory();
    } catch (err) {
      alert('Error: ' + err.message);
    } finally {
      setLoading(false);
    }
  });

  // Image generation
  $('#image-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const prompt = $('#image-input').value.trim();
    if (!prompt) return;
    setLoading(true);
    try {
      const data = await callGemini(prompt, 'image');
      const img = $('#image-output');
      if (data.image) {
        img.src = `data:${data.mime || 'image/png'};base64,${data.image}`;
        img.alt = prompt;
      } else {
        img.removeAttribute('src');
        img.alt = 'No image returned';
      }
      $('#image-result').classList.remove('hidden');
      // Save to history
      history.unshift({
        type: 'image',
        prompt,
        response: data.image ? `[image]${data.mime || 'image/png'}` : '(no image)',
        imageB64: data.image || null,
        mime: data.mime || null,
        ts: new Date().toISOString(),
      });
      persistHistory();
    } catch (err) {
      alert('Error: ' + err.message);
    } finally {
      setLoading(false);
    }
  });

  // History render
  function renderHistory() {
    const list = $('#history-list');
    if (!history.length) {
      list.innerHTML = '<p class="body-md" style="text-align:center;color:var(--color-muted)">No history yet.</p>';
      return;
    }
    list.innerHTML = history
      .map((item) => {
        const date = new Date(item.ts).toLocaleString();
        const resp =
          item.type === 'image' && item.imageB64
            ? `<img src="data:${item.mime};base64,${item.imageB64}" alt="${escapeHtml(item.prompt)}">`
            : `<div class="history-response">${escapeHtml(item.response || '')}</div>`;
        return `
          <div class="history-item">
            <div class="history-type">${item.type.toUpperCase()} &middot; ${date} ${item.model ? '&middot; ' + item.model : ''}</div>
            <div class="history-prompt">${escapeHtml(item.prompt)}</div>
            ${resp}
          </div>
        `;
      })
      .join('');
  }

  function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  // Restart
  $('#restart-btn').addEventListener('click', () => {
    userName = '';
    $('#name-input').value = '';
    $('#text-input').value = '';
    $('#image-input').value = '';
    $('#text-output').textContent = '';
    $('#text-result').classList.add('hidden');
    $('#image-result').classList.add('hidden');
    showScreen('landing');
  });

  // Init
  showScreen('landing');
})();
