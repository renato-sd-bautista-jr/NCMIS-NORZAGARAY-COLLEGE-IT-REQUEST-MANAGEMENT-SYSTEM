 
// ---------- CONSUMABLE HELPERS ----------
const CONSUMABLE_MODAL_ANIMATION_MS = 220;

function notifyUser(message, type = 'info') {
  if (typeof showToast === 'function') {
    showToast(message, type);
    return;
  }
  console.warn(message);
}

async function toggleSelectAllConsumables() {
  const master = document.getElementById("selectAllConsumables");
  document.querySelectorAll(".consumable-checkbox")
    .forEach(cb => cb.checked = master.checked);
}

window.openConsumableModalById = async function (id) {
  try {
    const res = await fetch(`/get-consumable-by-id/${id}`);
    if (!res.ok) throw new Error();

    const data = await res.json();
    openConsumableModal(data);

  } catch (err) {
    console.error(err);
    notifyUser("Failed to load consumable.");
  }
};

// Helper: read item name from element's data attribute, then call archiveConsumable
window.archiveConsumableFromEl = function (el, id) {
  try {
    const name = el && el.getAttribute ? el.getAttribute('data-item-name') : '';
    window.archiveConsumable(id, name);
  } catch (e) {
    // fallback: call without name
    window.archiveConsumable(id, '');
  }
};

async function openConsumableModal(data = null) {
  const modal = document.getElementById('consumableModal');
  const form = document.getElementById('consumableForm');
  const title = document.getElementById('consumableModalTitle');
  const deptSelect = document.getElementById('department_id');

  if (!modal || !form || !title || !deptSelect) {
    console.error("Consumable modal elements not found in DOM.");
    return;
  }

  form.reset();

  // Mode
  if (data) {
    title.textContent = "Edit Consumable";
    form.action = "/update-consumable";
  } else {
    title.textContent = "Add Consumable";
    form.action = "/add-consumable";
  }

  // ✅ LOAD departments FIRST
  try {
    const res = await fetch('/get-departments');
    const departments = await res.json();

    deptSelect.innerHTML = '<option value="">Select Department</option>';

    departments.forEach(dep => {
      const option = document.createElement("option");
      option.value = dep.department_id;
      option.textContent = dep.department_name;
      deptSelect.appendChild(option);
    });

  } catch (err) {
    console.error("Failed loading departments", err);
  }

  // ✅ THEN populate data
  if (data) {
    console.log("Editing:", data);

    document.getElementById('accession_id').value = data.accession_id || '';
    document.getElementById('item_name').value = data.item_name || '';
    document.getElementById('category').value = data.category || '';
    document.getElementById('brand').value = data.brand || '';
    document.getElementById('quantity').value = data.quantity || '';
    document.getElementById('unit').value = data.unit || '';
    document.getElementById('location').value = data.location || '';
    document.getElementById('status').value = data.status || 'Available';
    document.getElementById('description').value = data.description || '';
    document.getElementById('date_added').value = data.date_added || '';

    // ✅ VERY IMPORTANT: set AFTER options exist
    if (data.department_id) {
      deptSelect.value = String(data.department_id);
    }
  } else {
    // Set current date for new items
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('date_added').value = today;
  }

  if (modal._hideTimer) {
    window.clearTimeout(modal._hideTimer);
    modal._hideTimer = null;
  }

  modal.classList.remove('hidden');
  window.requestAnimationFrame(() => {
    modal.classList.add('modal-open');
  });
}

// Archive (delete) consumable with confirmation and AJAX
window.archiveConsumable = function (id, itemName) {
  if (typeof showConfirmationModal === 'function') {
    showConfirmationModal(
      'Archive Consumable',
      'Are you sure you want to archive "' + itemName + '"? This action cannot be undone.',
      'Archive',
      function () {
        const toastId = typeof showToast === 'function' ? showToast('Archiving consumable...', 'loading') : null;
        fetch(`/archive-consumable/${id}`, {
          method: 'POST',
          headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
          .then(async (res) => {
            const isJson = res.headers.get && res.headers.get('content-type') && res.headers.get('content-type').includes('application/json');
            const data = isJson ? await res.json() : null;

            if (!res.ok) {
              const msg = (data && (data.error || data.message)) || `Delete failed (${res.status})`;
              // If server says it cannot delete due to transaction history, offer to set to Inactive
              if (res.status === 400 && /transaction history|inactive status/i.test(msg)) {
                if (typeof showConfirmationModal === 'function') {
                  showConfirmationModal(
                    'Set Inactive Instead?',
                    msg + '\n\nWould you like to set this consumable to Inactive instead?',
                    'Set Inactive',
                    function () {
                      const body = new URLSearchParams();
                      body.set('accession_id', id);
                      body.set('status', 'Inactive');

                      const updatingToast = typeof showToast === 'function' ? showToast('Setting status to Inactive...', 'loading') : null;
                      fetch('/update-consumable', {
                        method: 'POST',
                        headers: {
                          'X-Requested-With': 'XMLHttpRequest',
                          'Content-Type': 'application/x-www-form-urlencoded'
                        },
                        body: body.toString()
                      })
                        .then(r => r.json())
                        .then(resData => {
                          if (updatingToast && typeof hideToast === 'function') hideToast(updatingToast);
                          if (resData && resData.success) {
                            if (typeof showToast === 'function') showToast('Consumable set to Inactive', 'success');
                            refreshConsumableTableWithoutReload();
                          } else {
                            if (typeof showToast === 'function') showToast(resData && (resData.error || resData.message) || 'Failed to set Inactive', 'error');
                          }
                        })
                        .catch(() => {
                          if (updatingToast && typeof hideToast === 'function') hideToast(updatingToast);
                          if (typeof showToast === 'function') showToast('Server error while setting inactive', 'error');
                        });
                    }
                  );
                } else {
                  if (confirm(msg + '\n\nSet to Inactive instead?')) {
                    const body = new URLSearchParams();
                    body.set('accession_id', id);
                    body.set('status', 'Inactive');
                    fetch('/update-consumable', {
                      method: 'POST',
                      headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'Content-Type': 'application/x-www-form-urlencoded'
                      },
                      body: body.toString()
                    })
                      .then(r => r.json())
                      .then(resData => {
                        if (resData && resData.success) {
                          if (typeof showToast === 'function') showToast('Consumable set to Inactive', 'success');
                          refreshConsumableTableWithoutReload();
                        } else {
                          if (typeof showToast === 'function') showToast(resData && (resData.error || resData.message) || 'Failed to set Inactive', 'error');
                        }
                      })
                      .catch(() => {
                        if (typeof showToast === 'function') showToast('Server error while setting inactive', 'error');
                      });
                  }
                }
              } else {
                if (typeof showToast === 'function') showToast(msg, 'error');
              }

              if (toastId && typeof hideToast === 'function') hideToast(toastId);
              return;
            }

            // Success path
            const d = data;
            if (toastId && typeof hideToast === 'function') hideToast(toastId);
            if (d && d.success) {
              if (typeof showDeleteConsumableToast === 'function') {
                showDeleteConsumableToast({ itemName });
              } else if (typeof showToast === 'function') {
                showToast('Consumable archived successfully', 'success');
              }
              refreshConsumableTableWithoutReload();
            } else {
              if (typeof showToast === 'function') showToast((d && (d.error || d.message)) || 'Failed to archive consumable', 'error');
            }
          })
          .catch(() => {
            if (toastId && typeof hideToast === 'function') hideToast(toastId);
            if (typeof showToast === 'function') showToast('Server error during archive', 'error');
          });
      }
    );
  } else {
    if (confirm('Archive this consumable?')) {
      fetch(`/delete-consumable/${id}`, {
        method: 'POST',
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
      })
        .then(() => refreshConsumableTableWithoutReload());
    }
  }
};

function closeConsumableModal() {
  const modal = document.getElementById('consumableModal');
  if (!modal || modal.classList.contains('hidden')) return;

  if (modal._hideTimer) {
    window.clearTimeout(modal._hideTimer);
    modal._hideTimer = null;
  }

  modal.classList.remove('modal-open');
  modal._hideTimer = window.setTimeout(() => {
    modal.classList.add('hidden');
    modal._hideTimer = null;
  }, CONSUMABLE_MODAL_ANIMATION_MS);
}

// Expose for inline onclick handlers in templates
window.openConsumableModal = openConsumableModal;
window.closeConsumableModal = closeConsumableModal;
window.editConsumable = function (id) {
  window.openConsumableModalById(id);
};

// Close when clicking the dark backdrop (but not when clicking the dialog)
document.addEventListener('click', function (e) {
  const modal = document.getElementById('consumableModal');
  if (!modal || modal.classList.contains('hidden')) return;
  if (e.target === modal) closeConsumableModal();
});

// Close on ESC
document.addEventListener('keydown', function (e) {
  if (e.key !== 'Escape') return;
  const modal = document.getElementById('consumableModal');
  if (!modal || modal.classList.contains('hidden')) return;
  closeConsumableModal();
});

// ---------- FORM SUBMIT ----------
document.addEventListener('DOMContentLoaded', function () {
  initConsumableExcelImportControls();

  const form = document.getElementById('consumableForm');
  if (!form) return;

  form.addEventListener('submit', async function (e) {
    e.preventDefault();

    const formData = new URLSearchParams(new FormData(form));
    const itemName = document.getElementById('item_name').value;
    const category = document.getElementById('category').value;
    const isEdit = form.action.includes('update');
    
    try {
      const res = await fetch(form.action, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: formData
      });

      const result = await res.json();
      if (result && result.success) {
        // Show specialized toast for save action
        if (typeof showSaveConsumableToast === 'function') {
          showSaveConsumableToast({
            itemName: itemName,
            action: isEdit ? 'Updated' : 'Added',
            category: category
          });
        } else {
          showToast(result.message || 'Saved successfully', 'success');
        }
        
        // Close modal and reload after a short delay
        closeConsumableModal();
        refreshConsumableTableWithoutReload();
        return;
      }

      // Show error
      const errorMsg = (result && result.message) ? result.message : 'Failed to save consumable.';
      if (typeof showToast === 'function') {
        showToast(errorMsg, 'error');
      } else {
        notifyUser(errorMsg);
      }
    } catch (err) {
      console.error(err);
      if (typeof showToast === 'function') {
        showToast('Error submitting form.', 'error');
      } else {
        notifyUser('Error submitting form.');
      }
    }
  });
});

function escapeConsumableHtml(value) {
  if (value === null || value === undefined) return '';

  if (typeof escapeHtml === 'function') {
    return escapeHtml(String(value));
  }

  const div = document.createElement('div');
  div.textContent = String(value);
  return div.innerHTML;
}

function getConsumableFilterValues() {
  const url = new URL(window.location.href);
  const filterKeys = [
    'search',
    'department_id',
    'status',
    'accountable',
    'item_name',
    'brand_model',
    'date_from',
    'date_to'
  ];

  const filters = {};
  // include 'search' in filterKeys so server-side search is forwarded
  filterKeys.forEach((key) => {
    const value = url.searchParams.get(key);
    if (value) {
      filters[key] = value;
    }
  });

  return filters;
}

function createConsumablePageUrl(page, perPage) {
  const url = new URL(window.location.href);
  url.searchParams.set('section', 'consumable');
  url.searchParams.set('consumable_page', String(page));
  url.searchParams.set('per_page', String(perPage));
  return `${url.pathname}?${url.searchParams.toString()}`;
}

function createConsumablePagedApiUrl(page, perPage) {
  const params = new URLSearchParams();
  params.set('page', String(page));
  params.set('per_page', String(perPage));

  const filters = getConsumableFilterValues();
  Object.keys(filters).forEach((key) => {
    params.set(key, filters[key]);
  });

  return `/manage_inventory/consumables-paged?${params.toString()}`;
}

function refreshConsumableTableWithoutReload() {
  const nav = document.getElementById('consumablePaginationNav');
  const perPageSelect = document.getElementById('consumablePerPageSelect');
  const pageInput = document.getElementById('consumablePageInput');

  const page = Number(nav?.dataset.page) || Number(pageInput?.value) || 1;
  const perPage = Number(perPageSelect?.value) || Number(nav?.dataset.perPage) || 10;

  if (typeof loadConsumablePageAjax === 'function') {
    loadConsumablePageAjax(page, perPage, false);
  }

  // If the archive page is open, also refresh its consumables list so newly
  // archived items appear immediately without a manual reload.
  if (typeof window.loadConsumables === 'function') {
    try {
      window.loadConsumables();
    } catch (e) {
      // ignore errors from unrelated pages
      console.debug('loadConsumables invoke failed', e);
    }
  }
}

function exportSelectedConsumables() {
  const selected = Array.from(document.querySelectorAll('.consumable-checkbox:checked'))
    .map((checkbox) => Number(checkbox.value))
    .filter((id) => Number.isFinite(id));

  if (!selected.length) {
    if (typeof showToast === 'function') {
      showToast('Please select at least one consumable to export', 'warning');
    } else {
      notifyUser('Please select at least one consumable to export.', 'warning');
    }
    return;
  }

  const toastId = typeof showToast === 'function'
    ? showToast(`Exporting ${selected.length} consumable(s)...`, 'loading')
    : null;

  fetch('/export-selected-consumables', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ consumable_ids: selected })
  })
    .then(async (response) => {
      if (!response.ok) {
        let message = 'Export failed';
        try {
          const data = await response.json();
          if (data && data.error) {
            message = data.error;
          }
        } catch (_) {
          // Keep fallback message when non-JSON response is returned.
        }
        throw new Error(message);
      }
      return response.blob();
    })
    .then((blob) => {
      if (toastId) hideToast(toastId);

      const url = window.URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = 'selected_consumables.xlsx';
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      window.URL.revokeObjectURL(url);

      if (typeof showExportToast === 'function') {
        showExportToast({
          count: selected.length,
          type: 'Consumable',
          filename: 'selected_consumables.xlsx'
        });
      } else if (typeof showToast === 'function') {
        showToast(`${selected.length} consumable(s) exported successfully`, 'success');
      }
    })
    .catch((error) => {
      if (toastId) hideToast(toastId);
      console.error(error);
      if (typeof showToast === 'function') {
        showToast(error?.message || 'Export failed. Please try again.', 'error');
      } else {
        notifyUser(error?.message || 'Export failed. Please try again.', 'error');
      }
    });
}

function importConsumableExcel(forceFirstPage = false) {
  const fileInput = document.getElementById('consumableExcelFile');
  const duplicateOptionInput = document.getElementById('consumableDuplicateOption');
  const duplicateOption = duplicateOptionInput ? duplicateOptionInput.value : 'skip';

  if (!fileInput || !fileInput.files || !fileInput.files.length) {
    if (typeof showToast === 'function') {
      showToast('Please select an Excel file first', 'warning');
    } else {
      notifyUser('Please select an Excel file first.', 'warning');
    }
    return;
  }

  const selectedFile = fileInput.files[0];
  const filename = selectedFile.name;

  const toastId = typeof showToast === 'function'
    ? showToast(`Importing ${filename}...`, 'loading')
    : null;

  const formData = new FormData();
  formData.append('file', selectedFile);
  formData.append('duplicate_option', duplicateOption);

  fetch('/import-consumables-excel', {
    method: 'POST',
    body: formData
  })
    .then((response) => response.json())
    .then((data) => {
      if (toastId) hideToast(toastId);

      if (!data || !data.success) {
        if (typeof showToast === 'function') {
          showToast((data && data.error) || 'Import failed', 'error');
        } else {
          notifyUser((data && data.error) || 'Import failed', 'error');
        }
        return;
      }

      const added = Number(data.added) || 0;
      const updated = Number(data.updated) || 0;
      const skipped = Number(data.skipped) || 0;

      if (typeof showImportToast === 'function') {
        showImportToast({
          type: 'Consumable',
          filename,
          added,
          updated,
          skipped
        });
      } else if (typeof showToast === 'function') {
        showToast(`Import complete: ${added} added, ${updated} updated, ${skipped} skipped`, 'success');
      }

      const nav = document.getElementById('consumablePaginationNav');
      const perPageSelect = document.getElementById('consumablePerPageSelect');
      const pageInput = document.getElementById('consumablePageInput');

      const perPage = Number(perPageSelect?.value) || Number(nav?.dataset.perPage) || 10;
      const currentPage = Number(nav?.dataset.page) || Number(pageInput?.value) || 1;
      const targetPage = forceFirstPage ? 1 : currentPage;

      if (typeof loadConsumablePageAjax === 'function') {
        loadConsumablePageAjax(targetPage, perPage, true);
      } else {
        refreshConsumableTableWithoutReload();
      }

      fileInput.value = '';
      const fileNameSpan = document.getElementById('consumableExcelFileName');
      if (fileNameSpan) {
        fileNameSpan.textContent = 'No file chosen';
        fileNameSpan.title = 'No file chosen';
      }
    })
    .catch((error) => {
      if (toastId) hideToast(toastId);
      console.error(error);
      if (typeof showToast === 'function') {
        showToast('Import failed. Please check the file and try again.', 'error');
      } else {
        notifyUser('Import failed. Please check the file and try again.', 'error');
      }
    });
}

function addConsumableExcelToManageList() {
  importConsumableExcel(true);
}

window.addConsumableExcelToManageList = addConsumableExcelToManageList;

function initConsumableExcelImportControls() {
  const fileInput = document.getElementById('consumableExcelFile');
  const fileNameSpan = document.getElementById('consumableExcelFileName');

  if (!fileInput || !fileNameSpan) {
    return;
  }

  const updateFileName = () => {
    const selectedFile = fileInput.files && fileInput.files[0];
    const text = selectedFile ? selectedFile.name : 'No file chosen';
    fileNameSpan.textContent = text;
    fileNameSpan.title = text;
  };

  fileInput.addEventListener('change', updateFileName);
  updateFileName();
}

window.refreshConsumableTableWithoutReload = refreshConsumableTableWithoutReload;

function getConsumableStatusBadgeClass(status) {
  if (status === 'Available') return 'bg-green-100 text-green-600';
  if (status === 'In Used') return 'bg-blue-100 text-blue-600';
  if (status === 'Inactive') return 'bg-gray-100 text-gray-500';
  return 'bg-red-100 text-red-600';
}

function parseConsumableQuantity(value) {
  const quantity = Number(value);
  return Number.isFinite(quantity) ? quantity : null;
}

function getConsumableStockLabel(quantity) {
  if (quantity === null) return '--';
  if (quantity === 0) return 'No Stock';
  if (quantity <= 50) return 'Low Stock';
  return 'Good Stock';
}

function getConsumableStockClass(quantity) {
  if (quantity === null) return 'text-gray-500';
  if (quantity === 0) return 'text-red-600';
  if (quantity <= 50) return 'text-yellow-500';
  return 'text-green-600';
}

function renderConsumableDesktopRows(consumables, canEdit) {
  const tbody = document.getElementById('consumableTableBody');
  if (!tbody) return;

  tbody.innerHTML = '';

  if (!consumables.length) {
    tbody.innerHTML = `
      <tr>
        <td colspan="14" class="px-4 py-6 text-center text-gray-500">No consumables found.</td>
      </tr>
    `;
    return;
  }

  consumables.forEach((item) => {
    const itemId = Number(item.accession_id);
    const quantity = parseConsumableQuantity(item.quantity);
    const stockLabel = getConsumableStockLabel(quantity);
    const stockClass = getConsumableStockClass(quantity);

    const actionsHtml = canEdit
      ? `
        <td class="px-4 py-2 border-b">
          <div class="flex flex-wrap gap-1">
            <button onclick="openConsumableModalById(${itemId})" class="bg-blue-500 hover:bg-blue-600 text-white px-2 py-1 rounded text-xs shadow whitespace-nowrap">Edit</button>
            <button type="button" data-item-name="${escapeConsumableHtml(item.item_name)}" onclick="archiveConsumableFromEl(this, ${itemId})" class="bg-red-600 hover:bg-red-700 text-white px-2 py-1 rounded text-xs shadow whitespace-nowrap">Archive</button>
            <button onclick="markChecked('CONSUMABLE', ${itemId})" class="bg-green-600 hover:bg-green-700 text-white px-2 py-1 rounded text-xs shadow whitespace-nowrap">Mark Checked</button>
            <button onclick="openMaintenanceLog(${itemId}, 'CONSUMABLE')" class="bg-gray-600 hover:bg-gray-700 text-white px-2 py-1 rounded text-xs shadow whitespace-nowrap">History</button>
          </div>
        </td>
      `
      : '<td class="px-4 py-2 border-b"></td>';

    tbody.insertAdjacentHTML(
      'beforeend',
      `
      <tr class="hover:bg-gray-100 transition">
        <td class="px-4 py-2 border-b">
          <input type="checkbox" class="consumable-checkbox" value="${escapeConsumableHtml(item.accession_id)}">
        </td>
        <td class="px-4 py-2 border-b">${escapeConsumableHtml(item.accession_id)}</td>
        <td class="px-4 py-2 border-b">${escapeConsumableHtml(item.item_name)}</td>
        <td class="px-4 py-2 border-b">${escapeConsumableHtml(item.category || '--')}</td>
        <td class="px-4 py-2 border-b">${escapeConsumableHtml(item.brand || '--')}</td>
        <td class="px-4 py-2 border-b">${escapeConsumableHtml(quantity === null ? '--' : quantity)}</td>
        <td class="px-4 py-2 border-b">${escapeConsumableHtml(item.unit || '--')}</td>
        <td class="px-4 py-2 border-b">${escapeConsumableHtml(item.department_name || '--')}</td>
        <td class="px-4 py-2 border-b">${escapeConsumableHtml(item.location || '--')}</td>
        <td class="px-4 py-2 border-b font-medium ${stockClass}">${escapeConsumableHtml(stockLabel)}</td>
        <td class="px-4 py-2 border-b">${escapeConsumableHtml(item.description || '--')}</td>
        <td class="px-4 py-2 border-b">${escapeConsumableHtml(item.date_added || '--')}</td>
        <td class="px-4 py-2 border-b">${escapeConsumableHtml(item.last_updated || '--')}</td>
        ${actionsHtml}
      </tr>
      `
    );
  });
}

function renderConsumableMobileCards(consumables, canEdit) {
  const container = document.getElementById('consumableMobileCards');
  if (!container) return;

  container.innerHTML = '';

  if (!consumables.length) {
    container.innerHTML = '<div class="bg-gray-100 text-gray-600 p-4 rounded-lg text-center">No consumables found.</div>';
    return;
  }

  consumables.forEach((item) => {
    const itemId = Number(item.accession_id);
    const quantity = parseConsumableQuantity(item.quantity);

    const actionsHtml = canEdit
      ? `
      <div class="grid grid-cols-2 gap-2">
        <button onclick="editConsumable(${itemId})" class="bg-blue-500 hover:bg-blue-600 text-white px-3 py-2 rounded text-xs font-medium transition">Edit</button>
        <button type="button" data-item-name="${escapeConsumableHtml(item.item_name)}" onclick="archiveConsumableFromEl(this, ${itemId})" class="bg-red-600 hover:bg-red-700 text-white px-3 py-2 rounded text-xs font-medium transition">Archive</button>
        <button onclick="markChecked('CONSUMABLE', ${itemId})" class="bg-green-600 hover:bg-green-700 text-white px-3 py-2 rounded text-xs font-medium transition">Mark Checked</button>
        <button onclick="openMaintenanceLog(${itemId}, 'CONSUMABLE')" class="bg-gray-600 hover:bg-gray-700 text-white px-3 py-2 rounded text-xs font-medium transition">History</button>
      </div>
      `
      : '';

    container.insertAdjacentHTML(
      'beforeend',
      `
      <div class="bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
        <div class="flex justify-between items-start mb-3">
          <div>
            <h4 class="font-semibold text-gray-900">${escapeConsumableHtml(item.item_name)}</h4>
            <p class="text-sm text-gray-600">ID: ${escapeConsumableHtml(item.accession_id)}</p>
          </div>
          <span class="px-2 py-1 text-xs font-semibold rounded-full ${getConsumableStatusBadgeClass(item.status)}">${escapeConsumableHtml(item.status || '--')}</span>
        </div>

        <div class="space-y-1 text-sm text-gray-600 mb-3">
          <p><span class="font-medium">Brand:</span> ${escapeConsumableHtml(item.brand || '--')}</p>
          <p><span class="font-medium">Quantity:</span> <span class="font-semibold">${escapeConsumableHtml(quantity === null ? '--' : quantity)}</span></p>
          <p><span class="font-medium">Department:</span> ${escapeConsumableHtml(item.department_name || '--')}</p>
          <p><span class="font-medium">Location:</span> ${escapeConsumableHtml(item.location || '--')}</p>
        </div>

        <div class="flex items-center gap-2 mb-3">
          <input type="checkbox" class="consumable-checkbox" value="${escapeConsumableHtml(item.accession_id)}">
          <label class="text-sm text-gray-600">Select for bulk actions</label>
        </div>

        ${actionsHtml}
      </div>
      `
    );
  });
}

function buildConsumablePaginationMarkup(currentPage, totalPages, perPage) {
  let html = '';

  const navButtonClass = 'flex items-center px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 hover:text-green-600 transition-colors';
  const disabledButtonClass = 'flex items-center px-3 py-2 text-sm font-medium text-gray-400 bg-gray-100 border border-gray-300 rounded-lg cursor-not-allowed';

  if (currentPage > 1) {
    html += `<button type="button" data-consumable-page="${currentPage - 1}" onclick="return goToConsumablePage(${currentPage - 1}, event)" class="${navButtonClass}"><svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path></svg>Prev</button>`;
  } else {
    html += `<span class="${disabledButtonClass}"><svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path></svg>Prev</span>`;
  }

  if (totalPages > 0) {
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, currentPage + 2);

    if (startPage > 1) {
      html += `<button type="button" data-consumable-page="1" onclick="return goToConsumablePage(1, event)" class="hidden sm:flex items-center justify-center w-10 h-10 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 hover:text-green-600 transition-colors">1</button>`;
      if (startPage > 2) {
        html += '<span class="hidden sm:flex items-center justify-center w-10 h-10 text-sm font-medium text-gray-500">...</span>';
      }
    }

    for (let page = startPage; page <= endPage; page++) {
      if (page === currentPage) {
        html += `<span class="flex items-center justify-center w-10 h-10 text-sm font-medium rounded-lg transition-colors z-10 bg-green-600 text-white border border-green-600">${page}</span>`;
      } else {
        html += `<button type="button" data-consumable-page="${page}" onclick="return goToConsumablePage(${page}, event)" class="flex items-center justify-center w-10 h-10 text-sm font-medium rounded-lg transition-colors text-gray-700 bg-white border border-gray-300 hover:bg-gray-50 hover:text-green-600">${page}</button>`;
      }
    }

    if (endPage < totalPages) {
      if (endPage < totalPages - 1) {
        html += '<span class="hidden sm:flex items-center justify-center w-10 h-10 text-sm font-medium text-gray-500">...</span>';
      }
      html += `<button type="button" data-consumable-page="${totalPages}" onclick="return goToConsumablePage(${totalPages}, event)" class="hidden sm:flex items-center justify-center w-10 h-10 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 hover:text-green-600 transition-colors">${totalPages}</button>`;
    }
  }

  if (currentPage < totalPages) {
    html += `<button type="button" data-consumable-page="${currentPage + 1}" onclick="return goToConsumablePage(${currentPage + 1}, event)" class="${navButtonClass}">Next<svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg></button>`;
  } else {
    html += `<span class="${disabledButtonClass}">Next<svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg></span>`;
  }

  return html;
}

function updateConsumablePaginationSummary(page, perPage, totalItems) {
  const summary = document.getElementById('consumablePaginationSummary');
  if (!summary) return;

  const start = totalItems > 0 ? (page - 1) * perPage + 1 : 0;
  const end = totalItems > 0 ? Math.min(page * perPage, totalItems) : 0;

  summary.innerHTML = `Showing <span class="font-medium">${start}</span> - <span class="font-medium">${end}</span> of <span class="font-medium">${totalItems}</span> records`;
}

function applyConsumablePaginationState(page, perPage, totalItems, totalPages) {
  const nav = document.getElementById('consumablePaginationNav');
  const perPageSelect = document.getElementById('consumablePerPageSelect');
  const pageInput = document.getElementById('consumablePageInput');
  const selectAll = document.getElementById('selectAllConsumables');

  if (nav) {
    nav.dataset.page = String(page);
    nav.dataset.perPage = String(perPage);
    nav.dataset.totalPages = String(totalPages);
    nav.dataset.totalItems = String(totalItems);
    nav.innerHTML = buildConsumablePaginationMarkup(page, totalPages, perPage);
  }

  if (perPageSelect) {
    perPageSelect.value = String(perPage);
  }

  if (pageInput) {
    pageInput.value = String(page);
  }

  if (selectAll) {
    selectAll.checked = false;
  }

  updateConsumablePaginationSummary(page, perPage, totalItems);
}

async function loadConsumablePageAjax(page, perPage, updateUrl = true) {
  try {
    const response = await fetch(createConsumablePagedApiUrl(page, perPage));
    if (!response.ok) {
      throw new Error(`Failed to load consumable page: ${response.status}`);
    }

    const data = await response.json();
    const consumables = Array.isArray(data.consumables) ? data.consumables : [];
    const currentPage = Number(data.page) || 1;
    const currentPerPage = Number(data.per_page) || perPage;
    const totalItems = Number(data.total_items) || 0;
    const totalPages = Number(data.total_pages) || 0;

    const tbody = document.getElementById('consumableTableBody');
    const canEdit = tbody && tbody.dataset.canEdit === '1';

    renderConsumableDesktopRows(consumables, canEdit);
    renderConsumableMobileCards(consumables, canEdit);
    applyConsumablePaginationState(currentPage, currentPerPage, totalItems, totalPages);

    if (window.lucide) {
      lucide.createIcons();
    }

    if (updateUrl) {
      window.history.replaceState({}, '', createConsumablePageUrl(currentPage, currentPerPage));
    }
  } catch (error) {
    console.error(error);
    if (typeof showToast === 'function') {
      showToast('Failed to load consumable page. Please try again.', 'error');
    }
  }
}

window.goToConsumablePage = function (page, event) {
  if (event) {
    event.preventDefault();
    event.stopPropagation();
  }

  const targetPage = Number(page);
  if (!targetPage) return false;

  const nav = document.getElementById('consumablePaginationNav');
  const perPageSelect = document.getElementById('consumablePerPageSelect');
  const perPage = Number(perPageSelect && perPageSelect.value)
    || Number(nav && nav.dataset.perPage)
    || 10;

  loadConsumablePageAjax(targetPage, perPage, true);
  return false;
};

function initConsumableAjaxPagination() {
  if (window.__consumablePaginationInitialized) {
    return;
  }

  const nav = document.getElementById('consumablePaginationNav');
  const perPageSelect = document.getElementById('consumablePerPageSelect');
  const perPageForm = document.getElementById('consumablePerPageForm');
  const tableBody = document.getElementById('consumableTableBody');

  if (!nav || !perPageSelect || !perPageForm || !tableBody) {
    return;
  }

  window.__consumablePaginationInitialized = true;

  nav.addEventListener('click', (event) => {
    const pageButton = event.target && event.target.closest
      ? event.target.closest('[data-consumable-page]')
      : null;

    if (!pageButton || !nav.contains(pageButton)) {
      return;
    }

    const page = Number(pageButton.getAttribute('data-consumable-page'));
    if (!page) {
      return;
    }

    event.preventDefault();
    event.stopPropagation();
    window.goToConsumablePage(page, event);
  });

  perPageForm.addEventListener('submit', (event) => {
    event.preventDefault();
  });

  perPageSelect.addEventListener('change', () => {
    const perPage = Number(perPageSelect.value) || 10;
    loadConsumablePageAjax(1, perPage, true);
  });

  window.addEventListener('popstate', () => {
    const url = new URL(window.location.href);
    const section = url.searchParams.get('section');
    if (section !== 'consumable') return;

    const page = Number(url.searchParams.get('consumable_page')) || 1;
    const perPage = Number(url.searchParams.get('per_page')) || Number(perPageSelect.value) || 10;
    loadConsumablePageAjax(page, perPage, false);
  });
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initConsumableAjaxPagination);
} else {
  initConsumableAjaxPagination();
}
