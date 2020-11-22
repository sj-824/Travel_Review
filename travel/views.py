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
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
from django.http import HttpResponse
import numpy as np
from django.db.models import Q
User = get_user_model()
# Create your views here.

class Login(LoginView):
    """ログインページ"""
    form_class = LoginForm
    template_name = 'login.html'

class Logout(LogoutView):
    """ログアウトページ"""
    template_name = 'list_review.html'
    model = TravelModel

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
    fields = (
        'prefecture','spot_name','stay_time','useful_review_record',
        'user_value1','user_value2','user_value3','user_value4','user_value5',
        'user_name'
        )
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

def setPlt(pk):
    value = TravelModel.objects.get(pk = pk)
    values = [value.user_value1,value.user_value2,value.user_value3,value.user_value4,value.user_value5]
    labels = ['青春','恋愛','バトル','シリアス','面白い']
    rader_values = np.concatenate([values, [values[0]]])
    angles = np.linspace(0,2*np.pi,len(labels) + 1, endpoint = True)
    rgrids = [0,1,2,3,4,5]

    fig = plt.figure (facecolor = 'w')
    ax = fig.add_subplot(1,1,1,polar = True)
    ax.plot(angles, rader_values)
    ax.fill(angles, rader_values, alpha = 0.2)
    ax.set_thetagrids(angles[:-1]*180/np.pi,labels,fontname = 'Source Han Code JP')
    ax.set_rgrids([])
    ax.spines['polar'].set_visible(False)
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)

    for grid_value in rgrids:
        grid_values = [grid_value] * (len(labels) + 1)
        ax.plot(angles, grid_values, color = 'gray', linewidth = 0.5)
    
    for t in rgrids:
        ax.text(x = 0,y = t, s = t)
    
    ax.set_rlim([min(rgrids), max(rgrids)])
    ax.set_title ('ジャンル', fontname = 'Source Han Code JP', pad = 20)

def plt2SVG():
    buf = io.BytesIO()
    plt.savefig(buf,format = 'svg',bbox_inches = 'tight')
    s = buf.getvalue()
    buf.close()
    return s

def get_svg(request,pk):
    setPlt(pk)
    svg = plt2SVG()
    plt.cla()
    response = HttpResponse(svg, content_type = 'image/svg+xml')
    return response

def search_list(request):
    query = request.GET.get('q')
    if query:
        object_list = TravelModel.objects.all().order_by('travel_date')
        object_list = object_list.filter(
            Q(prefecture__icontains=query)|
            Q(user_name__username__icontains=query)
            ).distinct()
    else:
        posts = Post.objects.all().order_by('created_at')
    return render(request, 'list_review.html', {'object_list' : object_list, 'query' : query})