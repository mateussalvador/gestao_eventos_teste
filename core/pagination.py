from rest_framework.pagination import PageNumberPagination

class CustomPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'tamanho'
    max_page_size = 100

# Configuração básica de logging para registrar eventos importantes