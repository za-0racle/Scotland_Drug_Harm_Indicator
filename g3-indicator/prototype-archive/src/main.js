// Archived prototype entry point. Reads the frozen quarterly input table exported to public/data.
// Charts and the alert overlay are added once the indicator outputs are frozen.
const status = document.getElementById('status');

async function loadQuarterly() {
  try {
    const res = await fetch('/data/quarterly_input_table.json');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const rows = await res.json();
    status.textContent = `Loaded ${rows.length} quarters (2017 Q1 to 2025 Q4).`;
    return rows;
  } catch (err) {
    status.textContent = `Data not yet exported to public/data (${err.message}).`;
    return null;
  }
}

loadQuarterly();
