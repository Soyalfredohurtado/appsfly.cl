// ============================================================================================
$(document).on('change', '.precio, .cantidad, .formaPagoMonto', function () {
    var fila = $(this).closest('tr');
    var precio = fila.find('.precio').val();
    var cantidad = fila.find('.cantidad').val();
    var total = precio * cantidad;
    fila.find('.total').text(total);
    calcularTotalFinal()
});

$(document).on('change', '.formaPagoMonto', function () {
    var abono = $('.formaPagoMonto').val();
    $('#ventaAbono').text(abono)
    calcularTotalFinal()
});

$(document).on('change', '.ventaProducto', function () {
    var precio = 100000;
    $('tr .precio').text(precio)
});


function calcularTotalFinal() {
    var suma = 0;
    var abono = $('.formaPagoMonto').val();
    $('#productosTable tbody tr').each(function () {
        var total = parseFloat($(this).find('.total').text());
        if (!isNaN(total)) {
            suma += total;
        }
    });
    var cxc = suma - abono
    $('#ventaTotal').text(suma);
    $('#ventaAbono').text(abono)
    $('#ventaCxc').text(cxc)
}
