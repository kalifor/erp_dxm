# -*- encoding: utf-8 -*-

from django.shortcuts import render
#from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.template import RequestContext, Context

# Geração de PDF
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.loader import get_template
from django.template import Context
import logging
import sys
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import date

from .models import NotaDebito

def notaDebitoPDF(request, idNota):
    template_name = "financeiro/nota_debito.html"

    notaDebito = NotaDebito.objects.get(id=idNota)

    # Nota
    idNota = notaDebito.id
    data_emissao = date.today().strftime('%d/%m/%Y')
    data_vencimento = (date.today() + timezone.timedelta(days=15)).strftime('%d/%m/%Y')

    # Empresa
    nome_empresa = notaDebito.natureza.fornecedor_despesa.nome
    endereco_empresa = notaDebito.natureza.fornecedor_despesa.endereco
    municipio_empresa = notaDebito.natureza.fornecedor_despesa.municipio
    cep_empresa = notaDebito.natureza.fornecedor_despesa.cep
    cnpj_empresa = notaDebito.natureza.fornecedor_despesa.cnpj

    # Banco
    nome_banco = 'Banco do Brasil'
    agencia_banco = '368-9'
    conta_banco = '72536-6'
    cnpj_banco = '22.371.382/0001-00'

    # Despesas
    historico_despesa = 'Reembolso de despesas'
    analista_despesa = notaDebito.analista.nome
    cliente_despesa = notaDebito.cliente_atendimento.nome
    cliente_codigo = notaDebito.cliente_atendimento.codigo
    despesa_despesa = notaDebito.despesa
    valor_despesa = notaDebito.liquido

    contexto_pdf = {
        'id_nota': idNota,
        'data_emissao': data_emissao,
        'data_vencimento': data_vencimento,
        'nome_empresa': nome_empresa,
        'endereco_empresa': endereco_empresa,
        'municipio_empresa': municipio_empresa,
        'cep_empresa': cep_empresa,
        'cnpj_empresa': cnpj_empresa,
        'nome_banco': nome_banco,
        'agencia_banco': agencia_banco,
        'conta_banco': conta_banco,
        'cnpj_banco': cnpj_banco,
        'historico_despesa': historico_despesa,
        'analista_despesa': analista_despesa,
        'cliente_despesa': cliente_despesa,
        'cliente_codigo': cliente_codigo,
        'despesa_despesa': despesa_despesa,
        'valor_despesa': valor_despesa,
    }

    '''
    template = get_template(template_name)
    html = template.render(Context(contexto_pdf))

    file = open('test.pdf', "w+b")
    pisaStatus = pisa.CreatePDF(html.encode('utf-8'), dest=file,
                                encoding='utf-8')

    file.seek(0)
    pdf = file.read()
    file.close()

    return HttpResponse(pdf, 'application/pdf')
    '''

    #rendered_html = render_to_string(template_name, contexto_pdf)
    #return html_to_pdf_response(rendered_html)

    #return render_to_pdf(template_name, contexto_pdf)

    '''
    path_wkthmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)

    template = get_template(template_name)
    context = Context({"data": contexto_pdf})  # data is the context data that is sent to the html file to render the output.
    html = template.render(context)  # Renders the template with the context data.
    #pdfkit.from_string(html, 'out.pdf', configuration=config)
    pdfkit.from_url("http://google.com", "out.pdf", configuration=config)
    #pdf = open("out.pdf")
    response = HttpResponse(pdf.read(), content_type='application/pdf')  # Generates the response as pdf response.
    response['Content-Disposition'] = 'attachment; filename=output.pdf'
    pdf.close()

    import os

    os.remove("out.pdf")  # remove the locally created pdf file.
    return response
    '''

    html = render_to_string(template_name,
                            contexto_pdf)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename=nota_debito-{0}.pdf'.format(idNota)
    weasyprint.HTML(string=html).write_pdf(response,
                                           stylesheets = fetch_resources)

    return response


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    context = Context(context_dict)
    html = template.render(context)
    result = StringIO.StringIO()

    pdf = pisa.pisaDocument(
        StringIO.StringIO(html.encode("UTF-8")),
        dest=result,
        encoding='UTF-8',
        link_callback=fetch_resources)

    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return HttpResponse('We had some errors<pre>%s</pre>' % escape(html))


def fetch_resources(uri, rel):
    import os.path
    from django.conf import settings
    path = os.path.join(
            settings.STATIC_ROOT,
            uri.replace(settings.STATIC_URL, ""))

    return path


def html_to_pdf_response(html):
    result = StringIO.StringIO()
    pdf = pisa.pisaDocument(
            StringIO.StringIO(html.encode("UTF-8")),
            result
    )

    if not pdf.err:
        return HttpResponse(
            result.getvalue(),
            content_type='application/pdf'
        )
    else:
        return HttpResponse('Erro ao gerar o PDF!')


def notaDebito(request, idNota):
    template_name = "financeiro/nota_debito.html"

    notaDebito = NotaDebito.objects.get(id=idNota)

    # Nota
    if notaDebito.despesa_antiga:
        codigo_nota = notaDebito.despesa_antiga
    else:
        codigo_nota = '{:02d}'.format(notaDebito.cliente_atendimento.fornecedor_despesa.id) + \
                            '{:06d}'.format(notaDebito.id)
    data_emissao = date.today().strftime('%d/%m/%Y')
    data_vencimento = (date.today() + timezone.timedelta(days=15)).strftime('%d/%m/%Y')

    # Empresa
    nome_empresa = notaDebito.cliente_atendimento.fornecedor_despesa.nome
    endereco_empresa = notaDebito.cliente_atendimento.fornecedor_despesa.endereco
    municipio_empresa = notaDebito.cliente_atendimento.fornecedor_despesa.municipio
    cep_empresa = notaDebito.cliente_atendimento.fornecedor_despesa.cep
    cnpj_empresa = notaDebito.cliente_atendimento.fornecedor_despesa.cnpj

    # Banco
    nome_banco = 'Banco do Brasil'
    agencia_banco = '368-9'
    conta_banco = '72536-6'
    cnpj_banco = '22.371.382/0001-00'

    # Despesas
    historico_despesa = 'Reembolso de despesas'
    analista_despesa = notaDebito.analista.nome
    cliente_despesa = notaDebito.cliente_atendimento.nome
    cliente_codigo = notaDebito.cliente_atendimento.codigo
    despesa_despesa = notaDebito.despesa
    valor_despesa = notaDebito.valor

    contexto_pdf = {
        'codigo_nota': codigo_nota,
        'data_emissao': data_emissao,
        'data_vencimento': data_vencimento,
        'nome_empresa': nome_empresa,
        'endereco_empresa': endereco_empresa,
        'municipio_empresa': municipio_empresa,
        'cep_empresa': cep_empresa,
        'cnpj_empresa': cnpj_empresa,
        'nome_banco': nome_banco,
        'agencia_banco': agencia_banco,
        'conta_banco': conta_banco,
        'cnpj_banco': cnpj_banco,
        'historico_despesa': historico_despesa,
        'analista_despesa': analista_despesa,
        'cliente_despesa': cliente_despesa,
        'cliente_codigo': cliente_codigo,
        'despesa_despesa': despesa_despesa,
        'valor_despesa': valor_despesa,
    }

    # retorna o contexto para o template
    return render_to_response(template_name, contexto_pdf)