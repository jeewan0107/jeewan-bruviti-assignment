const $ = (id) => document.getElementById(id);
const numeric = (id) => {
  const raw = $(id).value.trim();
  return raw === "" ? null : Number(raw);
};
function buildRequest() {
  return {
    case_id: $("case_id").value,
    product_category: $("product_category").value,
    product_age_months: numeric("product_age_months"),
    purchase_price: numeric("purchase_price"),
    replacement_price: numeric("replacement_price"),
    warranty_status: $("warranty_status").value,
    fault_category: $("fault_category").value,
    parts: [{
      sku: $("part_sku").value,
      description: $("part_description").value,
      price: numeric("part_price"),
      lead_time_days: numeric("lead_time_days")
    }],
    labour_hours: numeric("labour_hours"),
    labour_rate_per_hour: numeric("labour_rate_per_hour"),
    technician_travel_minutes: numeric("technician_travel_minutes"),
    prior_repairs_12m: numeric("prior_repairs_12m"),
    customer_sentiment: $("customer_sentiment").value,
    symptom_text: $("symptom_text").value
  };
}
$("loadExample").addEventListener("click", () => {
  $("case_id").value = "C-2001";
  $("product_category").value = "washing_machine";
  $("product_age_months").value = 30;
  $("purchase_price").value = 38000;
  $("replacement_price").value = 36000;
  $("warranty_status").value = "out_of_warranty";
  $("fault_category").value = "motor_or_drive";
  $("part_sku").value = "WM-MTR-114";
  $("part_description").value = "Drive motor";
  $("part_price").value = 6200;
  $("lead_time_days").value = 4;
  $("labour_hours").value = 1.5;
  $("labour_rate_per_hour").value = 900;
  $("technician_travel_minutes").value = 40;
  $("prior_repairs_12m").value = 0;
  $("customer_sentiment").value = "neutral";
  $("symptom_text").value = "drum does not turn, motor hums";
  $("error").textContent = "";
});
$("showJson").addEventListener("click", () => {
  $("requestPreview").textContent = JSON.stringify(buildRequest(), null, 2);
  $("requestPreview").classList.toggle("hidden");
});
$("caseForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  $("error").textContent = "";
  const request = buildRequest();
  try {
    const response = await fetch("/decide", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request)
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail ? JSON.stringify(data.detail) : `HTTP ${response.status}`);
    }
    $("resultPanel").classList.remove("hidden");
    $("resultSummary").innerHTML = `
      <div class="result-card">
        <div class="decision">${escapeHtml(data.decision)}</div>
        <p>${escapeHtml(data.reason)}</p>
        <p><strong>Estimated repair cost:</strong> ${data.estimated_repair_cost === null ? "Unavailable" : data.estimated_repair_cost.toLocaleString(undefined, {style:"currency", currency:"INR"})}</p>
        <p><strong>Confidence:</strong> ${data.confidence}</p>
        <p class="metric">Case ID: ${escapeHtml(data.case_id)}</p>
      </div>`;
    $("responseJson").textContent = JSON.stringify(data, null, 2);
    $("resultPanel").scrollIntoView({behavior:"smooth", block:"start"});
  } catch (err) {
    $("error").textContent = `Could not process case: ${err.message}. Confirm the API is running and input values are valid.`;
  }
});
function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (ch) => ({
    "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;"
  }[ch]));
}
