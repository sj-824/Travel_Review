from django.shortcuts import render,redirect
from .models import TravelModel, User
from django.views.generic import CreateView,DeleteView,UpdateView,ListView
from django.urls import reverse_lazy 
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (LoginView, LogoutView)
from django.views import generic
from .forms import (LoginForm, UserCreateForm)
from django.contrib.auth import login, authenticate, get_user_model, logout
from .forms import UserCreateForm
from django.views.decorators.http import require_POST

User = get_user_model()
# Create your views here.

class Top(generic.TemplateView):
    template_name = 'top.html'


class Login(LoginView):
    """ログインページ"""
    form_class = LoginForm
    template_name = 'login.html'

class Logout(LogoutView):
    """ログアウトページ"""
    template_name = 'top.html'

class UserCreate(generic.CreateView):
    form_class = UserCreateForm
    success_url = reverse_lazy('top')
    template_name = 'signup.html'

    def form_valid(self,form):
        response = super().form_valid(form)
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(username = username, password = password)
        login(self.request,user)
        return response

class UserDelete(LoginRequiredMixin, generic.View):

    def get(self, *args, **kwargs):
        user = User.objects.get(username = self.request.user.username)
        user.is_active = False
        user.save()
        logout(self.request)
        return render(self.request,'user_delete.html')

def userlist(request):
    user_name = request.user.username
    object_list = TravelModel.objects.filter(user_name = user_name)
    return render(request,'user_list.html', {'object_list' : object_list})

class CreateReview(CreateView):
    model = TravelModel
    template_name = 'review_create.html'
    fields = ('prefecture','spot_name','stay_time','useful_review_record','user_value','user_name')
    success_url = reverse_lazy('user_list')

def detail_review(request,pk):
    object = TravelModel.objects.get(pk = pk)
    return render (request,'detail_review.html', {'object' : object})

@require_POST
def delete_review(request,pk):
    article = TravelModel.objects.get(pk = pk)
    article.delete()
    return redirect('user_list')

def list_review(request):
    object_list = TravelModel.objects.all()
    return render (request,'list_review.html',{'object_list' : object_list})

   