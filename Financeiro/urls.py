# -*- encoding: utf-8 -*-

# bibliotecas django
from django.conf.urls import url

from .views import notaDebitoPDF, notaDebito

urlpatterns = [
    url(r'^financeiro/notaDebitoPDF/(?P<idNota>\d+)/$', notaDebitoPDF, name='notaDebitoPDF'),
    url(r'^financeiro/notaDebito/(?P<idNota>\d+)/$', notaDebito, name='notaDebito'),
]
