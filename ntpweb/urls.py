# C:\Users\91981\Desktop\Django_project\ntpweb\urls.py
from django.urls import path
from ntpweb.views import get_ntp_time, dynamic_graph, ntp_data, SearchView, csrf_token_view

urlpatterns = [
    path('', ntp_data, name='ntp_data'),
    path('api/dynamic-graph/',dynamic_graph, name='dynamic_graph'),
    path('api/search/',SearchView.as_view(), name='search_view'),
    path('api/get-ntp-time/',get_ntp_time, name='get_ntp_time'),
    path('api/csrf_token/',csrf_token_view, name='csrf_token'),
]
