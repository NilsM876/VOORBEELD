// Aandelenrijen toevoegen en verwijderen, het totaalbedrag tonen en het
// resultaat automatisch herberekenen terwijl de gebruiker typt.
// Alle berekeningen gebeuren in Python; dit script vraagt het resultaat op.
const form = document.querySelector('#portfolio-form');
const stockList = document.querySelector('#stocks');
const result = document.querySelector('#result');

// Een lege kopie van de eerste rij, om nieuwe rijen van te maken.
const emptyRow = stockList.firstElementChild.cloneNode(true);
emptyRow.querySelectorAll('input').forEach(input => input.value = '');

let timer;
let lastRequest = 0;

function showTotal() {
  let total = 0;
  stockList.querySelectorAll('[name="amount"]').forEach(input => total += Number(input.value));
  const valid = total > 0;
  document.querySelector('#amount-total').textContent =
    'Totaal bedrag: €' + total.toFixed(2) + (valid ? '' : ' (moet groter dan 0 zijn)');
  form.querySelectorAll('button[name="action"]').forEach(button => button.disabled = !valid);
  return valid;
}

function recalculate() {
  clearTimeout(timer);
  lastRequest++;  // een antwoord op een oudere aanvraag wordt zo genegeerd
  result.replaceChildren();
  if (!showTotal() || !form.checkValidity()) return;

  // Wacht 0,35 seconde na de laatste toetsaanslag en stuur dan het formulier.
  timer = setTimeout(async () => {
    const requestNumber = lastRequest;
    const data = new FormData(form);
    data.set('action', 'calculate');
    try {
      const response = await fetch(form.action, {method: 'POST', body: data});
      const page = new DOMParser().parseFromString(await response.text(), 'text/html');
      if (requestNumber !== lastRequest) return;
      // Neem uit de teruggestuurde pagina het resultaat, of de foutmelding.
      if (response.ok) {
        result.innerHTML = page.querySelector('#result').innerHTML;
      } else {
        result.innerHTML = page.querySelector('[role="alert"]').outerHTML;
      }
    } catch (error) {
      result.textContent = 'Automatisch berekenen mislukt. Gebruik de knop Berekenen.';
    }
  }, 350);
}

document.querySelector('#add-stock').addEventListener('click', () => {
  const row = emptyRow.cloneNode(true);
  stockList.append(row);
  row.querySelector('input').focus();
  recalculate();
});

stockList.addEventListener('click', event => {
  if (event.target.classList.contains('remove')) {
    event.target.closest('.stock').remove();
    recalculate();
  }
});

form.addEventListener('input', recalculate);
form.addEventListener('submit', () => {
  clearTimeout(timer);
  lastRequest++;
});
showTotal();
