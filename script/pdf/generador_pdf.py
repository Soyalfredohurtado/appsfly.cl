import jinja2
import pdfkit


def generate_pdf_(datos, plantilla_template, nombre='', ):
    """
    Genera pdf
    ARGS:
    datos = datos que van en el pdf
    plantilla_template = nombre de la platilla template
    nombre = nombre con el que se dav a guardar
    """
    template_loader = jinja2.FileSystemLoader('./templates/pdf')
    template_env = jinja2.Environment(loader=template_loader)

    # comprobante_venta.html
    html_template = plantilla_template
    template = template_env.get_template(html_template)
    output_text = template.render(data=datos)
    options = {
        'page-size': 'A4',
        'margin-top': '0.5in',
        'margin-right': '0.5in',
        'margin-bottom': '0.5in',
        'margin-left': '0.5in',
        'encoding': 'UTF-8'
    }

    config = pdfkit.configuration(
        wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')
    output_pdf = f'{nombre}.pdf'
    pdfkit.from_string(output_text, output_pdf,
                       options=options, configuration=config)
