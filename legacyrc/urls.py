from django.urls import path
from .views import (
    RCDetailCreateView,
    OldRcCreateView,
    RCDetailView,
    search_rc,
    delete_rc,
    fetch_reg_detail,
)

urlpatterns = [
    path("new_create_rc/", RCDetailCreateView.as_view(), name="legacy-newrc-create"),
    path("old_create_rc/", OldRcCreateView.as_view(), name="legacy-oldrc-create"),
    path("rc/<str:rc_type>/<str:reg_number>/", RCDetailView.as_view(), name="legacy-rc-detail"),
    path("search_rc/", search_rc, name="legacy-search_rc"),
    path("delete_rc/", delete_rc, name="legacy-delete-rc"),
    path("reg_detail/", fetch_reg_detail, name="legacy-reg-detail"),
]
