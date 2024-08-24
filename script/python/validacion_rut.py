
def formatear_rut(rut_original):
    """Elimina los signos y letras.

    Este es el formato que deve guardase en la db.
    ejemplo:
    12345678-9 => 123456789
    12345678-k => 12345678k
    """
    rut = rut_original.lower()
    rut_formateado = ''
    i = 1
    for n in rut:
        if (n.lower() == 'k' and i == len(rut_original)) or n.isdigit():
            rut_formateado += n
        i += 1
    return rut_formateado

def convertir_rut_en_lista_sin_div(rut):
    """
    div: diogito verificador 
    """
    rut_limpio = formatear_rut(rut)
    rut_lista = list(rut_limpio)
    div = rut_lista.pop()
    rut_lista_sin_div = rut_lista
    return rut_lista_sin_div


def calcular_div(rut):
    rut_sin_div = convertir_rut_en_lista_sin_div(rut)
    rut_sin_div.reverse()
    var = 0
    x = 2
    for n in rut_sin_div:
        if x > 7:
            x = 2       
        var += int(n) * x    
        x += 1    
    div = 11-(var % 11)
    if div == 11:
        div = 0
    elif div == 10:
        div = 'k'
    return div

def validar_rut(rut_original):
    """Validad si el rut es corcto y retorna True o False"""
    lista_rut_original = list(rut_original)
    div_original = lista_rut_original[-1]
    div_original_formateado = div_original.lower()
    # se formatea el div original del rut ingresado a typo string y minuscula
    div_original_str = str(div_original_formateado )

    # se obtine el div real 
    div_verificado = calcular_div(rut_original)
    div_verificado_str = str(div_verificado)    
    return div_original_str  == div_verificado_str 