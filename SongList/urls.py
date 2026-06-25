from django.urls import path
from SongList import views

app_name = "SongList"

urlpatterns = [
    path("variasmusicas/", views.MusicasView.as_view(), name='varias-musicas'),
    path('criar/', views.MusicaCreateView.as_view(), name='criar-musica'),
    path('umamusica/<int:pk>/', views.MusicaView.as_view(), name='uma-musica'),
]
