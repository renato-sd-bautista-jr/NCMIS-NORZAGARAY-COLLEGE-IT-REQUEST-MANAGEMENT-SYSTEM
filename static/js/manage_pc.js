// =======================
// MANAGE PC SECTION
// =======================

// SECTION STATE
let currentSection = "pc";

// ---------- SECTION SWITCHING ----------
function showSection(id) {
  document.querySelectorAll("section").forEach(sec =>
    sec.classList.add("hidden")
  );
  document.getElementById(id).classList.remove("hidden");

  const addBtn = document.getElementById("addButton");

  if (id === "inventorySection") {
    currentSection = "pc";
    addBtn.textContent = "Add PC";
  } else {
    currentSection = "item";
    addBtn.textContent = "Add Device";
  }
}

function handleAddButtonClick() {
  if (currentSection === "pc") openPcModal();
  else openItemModal();
}

// ---------- PC MODAL ----------
async function openPcModalById(pcid) {
  try {
    const res = await fetch(`/manage_inventory/get-pc-by-id/${pcid}`);
    if (!res.ok) throw new Error();
    const pc = await res.json();
    openPcModal(pc);
  } catch {
    alert("Failed to load PC data.");
  }
}

// ---------- MAINTENANCE ----------
function openMaintenanceLog(id, type) {
  window.location.href = `/maintenance-history?type=${type}&id=${id}`;
}

// ---------- CHECK / BULK CHECK ----------
function markPcChecked(pcid) {
  if (!confirm("Mark this PC as checked?")) return;

  fetch(`/inventory/pc/${pcid}/check`, { method: "POST" })
    .then(res => res.json())
    .then(d => d.success ? location.reload() : alert("Update failed"));
}

function bulkMarkPcChecked() {
  const selected = [...document.querySelectorAll(".pc-checkbox:checked")]
    .map(cb => cb.value);

  if (!selected.length) {
    alert("Select at least one PC.");
    return;
  }

  if (!confirm(`Mark ${selected.length} PCs as checked?`)) return;

  fetch("/inventory/pc/bulk-check", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ pcids: selected })
  })
    .then(res => res.json())
    .then(d => d.success ? location.reload() : alert("Bulk update failed"));
}

// ---------- SELECT ALL ----------
function toggleSelectAllPCs(master) {
  document.querySelectorAll(".pc-checkbox")
    .forEach(cb => cb.checked = master.checked);
}

// ---------- RISK UPDATE ----------
async function runRiskUpdate() {
  if (!confirm("Recalculate PC risk levels?")) return;

  try {
    const res = await fetch("/manage_inventory/run-risk-update", {
      method: "POST"
    });
    const data = await res.json();
    alert(data.message || "Risk updated.");
    location.reload();
  } catch {
    alert("Risk update failed.");
  }
}

window.openPcModalById = async function (pcid) {
  try {
    const res = await fetch(`/manage_inventory/get-pc-by-id/${pcid}`);
    if (!res.ok) throw new Error(res.status);
    const pc = await res.json();
    openPcModal(pc);
  } catch {
    alert("Failed to load PC data.");
  }
};

window.markPcChecked = function (pcid) {
  if (!confirm("Mark this PC as checked?")) return;

  fetch(`/inventory/pc/${pcid}/check`, { method: "POST" })
    .then(r => r.json())
    .then(d => d.success ? location.reload() : alert("Failed"));
};


window.bulkMarkPcChecked = function () {
  const ids = [...document.querySelectorAll(".pc-checkbox:checked")]
    .map(cb => cb.value);

  if (!ids.length) return alert("Select at least one PC.");

  fetch("/inventory/pc/bulk-check", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ pcids: ids })
  }).then(() => location.reload());
};

window.runRiskUpdate = async function () {
  if (!confirm("Run risk recalculation?")) return;
  await fetch("/manage_inventory/run-risk-update", { method: "POST" });
  location.reload();
};

window.openMaintenanceLog = function (id, type) {
  window.location.href = `/maintenance-history?type=${type}&id=${id}`;
};

function openDeleteModal(actionUrl) {
  const modal = document.getElementById("deleteModal");
  const form = document.getElementById("deleteForm");

  if (!modal || !form) {
    console.error("Delete modal or form not found in DOM");
    return;
  }

  form.action = actionUrl;
  modal.classList.remove("hidden");

  if (window.lucide) {
    lucide.createIcons();
  }
}

function closeDeleteModal() {
  const modal = document.getElementById("deleteModal");
  if (modal) modal.classList.add("hidden");
}

// Bind cancel button once DOM is ready
document.addEventListener("DOMContentLoaded", () => {
  const cancelBtn = document.getElementById("cancelDelete");
  if (cancelBtn) {
    cancelBtn.addEventListener("click", closeDeleteModal);
  }
});