$(document).ready(function () {
    $('#btn-vistaModal').click(function () {
        var id_cliente = $('#venta_cliente_id').val()
        $('#clienteRutVista').val(id_cliente);
        $('#clienteNombreVista').val('');

    });
});

