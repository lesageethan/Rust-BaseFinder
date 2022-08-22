from django.shortcuts import render
from django.template import loader
from .models import base
from .models import hit
from .models import rating
from .forms import SubmissionForm
from .forms import SearchForm
from .forms import SignUpForm
from .forms import LogInForm
from .forms import RatingForm
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from urllib.parse import urlparse, parse_qs
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout

TABLEROWTEMPLATE = """
<tr class="item">
    <th scope="row">
        <a href="/base_id/{}">{}</a><br>
        <img class="thumbnail" src="https://img.youtube.com/vi/{}/hqdefault.jpg"><br>
        <small>by {}</small><br>
    </th>
    <td>{}</td>
    <td>
        <p class="cost-ps bold" data-toggle="popover"  data-content="{} Stone, {} Frags, {} HiQual">{} Build</p><br>
        <p class="cost-ps" data-toggle="popover"  data-content="{} Stone, {} Frags, {} HiQual">{} Upkeep</p>
    </td>
    <td>{}</td>
    <td>{}<br><p class="stars-p">{}</p></td>
    <td>{}<button type="button" class="btn btn-secondary tag-btn">{}</button><br><button type="button" class="btn btn-secondary tag-btn">{}</button><br><button type="button" class="btn btn-secondary tag-btn">{}</button></td>
</tr>"""

def index(request):
    hit_instance = hit(page='index')
    hit_instance.save()
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            dbItems = base.objects.all().order_by('-efficiency_score')
            suitableBase = findSuitableBase(dbItems, form)
            if (suitableBase == False):
                message = 'Sorry, we could not find any bases within your budget. Try reducing your group size.'
                context = {'message' : message}
                return render(request, 'table/message.html', context)
            else:
                return HttpResponseRedirect(str('/base_id/'+str(suitableBase.pk)))
    else:
        form = SearchForm()
        totalTable = ""
        dbItems = base.objects.all().order_by('-id')[:5]
        for i in dbItems:
            eValue = i.efficiency_score
            if eValue > 0.1:
                eValue = 0.1
            efficiency = int(eValue//0.02)
            stars = "&#9733;"*efficiency + "&#9734;"*(5-efficiency)
            videoCode = video_id(i.link)
            if i.fortify_link == 'N/A':
                fortify = ''
            else:
                fortify='<button type="button" class="btn btn-secondary tag-btn fortify-btn">Fortify</button><br>'
            tableEntry = TABLEROWTEMPLATE.format(i.pk, i.name, videoCode, i.creator, i.group_size, i.build_cost_stone, i.build_cost_frags, i.build_cost_hqm, i.build_cost_scrap, i.upkeep_cost_stone, i.upkeep_cost_frags, i.upkeep_cost_hqm, i.upkeep_cost_scrap, i.raid_cost, i.efficiency_score, stars, fortify, i.feature_1, i.feature_2, i.feature_3)
            totalTable += tableEntry
        context = {'tableItems': totalTable, 'form':form}
        return render(request, 'table/index.html', context)

def findSuitableBase(dbItems, form):
    filteredDb = []
    for i in dbItems:
        if (i.group_size >= form.cleaned_data['request_group_size']) and (i.build_cost_stone <= form.cleaned_data['budget_stone']) and (i.build_cost_frags <= form.cleaned_data['budget_frags']) and (i.build_cost_hqm <= form.cleaned_data['budget_hqm']) and (i.build_cost_stone >= (form.cleaned_data['budget_stone']*0.5-1000)) and (i.build_cost_frags >= (form.cleaned_data['budget_frags']*0.5-1000)): 
            filteredDb.append(i)
    if len(filteredDb)>0:
        bestBase = filteredDb[0]
        return bestBase
    else:
        filteredDb = []
        for i in dbItems:
            if (i.group_size >= form.cleaned_data['request_group_size']) and (i.build_cost_stone <= form.cleaned_data['budget_stone']) and (i.build_cost_frags <= form.cleaned_data['budget_frags']) and (i.build_cost_hqm <= form.cleaned_data['budget_hqm']): 
                filteredDb.append(i)
        if len(filteredDb)>0:
            bestBase = filteredDb[0]
            return bestBase
        else:
            dbItems = base.objects.all().order_by('build_cost_frags')
            filteredDb = []
            for i in dbItems:
                if (i.group_size >= form.cleaned_data['request_group_size']): 
                    filteredDb.append(i)
            if len(filteredDb)>0:
                bestBase = filteredDb[0]
                return bestBase
            else:
                return False

def about(request):
    return render(request, 'table/about.html')

def submit(request):
    if request.method == 'POST':
        form = SubmissionForm(request.POST)
        if form.is_valid():
            createBase(form)
            message = 'Your base has been submitted to BaseFinder. Thank you!'
            context = {'message' : message}
            return render(request, 'table/message.html', context)
    else:
        if request.user.is_authenticated:
            form = SubmissionForm()
            return render(request, 'table/submit.html', {'form': form})
        else:
            return render(request, 'table/message.html', {'message' : 'You must be logged in to add a base.'})

def createBase(form):
    build_cost_scrap = int(round(form.cleaned_data['build_cost_stone']/20 + form.cleaned_data['build_cost_frags']/10 + form.cleaned_data['build_cost_hqm']/0.5, 0))
    upkeep_cost_scrap = int(round(form.cleaned_data['upkeep_cost_stone']/20 + form.cleaned_data['upkeep_cost_frags']/10 + form.cleaned_data['upkeep_cost_hqm']/0.5, 0))
    efficiency_score = round(form.cleaned_data['raid_cost']/upkeep_cost_scrap, 5)
    ytlink = form.cleaned_data['link']
    ytlink = 'https://www.youtube.com/watch?v=' + video_id(ytlink)

    """if 'pastebin' in str(form.cleaned_data['fortify_link']):
        fortify = form.cleaned_data['fortify_link']
    else:
        print('////NO FORTIFY LINK TRIGGERED')"""
    fortify = 'N/A'
    base_instance = base(
    name=form.cleaned_data['name'], 
    link=ytlink, 
    creator=form.cleaned_data['creator'], 
    group_size=form.cleaned_data['group_size'], 
    build_cost_stone=form.cleaned_data['build_cost_stone'], 
    build_cost_frags=form.cleaned_data['build_cost_frags'], 
    build_cost_hqm=form.cleaned_data['build_cost_hqm'], 
    build_cost_scrap=build_cost_scrap, 
    upkeep_cost_stone=form.cleaned_data['upkeep_cost_stone'], 
    upkeep_cost_frags=form.cleaned_data['upkeep_cost_frags'], 
    upkeep_cost_hqm=form.cleaned_data['upkeep_cost_hqm'], 
    upkeep_cost_scrap=upkeep_cost_scrap, 
    raid_cost=form.cleaned_data['raid_cost'], 
    efficiency_score=efficiency_score, 
    feature_1=form.cleaned_data['feature_1'], 
    feature_2=form.cleaned_data['feature_2'], 
    feature_3=form.cleaned_data['feature_3'],
    fortify_link=fortify)
    base_instance.save()

def efficiency_leaderboard(request):
    totalTable = ""
    dbItems = base.objects.all().order_by('-efficiency_score')[:10]
    counter=0
    for i in dbItems:
        counter+=1
        eValue = i.efficiency_score
        if eValue > 0.1:
            eValue = 0.1
        efficiency = int(eValue//0.02)
        stars = "&#9733;"*efficiency + "&#9734;"*(5-efficiency)
        videoCode = video_id(i.link)
        if i.fortify_link == 'N/A':
            fortify = ''
        else:
            fortify='<button type="button" class="btn btn-secondary tag-btn fortify-btn">Fortify</button><br>'
        tableEntry = TABLEROWTEMPLATE.format(i.id, '#'+str(counter)+': '+i.name, videoCode, i.creator, i.group_size, i.build_cost_stone, i.build_cost_frags, i.build_cost_hqm, i.build_cost_scrap, i.upkeep_cost_stone, i.upkeep_cost_frags, i.upkeep_cost_hqm, i.upkeep_cost_scrap, i.raid_cost, i.efficiency_score, stars, fortify, i.feature_1, i.feature_2, i.feature_3)
        totalTable += tableEntry
    context = {'tableItems': totalTable}
    return render(request, 'table/bestefficiency.html', context)

def defense_leaderboard(request):
    totalTable = ""
    dbItems = base.objects.all().order_by('-raid_cost')[:10]
    counter=0
    for i in dbItems:
        counter+=1
        eValue = i.efficiency_score
        if eValue > 0.1:
            eValue = 0.1
        efficiency = int(eValue//0.02)
        stars = "&#9733;"*efficiency + "&#9734;"*(5-efficiency)
        videoCode = video_id(i.link)
        if i.fortify_link == 'N/A':
            fortify = ''
        else:
            fortify='<button type="button" class="btn btn-secondary tag-btn fortify-btn">Fortify</button><br>'
        tableEntry = TABLEROWTEMPLATE.format(i.pk, '#'+str(counter)+': '+i.name, videoCode, i.creator, i.group_size, i.build_cost_stone, i.build_cost_frags, i.build_cost_hqm, i.build_cost_scrap, i.upkeep_cost_stone, i.upkeep_cost_frags, i.upkeep_cost_hqm, i.upkeep_cost_scrap, i.raid_cost, i.efficiency_score, stars, fortify, i.feature_1, i.feature_2, i.feature_3)
        totalTable += tableEntry
    context = {'tableItems': totalTable}
    return render(request, 'table/bestdefense.html', context)

def all_bases(request):
    totalTable = ""
    dbItems = base.objects.all().order_by('name')
    for i in dbItems:
        eValue = i.efficiency_score
        if eValue > 0.1:
            eValue = 0.1
        efficiency = int(eValue//0.02)
        stars = "&#9733;"*efficiency + "&#9734;"*(5-efficiency)
        videoCode = video_id(i.link)
        if i.fortify_link == 'N/A':
            fortify = ''
        else:
            fortify='<button type="button" class="btn btn-secondary tag-btn fortify-btn">Fortify</button><br>'
        tableEntry = TABLEROWTEMPLATE.format(i.pk, i.name, videoCode, i.creator, i.group_size, i.build_cost_stone, i.build_cost_frags, i.build_cost_hqm, i.build_cost_scrap, i.upkeep_cost_stone, i.upkeep_cost_frags, i.upkeep_cost_hqm, i.upkeep_cost_scrap, i.raid_cost, i.efficiency_score, stars, fortify, i.feature_1, i.feature_2, i.feature_3)
        totalTable += tableEntry
    context = {'tableItems': totalTable}
    return render(request, 'table/allbases.html', context)

def base_id(request, id):
    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            rating_instance = rating(base_foreign = id, account_foreign = request.user.id, stars = form.cleaned_data['stars'], content = form.cleaned_data['content'])
            rating_instance.save()
            context = {'message': 'Your rating has been added'}
            return render(request, 'table/message.html', context)
        else:
            context = {'message':'Rating failed.'}
            return render(request, 'table/message.html', context)
    else:
        bestBase = base.objects.get(pk=id)
        YTLink, Code = bestBase.link.split('=')
        ratings = rating.objects.filter(base_foreign = id)
        ratingList = []
        runningTotal = 0
        counter = 0
        for i in ratings:
            reviewer = User.objects.get(pk=i.account_foreign).username
            runningTotal += i.stars
            counter += 1
            stars = "&#9733;"*i.stars + "&#9734;"*(5-i.stars)
            ratingList.append({'reviewer':reviewer, 'stars':stars, 'content':i.content})
        if counter > 0:
            average = runningTotal / counter
            roundedAverage = round(average)
        else:
            roundedAverage = 0
        averageStars = "&#9733;"*roundedAverage + "&#9734;"*(5-roundedAverage)
        if bestBase.fortify_link == 'N/A':
            fortify = 'N/A'
        else:
            fortify = '<a target="_blank" href="' + bestBase.fortify_link + '">'+ bestBase.fortify_link + '</a>'
        context = {'name': bestBase.name, 'link': bestBase.link, 'group_size': bestBase.group_size, 'cost_stone': bestBase.build_cost_stone, 'cost_frags': bestBase.build_cost_frags, 'cost_hqm': bestBase.build_cost_hqm, 'upkeep_stone': bestBase.upkeep_cost_stone, 'upkeep_frags': bestBase.upkeep_cost_frags, 'upkeep_hqm': bestBase.upkeep_cost_hqm, 'video_code': Code, 'creator': bestBase.creator, 'raid_cost': bestBase.raid_cost, 'feature_1': bestBase.feature_1, 'feature_2': bestBase.feature_2, 'feature_3': bestBase.feature_3, 'fortify_link': fortify, 'ratingList': ratingList, 'averageStars': averageStars, 'form': RatingForm, 'id': bestBase.pk}
        return render(request, 'table/basedetails.html', context)

def video_id(value):
    query = urlparse(value)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            p = parse_qs(query.query)
            return p['v'][0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
    return None

def sponsor(request):
    return render(request, 'table/sponsor.html')

def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(form.cleaned_data['username'], form.cleaned_data['email'], form.cleaned_data['password'])
            context = {'message':'Account Created'}
            return render(request, 'table/message.html', context)
    else:
        context = {'form': SignUpForm}
        return render(request, 'table/signup.html', context)

def log_in(request):
    if request.method == 'POST':
        form = LogInForm(request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                context = {'message':'Successfully logged in. You can now add bases and ratings.'}
                return render(request, 'table/message.html', context)
            else:
                context = {'message':'Login Failed, Your username or password was incorrect.'}
                return render(request, 'table/message.html', context)
        else:
            context = {'message':'Something went wrong. Please try again.'}
            return render(request, 'table/message.html', context)
    else:
        context = {'form': LogInForm}
        return render(request, 'table/login.html', context)

def log_out(request):
    logout(request)
    return render(request, 'table/message.html', {'message' : 'Succesfully logged out.'})