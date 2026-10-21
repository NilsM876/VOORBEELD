const form = document.querySelector('#portfolio-form');
const stocks = document.querySelector('#stocks');
const prototype = stocks.firstElementChild.cloneNode(true);
let timer;
let pending;
function updateWeights() {
  const weights = [...stocks.querySelectorAll('[name="weight"]')];
  const total = weights.reduce((sum, input) => sum + Number(input.value), 0);
  const valid = weights.length > 0 && Math.abs(total - 100) <= 0.000001;
  document.querySelector('#weight-total').textContent = `Totaal gewicht: ${total.toFixed(2)}%${valid ? '' : ' — moet 100% zijn'}`;
  form.querySelectorAll('button[name="action"]').forEach(button => button.disabled = !valid);
  return valid;
}
function changed() {
  clearTimeout(timer);
  if (pending) pending.abort();
  const result = document.querySelector('#result');
  result.replaceChildren();
  if (!updateWeights() || !form.checkValidity()) return;
  timer = setTimeout(async () => {
    const controller = new AbortController();
    pending = controller;
    const data = new FormData(form);
    data.set('action', 'calculate');
    try {
      const response = await fetch(form.action, {method: 'POST', body: data, signal: controller.signal});
      const page = new DOMParser().parseFromString(await response.text(), 'text/html');
      if (controller.signal.aborted) return;
      const content = response.ok ? page.querySelector('#result') : page.querySelector('[role="alert"]');
      if (content) result.replaceChildren(...(response.ok ? [...content.childNodes] : [content]));
      else result.textContent = 'Berekenen mislukt. Probeer de knop Berekenen.';
    } catch (error) {
      if (error.name !== 'AbortError') result.textContent = 'Automatisch berekenen mislukt. Probeer de knop Berekenen.';
    }
  }, 350);
}
document.querySelector('#add-stock').addEventListener('click', () => {
  const row = prototype.cloneNode(true);
  row.querySelectorAll('input').forEach(input => input.value = '');
  stocks.append(row);
  row.querySelector('input').focus();
  changed();
});
stocks.addEventListener('click', event => {
  if (event.target.classList.contains('remove')) {
    event.target.closest('.stock').remove();
    changed();
  }
});
form.addEventListener('input', changed);
form.addEventListener('submit', () => {
  clearTimeout(timer);
  if (pending) pending.abort();
});
updateWeights();
