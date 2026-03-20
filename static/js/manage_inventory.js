window.currentSection = "pc";

function showSection(id) {

  document.querySelectorAll("section").forEach(sec =>
    sec.classList.add("hidden")
  );

  const target = document.getElementById(id);
  if (target) target.classList.remove("hidden");

  if (id === "inventorySection") {
    window.currentSection = "pc";
  }
  else if (id === "itemsSection") {
    window.currentSection = "item";
  }
  else if (id === "consumablesSection") {
    window.currentSection = "consumable";
  }
  else if (id === "surrenderedSection") {
    window.currentSection = "surrendered";
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

let sectionId = "inventorySection";
let buttonId = "inventoryBtn";

if (uiSection === "item") {
  sectionId = "itemsSection";
  buttonId = "itemsBtn";
}
else if (uiSection === "consumable") {
  sectionId = "consumablesSection";
  buttonId = "consumablesBtn";
}
else if (uiSection === "surrendered") {
  sectionId = "surrenderedSection";
  buttonId = "surrenderedBtn";
}

showSection(sectionId);

const btn = document.getElementById(buttonId);
if (btn) setActiveNav(btn);

  if (window.lucide) {
    lucide.createIcons();
  }

});

function toggleSelectAllDevices(master) {
  document.querySelectorAll(".device-checkbox")
    .forEach(cb => cb.checked = master.checked);
}