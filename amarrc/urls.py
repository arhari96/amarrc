"""
URL configuration for amarrc project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from smartrc.views import NewRcCreateView, OldRcCreateView, search_rc, delete_rc
from balance.views import BalanceListView
import smartrc.views as views
from django.urls import path, re_path

urlpatterns = [
    re_path(r"^$", views.ReactAppView.as_view(), name="react-app-view"),
    path("admin/", admin.site.urls),
    path("api/new_create_rc/", NewRcCreateView.as_view(), name="newrc-create"),
    path("api/old_create_rc/", OldRcCreateView.as_view(), name="oldrc-create"),
    path("api/search_rc/", search_rc, name="search_rc"),
    path("api/delete_rc/", delete_rc, name="delete-rc"),
    path("api/balance_list/", BalanceListView.as_view(), name="balance-list"),
    # path("frontrc/<str:reg_number>/", views.delete_frontrc, name="delete_frontrc"),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
