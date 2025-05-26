
$.fn.datepicker.dates['es'] = {
    days: ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'],
    daysShort: ['Dom', 'Lun', 'Mar', 'Mié', 'Juv', 'Vie', 'Sáb'],
    daysMin: ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'],
    months: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
    monthsShort: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
    today: 'Seleccionar hoy',
    clear: 'Borrar fecha',
    format: 'dd/mm/yyyy',
    titleFormat: "MM yyyy",
    weekStart: 1
};

const picker = $('#datepicker').datepicker({
    startView:0,
    maxViewMode: 0,
    minViewMode: 0,
    updateViewDate: false,
    language: 'es',
    toggleActive:true,
    format: 'yyyy-mm-dd',
    startDate: new Date(),
    endDate: new Date(new Date().getFullYear(), new Date().getMonth() + 3, 0),
    datesDisabled: api_fechas_bloqueadas(new Date().getFullYear(), new Date().getMonth() + 1),
});

//Este objeto es útil para obtener la configuración del picker
const pickerData = $('#datepicker').data('datepicker');

/* Para modificar los estilos del calendario */
$(document.querySelectorAll('.datepicker')).addClass('w-100')
$(document.querySelectorAll('.table-condensed')).addClass('table').removeClass('table-condensed')
$(document.querySelectorAll('.datepicker-days')).addClass('table-responsive')
$(document.querySelectorAll('.today')).addClass('!bg-blue-500 !text-white !px-4 !py-2 !rounded hover:!bg-blue-400 !my-3')
$(document.querySelectorAll('.clear')).addClass('!bg-gray-400 !text-white !px-4 !py-2 !rounded hover:!bg-gray-500 !my-3')

const disabled_dates = []
function api_fechas_bloqueadas(year, month) {
    fetch(`/api/fechas-bloqueadas/${year}/${month}?format=json`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json', }
    })
    .then(response => response.json())
    .then(data => {
        if (data.length > 0) {
            console.log(`Se encontraron las fechas:`)
            console.log(data)
            data.forEach(obj => {
                let fecha_recuperada = new Date(obj.unix_timestamp)
                agregarFechaBloqueada(fecha_recuperada)
            })
        } else {
            console.log(`No se encontraron fechas bloqueadas para ${year}/${month}`)
        }
    })
    .catch(error => console.error('Error:', error));
}

// Actualizar las fechas bloqueadas
picker.on('changeMonth', evt => {
    pickerData.o.datesDisabled.length = 0
    api_fechas_bloqueadas(evt.date.getFullYear(), evt.date.getMonth() + 1)
})


const dialog = document.getElementById('modal-fecha')
const inputFecha = document.getElementById('id_fecha_cita')
const inputHorario = document.getElementById('id_horario')
const inputCategoria = document.getElementById('id_categoria')
const serviciosContainer = document.getElementById('id_servicios')

inputCategoria.disabled = true
inputCategoria.value = ''
inputHorario.disabled = true
inputHorario.value = ''
serviciosContainer.parentNode.style.display = 'none'

const inputBotonFecha = document.getElementById('abrir-datepicker')
const inputLimpiarFecha = document.getElementById('resetear-fecha')
const dialogConfirmar = document.getElementById('modal-confirmar')


if (dialogConfirmar) {
    dialogConfirmar.addEventListener('click', evt => {
        const fechaSeleccionada = picker.datepicker('getFormattedDate')
        if (fechaSeleccionada.length > 0) {
            // detectar si se seleccionó una fecha distinta
            const mismaFecha = inputFecha.value === fechaSeleccionada
            if (mismaFecha) {
                // no debería cambiar nada, se queda igual
            } else {
                // cambiar el input con el nuevo valor
                resetearHorarioServicios()
                inputFecha.value = fechaSeleccionada
                console.log(`Se seleccionó la fecha ${fechaSeleccionada}`)
            }
            dialog.close()
            inputCategoria.disabled = false
        } else {
            console.log('No se ha seleccionado ninguna fecha... no se puede confirmar')
        }
    })
}

if (inputFecha) {
    inputFecha.addEventListener('click', evt => {
        dialog.showModal()
    })
}

if (inputBotonFecha) {
    inputBotonFecha.addEventListener('click', evt => {
        dialog.showModal()
    })
}

if (inputLimpiarFecha) {
    inputLimpiarFecha.addEventListener('click', evt => {
        resetearHorarioServicios()
        inputFecha.value = ''
        inputHorario.value = 'NA'
        picker.datepicker('clearDates')  
        serviciosContainer.parentNode.style.display = 'none'
    })
}

if (inputCategoria) {
    inputCategoria.addEventListener('change', evt => {
        // borrar las opciones
        borrarHorarios()
        borrarServicios()
        if (inputCategoria.selectedIndex > 0) {
            inputHorario.disabled = false
            api_horarios_de_servicio()
            api_get_servicios()
            serviciosContainer.parentNode.style.display = 'block'
        } else {
            inputHorario.disabled = true
            agregarOpcionVacia('Elige un tipo de servicio')
            serviciosContainer.parentNode.style.display = 'none'
        }
    })
}

function agregarFechaBloqueada(fecha) {
    let fechas = pickerData.o.datesDisabled
    if (fecha === null || typeof fecha === 'undefined')
        return 'Fecha no válida'

    if (!fechas.includes(fecha)) {
        fechas.push(fecha)    
        picker.datepicker('setDatesDisabled', fechas)
    }
}

function resetearHorarioServicios() {
    inputCategoria.disabled = true
    inputCategoria.selectedIndex = 0

    inputHorario.disabled = true
    inputHorario.selectedIndex = 0

    borrarHorarios()
    borrarServicios()
    agregarOpcionVacia('Sin asignar')
}

function agregarOpcionVacia(mensaje) {
    let option = document.createElement('option');
    option.value = 'NA';
    option.textContent = mensaje;
    inputHorario.appendChild(option); 
}


async function api_horarios_de_servicio() {
    const fecha = picker.datepicker('getDate')
    if (fecha === null) 
        return 'Fecha inválida'

    const llamar_api = (inputCategoria.value !== '' && inputCategoria.selectedIndex > 0)
    if (!llamar_api) 
        return 'Categoría inválida'

    const response = await fetch(`/api/horarios_servicio_disponibles/${inputCategoria.value}/${fecha.getFullYear()}/${fecha.getMonth() + 1}/${fecha.getDate()}?format=json`, {
        method: 'GET', // O 'POST', 'PUT', 'DELETE'
        headers: {
            'Content-Type': 'application/json',
        }
    })

    if (!response.ok) {
        throw new Error(`Response status: ${response.status}`);
    }

    const json = await response.json();
    console.log(json)
    if (json.length == 0) {
        inputHorario.disabled = true
        agregarOpcionVacia('No hay horarios disponibles')

    } else {
        inputHorario.disabled = false


        json.forEach(horario => {
            let option = document.createElement('option');
            option.value = horario.hora;
            option.textContent = `🕗 ${horario.hora_string}`;
            inputHorario.appendChild(option);
        })
    }
    return 'Hola mundo'
}

async function api_get_servicios() {
    if (inputCategoria.value === '')
        return 'Categoría inválida'

    const response = await fetch(`/api/servicios/${inputCategoria.value}?format=json`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    if (!response.ok)
        throw new Error(`Response status: ${response.status}`);
    const json = await response.json();

    json.forEach(insertar_servicio)

}


function insertar_servicio(servicio) {
    let element = document.getElementById('id_servicios')
    if (element) {
        let template = `
        <div class="form-check">
            <input class="form-check-input shadow" type="checkbox" value="${servicio.id}" id="id_servicios_${servicio.id}" name="servicios">
            <label class="form-check-label" for="id_servicios_${servicio.id}">${servicio.nombre}</label>
        </div>`
        element.insertAdjacentHTML('beforeend', template)
    }
}

function borrarServicios() {
    let element = document.getElementById('id_servicios')
    if (element)
        while (element.firstChild)
            element.removeChild(element.firstChild)
}

function borrarHorarios() {
    if (inputHorario)
        while (inputHorario.firstChild)
            inputHorario.removeChild(inputHorario.firstChild)
}
