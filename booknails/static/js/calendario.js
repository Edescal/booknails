$.fn.datepicker.dates['es'] = {
    days: ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'],
    daysShort: ['Dom', 'Lun', 'Mar', 'Mié', 'Juv', 'Vie', 'Sáb'],
    daysMin: ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'],
    months: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
    monthsShort: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
    today: 'Hoy',
    clear: 'Limpiar',
    format: 'dd/mm/yyyy',
    titleFormat: "MM yyyy",
    weekStart: 1
};

const picker = $('#datepicker').datepicker({
    language: 'es-419',
    todayHighlight: true,
    changeMonth: false,
    changeYear: false,
    format: 'yyyy-mm-dd',
    startDate: new Date(),
    endDate: new Date(new Date().getFullYear(), new Date().getMonth() + 3, 0),
    datesDisabled: api_fechas_bloqueadas(new Date().getFullYear(), new Date().getMonth() + 1),
});

picker.on('changeMonth', evt => {
    /*
    Por algún motivo, la fecha de evt.date o 'getDate NO ES CORRECTA
    Lo mejor es poner un delay para que después de que se actualice el
    datepicker, entonces ya se recupera el nuevo valor y se actualiza el picker
    */
    setTimeout(() => {
        const fecha = picker.datepicker('getDate')
        console.log( `Nueva fecha seleccionada: ${fecha}` )
        api_fechas_bloqueadas(picker.datepicker('getDate').getFullYear(), picker.datepicker('getDate').getMonth() + 1)
      }, 10);
})

picker.on('changeDate', function (evt) {
    let data = picker.datepicker('getFormattedDate')
    console.log(`Cambiando fecha y horarios del dia: ${data}`)
    let input = document.getElementById('id_fecha_cita')
    if (input) {
        input.setAttribute('value', data)
        delHorarios()
        getHorarios(evt.date.getFullYear(), evt.date.getMonth(), evt.date.getDate())
    }
});
/* Para modificar los estilos del calendario */
$(document.querySelectorAll('.datepicker')).addClass('w-100')
$(document.querySelectorAll('.table-condensed')).addClass('table').removeClass('table-condensed')
$(document.querySelectorAll('.datepicker-days')).addClass('table-responsive')

const categoria = document.getElementById('id_categoria')
if (categoria) {
    categoria.addEventListener('input', evt => {
        del()
        api(`${evt.target.value}`)
    })
}

function del() {
    let element = document.getElementById('id_servicios')
    if (element) {
        while (element.firstChild)
            element.removeChild(element.firstChild)
    }
}

function api(categoria) {
    fetch(`/api/servicios/${categoria}?format=json`, {
        method: 'GET', // O 'POST', 'PUT', 'DELETE'
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{csrf_token}}' // Solo si es POST o PUT
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.length > 0) {
                for (var i = 0; i < data.length; i++)
                    insert(data[i].nombre, data[i].id)
            }
        })
        .catch(error => console.error('Error:', error));
}

function insert(name, value) {
    let element = document.getElementById('id_servicios')
    if (element) {
        let template = `
        <label for="id_servicios_${value}">
            <input type="checkbox" name="servicios" value="${value}" class="form-check-input shadow" id="id_servicios_${value}">
             ${name}
        </label>`
        new_ele = document.createElement('div')
        new_ele.innerHTML = template
        element.insertAdjacentElement('beforeend', new_ele)
    }
}



function delHorarios() {
    let element = document.getElementById('id_horario')
    if (element) {
        while (element.firstChild)
            element.removeChild(element.firstChild)
    }
}

async function getHorarios(year, month, day) {
    try {
        const response = await fetch(`/api/horarios/${year}/${month + 1}/${day}?format=json`, {
            method: 'GET', // O 'POST', 'PUT', 'DELETE'
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': '{{csrf_token}}' // Solo si es POST o PUT
            }
        });

        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }

        const json = await response.json();
        let element = document.getElementById('id_horario')
        if (element) {
            if (json.length == 0) {
                let title = `<option value="NA">Sin horarios disponibles para esta fecha</option>`
                let base_elem = document.createElement('template')
                base_elem.innerHTML = title.trim()
                element.insertAdjacentElement('beforeend', base_elem.content.firstElementChild)
                return
            }


            let title = `<option value="NA">Selecciona un horario</option>`
            let base_elem = document.createElement('template')
            base_elem.innerHTML = title.trim()
            element.insertAdjacentElement('beforeend', base_elem.content.firstElementChild)

            console.log(`\u{1F6A8} \u{26A0} \u{2705} Horarios disponibles:`);
            json.forEach(d => {
                let template = `<option value="${d[0]}">\u{2705} ${d[1]}</option>`
                new_ele = document.createElement('div')
                new_ele.innerHTML = template
                element.insertAdjacentElement('beforeend', new_ele)
            })
        }

    } catch (error) {
        console.error(`Fetch error: ${error.message}`);
    }
}

const disabled_dates = []
function api_fechas_bloqueadas(year, month) {
    fetch(`/api/fechas-bloqueadas/${year}/${month}?format=json`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json', }
    })
        .then(response => response.json())
        .then(data => {
            if (data.length > 0) {
                disabled_dates.length = 0
                // Agregar todas las fechas a un array limpio
                data.forEach(obj => disabled_dates.push(new Date(obj.unix_timestamp)))
                // Deshabilitar las fechas
                picker.datepicker('setDatesDisabled', disabled_dates);
                // Debuggear en consola
                // console.log(`Fechas deshabilitadas: ${disabled_dates}`)
            }
        })
        .catch(error => console.error('Error:', error));
}

//Lo utiliza el evento "changeMonth" del datepicker
function formatearFecha(fecha) {
    const year = fecha.getFullYear();
    const month = String(fecha.getMonth() + 1).padStart(2, '0');
    const day = String(fecha.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}