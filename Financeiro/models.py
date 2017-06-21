# -*- encoding: utf-8 -*-

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import date, datetime
from django.db.models import Sum

TIPO_CHOICES = (
        ('NDE', u'Nota de débito'),
        ('REP', u'Repasse'),
        ('IMP', u'Imposto'),
        ('BCO', u'Despesa bancária'),
    )

MONTH_CHOICES = (
    (1, '01'),
    (2, '02'),
    (3, '03'),
    (4, '04'),
    (5, '05'),
    (6, '06'),
    (7, '07'),
    (8, '08'),
    (9, '09'),
    (10, '10'),
    (11, '11'),
    (12, '12'),
)

YEAR_CHOICES = []
for r in range(2010, (datetime.now().year+1)):
    YEAR_CHOICES.append((r, r))


# Cliente
class Cliente(models.Model):
    codigo = models.CharField(max_length=6, blank=True, null=True)
    nome = models.CharField(max_length=64)
    endereco = models.CharField(max_length=64, blank=True, null=True)
    municipio = models.CharField(max_length=64, blank=True, null=True)
    cep = models.CharField(max_length=9, blank=True, null=True)
    cnpj = models.CharField(max_length=18, blank=True, null=True)
    fornecedor_despesa = models.ForeignKey(u"Fornecedor", related_name="Fornecedor_despesa", blank=True, null=True)
    fornecedor_imposto = models.ForeignKey(u"Fornecedor", related_name="Fornecedor_imposto", blank=True, null=True)

    def __unicode__(self):
        return self.nome

    class Meta:
        ordering = ['-id']
        verbose_name = u'Cliente'
        verbose_name_plural = u'Clientes'


# Fornecedor
class Fornecedor(models.Model):
    nome = models.CharField(max_length=64)
    doc_ted = models.DecimalField('Valor doc/ted', max_digits=8, decimal_places=2, blank=True, null=True)
    endereco = models.CharField(max_length=64, blank=True, null=True)
    municipio = models.CharField(max_length=64, blank=True, null=True)
    cep = models.CharField(max_length=9, blank=True, null=True)
    cnpj = models.CharField(max_length=18, blank=True, null=True)

    def __unicode__(self):
        return self.nome

    class Meta:
        ordering = ['-id']
        verbose_name = u'Fornecedor'
        verbose_name_plural = u'Fornecedores'


# Natureza
class Natureza(models.Model):
    nome = models.CharField(max_length=64)
    aliquota_imposto = models.DecimalField(u'Alíquota de imposto (%)', max_digits=5, decimal_places=2)
    aliquota_repasse = models.DecimalField(u'Percentual de repasse', max_digits=5, decimal_places=2, blank=True,
                                           null=True)

    def __unicode__(self):
        return self.nome

    class Meta:
        ordering = ['-id']
        verbose_name = u'Natureza'
        verbose_name_plural = u'Naturezas'


# Analista
class Analista(models.Model):
    nome = models.CharField(max_length=64)
    fornecedor_repasse = models.ForeignKey(u"Fornecedor", related_name="Fornecedor_repasse", blank=True, null=True)
    aliquota_despesa = models.DecimalField(u'Percentual repasse de despesa', max_digits=5, decimal_places=2, blank=True,
                                           null=True)

    def __unicode__(self):
        return self.nome

    class Meta:
        ordering = ['-id']
        verbose_name = u'Analista'
        verbose_name_plural = u'Analistas'


# Nota
class Nota(models.Model):
    cliente = models.ForeignKey("Cliente")
    inclusao = models.DateField("Data de inclusão", default=timezone.now)
    mes_competencia = models.IntegerField(u"Mês", choices=MONTH_CHOICES,
                                          default=datetime.now().month)
    ano_competencia = models.IntegerField(u'Ano', choices=YEAR_CHOICES,
                                          default=datetime.now().year)
    valor = models.DecimalField('Valor', max_digits=8, decimal_places=2, default=0)
    imposto = models.DecimalField('Imposto', max_digits=8, decimal_places=2, blank=True, null=True, default=0)
    baixa = models.DateField("Baixa", blank=True, null=True)

    def save(self, *args, **kwargs):

        receber = Receber.objects.filter(nota=self)
        if receber:
            self.valor = receber.aggregate(total_valor=Sum('valor')).get('total_valor', 0.00)
            self.imposto = receber.aggregate(total_imposto=Sum('imposto')).get('total_imposto', 0.00)
        else:
            self.valor = 0.00
            self.imposto = 0.00

        if self.imposto:
            # Gera contas a pagar de imposto
            try:
                pagar_imposto = Pagar.objects.get(nota=self)
            except Pagar.DoesNotExist:
                pagar_imposto = None

            if pagar_imposto:
                pagar_imposto.mes_competencia = self.mes_competencia
                pagar_imposto.ano_competencia = self.ano_competencia
                pagar_imposto.valor = self.imposto
            else:
                pagar_imposto = Pagar.objects.create(fornecedor=self.cliente.fornecedor_imposto,
                                                     tipo='IMP',
                                                     mes_competencia=self.mes_competencia,
                                                     ano_competencia=self.ano_competencia,
                                                     valor=self.imposto,
                                                     )
            # Relaciona o titulo de imposto com o tittulo do contas a receber
            if pagar_imposto:
                pagar_imposto.nota = self
                pagar_imposto.save()

        super(Nota, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'Nota '+str(self.id)

    class Meta:
        ordering = ['-id']
        verbose_name = u'Nota'
        verbose_name_plural = u'Notas'


# Contas a receber
class Receber(models.Model):
    nota = models.ForeignKey("Nota")
    cliente = models.ForeignKey("Cliente")
    natureza = models.ForeignKey("Natureza")
    analista = models.ForeignKey("Analista")
    inclusao = models.DateField("Data de inclusão", default = timezone.now)
    mes_competencia = models.IntegerField(u"Mês de competência", choices=MONTH_CHOICES,
                                          default=datetime.now().month)
    ano_competencia = models.IntegerField(u'Ano de competência', choices=YEAR_CHOICES,
                                          default=datetime.now().year)
    valor = models.DecimalField('Valor', max_digits=8, decimal_places=2)
    imposto = models.DecimalField('Imposto', max_digits=8, decimal_places=2, blank=True, null=True)
    taxa = models.DecimalField('Taxa', max_digits=8, decimal_places=2, blank=True, null=True)
    valor_repasse = models.DecimalField('Valor repasse', max_digits=8, decimal_places=2, blank=True, null=True)
    liquido = models.DecimalField('Valor líquido', max_digits=8, decimal_places=2, blank=True, null=True)
    baixa = models.DateField("Data de baixa", blank=True, null=True)

    def save(self, *args, **kwargs):
        # atualiza os campos chaves pela nota
        if self.nota:
            self.inclusao = self.nota.inclusao
            self.cliente = self.nota.cliente
            self.mes_competencia = self.nota.mes_competencia
            self.ano_competencia = self.nota.ano_competencia
            self.baixa = self.nota.baixa

        # Calcula valor de imposto com base na natureza
        if self.natureza.aliquota_imposto > 0:
            self.imposto = self.imposto = self.valor*self.natureza.aliquota_imposto/100
        else:
            self.imposto = 0

        # Calcula valor de taxa com base na natureza
        if self.natureza.aliquota_repasse > 0:
            self.taxa = self.valor*(100-self.natureza.aliquota_repasse)/100
        else:
            self.taxa = 0

        # Calcula valor de repasse com base na natureza
        if self.natureza.aliquota_repasse > 0:
            self.valor_repasse = self.valor - self.imposto - self.taxa
        else:
            self.valor_repasse = 0

        # Calcula valor líquido descontando imposto e repasse
        self.liquido = self.valor - self.imposto - self.valor_repasse

        # Gera contas a pagar de repasse, se houver na natureza
        pagar_repasse = ''
        if self.analista.fornecedor_repasse:
            # Se for alteração já possui ID
            if self.id:
                try:
                    pagar_repasse = Pagar.objects.get(receber = self)
                except Pagar.DoesNotExist:
                    pagar_repasse = None
            # Se for alteração, somente realiza a atualização
            if pagar_repasse:
                pagar_repasse.mes_competencia = self.mes_competencia
                pagar_repasse.ano_competencia = self.ano_competencia
                pagar_repasse.valor  =self.valor_repasse
            else:
                pagar_repasse = Pagar.objects.create(fornecedor=self.analista.fornecedor_repasse,
                                                     tipo='REP',
                                                     mes_competencia=self.mes_competencia,
                                                     ano_competencia=self.ano_competencia,
                                                     valor=self.valor_repasse,
                                                     )

        super(Receber, self).save(*args, **kwargs)

        # Relaciona o titulo de repasse com o tittulo do contas a receber
        if pagar_repasse:
            pagar_repasse.receber = self
            pagar_repasse.save()

        # Atualiza o valor da nota
        self.nota.save()

    def __unicode__(self):
        return u'Título '+str(self.id)

    class Meta:
        ordering = ['-id']
        verbose_name = u'Conta a receber'
        verbose_name_plural = u'Contas a receber'


# Contas a pagar
class Pagar(models.Model):
    fornecedor = models.ForeignKey("Fornecedor")
    inclusao = models.DateField("Data de inclusão", default = timezone.now)
    tipo = models.CharField(choices=TIPO_CHOICES, max_length=3)
    mes_competencia = models.IntegerField(u"Mês de competência", choices=MONTH_CHOICES, default=datetime.now().month)
    ano_competencia = models.IntegerField(u'Ano de competência', choices=YEAR_CHOICES, default=datetime.now().year)
    valor = models.DecimalField('Valor a pagar', max_digits=8, decimal_places=2, default=0)
    transferencia = models.DecimalField(u'Transferência', max_digits=8, decimal_places=2, blank=True, null=True,
                                        default=0)
    desconto = models.DecimalField(u'Desconto', max_digits=8, decimal_places=2, blank=True, null=True, default=0)
    liquido = models.DecimalField('Valor a repassar', max_digits=8, decimal_places=2, blank=True, null=True)
    baixa = models.DateField("Data de baixa", blank=True, null=True)
    receber = models.ForeignKey("Receber", blank=True, null=True)
    nota_debito = models.ForeignKey(u'NotaDebito', blank=True, null=True)
    nota = models.ForeignKey(u'Nota', blank=True, null=True)

    def save(self, *args, **kwargs):
        # Preenche o valor de transferência
        self.transferencia = self.fornecedor.doc_ted

        # Calcula o valor líquido
        self.liquido = self.valor-self.transferencia+self.desconto

        super(Pagar, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'Título ' + str(self.id)

    class Meta:
        ordering = ['-id']
        verbose_name = u'Conta a pagar'
        verbose_name_plural = u'Contas a pagar'


# Nota de debito
class NotaDebito(models.Model):
    inclusao = models.DateField("Data de inclusão", default = timezone.now)
    mes_competencia = models.IntegerField(u"Mês de competência", choices=MONTH_CHOICES, default=datetime.now().month)
    ano_competencia = models.IntegerField(u'Ano de competência', choices=YEAR_CHOICES, default=datetime.now().year)
    valor = models.DecimalField('Valor', max_digits=8, decimal_places=2)
    valor_repasse = models.DecimalField('Valor repasse', max_digits=8, decimal_places=2, blank=True, null=True)
    taxa = models.DecimalField('Taxa', max_digits=8, decimal_places=2, blank=True, null=True)
    liquido = models.DecimalField('Valor líquido', max_digits=8, decimal_places=2, blank=True, null=True)
    baixa = models.DateField("Data de baixa", blank=True, null=True)
    despesa = models.CharField(u"Código da despesa", max_length=10)
    despesa_antiga = models.CharField("Código nota antiga", max_length=8, blank=True, null=True)
    analista = models.ForeignKey("Analista")
    cliente_atendimento = models.ForeignKey("Cliente", related_name="Cliente_atendimento")

    def save(self, *args, **kwargs):
        # Calcula valor de repasse com base na natureza
        if self.analista.aliquota_despesa > 0:
            self.valor_repasse = self.valor * self.analista.aliquota_despesa / 100
        else:
            self.valor_repasse = 0

        # Calcula valor líquido descontando imposto e repasse
        self.liquido = self.valor - self.valor_repasse

        # Gera contas a pagar de repasse, se houver na natureza
        pagar_repasse = ''
        if self.analista.fornecedor_repasse:
            # Se for alteração já possui ID
            if self.id:
                try:
                    pagar_repasse = Pagar.objects.get(nota_debito=self)
                except Pagar.DoesNotExist:
                    pagar_repasse = None
            # Se for alteração, somente realiza a atualização
            if pagar_repasse:
                pagar_repasse.mes_competencia = self.mes_competencia
                pagar_repasse.ano_competencia = self.ano_competencia
                pagar_repasse.valor=self.valor_repasse
            else:
                pagar_repasse = Pagar.objects.create(fornecedor=self.analista.fornecedor_repasse,
                                                     tipo='NDE',
                                                     mes_competencia=self.mes_competencia,
                                                     ano_competencia=self.ano_competencia,
                                                     valor=self.valor_repasse,
                                                     )

        super(NotaDebito, self).save(*args, **kwargs)

        # Relaciona o titulo de repasse com o titulo do contas a receber
        if pagar_repasse:
            pagar_repasse.nota_debito = self
            pagar_repasse.save()

    def __unicode__(self):
        return 'ND '+str(self.id)

    class Meta:
        ordering = ['-id']
        verbose_name = u'Nota de débito'
        verbose_name_plural = u'Notas de débito'
