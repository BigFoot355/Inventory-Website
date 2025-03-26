# inventory/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register_component/', views.register_component, name='register_component'),
    path('edit/<int:component_id>/', views.edit_component, name='edit_component'),
    path('delete/<int:component_id>/', views.delete_component, name='delete_component'),
    path('give_low/<int:component_id>/', views.give_low, name='give_low'),
    path('create_room/', views.create_room, name='create_room'),
    path('create_cabinet/', views.create_cabinet, name='create_cabinet'),
    path('export_excel/', views.export_excel, name='export_excel'),
    path('export_pdf/', views.export_pdf, name='export_pdf'),
    # Novas rotas para exclusão
    path('delete_page/', views.delete_page, name='delete_page'),
    path('delete_room/<int:room_id>/', views.delete_room, name='delete_room'),
    path('delete_cabinet/<int:cabinet_id>/', views.delete_cabinet, name='delete_cabinet'),
]