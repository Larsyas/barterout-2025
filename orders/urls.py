from django.urls import path
from . import views


urlpatterns = [
    path('place_order/', views.place_order, name='place_order'),  # type:ignore
    path('payments/', views.payments, name='payments'),  # type:ignore
    path('process_payment/<str:order_number>/',
         views.process_payment, name='process_payment'),
]
