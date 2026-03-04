// static/js/filter_device_modal.js

async function openDeviceFilterModalFromFile() {
  // Load modal dynamically if it doesn't exist yet
  if (!document.getElementById("filterDeviceModal")) {
    try {
      const res = await fetch("/device-filter-modal");
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

  // prefill device type filter based on current section
  if (window.currentSection === 'consumable') {
    const dtInput = modal.querySelector('input[name="device_type"]');
    if (dtInput) dtInput.value = 'Consumable';
  } else if (window.currentSection === 'item') {
    const dtInput = modal.querySelector('input[name="device_type"]');
    if (dtInput) dtInput.value = '';
  }

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

    const params = new URLSearchParams(new FormData(e.target));
    
    // determine section based on global state (managed in manage_pc.js)
    let sectionParam = 'pc';
    if (window.currentSection === 'item') {
      sectionParam = 'items';
    } else if (window.currentSection === 'consumable') {
      sectionParam = 'consumable';
      // ensure device_type filter is set so backend restricts to consumables
      params.set('device_type', 'Consumable');
    }
    params.set('section', sectionParam);
    
    // Redirect to the same page with filter parameters
    window.location.href = `/manage_inventory?${params.toString()}`;
  });
});
