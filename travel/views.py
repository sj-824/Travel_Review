from django.shortcuts import render,redirect
from .models import User, AnimeModel, ReviewModel, User_Profile, Access_Counter
from django.views.generic import CreateView,DeleteView,UpdateView,ListView
from django.urls import reverse_lazy 
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (LoginView, LogoutView)
from django.views import generic
from .forms import (LoginForm, UserCreateForm, CreateForm, Create_UserProfile)
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
from datetime import timedelta
from django.utils import timezone
import random
import math

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

def user_profile_create(request):
    if request.method == 'POST':
        form = Create_UserProfile(request.POST)
        if form.is_valid():
            object = form.save(commit = False)
            object.user_name = request.user
            object.save()
            return redirect('user_list')
    else:
        form = Create_UserProfile
    return render(request,'user_profile_create.html',{'form' : form})

def detail_review(request,pk):
    evaluation(request,pk)
    object = ReviewModel.objects.get(pk = pk)
    user_name = request.user
    access_counter_object = Access_Counter.objects.filter(access_name = user_name).filter(review = object)
    print(access_counter_object)
    if not access_counter_object:
        access_counter = Access_Counter(access_name = user_name, review = object)
        access_counter.save()
    
    ###レビュー者のおすすめを表示###
    object_list = ReviewModel.objects.all().filter(user_name = object.user_name).filter(user_value_ave__gt = 4.5)
    random_list = []
    object_list_num = []
    if object_list.count() < 2:
        return render(request,'detail_review.html',{'object' : object})
    elif object_list.count() <= 3:
        return render(request,'detail_review.html',{'object' : object,'object_list' : object_list})
    elif object_list.count() > 3:
        for item in object_list:
            object_list_num.append(item.user_Anime.id)
        random_list = random.sample(object_list_num,3)
        object_list = object_list.filter(
            Q(user_Anime__id = random_list[0])|
            Q(user_Anime__id = random_list[1])|
            Q(user_Anime__id = random_list[2])).distinct()
        return render (request,'detail_review.html', {'object' : object, 'object_list' : object_list})

def evaluation(request,pk):
    object = ReviewModel.objects.get(pk=pk)
    user_name = request.user.username
    anime = Access_Counter.objects.all().filter(access_name = user_name).filter(review__user_Anime = object.user_Anime)
    print(anime)
    if not anime and user_name != object.user_name.username:
        ###アニメの平均値###
        anime_title = ReviewModel.objects.filter(user_Anime = object.user_Anime)
        object_num = anime_title.count()
        user_value_sum = [0,0,0,0,0]
        for item in anime_title:
            user_value = [item.user_value1,item.user_value2,item.user_value3,item.user_value4,item.user_value5]
            user_value_sum += np.array(user_value)
        user_value_ave = []
        for i in range(0,5):
            ave = user_value_sum[i]/object_num
            user_value_ave.append(ave)
        values = user_value_ave
        ###保存###
        user_profile = User_Profile.objects.get(user_name = user_name)
        print(user_profile)
        if object.user_Anime.anime_genre == 'SF':
                user_profile.count_SF += 1
                user_profile.SF_sum_value1 += values[0]
                user_profile.SF_sum_value2 += values[1]
                user_profile.SF_sum_value3 += values[2]
                user_profile.SF_sum_value4 += values[3]
                user_profile.SF_sum_value5 += values[4]
                user_profile.save()
        
        if object.user_Anime.anime_genre == 'ギャグ':
                user_profile.count_gag += 1
                user_profile.gag_sum_value1 += values[0]
                user_profile.gag_sum_value2 += values[1]
                user_profile.gag_sum_value3 += values[2]
                user_profile.gag_sum_value4 += values[3]
                user_profile.gag_sum_value5 += values[4]
                user_profile.save()
        
        if object.user_Anime.anime_genre == '恋愛':
                user_profile.count_love += 1
                user_profile.love_sum_value1 += values[0]
                user_profile.love_sum_value2 += values[1]
                user_profile.love_sum_value3 += values[2]
                user_profile.love_sum_value4 += values[3]
                user_profile.love_sum_value5 += values[4]
                user_profile.save()
        
        if object.user_Anime.anime_genre == '青春':
                user_profile.count_youth += 1
                user_profile.youth_sum_value1 += values[0]
                user_profile.youth_sum_value2 += values[1]
                user_profile.youth_sum_value3 += values[2]
                user_profile.youth_sum_value4 += values[3]
                user_profile.youth_sum_value5 += values[4]
                user_profile.save()
        
        if object.user_Anime.anime_genre == 'ホラー':
                user_profile.count_horor += 1
                user_profile.horor_sum_value1 += values[0]
                user_profile.horor_sum_value2 += values[1]
                user_profile.horor_sum_value3 += values[2]
                user_profile.horor_sum_value4 += values[3]
                user_profile.horor_sum_value5 += values[4]
                user_profile.save()
        
        if object.user_Anime.anime_genre == '日常':
                user_profile.count_everyday += 1
                user_profile.everyday_sum_value1 += values[0]
                user_profile.everyday_sum_value2 += values[1]
                user_profile.everyday_sum_value3 += values[2]
                user_profile.everyday_sum_value4 += values[3]
                user_profile.everyday_sum_value5 += values[4]
                user_profile.save()

        if object.user_Anime.anime_genre == 'ミステリー':
                user_profile.count_mystery += 1
                user_profile.mystery_sum_value1 += values[0]
                user_profile.mystery_sum_value2 += values[1]
                user_profile.mystery_sum_value3 += values[2]
                user_profile.mystery_sum_value4 += values[3]
                user_profile.mystery_sum_value5 += values[4]
                user_profile.save()

        if object.user_Anime.anime_genre == 'バトル':
                user_profile.count_battle += 1
                user_profile.battle_sum_value1 += values[0]
                user_profile.battle_sum_value2 += values[1]
                user_profile.battle_sum_value3 += values[2]
                user_profile.battle_sum_value4 += values[3]
                user_profile.battle_sum_value5 += values[4]
                user_profile.save()
        
   
@require_POST
def delete_review(request,pk):
    article = ReviewModel.objects.get(pk = pk)
    article.delete()
    return redirect('user_list')

def list_review(request):
    ###今週のおすすめ###
    object_list = ReviewModel.objects.all().order_by('-post_date')
    today = timezone.now()
    limited_day = (today-timedelta(days = 7,))
    r = ReviewModel.objects.filter(post_date__range=(limited_day,today))
    s = r.values('user_Anime').annotate(kensu=Count('id')).order_by('-user_Anime__id')
    num = (s[0]['user_Anime'])
    object_1 = AnimeModel.objects.filter(id = num)
    high_post_anime = object_1[0]
    
    ###あなたへのおすすめ###

    ###ジャンルごとのuserの平均評価の取得###
    user_profile = User_Profile.objects.get(user_name = request.user)
    genre_count = {
        'SF' : user_profile.count_SF,
        'ギャグ' : user_profile.count_gag,
        '恋愛' : user_profile.count_love,
        '青春' : user_profile.count_youth,
        'ホラー' : user_profile.count_horor,
        '日常' : user_profile.count_everyday,
        'ミステリー' : user_profile.count_mystery,
        'バトル' : user_profile.count_battle,
        }
    print(genre_count)
    genre_max = max(genre_count, key = genre_count.get)
    count_max = max(genre_count.values())
    print(genre_max)

    if genre_max == 'SF':
        access_val_sum = [
            user_profile.SF_sum_value1,
            user_profile.SF_sum_value2,
            user_profile.SF_sum_value3,
            user_profile.SF_sum_value4,
            user_profile.SF_sum_value5,
            ]

    if genre_max == 'ギャグ':
        access_val_sum = [
            user_profile.SF_sum_value1,
            user_profile.SF_sum_value2,
            user_profile.SF_sum_value3,
            user_profile.SF_sum_value4,
            user_profile.SF_sum_value5,
            ]

    if genre_max == '恋愛':
        access_val_sum = [
            user_profile.SF_sum_value1,
            user_profile.SF_sum_value2,
            user_profile.SF_sum_value3,
            user_profile.SF_sum_value4,
            user_profile.SF_sum_value5,
            ]

    if genre_max == '青春':
        access_val_sum = [
            user_profile.SF_sum_value1,
            user_profile.SF_sum_value2,
            user_profile.SF_sum_value3,
            user_profile.SF_sum_value4,
            user_profile.SF_sum_value5,
            ]

    if genre_max == 'ホラー':
        access_val_sum = [
            user_profile.SF_sum_value1,
            user_profile.SF_sum_value2,
            user_profile.SF_sum_value3,
            user_profile.SF_sum_value4,
            user_profile.SF_sum_value5,
            ]

    if genre_max == '日常':
        access_val_sum = [
            user_profile.SF_sum_value1,
            user_profile.SF_sum_value2,
            user_profile.SF_sum_value3,
            user_profile.SF_sum_value4,
            user_profile.SF_sum_value5,
            ]

    if genre_max == 'ミステリー':
        access_val_sum = [
            user_profile.SF_sum_value1,
            user_profile.SF_sum_value2,
            user_profile.SF_sum_value3,
            user_profile.SF_sum_value4,
            user_profile.SF_sum_value5,
            ]

    if genre_max == 'バトル':
        access_val_sum = [
            user_profile.SF_sum_value1,
            user_profile.SF_sum_value2,
            user_profile.SF_sum_value3,
            user_profile.SF_sum_value4,
            user_profile.SF_sum_value5,
            ]

    access_val_ave = []
    for i in range(0,5):
        ave = access_val_sum[i]/count_max
        access_val_ave.append(ave)
    print(access_val_ave)

   ###各アニメの平均評価の取得###
    value_dict = {}
    user_value_sum = [0,0,0,0,0]
    for anime in AnimeModel.objects.filter(anime_genre = genre_max):
        review_all = ReviewModel.objects.all().filter(user_Anime__id = anime.id)
        for item in review_all:
            user_value = [item.user_value1,item.user_value2,item.user_value3,item.user_value4,item.user_value5]
            user_value_sum += np.array(user_value)
            user_value_ave = []
            for i in range(0,5):
                ave = user_value_sum[i]/review_all.count()
                user_value_ave.append(ave)
            value_dict[item.user_Anime.anime_title] = user_value_ave
        user_value_sum = [0,0,0,0,0]
    print(value_dict)

    ###類似性の高いアニメの抽出###
    similarity = {}
    for title,value in value_dict.items():
        value_sub = np.array(value) - np.array(access_val_ave)
        value_sub_sqr = map(lambda x : x**2, value_sub)
        similarity[title] = math.sqrt(sum(value_sub_sqr))
    anime_title = min(similarity,key = similarity.get)
    print(anime_title)
    high_similarity_anime = AnimeModel.objects.get(anime_title = anime_title)
    print(high_similarity_anime)
    return render (request,'list_review.html',{'object_list' : object_list,'high_post_anime' : high_post_anime, 'high_similarity_anime' : high_similarity_anime})

def setPlt(pk):
    ###レビュー者の評価###
    value = ReviewModel.objects.get(pk = pk)
    values = [value.user_value1,value.user_value2,value.user_value3,value.user_value4,value.user_value5]
    labels = ['シナリオ','作画','キャラクター','音楽','声優']
    rader_values = np.concatenate([values, [values[0]]])
    angles = np.linspace(0,2*np.pi,len(labels) + 1, endpoint = True)
    rgrids = [0,1,2,3,4,5]

    ###全体の平均評価###
    anime_title = ReviewModel.objects.filter(user_Anime__pk = value.user_Anime.pk)
    object_num = anime_title.count()
    user_value_sum = [0,0,0,0,0]
    for item in anime_title:
        user_value = [item.user_value1,item.user_value2,item.user_value3,item.user_value4,item.user_value5]
        user_value_sum += np.array(user_value)
    user_value_ave = []
    for i in range(0,5):
        ave = user_value_sum[i]/object_num
        user_value_ave.append(ave)
    values = user_value_ave
    rader_values_ave = np.concatenate([values, [values[0]]])

#######グラフ作成##########
    fig = plt.figure (facecolor = 'w')
    ax = fig.add_subplot(1,1,1,polar = True)
    ax.plot(angles, rader_values, color = 'r', label = 'Reviwer.')
    ax.plot(angles,rader_values_ave, color = 'b', label = 'Ave.')
    ax.fill(angles, rader_values_ave, alpha = 0.1, facecolor = 'b')
    ax.fill(angles, rader_values, alpha = 0.2, facecolor = 'r')
    ax.set_thetagrids(angles[:-1]*180/np.pi,labels,fontname = 'Source Han Code JP')
    ax.set_rgrids([])
    ax.spines['polar'].set_visible(False)
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.legend(bbox_to_anchor = (1.05,1.0), loc = 'upper left')

    for grid_value in rgrids:
        grid_values = [grid_value] * (len(labels) + 1)
        ax.plot(angles, grid_values, color = 'gray', linewidth = 0.5)
    
    for t in rgrids:
        ax.text(x = 0,y = t, s = t)
    
    ax.set_rlim([min(rgrids), max(rgrids)])
    ax.set_title ('評価', fontname = 'Source Han Code JP', pad = 20)

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

