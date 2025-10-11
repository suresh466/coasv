// transaction list
//
function toggleTransaction(transactionId) {
  var detailsDiv = document.getElementById("transaction-" + transactionId);
  var chevron = document.getElementById("chevron-" + transactionId);
  if (detailsDiv.classList.contains("hidden")) {
    detailsDiv.classList.remove("hidden");
    chevron.classList.add("rotate-180");
  } else {
    detailsDiv.classList.add("hidden");
    chevron.classList.remove("rotate-180");
  }
}

// payments
//
document.getElementById("interest-type")?.addEventListener("change", e => handleInterestTypeChange(e))
document.getElementById("amount")?.addEventListener("input", e => handleAmountChange(e))

async function handleInterestTypeChange(e) {
  const amountContainer = document.getElementById("amount-container")
  const total = document.getElementById("total-col")

  // custom calculation
  if (e.target.value === "custom") {
    if (amountContainer.classList.contains("hidden")) amountContainer.classList.remove("hidden")
    const amount = document.getElementById("amount").value
    if (amount) {
      const params = new URLSearchParams();
      params.append('interest-type', e.target.value);
      params.append('amount', amount);
      const response = await fetch(`calculate-interest?${params.toString()}`)
      const calculatedInterest = await response.json()
      total.innerText = calculatedInterest.total

    }
    else total.innerText = ""
  }
  // regular and to-date interest calculation
  else {
    if (!amountContainer.classList.contains("hidden")) amountContainer.classList.add("hidden")
    const response = await fetch(`calculate-interest?interest-type=${e.target.value}`)
    const calculatedInterest = await response.json()
    total.innerText = calculatedInterest.total
  }
}

async function handleAmountChange(e) {
  const totalCol = document.getElementById("total-col")
  const amount = e.target.value

  const interestType = document.querySelector('input[name="interest-type"]:checked')?.value;
  const params = new URLSearchParams();
  params.append('interest-type', interestType);
  params.append('amount', amount);
  const response = await fetch(`calculate-interest?${params.toString()}`)
  const calculatedInterest = await response.json()
  totalCol.innerText = calculatedInterest.total
}
