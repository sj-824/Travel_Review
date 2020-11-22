from django.urls import path
from . import views 

urlpatterns = [
    path('',views.Top.as_view(), name = 'top'),
    path('login/',views.Login.as_view(),name = 'login'),
    path('logout/',views.Logout.as_view(), name = 'logout'),
    path('user_create/',  views.UserCreate.as_view(), name = 'user_create'),
    path('user_delete/', views.UserDelete.as_view(), name = 'user_delete'),
    path('user_list/', views.userlist, name = 'user_list'),
    path('create_review/', views.CreateReview.as_view(), name = 'create_review'),
    path('detail_review/<int:pk>',views.detail_review, name = 'detail_review'),
    path('delete_review/<int:pk>',views.delete_review, name = 'delete_review'),
    path('list_review',views.list_review, name = 'list_review'),
]