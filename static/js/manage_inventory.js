window.currentSection = "pc";

function getSectionKeyFromId(id) {
  if (id === "inventorySection") return "pc";
  if (id === "itemsSection") return "item";
  if (id === "consumablesSection") return "consumable";
  if (id === "surrenderedSection") return "surrendered";
  return null;
}

function getSectionTargets(sectionParam) {
  if (sectionParam === "item" || sectionParam === "items") {
    return { sectionId: "itemsSection", buttonId: "itemsBtn" };
  }

  if (sectionParam === "consumable" || sectionParam === "consumables") {
    return { sectionId: "consumablesSection", buttonId: "consumablesBtn" };
  }

  if (sectionParam === "surrendered") {
    return { sectionId: "surrenderedSection", buttonId: "surrenderedBtn" };
  }

  return { sectionId: "inventorySection", buttonId: "inventoryBtn" };
}

function syncSectionQueryParam(sectionKey) {
  if (!sectionKey || !window.history || typeof window.history.replaceState !== "function") {
    return;
  }

  const url = new URL(window.location.href);
  url.searchParams.set("section", sectionKey);

  if (sectionKey !== "surrendered") {
    url.searchParams.delete("surrendered_page");
    url.searchParams.delete("surrendered_per_page");
  }

  window.history.replaceState({}, "", `${url.pathname}?${url.searchParams.toString()}`);
}

function showSection(id) {

  document.querySelectorAll("section").forEach(sec =>
    sec.classList.add("hidden")
  );

  const target = document.getElementById(id);
  if (target) target.classList.remove("hidden");

  const sectionKey = getSectionKeyFromId(id);
  if (sectionKey) {
    window.currentSection = sectionKey;
    syncSectionQueryParam(sectionKey);
  }

}

// ---------- ACTIVE NAV BUTTON ----------
function setActiveNav(button) {

  const navButtons = document.querySelectorAll("nav button");

  navButtons.forEach(btn => {
    btn.classList.remove(
      "bg-blue-50",
      "text-blue-700",
      "border-blue-300"
    );

    btn.classList.add(
      "bg-white",
      "text-gray-700",
      "border-gray-200"
    );
  });

  button.classList.remove(
    "bg-white",
    "text-gray-700",
    "border-gray-200"
  );

  button.classList.add(
    "bg-blue-50",
    "text-blue-700",
    "border-blue-300"
  );
}

// ---------- OPTIONAL AUTO LOAD ----------
document.addEventListener("DOMContentLoaded", () => {

  const params = new URLSearchParams(window.location.search);
  const section = params.get("section");

const { sectionId, buttonId } = getSectionTargets(section);

showSection(sectionId);

const btn = document.getElementById(buttonId);
if (btn) setActiveNav(btn);

  if (window.lucide) {
    lucide.createIcons();
  }

});

window.openDeleteModal = function openDeleteModal(actionUrl) {
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
};

window.closeDeleteModal = function closeDeleteModal() {
  const modal = document.getElementById("deleteModal");
  if (modal) modal.classList.add("hidden");
};

document.addEventListener("DOMContentLoaded", () => {
  const cancelBtn = document.getElementById("cancelDelete");
  if (cancelBtn) {
    cancelBtn.addEventListener("click", window.closeDeleteModal);
  }

  const modal = document.getElementById("deleteModal");
  if (modal) {
    modal.addEventListener("click", function (e) {
      if (e.target === modal) {
        window.closeDeleteModal();
      }
    });
  }
});

function toggleSelectAllDevices(master) {
  document.querySelectorAll(".device-checkbox")
    .forEach(cb => cb.checked = master.checked);
}

function escapeInventoryHtml(value) {
  if (value === null || value === undefined) return "";

  if (typeof window.escapeHtml === "function") {
    return window.escapeHtml(String(value));
  }

  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function createSurrenderedPageUrl(page, perPage) {
  const url = new URL(window.location.href);
  url.searchParams.set("section", "surrendered");
  url.searchParams.set("surrendered_page", String(page));
  url.searchParams.set("surrendered_per_page", String(perPage));
  return `${url.pathname}?${url.searchParams.toString()}`;
}

function createSurrenderedPagedApiUrl(page, perPage) {
  const params = new URLSearchParams();
  params.set("page", String(page));
  params.set("per_page", String(perPage));
  return `/manage_inventory/surrendered-pcs-paged?${params.toString()}`;
}

function renderSurrenderedDesktopRows(pcs) {
  const tbody = document.getElementById("surrenderedPcTableBody");
  if (!tbody) return;

  tbody.innerHTML = "";

  if (!pcs.length) {
    tbody.innerHTML = `
      <tr>
        <td colspan="8" class="px-4 py-6 text-center text-gray-500">No surrendered PCs found.</td>
      </tr>
    `;
    return;
  }

  pcs.forEach((pc) => {
    tbody.insertAdjacentHTML(
      "beforeend",
      `
      <tr class="hover:bg-gray-100 transition">
        <td class="px-4 py-2 border-b">${escapeInventoryHtml(pc.pcid)}</td>
        <td class="px-4 py-2 border-b">${escapeInventoryHtml(pc.pcname)}</td>
        <td class="px-4 py-2 border-b">${escapeInventoryHtml(pc.department_name || "--")}</td>
        <td class="px-4 py-2 border-b">${escapeInventoryHtml(pc.location || "--")}</td>
        <td class="px-4 py-2 border-b">${escapeInventoryHtml(pc.accountable || "--")}</td>
        <td class="px-4 py-2 border-b">${escapeInventoryHtml(pc.serial_no || "--")}</td>
        <td class="px-4 py-2 border-b">${escapeInventoryHtml(pc.date_acquired || "--")}</td>
        <td class="px-4 py-2 border-b text-red-600 font-medium">${escapeInventoryHtml(pc.status || "Surrendered")}</td>
      </tr>
      `
    );
  });
}

function renderSurrenderedMobileCards(pcs) {
  const container = document.getElementById("surrenderedPcMobileCards");
  if (!container) return;

  container.innerHTML = "";

  if (!pcs.length) {
    container.innerHTML = '<div class="bg-gray-100 text-gray-600 p-4 rounded-lg text-center">No surrendered PCs found.</div>';
    return;
  }

  pcs.forEach((pc) => {
    container.insertAdjacentHTML(
      "beforeend",
      `
      <div class="bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
        <div class="flex justify-between items-start mb-2">
          <div>
            <h4 class="font-semibold text-gray-900">${escapeInventoryHtml(pc.pcname)}</h4>
            <p class="text-sm text-gray-600">ID: ${escapeInventoryHtml(pc.pcid)}</p>
          </div>
          <span class="px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-600">${escapeInventoryHtml(pc.status || "Surrendered")}</span>
        </div>
        <div class="space-y-1 text-sm text-gray-600">
          <p><span class="font-medium">Department:</span> ${escapeInventoryHtml(pc.department_name || "--")}</p>
          <p><span class="font-medium">Location:</span> ${escapeInventoryHtml(pc.location || "--")}</p>
          <p><span class="font-medium">Accountable:</span> ${escapeInventoryHtml(pc.accountable || "--")}</p>
          <p><span class="font-medium">Serial:</span> ${escapeInventoryHtml(pc.serial_no || "--")}</p>
          <p><span class="font-medium">Date Acquired:</span> ${escapeInventoryHtml(pc.date_acquired || "--")}</p>
        </div>
      </div>
      `
    );
  });
}

function buildSurrenderedPaginationMarkup(currentPage, totalPages) {
  let html = "";

  const navButtonClass = "flex items-center px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 hover:text-red-600 transition-colors";
  const disabledButtonClass = "flex items-center px-3 py-2 text-sm font-medium text-gray-400 bg-gray-100 border border-gray-300 rounded-lg cursor-not-allowed";

  if (currentPage > 1) {
    html += `<button type="button" data-surrendered-page="${currentPage - 1}" onclick="return goToSurrenderedPage(${currentPage - 1}, event)" class="${navButtonClass}"><svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path></svg>Prev</button>`;
  } else {
    html += `<span class="${disabledButtonClass}"><svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path></svg>Prev</span>`;
  }

  if (totalPages > 0) {
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, currentPage + 2);

    if (startPage > 1) {
      html += '<button type="button" data-surrendered-page="1" onclick="return goToSurrenderedPage(1, event)" class="hidden sm:flex items-center justify-center w-10 h-10 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 hover:text-red-600 transition-colors">1</button>';
      if (startPage > 2) {
        html += '<span class="hidden sm:flex items-center justify-center w-10 h-10 text-sm font-medium text-gray-500">...</span>';
      }
    }

    for (let page = startPage; page <= endPage; page++) {
      if (page === currentPage) {
        html += `<span class="flex items-center justify-center w-10 h-10 text-sm font-medium rounded-lg transition-colors z-10 bg-red-600 text-white border border-red-600">${page}</span>`;
      } else {
        html += `<button type="button" data-surrendered-page="${page}" onclick="return goToSurrenderedPage(${page}, event)" class="flex items-center justify-center w-10 h-10 text-sm font-medium rounded-lg transition-colors text-gray-700 bg-white border border-gray-300 hover:bg-gray-50 hover:text-red-600">${page}</button>`;
      }
    }

    if (endPage < totalPages) {
      if (endPage < totalPages - 1) {
        html += '<span class="hidden sm:flex items-center justify-center w-10 h-10 text-sm font-medium text-gray-500">...</span>';
      }
      html += `<button type="button" data-surrendered-page="${totalPages}" onclick="return goToSurrenderedPage(${totalPages}, event)" class="hidden sm:flex items-center justify-center w-10 h-10 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 hover:text-red-600 transition-colors">${totalPages}</button>`;
    }
  }

  if (currentPage < totalPages) {
    html += `<button type="button" data-surrendered-page="${currentPage + 1}" onclick="return goToSurrenderedPage(${currentPage + 1}, event)" class="${navButtonClass}">Next<svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg></button>`;
  } else {
    html += `<span class="${disabledButtonClass}">Next<svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg></span>`;
  }

  return html;
}

function updateSurrenderedPaginationSummary(page, perPage, totalItems) {
  const summary = document.getElementById("surrenderedPaginationSummary");
  if (!summary) return;

  const start = totalItems > 0 ? (page - 1) * perPage + 1 : 0;
  const end = totalItems > 0 ? Math.min(page * perPage, totalItems) : 0;

  summary.innerHTML = `Showing <span class="font-medium">${start}</span> - <span class="font-medium">${end}</span> of <span class="font-medium">${totalItems}</span> records`;
}

function updateSurrenderedPageSummary(page, totalPages, totalItems) {
  const pageSummary = document.getElementById("surrenderedPageSummary");
  if (!pageSummary) return;

  pageSummary.textContent = `Showing page ${page} of ${totalPages} (${totalItems} total surrendered)`;
}

function applySurrenderedPaginationState(page, perPage, totalItems, totalPages) {
  const nav = document.getElementById("surrenderedPaginationNav");
  const perPageSelect = document.getElementById("surrenderedPerPageSelect");
  const pageInput = document.getElementById("surrenderedPageInput");

  if (nav) {
    nav.dataset.page = String(page);
    nav.dataset.perPage = String(perPage);
    nav.dataset.totalPages = String(totalPages);
    nav.dataset.totalItems = String(totalItems);
    nav.innerHTML = buildSurrenderedPaginationMarkup(page, totalPages);
  }

  if (perPageSelect) {
    perPageSelect.value = String(perPage);
  }

  if (pageInput) {
    pageInput.value = String(page);
  }

  updateSurrenderedPaginationSummary(page, perPage, totalItems);
  updateSurrenderedPageSummary(page, totalPages, totalItems);
}

async function loadSurrenderedPageAjax(page, perPage, updateUrl = true) {
  try {
    const response = await fetch(createSurrenderedPagedApiUrl(page, perPage));
    if (!response.ok) {
      throw new Error(`Failed to load surrendered page: ${response.status}`);
    }

    const data = await response.json();
    const pcs = Array.isArray(data.pcs) ? data.pcs : [];
    const currentPage = Number(data.page) || 1;
    const currentPerPage = Number(data.per_page) || perPage;
    const totalItems = Number(data.total_items) || 0;
    const totalPages = Number(data.total_pages) || 0;

    renderSurrenderedDesktopRows(pcs);
    renderSurrenderedMobileCards(pcs);
    applySurrenderedPaginationState(currentPage, currentPerPage, totalItems, totalPages);

    if (window.lucide) {
      lucide.createIcons();
    }

    if (updateUrl) {
      window.history.replaceState({}, "", createSurrenderedPageUrl(currentPage, currentPerPage));
    }
  } catch (error) {
    console.error(error);
    if (typeof showToast === "function") {
      showToast("Failed to load surrendered page. Please try again.", "error");
    }
  }
}

window.goToSurrenderedPage = function (page, event) {
  if (event) {
    event.preventDefault();
    event.stopPropagation();
  }

  const targetPage = Number(page);
  if (!targetPage) return false;

  const nav = document.getElementById("surrenderedPaginationNav");
  const perPageSelect = document.getElementById("surrenderedPerPageSelect");
  const perPage = Number(perPageSelect && perPageSelect.value)
    || Number(nav && nav.dataset.perPage)
    || 10;

  loadSurrenderedPageAjax(targetPage, perPage, true);
  return false;
};

function initSurrenderedAjaxPagination() {
  if (window.__surrenderedPaginationInitialized) {
    return;
  }

  const nav = document.getElementById("surrenderedPaginationNav");
  const perPageSelect = document.getElementById("surrenderedPerPageSelect");
  const perPageForm = document.getElementById("surrenderedPerPageForm");
  const tableBody = document.getElementById("surrenderedPcTableBody");

  if (!nav || !perPageSelect || !perPageForm || !tableBody) {
    return;
  }

  window.__surrenderedPaginationInitialized = true;

  nav.addEventListener("click", (event) => {
    const pageButton = event.target && event.target.closest
      ? event.target.closest("[data-surrendered-page]")
      : null;

    if (!pageButton || !nav.contains(pageButton)) {
      return;
    }

    const page = Number(pageButton.getAttribute("data-surrendered-page"));
    if (!page) {
      return;
    }

    event.preventDefault();
    event.stopPropagation();
    window.goToSurrenderedPage(page, event);
  });

  perPageForm.addEventListener("submit", (event) => {
    event.preventDefault();
  });

  perPageSelect.addEventListener("change", () => {
    const perPage = Number(perPageSelect.value) || 10;
    loadSurrenderedPageAjax(1, perPage, true);
  });

  window.addEventListener("popstate", () => {
    const url = new URL(window.location.href);
    const section = url.searchParams.get("section");
    if (section !== "surrendered") return;

    const page = Number(url.searchParams.get("surrendered_page")) || 1;
    const perPage = Number(url.searchParams.get("surrendered_per_page")) || Number(perPageSelect.value) || 10;
    loadSurrenderedPageAjax(page, perPage, false);
  });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initSurrenderedAjaxPagination);
} else {
  initSurrenderedAjaxPagination();
}