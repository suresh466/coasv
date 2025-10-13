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
document.getElementById("interest-type")?.addEventListener("change", e => onInterestTypeChange(e))
document.getElementById("interest-amount")?.addEventListener("input", e => onInterestAmountInput(e))
document.getElementById("principal-amount")?.addEventListener("input", e => onPrincipalAmountInput(e))

async function onInterestTypeChange(e) {
  const amountContainer = document.getElementById("amount-container")
  const amountInput = document.getElementById('interest-amount')

  // custom calculation
  if (e.target.value === "custom") {
    if (amountContainer.classList.contains("hidden")) amountContainer.classList.remove("hidden")
    amountInput.required = true;
    if (amountInput) {
      const params = new URLSearchParams();
      params.append('interest-type', e.target.value);
      params.append('amount', amountInput.value);
      url = `calculate-interest?${params.toString()}`
      const response = await fetch(url)
      const calculatedInterest = await response.json()
      displayCalculatedInterest(calculatedInterest)
    }
    else {
      displayCalculatedInterest()
    }
  }
  // regular and to-date interest calculation
  else {
    if (!amountContainer.classList.contains("hidden")) amountContainer.classList.add("hidden")
    amountInput.required = false;
    const response = await fetch(`calculate-interest?interest-type=${e.target.value}`)
    const calculatedInterest = await response.json()
    displayCalculatedInterest(calculatedInterest)
  }
}

async function onInterestAmountInput(e) {
  const amount = e.target.value

  const interestType = document.querySelector('input[name="interest-type"]:checked')?.value;
  const params = new URLSearchParams();
  params.append('interest-type', interestType);
  params.append('amount', amount);
  const response = await fetch(`calculate-interest?${params.toString()}`)
  const calculatedInterest = await response.json()
  displayCalculatedInterest(calculatedInterest)
}

function onPrincipalAmountInput(e) {
  amount = e.target.value
  document.getElementById('principal-amount-col').innerText = amount

}

function displayCalculatedInterest(calculatedInterest = null) {
  const totalCol = document.getElementById("total-col")
  const perioidStartCol = document.getElementById("period-start-col")
  const periodEndCol = document.getElementById("period-end-col")
  const daysCol = document.getElementById("days-col")

  if (calculatedInterest) {
    totalCol.innerText = calculatedInterest.total
    perioidStartCol.innerText = calculatedInterest.period_start
    periodEndCol.innerText = calculatedInterest.period_end
    daysCol.innerText = calculatedInterest.days
  }
  else {
    totalCol.innerText = ""
    perioidStartCol.innerText = ""
    periodEndCol.innerText = ""
    daysCol.innerText = ''
  }
}
