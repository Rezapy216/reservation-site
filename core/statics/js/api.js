/**
 * api.js — jQuery client for the reservation-site REST API (branch: feature/api)
 *
 * Load AFTER jQuery and BEFORE/AFTER main.js (in base.html):
 *   <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
 *   <script src="{% static 'js/api.js' %}"></script>
 *
 * Endpoints used (all relative to the site origin):
 *   POST   /accounts/api/v1/jwt/create/        { phone, password } -> { access, refresh, phone, user }
 *   POST   /accounts/api/v1/jwt/refresh/       { refresh }         -> { access }
 *   POST   /accounts/api/v1/registration/      { phone, name, password, confirm_password }
 *   GET    /accounts/api/v1/profile/
 *   GET    /api/v1/room/                       ?page= &search= &ordering= &permitted_guests= &amenities= &owner=
 *   GET    /api/v1/room/{id}/
 *   GET    /bookings/api/v1/booking/           ?guest= &room= &min_total_price= ...
 *   PATCH  /bookings/api/v1/booking/{id}/      { status }  (superuser only, currently)
 *
 * Page hooks (put these ids / classes in your templates; each block runs only if its element exists):
 *   #popularRooms        home.html          -> latest rooms as small cards
 *   #roomsList           room_list.html     -> room cards (_room_card layout)
 *   #roomsCount          room_list.html     -> "N rooms found"
 *   #roomsPagination     room_list.html     -> pagination <ul>
 *   #filterForm          room_list.html     -> filter form (inputs: search, guests, ordering)
 *   #roomDetail          room_detail.html   -> wrapper, needs data-room-id="{{ room.pk }}"
 *       .js-room-name  .js-room-owner  .js-room-price  .js-room-capacity  .js-room-amenities  .js-room-pictures
 *   #bookingForm         booking_form.html  -> data-room-id, inputs date_in / date_out / number_of_people
 *   #myBookings          my_bookings.html   -> booking cards
 *   #loginForm           login.html         -> inputs phone / password
 *   #registerForm        register.html      -> inputs phone / name / password / confirm_password
 *   #apiMessages         (optional)         -> where errors/alerts are written
 *   .js-logout           (optional)         -> logout button/link
 */
(function ($) {
  'use strict';

  // ---------------------------------------------------------------- config
  var API = {
    login:    '/accounts/api/v1/jwt/create/',
    refresh:  '/accounts/api/v1/jwt/refresh/',
    register: '/accounts/api/v1/registration/',
    profile:  '/accounts/api/v1/profile/',
    rooms:    '/api/v1/room/',
    bookings: '/bookings/api/v1/booking/'
  };
  var PAGES = {
    login:      '/accounts/login/',
    roomDetail: function (id) { return '/room-detail/' + id + '/'; },
    home:       '/'
  };
  var CURRENCY = '$';
  var KEY = { access: 'rs_access', refresh: 'rs_refresh', user: 'rs_user' };

  // ---------------------------------------------------------------- helpers
  function esc(v) {
    return $('<div>').text(v == null ? '' : String(v)).html();
  }

  function money(v) {
    var n = Number(v);
    return CURRENCY + (isNaN(n) ? esc(v) : n.toLocaleString());
  }

  function alertBox(type, text) {
    var $box = $('#apiMessages');
    if (!$box.length) { window.alert(text); return; }
    $box.html(
      '<div class="alert alert-' + type + ' alert-dismissible fade show">' +
      esc(text) +
      '<button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>'
    );
  }

  // Flatten DRF error bodies ({field:[msgs]}, {detail:..}, [..]) to one string
  function errorText(xhr) {
    var d = xhr && xhr.responseJSON;
    if (!d) return xhr && xhr.status === 0 ? 'Server is not reachable.' : 'Unexpected error.';
    if (typeof d === 'string') return d;
    if (d.detail) return d.detail;
    var out = [];
    $.each(d, function (k, v) {
      var msg = $.isArray(v) ? v.join(' ') : (typeof v === 'object' ? JSON.stringify(v) : v);
      out.push(k === 'non_field_errors' || k === 'detail' || k === 'details' ? msg : k + ': ' + msg);
    });
    return out.join(' | ') || 'Unexpected error.';
  }

  function getParam(name) {
    return new URLSearchParams(window.location.search).get(name);
  }

  // ---------------------------------------------------------------- auth
  var Auth = {
    access:  function () { return localStorage.getItem(KEY.access); },
    refresh: function () { return localStorage.getItem(KEY.refresh); },
    user:    function () {
      try { return JSON.parse(localStorage.getItem(KEY.user)); } catch (e) { return null; }
    },
    isLoggedIn: function () { return !!Auth.access(); },
    save: function (data) {
      localStorage.setItem(KEY.access, data.access);
      if (data.refresh) localStorage.setItem(KEY.refresh, data.refresh);
      if (data.user !== undefined) {
        localStorage.setItem(KEY.user, JSON.stringify({ id: data.user, phone: data.phone }));
      }
    },
    clear: function () {
      $.each(KEY, function (_, k) { localStorage.removeItem(k); });
    },
    logout: function () {
      Auth.clear();
      window.location.href = PAGES.login;
    }
  };

  // Attach "Authorization: Bearer <access>" to every API call
  $.ajaxSetup({
    beforeSend: function (xhr, settings) {
      var token = Auth.access();
      if (token && settings.url.indexOf('/jwt/') === -1 && settings.url.indexOf('/registration/') === -1) {
        xhr.setRequestHeader('Authorization', 'Bearer ' + token);
      }
    }
  });

  /**
   * Wrapper around $.ajax: sends/receives JSON, and on a 401 tries ONE token refresh
   * then replays the request. If refresh fails -> user goes to the login page.
   */
  function request(opts, _retried) {
    var dfd = $.Deferred();
    var cfg = $.extend({ dataType: 'json' }, opts);
    if (cfg.data && typeof cfg.data === 'object' && /^(POST|PUT|PATCH)$/i.test(cfg.method || cfg.type || '')) {
      cfg.contentType = 'application/json';
      cfg.data = JSON.stringify(cfg.data);
    }
    $.ajax(cfg).done(function (data) {
      dfd.resolve(data);
    }).fail(function (xhr) {
      var canRefresh = xhr.status === 401 && !_retried && Auth.refresh() &&
                       cfg.url.indexOf('/jwt/') === -1;
      if (canRefresh) {
        $.ajax({
          url: API.refresh, method: 'POST', contentType: 'application/json',
          data: JSON.stringify({ refresh: Auth.refresh() }), dataType: 'json'
        }).done(function (r) {
          Auth.save({ access: r.access, refresh: r.refresh });
          request(opts, true).then(dfd.resolve, dfd.reject);
        }).fail(function () {
          Auth.clear();
          dfd.reject(xhr);
        });
      } else {
        dfd.reject(xhr);
      }
    });
    return dfd.promise();
  }

  function requireLogin() {
    if (!Auth.isLoggedIn()) {
      window.location.href = PAGES.login + '?next=' + encodeURIComponent(window.location.pathname);
      return false;
    }
    return true;
  }

  // 401/403 on a data page -> friendly message
  function handleFail(xhr) {
    if (xhr.status === 401) {
      alertBox('warning', 'Please log in first.');
      setTimeout(function () {
        window.location.href = PAGES.login + '?next=' + encodeURIComponent(window.location.pathname);
      }, 800);
    } else if (xhr.status === 403) {
      alertBox('danger', 'You do not have permission to do this.');
    } else {
      alertBox('danger', errorText(xhr));
    }
  }

  // ---------------------------------------------------------------- templates (JS versions of your Django templates)

  // images: API doesn't return pictures yet -> uses room.pictures if you add it to the serializer
  function picturesHtml(room, onlyFirst) {
    var pics = $.grep(room.pictures || [], function (p) { return p && (p.image || typeof p === 'string'); });
    if (!pics.length) return '<div class="room-thumb placeholder-img"><i class="bi bi-image"></i></div>';
    if (onlyFirst) pics = pics.slice(0, 1);
    return $.map(pics, function (p) {
      var src = typeof p === 'string' ? p : p.image;
      return '<img src="' + esc(src) + '" class="room-slide-img" alt="' + esc(room.name) + '">';
    }).join('');
  }

  // templates/rooms/_room_card.html
  function roomCard(room) {
    var detail = PAGES.roomDetail(room.id);
    var ci = getParam('check_in'), co = getParam('check_out');
    var qs = ci ? '?check_in=' + encodeURIComponent(ci) + '&check_out=' + encodeURIComponent(co || '') : '';
    var amenities = $.map(room.amenities || [], function (a) {
      return '<span class="badge text-bg-light border me-1">' + esc(a.name) + '</span>';
    }).join('');
    return '' +
    '<div class="card room-card mb-3"><div class="row g-0">' +
      '<div class="col-md-4">' + picturesHtml(room, true) + '</div>' +
      '<div class="col-md-5 p-3">' +
        '<h5 class="mb-1"><a class="text-decoration-none" href="' + detail + '">' + esc(room.name) + '</a></h5>' +
        '<div class="small text-muted mb-2"><i class="bi bi-people"></i> Up to ' + esc(room.permitted_guests) +
          ' guests · <i class="bi bi-person"></i> ' + esc(room.owner_name) + '</div>' +
        '<div>' + amenities + '</div>' +
      '</div>' +
      '<div class="col-md-3 p-3 border-start d-flex flex-column justify-content-between text-md-end">' +
        '<div></div>' +
        '<div>' +
          '<div class="small text-muted">per night</div>' +
          '<div class="price">' + money(room.pay_per_night) + '</div>' +
          '<a href="' + detail + qs + '" class="btn btn-primary btn-sm mt-2">See availability</a>' +
        '</div>' +
      '</div>' +
    '</div></div>';
  }

  // templates/rooms/home.html  ("Popular rooms" block)
  function roomMini(room) {
    return '' +
    '<div class="col-md-6 col-lg-3">' +
      '<a href="' + PAGES.roomDetail(room.id) + '" class="text-decoration-none text-dark">' +
        picturesHtml(room, true) +
        '<p>' + esc(room.name) + '</p><p>------</p>' +
        '<p>' + money(room.pay_per_night) + ' per night</p>' +
      '</a>' +
    '</div>';
  }

  // templates/bookings/my_bookings.html
  var STATUS_BADGE = {
    confirmed: '<span class="badge text-bg-success">Confirmed</span>',
    cancelled: '<span class="badge text-bg-secondary">Cancelled</span>',
    expired:   '<span class="badge text-bg-dark">Expired</span>',
    pending:   '<span class="badge text-bg-warning">Pending</span>'
  };
  function bookingCard(b) {
    var cancel = (b.status === 'pending' || b.status === 'confirmed')
      ? '<button class="btn btn-sm btn-outline-danger ms-2 js-cancel-booking" data-id="' + b.id + '">Cancel</button>'
      : '';
    return '' +
    '<div class="card mb-3"><div class="card-body d-md-flex justify-content-between align-items-center">' +
      '<div>' +
        '<h6 class="mb-1">Room #' + esc(b.room) + '</h6>' +
        '<div class="small text-muted">' + esc(b.date_in) + ' → ' + esc(b.date_out) + ' · Booking #' + esc(b.id) +
          ' · ' + esc(b.number_of_people) + ' guest(s)</div>' +
        '<div class="small text-muted">Host phone: ' + esc(b.owner_phone_number) + '</div>' +
        '<div class="fw-bold mt-1">' + money(b.total_price) + '</div>' +
      '</div>' +
      '<div class="text-md-end mt-2 mt-md-0">' + (STATUS_BADGE[b.status] || esc(b.status)) + cancel + '</div>' +
    '</div></div>';
  }

  // ---------------------------------------------------------------- API calls
  var Rooms = {
    list: function (params) { return request({ url: API.rooms, data: params || {} }); },
    get:  function (id)     { return request({ url: API.rooms + id + '/' }); }
  };

  var Bookings = {
    list:   function (params) { return request({ url: API.bookings, data: params || {} }); },
    cancel: function (id)     { return request({ url: API.bookings + id + '/', method: 'PATCH', data: { status: 'cancelled' } }); },
    // NOTE: the backend has no create endpoint yet (BookingModelViewSet has no CreateModelMixin).
    create: function (data)   { return request({ url: API.bookings, method: 'POST', data: data }); }
  };

  // ---------------------------------------------------------------- pages
  function renderPagination($ul, data, current, onPage) {
    $ul.empty();
    if (!data.total_pages || data.total_pages < 2) return;
    function item(label, page, disabled, active) {
      return $('<li class="page-item">')
        .toggleClass('disabled', !!disabled).toggleClass('active', !!active)
        .append($('<a class="page-link" href="#">').text(label).data('page', page));
    }
    $ul.append(item('Previous', current - 1, !data.links.previous));
    for (var p = 1; p <= data.total_pages; p++) $ul.append(item(p, p, false, p === current));
    $ul.append(item('Next', current + 1, !data.links.next));
    $ul.off('click').on('click', 'a.page-link', function (e) {
      e.preventDefault();
      if ($(this).parent().hasClass('disabled')) return;
      onPage($(this).data('page'));
    });
  }

  // home.html — popular rooms
  function initHome() {
    var $box = $('#popularRooms');
    if (!$box.length) return;
    $box.html('<p class="text-muted">Loading...</p>');
    Rooms.list({ ordering: '-created_date' }).done(function (data) {
      var rooms = (data.results || []).slice(0, 4);
      $box.html(rooms.length
        ? $.map(rooms, roomMini).join('')
        : '<p class="text-muted">No rooms yet. Add some from the admin panel.</p>');
    }).fail(function (xhr) {
      $box.empty(); handleFail(xhr);
    });
  }

  // room_list.html — list + filter + search + sort + pagination
  function initRoomList() {
    var $list = $('#roomsList');
    if (!$list.length) return;
    var $form = $('#filterForm');
    var state = { page: 1 };

    function params() {
      var p = { page: state.page };
      var g = $form.find('[name=guests]').val() || getParam('guests');
      var s = $form.find('[name=search]').val();
      var o = $form.find('[name=ordering]').val();
      if (g) p.permitted_guests = g;
      if (s) p.search = s;
      if (o) p.ordering = o;               // pay_per_night | -pay_per_night | permitted_guests | created_date
      var am = $form.find('[name=amenities]:checked').map(function () { return this.value; }).get();
      if (am.length === 1) p.amenities = am[0];
      return p;
    }

    function load() {
      $list.html('<p class="text-muted">Loading...</p>');
      Rooms.list(params()).done(function (data) {
        var rooms = data.results || [];
        // max_price isn't supported by the API filter -> filtered client side
        var max = parseFloat($form.find('[name=max_price]').val());
        if (!isNaN(max)) rooms = $.grep(rooms, function (r) { return parseFloat(r.pay_per_night) <= max; });
        $('#roomsCount').text(data.total_objects + ' room' + (data.total_objects === 1 ? '' : 's') + ' found');
        $list.html(rooms.length
          ? $.map(rooms, roomCard).join('')
          : '<div class="alert alert-warning">No rooms match your search.</div>');
        renderPagination($('#roomsPagination'), data, state.page, function (p) {
          state.page = p; load(); window.scrollTo(0, 0);
        });
      }).fail(function (xhr) {
        $list.empty(); handleFail(xhr);
      });
    }

    $form.on('submit', function (e) { e.preventDefault(); state.page = 1; load(); });
    load();
  }

  // room_detail.html
  function initRoomDetail() {
    var $root = $('#roomDetail');
    if (!$root.length) return;
    var id = $root.data('room-id');
    Rooms.get(id).done(function (room) {
      document.title = room.name + ' — MyHotel';
      $root.find('.js-room-name').text(room.name);
      $root.find('.js-room-owner').text(room.owner_name);
      $root.find('.js-room-price').text(money(room.pay_per_night));
      $root.find('.js-room-capacity').text(room.permitted_guests);
      $root.find('.js-room-pictures').html(picturesHtml(room));
      $root.find('.js-room-amenities').html($.map(room.amenities || [], function (a) {
        return '<div class="col-6 col-md-4"><i class="bi bi-check-circle text-success"></i> ' + esc(a.name) + '</div>';
      }).join('') || '<div class="col-12 text-muted">No facilities listed.</div>');
      // feed main.js price calculator
      $('#priceCard').attr('data-price', room.pay_per_night).data('price', room.pay_per_night);
      if (typeof window.updatePrice === 'function') window.updatePrice();
      $root.find('.js-reserve').attr('href', '/bookings/booking/' + room.id + '/create/');
    }).fail(handleFail);
  }

  // booking_form.html — live price + submit through API
  function initBookingForm() {
    var $f = $('#bookingForm');
    if (!$f.length) return;
    if (!requireLogin()) return;
    var roomId = $f.data('room-id');
    var price = 0;

    function recalc() {
      var a = $f.find('[name=date_in]').val(), b = $f.find('[name=date_out]').val();
      var nights = (a && b) ? Math.round((new Date(b) - new Date(a)) / 86400000) : 0;
      $('#total-price, #subtotal-price').text(nights > 0 ? money(nights * price) : money(price));
      $('#rate-summary').text(nights > 0 ? money(price) + ' × ' + nights + ' night' + (nights > 1 ? 's' : '') : money(price) + ' per night');
    }

    Rooms.get(roomId).done(function (room) {
      price = Number(room.pay_per_night);
      $('.js-room-name').text(room.name);
      $f.find('[name=number_of_people]').attr('max', room.permitted_guests);
      recalc();
    }).fail(handleFail);

    $f.on('change input', '[name=date_in], [name=date_out]', recalc);

    $f.on('submit', function (e) {
      e.preventDefault();
      var $btn = $f.find('[type=submit]').prop('disabled', true);
      Bookings.create({
        room: roomId,
        date_in: $f.find('[name=date_in]').val(),
        date_out: $f.find('[name=date_out]').val(),
        number_of_people: Number($f.find('[name=number_of_people]').val())
      }).done(function () {
        window.location.href = PAGES.home;
      }).fail(function (xhr) {
        handleFail(xhr); $btn.prop('disabled', false);
      });
    });
  }

  // my_bookings.html
  function initMyBookings() {
    var $box = $('#myBookings');
    if (!$box.length) return;
    if (!requireLogin()) return;
    var user = Auth.user();

    function load() {
      $box.html('<p class="text-muted">Loading...</p>');
      // API lists ALL bookings -> restrict to current guest
      Bookings.list(user ? { guest: user.id } : {}).done(function (data) {
        var items = data.results || [];
        $box.html(items.length
          ? $.map(items, bookingCard).join('')
          : '<div class="alert alert-info">You have no bookings yet. <a href="/rooms-list/">Browse rooms</a></div>');
      }).fail(function (xhr) { $box.empty(); handleFail(xhr); });
    }

    $box.on('click', '.js-cancel-booking', function () {
      if (!window.confirm('Cancel this booking?')) return;
      Bookings.cancel($(this).data('id')).done(load).fail(handleFail);
    });
    load();
  }

  // login.html
  function initLogin() {
    var $f = $('#loginForm');
    if (!$f.length) return;
    $f.on('submit', function (e) {
      e.preventDefault();
      var $btn = $f.find('[type=submit]').prop('disabled', true);
      request({
        url: API.login, method: 'POST',
        data: { phone: $f.find('[name=phone]').val(), password: $f.find('[name=password]').val() }
      }).done(function (data) {
        Auth.save(data);
        window.location.href = getParam('next') || PAGES.home;
      }).fail(function (xhr) {
        alertBox('danger', errorText(xhr)); $btn.prop('disabled', false);
      });
    });
  }

  // register.html
  function initRegister() {
    var $f = $('#registerForm');
    if (!$f.length) return;
    $f.on('submit', function (e) {
      e.preventDefault();
      var $btn = $f.find('[type=submit]').prop('disabled', true);
      var body = {};
      $.each(['phone', 'name', 'password', 'confirm_password'], function (_, n) {
        body[n] = $f.find('[name=' + n + ']').val();
      });
      request({ url: API.register, method: 'POST', data: body }).done(function () {
        alertBox('success', 'Account created. Check your messages for the activation link, then log in.');
        $f[0].reset(); $btn.prop('disabled', false);
      }).fail(function (xhr) {
        alertBox('danger', errorText(xhr)); $btn.prop('disabled', false);
      });
    });
  }

  // navbar: logout + show username if logged in via JWT
  function initNav() {
    $(document).on('click', '.js-logout', function (e) { e.preventDefault(); Auth.logout(); });
  }

  // ---------------------------------------------------------------- boot
  $(function () {
    initNav();
    initHome();
    initRoomList();
    initRoomDetail();
    initBookingForm();
    initMyBookings();
    initLogin();
    initRegister();
  });

  // expose for console / other scripts
  window.ReservationAPI = { Auth: Auth, Rooms: Rooms, Bookings: Bookings, request: request };

})(jQuery);
