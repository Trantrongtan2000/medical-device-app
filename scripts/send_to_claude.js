const p = "Review FastAPI routes: routes_schedules.py, routes_inspections.py, routes_repairs.py, routes_transfers.py. Find SQL injection, Pydantic v2 Optional bugs, Transaction issues. Return JSON array.";
const ta = document.querySelector("textarea[data-testid]");
ta.focus();
ta.value = p;
ta.dispatchEvent(new Event("input", {bubbles: true}));
"sent";