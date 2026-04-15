from django.urls import path
from .views import HostDetailCreateUpdateView, HostListView, SendMailView, CanCallView

urlpatterns = [
    path('host/', HostDetailCreateUpdateView.as_view(), name='host-create-update'),
    path('hosts/', HostListView.as_view(), name='host-list'),
        path('send-mail/', SendMailView.as_view(), name='send-mail'),
    path('can-call/', CanCallView.as_view(), name='can-call'),

]