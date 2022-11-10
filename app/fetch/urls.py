from django.urls import path

from fetch import views

# app name for reverse mapping
app_name = 'fetch'

urlpatterns = [
    path('data/', views.FetchAPIView.as_view(), name='data'),
]
