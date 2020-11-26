from django.shortcuts import render,redirect
from .models import User, AnimeModel, ReviewModel
from django.views.generic import CreateView,DeleteView,UpdateView,ListView
from django.urls import reverse_lazy 
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (LoginView, LogoutView)
from django.views import generic
from .forms import (LoginForm, UserCreateForm, CreateForm)
from django.contrib.auth import login, authenticate, get_user_model, logout
from .forms import UserCreateForm
from django.views.decorators.http import require_POST
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
from django.http import HttpResponse
import numpy as np
from django.db.models import Q, Count, Avg
from datetime import date, timedelta

User = get_user_model()
# Create your views here.

class Login(LoginView):
    """ログインページ"""
    form_class = LoginForm
    template_name = 'login.html'

class Logout(LogoutView):
    """ログアウトページ"""
    template_name = 'list_review.html'
    model = ReviewModel

class UserCreate(generic.CreateView):
    form_class = UserCreateForm
    success_url = reverse_lazy('list_review')
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

# def userrecreate(request):
#     if request.method == 'POST':
#         name = request.POST.get('name')
#         password = request.POST.get('passward')
#         if User.objects.get(username = name):
#             user = User.objects.get(username = name)
#             user.is_active = True
#             user.save()
#             print('A')
#             return render(request,'user_list.html')
#         else:
#             return render(request,'user_recreate.html')
#             print('accountがありません')    
#     else:
#         print('C')
#         return render(request,'user_recreate.html')

def userlist(request):
    user_name = request.user.username
    object_list = ReviewModel.objects.filter(user_name = user_name)
    return render(request,'user_list.html', {'object_list' : object_list})

def createreview(request):
    if request.method == 'POST':
        form = CreateForm(request.POST)
        query = request.POST.get('q')
        items = AnimeModel.objects.all()
        for item in items:
            if query == item.anime_title or query == item.anime_title_abb:
                Anime_object = item
        if form.is_valid():
            object = form.save(commit = False)
            object.user_Anime = Anime_object
            user_value_ave = (object.user_value1 + object.user_value2 + object.user_value3 + object.user_value4 + object.user_value5)/5
            object.user_value_ave = user_value_ave
            object.save()
            return redirect('detail_review',pk = object.pk)
    else:
        form  = CreateForm
    return render(request,'create_review.html',{'form' : form})

def detail_review(request,pk):
    object = ReviewModel.objects.get(pk = pk)
    return render (request,'detail_review.html', {'object' : object})

@require_POST
def delete_review(request,pk):
    article = ReviewModel.objects.get(pk = pk)
    article.delete()
    return redirect('user_list')

def list_review(request):
    object_list = ReviewModel.objects.all().order_by('post_date')
    today = date.today()
    limited_day = (today-timedelta(days = 7))
    r = ReviewModel.objects.filter(post_date__range=(limited_day,today))
    s = r.values('user_Anime').annotate(kensu=Count('id')).order_by('-user_Anime__id')
    num = (s[0]['user_Anime'])
    object_1 = AnimeModel.objects.filter(id = num)
    high_post_anime = object_1[0]
    return render (request,'list_review.html',{'object_list' : object_list,'high_post_anime' : high_post_anime})

def setPlt(pk):
    value = ReviewModel.objects.get(pk = pk)
    values = [value.user_value1,value.user_value2,value.user_value3,value.user_value4,value.user_value5]
    labels = ['シナリオ','作画','キャラクター','音楽','声優']
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
        object_list = ReviewModel.objects.all().order_by('post_date')
        object_list = object_list.filter(
            Q(user_Anime__anime_title__icontains=query)|
            Q(user_Anime__anime_title_abb__icontains=query)|
            Q(user_name__username__icontains=query)
            ).distinct()
    else:
        posts = Post.objects.all().order_by('created_at')
    return render(request, 'list_review.html', {'object_list' : object_list, 'query' : query})

