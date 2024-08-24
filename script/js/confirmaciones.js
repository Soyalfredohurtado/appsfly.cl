function confirmarEliminarProducto(producto) {
    var confirmacion = confirm('Eliminar producto?');
    if (confirmacion) {
        window.location.href = "/productos_y_servicios/delete/" + encodeURIComponent(producto);
    }
}

function confirmarAddProducto() {
    var confirmacion = confirm('Seguro de crear producto?');
    if (confirmacion) {
        window.location.href = "/productos_y_servicios";
    }
}

function confirmUpdateProducto() {
    var confirmacion = confirm('Seguro de modificar producto?');
    if (confirmacion) {
        window.location.href = "/productos_y_servicios";
    }
}


