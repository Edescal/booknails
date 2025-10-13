(function () {
  'use strict';

  const $ = window.$;

  const pickerEl   = document.getElementById('datepicker');
  const inpFecha   = document.getElementById('id_fecha_cita');
  const selHorario = document.getElementById('id_horario');
  const categoria  = document.getElementById('id_categoria');
  const contServ   = document.getElementById('id_servicios');

  function clearChildren(el) { if (el) while (el.firstChild) el.removeChild(el.firstChild); }

  function setHorarioPlaceholder(text) {
    if (!selHorario) return;
    clearChildren(selHorario);
    const opt = new Option(text, '');
    opt.disabled = true;
    opt.selected = true;
    selHorario.add(opt);
  }

  function hhmmTo12hLabel(value) {
    const parts = String(value || '').split(':');
    if (parts.length < 2) return String(value || '').slice(0, 5) || '—';
    const H = parseInt(parts[0], 10);
    const M = parseInt(parts[1], 10);
    if (Number.isNaN(H) || Number.isNaN(M)) return String(value || '').slice(0, 5) || '—';
    const h = ((H + 11) % 12) + 1;
    const ampm = H < 12 ? 'AM' : 'PM';
    return `${h}:${String(M).padStart(2, '0')} ${ampm}`;
  }

  function normalizeHorarios(json) {
    if (!Array.isArray(json)) return [];
    return json.map(it => {
      let value, label;

      if (Array.isArray(it)) {
        value = it[0];
        label = it[1];
      } else if (it && typeof it === 'object') {
        value = it.value ?? it.hora ?? it.time ?? it.val ?? it['0'];
        label = it.label ?? it.text ?? it.caption ?? it['1'];
      }

      if (!value) return null;
      if (!label) label = hhmmTo12hLabel(value);

      return { value: String(value), label: String(label) };
    }).filter(Boolean);
  }

  async function cargarHorarios(isoDate) {
    if (!selHorario) return;

    if (!isoDate) { setHorarioPlaceholder('Selecciona un horario'); return; }
    const [Y, M, D] = String(isoDate).split('-');
    if (!Y || !M || !D) { setHorarioPlaceholder('Selecciona un horario'); return; }

    setHorarioPlaceholder('Cargando...');
    try {
      const y = parseInt(Y, 10);
      const m = parseInt(M, 10);
      const d = parseInt(D, 10);

      const res = await fetch(`/api/horarios/${y}/${m}/${d}/`, {
        headers: { 'Accept': 'application/json' }
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const json  = await res.json();
      const items = normalizeHorarios(json);

      clearChildren(selHorario);

      if (!items.length) {
        const opt = new Option('Sin horarios disponibles para esta fecha', '');
        opt.disabled = true;
        opt.selected = true;
        selHorario.add(opt);
        return;
      }

      const ph = new Option('Selecciona un horario', '');
      ph.disabled = true;
      ph.selected = true;
      selHorario.add(ph);

      items.forEach(({ value, label }) => {
        selHorario.add(new Option(label, value));
      });
    } catch (err) {
      console.error('Error cargando horarios:', err);
      setHorarioPlaceholder('Error al cargar horarios');
    }
  }

  if ($ && $.fn && $.fn.datepicker && pickerEl) {
    $.fn.datepicker.dates['es-419'] = {
        days: ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'],
        daysShort: ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'],
        daysMin: ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'],
        months: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
        monthsShort: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
        today: 'Hoy',
        clear: 'Limpiar',
        format: 'dd/mm/yyyy',
        titleFormat: 'MM yyyy',
        weekStart: 1
    };

    const start = new Date();
    start.setHours(0,0,0,0);
    const end = new Date(start.getFullYear(), start.getMonth() + 3, 0);

    const disabledDates = [];
    const diffMonths = (end.getFullYear() - start.getFullYear()) * 12 + (end.getMonth() - start.getMonth());

    async function preloadDisabled() {
        const fetches = [];
        for (let i = 0; i <= diffMonths; i++) {
        const d = new Date(start.getFullYear(), start.getMonth() + i, 1);
        const y = d.getFullYear();
        const m = d.getMonth() + 1;
        fetches.push(
            fetch(`/api/fechas-bloqueadas/${y}/${m}?format=json`, {
            headers: { 'Accept': 'application/json' }
            })
            .then(r => r.ok ? r.json() : [])
            .then(arr => {
            (Array.isArray(arr) ? arr : []).forEach(obj => {
                const ts = obj.unix_timestamp ?? obj.UNIX_timestamp ?? obj.timestamp;
                if (typeof ts === 'number') {
                const day = new Date(ts);
                day.setHours(0,0,0,0);
                disabledDates.push(day);
                }
            });
            })
            .catch(() => {})
        );
        }
        await Promise.all(fetches);
    }

    (async () => {
        try {
        await preloadDisabled();
        } catch (_) {}

        const picker = $('#datepicker').datepicker({
        language: 'es-419',
        todayHighlight: true,
        format: 'yyyy-mm-dd',
        startDate: start,
        endDate: end,
        datesDisabled: disabledDates 
        });

        $(document.querySelectorAll('.datepicker')).addClass('w-100');
        $(document.querySelectorAll('.table-condensed')).addClass('table').removeClass('table-condensed');
        $(document.querySelectorAll('.datepicker-days')).addClass('table-responsive');

        picker.on('changeDate', function (evt) {
        const d  = evt.date;
        const yy = d.getFullYear();
        const mm = String(d.getMonth() + 1).padStart(2, '0');
        const dd = String(d.getDate()).padStart(2, '0');
        const iso = `${yy}-${mm}-${dd}`;

        if (inpFecha) inpFecha.value = iso;
        cargarHorarios(iso);
        });
    })();
  }

  if (inpFecha) {
    inpFecha.addEventListener('change', () => cargarHorarios(inpFecha.value));
    if (inpFecha.value) cargarHorarios(inpFecha.value);
  } else if (selHorario) {
    setHorarioPlaceholder('Selecciona un horario');
  }

  if (categoria) {
    categoria.addEventListener('input', evt => {
      limpiarServicios();
      cargarServicios(`${evt.target.value}`);
    });
  }

    function limpiarServicios() {
    if (!contServ) return;
    contServ.innerHTML = '';
    }

    function money(v) {
    if (v === null || v === undefined || v === '') return '$0.00';
    const n = Number(v);
    if (!isNaN(n)) return n.toLocaleString('es-MX', { style: 'currency', currency: 'MXN' });
    return `$${String(v)}`;
    }

    function checkboxServicioHTML(s) {
    const id = `id_servicios_${s.id}`;
    const etiqueta = `${s.nombre} — ${money(s.precio)}`; // ← sin categoría
    return `
        <div class="form-check mb-1">
        <input type="checkbox" name="servicios" value="${s.id}" class="form-check-input shadow" id="${id}">
        <label class="form-check-label" for="${id}">${etiqueta}</label>
        </div>`;
    }

    function cargarServicios(catId) {
    if (!catId || !contServ) return;
    limpiarServicios();
    fetch(`/api/servicios/${catId}?format=json`, {
        method: 'GET',
        headers: { 'Accept': 'application/json' }
    })
    .then(r => r.json())
    .then(data => {
        const arr = Array.isArray(data) ? data : [];
        if (arr.length === 0) {
        contServ.innerHTML = `<small class="text-muted">No hay servicios en esta categoría.</small>`;
        return;
        }
        const html = arr.map(checkboxServicioHTML).join('');
        contServ.insertAdjacentHTML('beforeend', html);
    })
    .catch(err => console.error('Error:', err));
    }

  const disabled_dates = [];
  function api_fechas_bloqueadas(year, month, picker) {
    fetch(`/api/fechas-bloqueadas/${year}/${month}?format=json`, {
      method: 'GET',
      headers: { 'Accept': 'application/json' }
    })
    .then(r => r.json())
    .then(data => {
      disabled_dates.length = 0;
      (Array.isArray(data) ? data : []).forEach(obj => {
        const ts = obj.unix_timestamp ?? obj.UNIX_timestamp ?? obj.timestamp;
        if (typeof ts === 'number') disabled_dates.push(new Date(ts));
      });
      if (picker) picker.datepicker('setDatesDisabled', disabled_dates);
    })
    .catch(error => console.error('Error:', error));
  }
})();