// Replace Part JS (supports multiple parts)

const RP_PARTS = ['monitor','motherboard','ram','storage','gpu','psu','casing','mouse','keyboard','other_parts'];
window.selectedParts = window.selectedParts || {};
function getRowForPcid(pcid) {
  const checkbox = document.querySelector(`#pcTableBody input.pc-checkbox[value="${pcid}"]`);
  return checkbox ? checkbox.closest('tr') : null;
}

function getAttrFromRow(row, part) {
  if (!row) return '';
  const attr = 'data-' + part.replace(/_/g, '-');
  return row.getAttribute(attr) || '';
}

function setAttrOnRow(row, part, value) {
  if (!row) return;
  const attr = 'data-' + part.replace(/_/g, '-');
  row.setAttribute(attr, value || '');
}
    function debounce(fn, wait) {
    let t = null;
    return function(...args) {
      if (t) clearTimeout(t);
      t = setTimeout(() => fn.apply(this, args), wait);
    };
  }
function openReplacePartModal(pcid, triggerEl) {
  window.selectedParts = {};
  const modal = document.getElementById('replacePartModal');
  const content = document.getElementById('replacePartModalContent');
  const replacePcId = document.getElementById('replacePcId');
  const replacePcIdWrapper = document.getElementById('replacePcIdWrapper');
  const replacePcIdInput = document.getElementById('replacePcIdInput');

  // Show input for PC ID when no pcid provided (toolbar invocation)
  if (pcid) {
    replacePcId.value = pcid;
    if (replacePcIdWrapper) replacePcIdWrapper.classList.add('hidden');
    if (replacePcIdInput) replacePcIdInput.value = '';
  } else {
    replacePcId.value = '';
    if (replacePcIdWrapper) replacePcIdWrapper.classList.remove('hidden');
    if (replacePcIdInput) replacePcIdInput.value = '';
  }

  let row = triggerEl ? triggerEl.closest('tr') : (pcid ? getRowForPcid(pcid) : null);

  // populate current values and clear new-value inputs
  RP_PARTS.forEach(part => {
    const neu = document.getElementById(`new-${part}`);
    const val = getAttrFromRow(row, part) || '';
    if (neu) {
      neu.value = '';
      neu.placeholder = val;
    }
  });

  // --- Autocomplete / suggestions for part inputs ---
RP_PARTS.forEach(part => {
  const input = document.getElementById(`new-${part}`);
  const container = document.getElementById(`sug-${part}`);
  if (!input || !container) return;

  const fetchAndShow = debounce(async () => {
    const q = input.value.trim();

    const results = await getSuggestions(part, q);

    console.log(`🔎 ${part} q="${q}"`);
    console.log(`📦 results:`, results);

    renderSuggestions(container, results, input, part);

    console.log(`✅ rendered: ${part}`);
  }, 220);

  if (!input.dataset.bound) {

    // 🔥 CRITICAL FIX: ADD MISSING EVENTS
    input.addEventListener('input', fetchAndShow);

    input.addEventListener('focus', () => {
      fetchAndShow(); // always show on focus
    });

    input.addEventListener('keydown', (ev) => {
      if (ev.key === 'Escape') {
        container.style.display = 'none';
        input.blur();
      }
    });

    input.dataset.bound = '1';
  }
});

async function getSuggestions(part, q) {
  try {
    const url = `/part-suggestions?part=${encodeURIComponent(part)}&q=${encodeURIComponent(q || '')}`;
    const res = await fetch(url);
    const data = await res.json();

    console.log("🌐 API RESPONSE:", data); // 🔥 ADD THIS

    if (res.ok && data && data.success) return data.results || [];
  } catch (e) {
    console.error('Suggestion fetch error:', e);
  }
  return [];
}

  function renderSuggestions(container, results, inputEl, part) {
      container.innerHTML = '';
      if (!results || results.length === 0) {
        container.style.display = 'none';
        container.setAttribute('aria-hidden', 'true');
        return;
      }
      results.forEach(r => {
        const d = document.createElement('div');
        d.className = 'rp-suggestion';
        d.tabIndex = 0;

        const labelSpan = document.createElement('span');
        labelSpan.className = 'rp-suggestion-label';
        labelSpan.textContent = r.label || (r.accession_id || '');

        const idSpan = document.createElement('small');
        idSpan.className = 'rp-suggestion-id';
        idSpan.textContent = r.accession_id ? `#${r.accession_id}` : '';

        d.appendChild(labelSpan);
        if (idSpan.textContent) d.appendChild(idSpan);

        d.dataset.value = r.label || (r.accession_id || '');
        d.dataset.acc = r.accession_id || '';
        d.addEventListener('click', () => {
          inputEl.value = d.dataset.value;

          // ✅ STORE accession_id
          const acc = Number(d.dataset.acc || 0);

          window.selectedParts[part] = {
            accession_id: acc,
            label: d.dataset.value
          };

          inputEl.value = d.dataset.value;
          inputEl.dataset.acc = acc;
          container.style.display = 'none';
          container.setAttribute('aria-hidden', 'true');
        });
        d.addEventListener('keydown', (ev) => {
          if (ev.key === 'Enter') {
            ev.preventDefault();
            d.click();
          }
        });
        container.appendChild(d);
      });
      container.style.display = 'block';
      container.setAttribute('aria-hidden', 'false');
  }

 

if (!window._rpGlobalClickBound) {
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.rp-field') && !e.target.classList.contains('rp-suggestion')) {
      document.querySelectorAll('.rp-suggestions').forEach(c => {
        c.style.display = 'none';
        c.setAttribute('aria-hidden', 'true');
      });
    }
  });
  window._rpGlobalClickBound = true;
}

  function tryUpdateFromInputId() {
    if (!replacePcIdInput) return;
    const idVal = replacePcIdInput.value.trim();
    if (!idVal) return;
    const r = getRowForPcid(idVal);
    if (!r) return;
    RP_PARTS.forEach(part => {
      const neu = document.getElementById(`new-${part}`);
      if (neu) neu.placeholder = getAttrFromRow(r, part) || '';
    });
  }

  if (replacePcIdInput) replacePcIdInput.oninput = tryUpdateFromInputId;

  modal.classList.remove('hidden');
  document.body.classList.add('modal-open-pc');
  setTimeout(() => content.classList.add('scale-100'), 50);
  if (window.lucide && typeof window.lucide.createIcons === 'function') window.lucide.createIcons();
}

function closeReplacePartModal() {
  const modal = document.getElementById('replacePartModal');
  const content = document.getElementById('replacePartModalContent');
  if (content) content.classList.remove('scale-100');
  if (modal) {
    modal.classList.add('hidden');
    document.body.classList.remove('modal-open-pc');
  }
}

document.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById('replacePartForm');
  if (!form) return;

form.addEventListener('submit', async function(e) {
  e.preventDefault();

  let pcid = (document.getElementById('replacePcId') || {}).value || '';
  const replacePcIdInput = document.getElementById('replacePcIdInput');
  if (!pcid && replacePcIdInput) pcid = replacePcIdInput.value.trim();

  if (!pcid) {
    if (typeof showPopup === 'function') showPopup('error', 'Please provide a PC ID.');
    return;
  }

  const replacements = {};
  RP_PARTS.forEach(part => {
    const input = document.getElementById(`new-${part}`);
    if (!input) return;

    const accessionId = Number(input.dataset.acc || 0);
    const label = (input.value || '').trim();
    const selected = window.selectedParts && window.selectedParts[part];

    if (accessionId && label && selected && selected.accession_id === accessionId && selected.label === label) {
      replacements[part] = selected;
    }
  });





  // ✅ DEBUG HERE (CORRECT PLACE)
  console.log("FINAL REPLACEMENTS:", replacements);

  if (Object.keys(replacements).length === 0) {
    if (typeof showPopup === 'function') showPopup('error', 'Select a part from suggestions.');
    return;
  }

  try {
    const res = await fetch('/replace-pc-part', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pcid: pcid, replacements: replacements })
    });

    const data = await res.json();

    if (res.ok && data.success) {
      if (typeof showPopup === 'function') showPopup('success', data.message);

      const row = getRowForPcid(pcid);

      Object.keys(replacements).forEach(part => {
        const val = replacements[part].label; // display label only
        setAttrOnRow(row, part, val);
      });

      closeReplacePartModal();

      if (typeof window.refreshPcTableWithoutReload === 'function') window.refreshPcTableWithoutReload();
      if (typeof window.refreshItemTableWithoutReload === 'function') window.refreshItemTableWithoutReload();

    } else {
      if (typeof showPopup === 'function') showPopup('error', data.error);
    }

  } catch (err) {
    console.error('Replace part error:', err);
    if (typeof showPopup === 'function') showPopup('error', 'Something went wrong.');
  }
});
});
