// ===========================
// PC Filter Modal Management
// ===========================

// ✅ Open Modal
async function openPcFilterModal() {
  const existingModal = document.getElementById('pcFilterModal');
  if (!existingModal) {
    const res = await fetch('/manage_inventory/pc-filter-modal');
    const html = await res.text();
    document.body.insertAdjacentHTML('beforeend', html);
  }

  // Load department list only once
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

  document.getElementById('pcFilterModal').classList.remove('hidden');
  lucide.createIcons();
}

// ✅ Close Modal
function closePcFilterModal() {
  const modal = document.getElementById('pcFilterModal');
  if (modal) modal.classList.add('hidden');
}

// ✅ Handle Filter Form Submission
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

// ✅ Helper: Render filtered PCs into table
function renderPcTable(pcs) {
  const tableBody = document.querySelector("#pcTableBody");
  if (!tableBody) return;

  tableBody.innerHTML = "";

  pcs.forEach(pc => {
    const row = document.createElement("tr");
    row.classList.add("border-b");
    row.innerHTML = `
      <td class="px-4 py-2 border-b">${ pc.pcid }</td>
                  <td class="px-4 py-2 border-b">${ pc.pcname }</td>
                  <td class="px-4 py-2 border-b">${ pc.department_name }</td>
                  <td class="px-4 py-2 border-b">${ pc.location }</td>
                  <td class="px-4 py-2 border-b">${ pc.acquisition_cost }</td>
                  <td class="px-4 py-2 border-b">${ pc.date_acquired }</td>
                  <td class="px-4 py-2 border-b">${ pc.accountable }</td>
                  <td class="px-4 py-2 border-b">${ pc.serial_no }</td>
                  <td class="px-4 py-2 border-b">${ pc.municipal_serial_no }</td>
                  <td class="px-4 py-2 border-b">${ pc.note }</td>
      
      <td class="px-2 py-1 text-right">
        <button class="text-blue-600 hover:underline" onclick='openPcModal(${JSON.stringify(pc)})'>Edit</button>
      </td>
    `;
    tableBody.appendChild(row);
  });
}
