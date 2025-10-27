// static/js/filter_device_modal.js

async function openDeviceFilterModalFromFile() {
  // Load modal dynamically if it doesn't exist yet
  if (!document.getElementById("filterDeviceModal")) {
    try {
      const res = await fetch("/manage_inventory/device-filter-modal");
      if (!res.ok) throw new Error(`Failed to load modal: ${res.status}`);
      const html = await res.text();
      document.body.insertAdjacentHTML("beforeend", html);
      lucide.createIcons();
    } catch (err) {
      console.error("❌ Error loading Device Filter Modal:", err);
      alert("Failed to load Device Filter Modal.");
      return;
    }
  }

  const modal = document.getElementById("filterDeviceModal");
  const content = document.getElementById("deviceFilterModalContent");

  modal.classList.remove("hidden");
  setTimeout(() => {
    content.classList.add("scale-100");
  }, 50);

  lucide.createIcons();
}

// Close modal
function closeDeviceFilterModal() {
  const modal = document.getElementById("filterDeviceModal");
  if (modal) modal.classList.add("hidden");
}

// Handle filtering (rest of the code from earlier)
document.addEventListener("DOMContentLoaded", () => {
  const tableBody = document.getElementById("deviceTableBody");

  document.addEventListener("submit", async (e) => {
    if (e.target.id !== "filterDeviceForm") return;
    e.preventDefault();

    const params = new URLSearchParams(new FormData(e.target)).toString();

    try {
      const res = await fetch(`/manage_inventory/filter-device?${params}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      tableBody.innerHTML = "";
      if (data.length === 0) {
        tableBody.innerHTML = `
          <tr><td colspan="11" class="text-center text-gray-500 py-4">
          No devices found for the selected filters.
          </td></tr>`;
        return;
      }

      data.forEach((item) => {
        tableBody.innerHTML += `
          <tr class="hover:bg-gray-100 transition">
            <td class="px-4 py-2 border-b">${item.accession_id}</td>
            <td class="px-4 py-2 border-b">${item.item_name || "—"}</td>
            <td class="px-4 py-2 border-b">${item.brand_model || "—"}</td>
            <td class="px-4 py-2 border-b">${item.serial_no || "—"}</td>
            <td class="px-4 py-2 border-b">${item.municipal_serial_no || "—"}</td>
            <td class="px-4 py-2 border-b">₱${parseFloat(item.acquisition_cost || 0).toFixed(2)}</td>
            <td class="px-4 py-2 border-b">${item.date_acquired || "—"}</td>
            <td class="px-4 py-2 border-b">${item.accountable || "—"}</td>
            <td class="px-4 py-2 border-b">${item.department_name || "—"}</td>
            <td class="px-4 py-2 border-b">
              <span class="${
                item.status === "Available"
                  ? "text-green-600"
                  : item.status === "In Used"
                  ? "text-blue-600"
                  : item.status === "Inactive"
                  ? "text-gray-500"
                  : "text-red-600"
              } font-medium">${item.status}</span>
            </td>
            <td class="px-4 py-2 border-b flex gap-2">
              <button onclick="openItemModalById(${item.accession_id})"
                class="bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded text-xs shadow">
                Edit
              </button>
              <button 
                type="button"
                onclick="openDeleteModal('/manage_inventory/delete-item/${item.accession_id}')"
                class="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-xs shadow">
                Delete
              </button>
            </td>
          </tr>`;
      });

      closeDeviceFilterModal();
      lucide.createIcons();

    } catch (error) {
      console.error("❌ Filter error:", error);
      alert("Failed to filter devices.");
    }
  });
});
