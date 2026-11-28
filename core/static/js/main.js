// Date helpers: block past dates and keep check-out after check-in
(function () {
  // Local date (not UTC) so "today" is correct in every timezone
  function localISO(d) {
    return new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().split('T')[0];
  }

  // Price calculation on the room detail page (global: api.js calls it after loading a room)
  window.updatePrice = function updatePrice() {
    const card = document.getElementById('priceCard');
    if (!card) return;
    const inEl = card.querySelector('.js-checkin');
    const outEl = card.querySelector('.js-checkout');
    const nightsEl = document.getElementById('nightsCount');
    const totalEl = document.getElementById('totalPrice');
    if (!inEl || !outEl || !nightsEl || !totalEl) return;

    let nights = 0;
    if (inEl.value && outEl.value) {
      nights = Math.max(0, Math.round((new Date(outEl.value) - new Date(inEl.value)) / 86400000));
    }
    const price = Number(card.dataset.price) || 0;
    nightsEl.textContent = nights;
    totalEl.textContent = '$' + (nights * price).toLocaleString('en-US');
  };

  function init() {
    const today = localISO(new Date());

    document.querySelectorAll('.js-checkin').forEach(checkIn => {
      const form = checkIn.closest('form');
      const checkOut = form && form.querySelector('.js-checkout');
      if (!checkOut) return;
      checkIn.min = today;
      checkOut.min = checkIn.value || today;

      checkIn.addEventListener('change', () => {
        checkOut.min = checkIn.value || today;
        if (checkOut.value && checkOut.value <= checkIn.value) checkOut.value = '';
        window.updatePrice();
      });
      checkOut.addEventListener('change', window.updatePrice);
    });

    window.updatePrice();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
