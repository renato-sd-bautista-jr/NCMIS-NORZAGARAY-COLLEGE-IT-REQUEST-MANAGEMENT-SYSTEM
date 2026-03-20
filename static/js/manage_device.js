// =======================
// MANAGE DEVICES SECTION
// =======================


 
// ---------- BULK STATUS UPDATE ----------
function bulkUpdateDevices() {
  const status = document.getElementById("bulkDeviceStatus").value;
  const selected = [...document.querySelectorAll(".device-checkbox:checked")]
    .map(cb => cb.value);

  if (!status) {
    alert("Select a status.");
    return;
  }

  if (!selected.length) {
    alert("Select at least one device.");
    return;
  }

  // Use confirmation modal instead of native confirm
  showConfirmationModal(
    'Confirm Bulk Update',
    `Update ${selected.length} selected device(s) to status "${status}"? This action cannot be undone.`,
    'Update',
    function() {
      fetch("/inventory/device/bulk-update", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          device_ids: selected,
          new_status: status
        })
      })
        .then(res => res.json())
        .then(d => d.success ? location.reload() : alert("Bulk update failed"));
    }
  );
}

// ---------- DEVICE MODAL ----------
async function openItemModalById(id) {
  try {
    const res = await fetch(`/manage_inventory/get-item-by-id/${id}`);
    if (!res.ok) throw new Error();
    const item = await res.json();
    openItemModal(item);
  } catch {
    alert("Failed to load device data.");
  }
}

// ---------- CHECK ----------
function markChecked(type, id) {
  fetch(`/inventory/${type}/${id}/check`, { method: "POST" })
    .then(res => res.json())
    .then(d => d.success ? location.reload() : alert("Update failed"));
}

window.openItemModalById = async function (id) {
  try {
    const res = await fetch(`/manage_inventory/get-item-by-id/${id}`);
    const item = await res.json();
    openItemModal(item);
  } catch {
    alert("Failed to load device.");
  }
};

window.bulkUpdateDevices = function () {
  const status = document.getElementById("bulkDeviceStatus").value;
  const ids = [...document.querySelectorAll(".device-checkbox:checked")]
    .map(cb => cb.value);

  if (!status) {
    alert("Select a status.");
    return;
  }

  if (!ids.length) {
    alert("Select at least one device.");
    return;
  }

  // Use confirmation modal instead of native confirm
  showConfirmationModal(
    'Confirm Bulk Update',
    `Update ${ids.length} selected device(s) to status "${status}"? This action cannot be undone.`,
    'Update',
    function() {
      fetch("/inventory/device/bulk-update", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ device_ids: ids, new_status: status })
      })
        .then(res => res.json())
        .then(d => d.success ? location.reload() : alert("Bulk update failed"));
    }
  );
};

 
function bulkMarkDamagedSelectedDevices() {
  const checked = Array.from(document.querySelectorAll('.device-checkbox'))
    .filter(cb => cb.checked)
    .map(cb => cb.value);

  if (checked.length === 0) {
    alert('No Devices selected');
    return;
  }

  if (!confirm(`Mark ${checked.length} Device(s) as DAMAGED?`)) return;

  fetch('/inventory/device-bulk-damaged', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      device_ids: checked,
      damage_type: 'General Damage',
      description: 'Bulk marked as damaged'
    })
  })
  .then(r => r.json())
  .then(d => {
    if (d && d.success) location.reload();
    else alert('Failed: ' + (d.error || 'unknown'));
  })
  .catch(err => {
    console.error(err);
    alert('Operation failed');
  });
}

function toggleSelectAllDevices(master) {
  document.querySelectorAll(".device-checkbox")
    .forEach(cb => cb.checked = master.checked);
}