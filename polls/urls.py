from django import views
from django.urls import path

app_name = 'polls'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('<int:pk>/results/', views.ResuitsView.as_view(), name='results'),
    path('<int:question_id>/vote/', views.vote, name='vote'),
]