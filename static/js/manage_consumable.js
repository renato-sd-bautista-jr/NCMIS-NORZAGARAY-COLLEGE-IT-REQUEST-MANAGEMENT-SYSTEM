async function openConsumableModalById(id) {
  try {
    const res = await fetch(`/manage_consumable/get-consumable-by-id/${id}`);
    if (!res.ok) throw new Error();
    const item = await res.json();
    openConsumableModal(item);
  } catch {
    alert("Failed to load consumable data.");
  }
}

 

window.openConsumableModalById = async function (id) {
  try {
    const res = await fetch(`/manage_consumable/get-consumable-by-id/${id}`);
    const item = await res.json();
    openConsumableModal(item);
  } catch {
    alert("Failed to load consumable data.");
  }
};
