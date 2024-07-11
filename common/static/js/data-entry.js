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
