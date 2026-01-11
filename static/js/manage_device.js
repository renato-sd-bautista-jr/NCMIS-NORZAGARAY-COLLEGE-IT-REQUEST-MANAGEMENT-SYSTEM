// =======================
// MANAGE DEVICES SECTION
// =======================

// ---------- SELECT ALL ----------
function toggleSelectAllDevices() {
  const master = document.getElementById("selectAllDevices");
  document.querySelectorAll(".device-checkbox")
    .forEach(cb => cb.checked = master.checked);
}

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

  if (!confirm(`Update ${selected.length} device(s)?`)) return;

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

  if (!status || !ids.length) return alert("Missing selection.");

  fetch("/inventory/device/bulk-update", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ device_ids: ids, new_status: status })
  }).then(() => location.reload());
};


window.toggleSelectAllDevices = function () {
  const master = document.getElementById("selectAllDevices");
  document.querySelectorAll(".device-checkbox")
    .forEach(cb => cb.checked = master.checked);
};