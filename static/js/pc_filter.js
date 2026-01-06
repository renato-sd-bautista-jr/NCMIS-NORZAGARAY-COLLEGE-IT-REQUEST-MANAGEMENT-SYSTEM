// ===========================
// PC Filter Modal Management
// ===========================

// Open Modal
async function openPcFilterModal() {
  let modal = document.getElementById('pcFilterModal');

  if (!modal) {
    try {
      const res = await fetch('/manage_inventory/pc-filter-modal');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const html = await res.text();
      document.body.insertAdjacentHTML('beforeend', html);
      modal = document.getElementById('pcFilterModal');
      lucide.createIcons();
    } catch (err) {
      console.error("❌ Error loading PC filter modal:", err);
      alert("Failed to load PC filter modal.");
      return;
    }
  }

  // Load departments once
  const deptSelect = document.getElementById('filter_department');
  if (deptSelect && deptSelect.options.length <= 1) {
    try {
      const res = await fetch('/get-departments');
      const departments = await res.json();
      deptSelect.innerHTML = '<option value="">All</option>';
      departments.forEach(dep => {
        const opt = document.createElement('option');
        opt.value = dep.department_id;
        opt.textContent = dep.department_name;
        deptSelect.appendChild(opt);
      });
    } catch {
      deptSelect.innerHTML = '<option value="">Error loading</option>';
    }
  }

  modal.classList.remove('hidden');
}

// Close Modal
function closePcFilterModal() {
  const modal = document.getElementById('pcFilterModal');
  if (modal) modal.classList.add('hidden');
}

// Filter Form Submission
document.addEventListener("submit", async (e) => {
  if (e.target.id === "pcFilterForm") {
    e.preventDefault();
    const form = e.target;
    const params = new URLSearchParams(new FormData(form)).toString();

    try {
      const res = await fetch(`/filter-pcs?${params}`);
      const data = await res.json();

      if (Array.isArray(data)) {
        renderPcTable(data);
        closePcFilterModal();
      } else {
        alert("⚠️ Error filtering PCs");
      }
    } catch (err) {
      console.error("❌ Filter error:", err);
      alert("Server error while filtering PCs.");
    }
  }
});

// Render PCs into table
function renderPcTable(pcs) {
  const tbody = document.getElementById("pcTableBody");
  if (!tbody) return;
  tbody.innerHTML = "";

  if (!pcs.length) {
    tbody.innerHTML = `
      <tr>
        <td colspan="13" class="text-center py-6 text-gray-500">No PCs found.</td>
      </tr>`;
    return;
  }

  pcs.forEach(pc => {
    const riskClass =
      pc.risk_level === "High" ? "text-red-600" :
      pc.risk_level === "Medium" ? "text-yellow-600" :
      "text-green-600";

    const statusClass =
      pc.status === "Needs Checking" ? "text-yellow-600" :
      pc.status === "Critical" ? "text-red-700 font-bold" :
      "text-green-600";

    tbody.insertAdjacentHTML("beforeend", `
      <tr class="hover:bg-gray-100 transition">
      <th class="px-4 py-2 border-b text-left">
  <input type="checkbox" id="selectAllPcs" onclick="toggleSelectAllPCs()">
</th>
        <td class="px-4 py-2 border-b">${pc.pcid ?? "—"}</td>
        <td class="px-4 py-2 border-b">${pc.pcname ?? "—"}</td>
        <td class="px-4 py-2 border-b">${pc.department_name ?? "—"}</td>
        <td class="px-4 py-2 border-b">${pc.location ?? "—"}</td>
        <td class="px-4 py-2 border-b">${pc.acquisition_cost ?? "—"}</td>
        <td class="px-4 py-2 border-b">${pc.date_acquired ?? "—"}</td>
        <td class="px-4 py-2 border-b">${pc.accountable ?? "—"}</td>
        <td class="px-4 py-2 border-b">${pc.serial_no ?? "—"}</td>
        <td class="px-4 py-2 border-b">${pc.municipal_serial_no ?? "—"}</td>
        <td class="px-4 py-2 border-b">${pc.note ?? "—"}</td>

        <td class="px-4 py-2 border-b ${statusClass}">${pc.status ?? "—"}</td>
        <td class="px-4 py-2 border-b font-semibold ${riskClass}">${pc.risk_level ?? "—"}</td>
        <td class="px-4 py-2 border-b">${pc.health_score ?? "—"}%</td>

        <td class="px-4 py-2 border-b flex gap-2">
          <button
            class="bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded text-xs"
            data-pc='${encodeURIComponent(JSON.stringify(pc))}'
            onclick="openPcModalFromBtn(this)">
            Edit
          </button>

          <button
            onclick="markPcChecked(${pc.pcid})"
            class="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded text-xs">
            Mark Checked
          </button>

          <button
            onclick="openMaintenanceLog(${pc.pcid}, 'PC')"
            class="bg-gray-600 hover:bg-gray-700 text-white px-3 py-1 rounded text-xs">
            History
          </button>
        </td>
      </tr>
    `);
  });
}

// Open PC modal safely from button
function openPcModalFromBtn(btn) {
  const pc = JSON.parse(decodeURIComponent(btn.dataset.pc));
  openPcModal(pc);
}
