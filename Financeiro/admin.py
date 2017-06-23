# -*- encoding: utf-8 -*-
from django.contrib import admin
from .models import Receber, Cliente, Natureza, Fornecedor, Pagar, Analista, NotaDebito, Nota


class ReceberInlineAdmin(admin.TabularInline):
    model = Receber
    extra = 0

    exclude = ('cliente', 'mes_competencia', 'ano_competencia', 'baixa', 'inclusao', 'imposto', 'taxa', 'valor_repasse',
               'liquido',)


class NotaAdmin(admin.ModelAdmin):
    """
    Responsável por manipular o admin Nota
    """

    icon = '<i class="material-icons">call_received</i>'

    model = Nota
    inlines = [ReceberInlineAdmin]

    list_display = ['cliente', 'mes_competencia', 'ano_competencia', 'valor', 'imposto', 'baixa', ]
    list_display_links = ['cliente', 'mes_competencia', 'ano_competencia', 'valor', 'imposto', 'baixa', ]
    search_fields = ['cliente', 'mes_competencia', 'ano_competencia', 'valor', 'imposto', 'baixa', ]
    empty_value_display = ''
    readonly_fields = ('valor', 'imposto', )

admin.site.register(Nota, NotaAdmin)


class ReceberGeralAdmin(admin.ModelAdmin):
    """
    Responsável por manipular o admin Receber
    """

    icon = '<i class="material-icons">call_received</i>'

    model = Receber
    save_on_top = True

    list_display = ['id', 'cliente', 'analista', 'valor', 'imposto', 'taxa', 'valor_repasse', 'liquido', 'baixa', ]
    list_display_links = ['id', 'cliente', 'analista', 'valor', 'imposto', 'taxa', 'valor_repasse', 'liquido',
                          'baixa', ]
    search_fields = ['id', 'cliente', 'analista', 'valor', 'imposto', 'taxa', 'valor_repasse', 'liquido', 'baixa', ]
    list_filter = ('cliente', 'analista', 'baixa')
    empty_value_display = ''
    readonly_fields = ('inclusao', 'imposto', 'taxa', 'valor_repasse', 'liquido',)

    fieldsets = (
        ('Dados', {
            'fields': ('cliente', 'analista', 'natureza', 'inclusao', 'mes_competencia', 'ano_competencia', 'baixa')
        }),
        ('Valores', {
            'fields': ('valor', 'imposto', 'taxa', 'valor_repasse', 'liquido'),
        }),
    )

admin.site.register(Receber, ReceberGeralAdmin)


class ReceberAnalista(Receber):
    class Meta:
        proxy = True
        app_label = 'Financeiro'
        verbose_name = u'Conta a receber Analista'
        verbose_name_plural = u'Contas a receber Analista'

class ReceberAnalistaAdmin(ReceberGeralAdmin):
    """
    Responsável por manipular o admin Receber
    """

    icon = '<i class="material-icons">call_received</i>'

    model = Receber
    save_on_top = True

    list_display = ['id', 'cliente', 'analista', 'valor', 'valor_repasse', 'baixa', ]
    list_display_links = ['id', 'cliente', 'analista', 'valor', 'valor_repasse', 'baixa',]
    search_fields = ['id', 'cliente', 'analista', 'valor', 'valor_repasse', 'baixa', ]
    list_filter = ('cliente', 'analista', 'baixa')
    empty_value_display = ''
    readonly_fields = ('cliente', 'analista', 'natureza', 'inclusao', 'mes_competencia', 'ano_competencia', 'baixa',
                       'valor', 'valor_repasse',)

    fieldsets = (
        ('Dados', {
            'fields': ('cliente', 'analista', 'natureza', 'inclusao', 'mes_competencia', 'ano_competencia', 'baixa')
        }),
        ('Valores', {
            'fields': ('valor', 'valor_repasse', ),
        }),
    )

    def get_queryset(self, request):
        """
        Filter the objects displayed in the change_list to only
        display those for the currently signed in user.
        """

        querySet = filtro_analista(request, self, ReceberAnalistaAdmin)
        return querySet

admin.site.register(ReceberAnalista, ReceberAnalistaAdmin)


class PagarAdmin(admin.ModelAdmin):
    """
    Responsável por manipular o admin Pagar
    """

    icon = '<i class="material-icons">call_made</i>'

    model = Pagar
    save_on_top = True

    list_display = ['id', 'fornecedor', 'tipo', 'valor', 'transferencia', 'liquido', 'baixa', ]
    list_display_links = ['id', 'fornecedor', 'tipo', 'valor', 'transferencia', 'liquido', 'baixa', ]
    search_fields = ['id', 'tipo', 'valor', 'transferencia', 'liquido', 'baixa', ]
    empty_value_display = ''
    exclude = ('receber', 'nota_debito', 'nota')
    readonly_fields = ('transferencia', 'liquido',)

    fieldsets = (
        ('Dados', {
            'fields': ('fornecedor', 'tipo', 'inclusao', 'mes_competencia', 'ano_competencia', 'baixa')
        }),
        ('Valores', {
            'fields': ('valor', 'transferencia', 'desconto', 'liquido'),
        }),
    )

admin.site.register(Pagar, PagarAdmin)


class NotaDebitoAdmin(admin.ModelAdmin):
    """
    Responsável por manipular o admin Nota de débito
    """

    icon = '<i class="material-icons">local_taxi</i>'

    model = NotaDebito
    save_on_top = True

    def get_queryset(self, request):
        """
        Filter the objects displayed in the change_list to only
        display those for the currently signed in user.
        """

        querySet = filtro_analista(request, self, NotaDebitoAdmin)
        return querySet

    def notaDebitoPDF(self, obj):
        if obj.analista:
            return '<a target="_blank" href="%s%s">%s</a>' % (
                '/financeiro/notaDebitoPDF/', obj.id, 'Gerar')  # , obj.url_field, obj.url_field)
        else:
            return ''

    notaDebitoPDF.allow_tags = True
    notaDebitoPDF.short_description = 'PDF'

    def notaDebito(self, obj):
        if obj.analista:
            return '<a target="_blank" href="%s%s">%s</a>' % (
                '/financeiro/notaDebito/', obj.id, 'Gerar')  # , obj.url_field, obj.url_field)
        else:
            return ''

    notaDebito.allow_tags = True
    notaDebito.short_description = 'Nota de débito'

    list_display = ['analista', 'cliente_atendimento', 'valor', 'baixa', 'despesa', 'notaDebito',]
    list_display_links = ['analista', 'cliente_atendimento', 'valor', 'baixa', 'despesa', 'notaDebito',]
    search_fields = ['analista', 'cliente_atendimento', 'valor', 'baixa', 'despesa',  'notaDebito',]
    list_filter = (('cliente_atendimento',  admin.RelatedOnlyFieldListFilter),
                   ('analista', admin.RelatedOnlyFieldListFilter),
                   'baixa',)
    empty_value_display = ''
    readonly_fields = ('inclusao', 'taxa', 'valor_repasse', 'liquido',)

    fieldsets = (
        ('Dados', {
            'fields': ('inclusao', 'mes_competencia', 'ano_competencia', 'despesa',
                       'cliente_atendimento', 'analista', 'baixa',
                       ),
        }),
        ('Valores', {
            'fields': ('valor', 'taxa', 'valor_repasse', 'liquido'),
        }),
    )

admin.site.register(NotaDebito, NotaDebitoAdmin)


class ClienteAdmin(admin.ModelAdmin):
    """
    Responsável por manipular o admin Cliente
    """

    icon = '<i class="material-icons">person_outline</i>'
admin.site.register(Cliente, ClienteAdmin)


class NaturezaAdmin(admin.ModelAdmin):
    """
    Responsável por manipular o admin Natureza
    """

    icon = '<i class="material-icons">local_florist</i>'
admin.site.register(Natureza, NaturezaAdmin)


class FornecedorAdmin(admin.ModelAdmin):
    """
    Responsável por manipular o admin Fornecedor
    """

    icon = '<i class="material-icons">stores</i>'
admin.site.register(Fornecedor, FornecedorAdmin)


class AnalistaAdmin(admin.ModelAdmin):
    """
    Responsável por manipular o admin Cliente
    """

    icon = '<i class="material-icons">people</i>'
admin.site.register(Analista, AnalistaAdmin)


def filtro_analista(request, model, modelAdmin):
    queryset = super(modelAdmin, model).get_queryset(request)
    analista = Analista.objects.filter(Usuário=request.user)
    if analista:
        return queryset.filter(analista__in=analista)
    else:
        return queryset