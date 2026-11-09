// Date helpers: block past dates and keep check-out after check-in
const today = new Date().toISOString().split('T')[0];

document.querySelectorAll('.js-checkin').forEach(checkIn => {
  const form = checkIn.closest('form');
  const checkOut = form.querySelector('.js-checkout');
  checkIn.min = today;
  checkOut.min = checkIn.value || today;

  checkIn.addEventListener('change', () => {
    checkOut.min = checkIn.value;
    if (checkOut.value && checkOut.value <= checkIn.value) checkOut.value = '';
    updatePrice();
  });
  checkOut.addEventListener('change', updatePrice);
});

// Price calculation on the room detail page
function updatePrice() {
  const card = document.getElementById('priceCard');
  if (!card) return;
  const inVal = card.querySelector('.js-checkin').value;
  const outVal = card.querySelector('.js-checkout').value;
  let nights = 0;
  if (inVal && outVal) {
    nights = Math.max(0, Math.round((new Date(outVal) - new Date(inVal)) / 86400000));
  }
  document.getElementById('nightsCount').textContent = nights;
  document.getElementById('totalPrice').textContent = '$' + nights * Number(card.dataset.price);
}
updatePrice();
