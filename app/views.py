import hashlib
import os
import uuid
from django.contrib.auth import logout
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from AXF import settings
from app.models import *


# Create your views here.


# 首页
def home(request):
    wheels = Wheel.objects.all()
    navs = Nav.objects.all()
    mustbuys = Mustbuy.objects.all()
    shoplist = Shop.objects.all()
    shophead = shoplist[0]
    shoptab = shoplist[1:3]
    shopclass = shoplist[3:7]
    shopcommend = shoplist[7:11]

    mainshows = MainShow.objects.all()

    data = {
        'title': '首页',
        'wheels': wheels,
        'navs': navs,
        'mustbuys': mustbuys,
        'shophead': shophead,
        'shoptab': shoptab,
        'shopclass': shopclass,
        'shopcommmend':shopcommend,
        'mainshows': mainshows
    }
    return render(request, 'home/home.html', context=data)


# 闪购超市
def market(request, categoryid, childid, sortid):
    foodtypes = Foodtypes.objects.all()
    typeIndex = int(request.COOKIES.get('typeIndex', 0))
    categoryid = foodtypes[typeIndex].typeid
    childtypenames = foodtypes.get(typeid=categoryid).childtypenames
    childlist = []
    for item in childtypenames.split('#'):
        arr = item.split(':')
        obj = {'childname': arr[0], 'childid': arr[1]}
        childlist.append(obj)
    if childid == '0':
        goodslist = Goods.objects.filter(categoryid=categoryid)
    else:
        goodslist = Goods.objects.filter(categoryid=categoryid, childid=childid)

    if sortid == '1':
        goodslist = goodslist.order_by('productnum')
    elif sortid == '2':
        goodslist = goodslist.order_by('price')
    elif sortid == '3':
        goodslist = goodslist.order_by('-price')

    token = request.session.get('token')
    carts = []
    if token:
        user = User.objects.get(token=token)
        carts = Cart.objects.filter(user=user).exclude(number=0)

    data = {
        'title': '闪购超市',
        'foodtypes': foodtypes,
        'goodslist': goodslist,
        'childlist': childlist,
        'categoryid': categoryid,
        'childid': childid,
        'carts': carts
    }
    return render(request, 'market/market.html', context=data)


# 购物车
def cart(request):
    token = request.session.get('token')
    carts = []
    if token:
        user = User.objects.get(token=token)
        carts = Cart.objects.filter(user=user).exclude(number=0)
    responseData = {
        'title': '购物车',
        'carts': carts
    }
    return render(request, 'cart/cart.html', context=responseData)


# 我的
def mine(request):
    token = request.session.get('token')
    responseData = {
        'title': '我的'
    }
    if token:
        user = User.objects.get(token=token)
        responseData['name'] = user.name
        responseData['rank'] = user.rank
        responseData['img'] = '/static/uploads/' + user.img
        responseData['islogin'] = True

    else:
        responseData['name'] = '未登录'
        responseData['rank'] = '无等级(未登录)'
        responseData['img'] = '/static/uploads/axf.png'
        responseData['islogin'] = False
    return render(request, 'mine/mine.html', context=responseData)


# 注册
def register(request):
    if request.method == 'POST':
        user = User()
        user.account = request.POST.get('account')
        user.password = generate_password(request.POST.get('password'))
        user.name = request.POST.get('name')
        user.tel = request.POST.get('tel')
        user.address = request.POST.get('address')
        imgName = user.account + '.png'
        imgPath = os.path.join(settings.MEDIA_ROOT, imgName)
        file = request.FILES.get('file')
        with open(imgPath, 'wb') as fp:
            for data in file.chunks():
                fp.write(data)
        user.img = imgName
        user.token = str(uuid.uuid5(uuid.uuid4(), 'register'))
        user.save()
        request.session['token'] = user.token
        return redirect('axf:mine')

    elif request.method == 'GET':
        return render(request, 'mine/register.html')

    else:
        return HttpResponse(request, '注册失败!')


# 密码
def generate_password(password):
    sha = hashlib.sha512()
    sha.update(password.encode('utf-8'))
    return sha.hexdigest()


# 退出登录
def quit(request):
    logout(request)
    return redirect('axf:mine')


# 登录
def login(request):
    if request.method == 'POST':
        account = request.POST.get('account')
        password = request.POST.get('password')

        try:
            user = User.objects.get(account=account)
            if user.password != generate_password(password):
                return render(request, 'mine/login.html', context={'error': '密码错误!'})
            else:
                user.token = str(uuid.uuid5(uuid.uuid4(), 'login'))
                user.save()
                request.session['token'] = user.token
                return redirect('axf:mine')
        except:
            return render(request, 'mine/login.html', context={'error': '用户名有误，请检查后输入!'})
    elif request.method == 'GET':
        return render(request, 'mine/login.html')
    else:
        return HttpResponse(request, '登录失败!')


# 用户验证
def check_user(request):
    account = request.GET.get('account')
    try:
        user = User.objects.get(account=account)
        return JsonResponse({'msg': '用户名已存在!', 'status': '-1'})
    except:
        return JsonResponse({'msg': '用户名可用!', 'status': '1'})


# 添加购物车
def addToCart(request):
    goodsid = request.GET.get('goodsid')
    token = request.session.get('token')
    responseData = {
        'msg': '',
        'status': ''
    }
    if token:
        user = User.objects.get(token=token)
        goods = Goods.objects.get(pk=goodsid)
        carts = Goods.objects.filter(goods=goods).filter(user=user)
        if carts.exists():
            cart = carts.first()
            cart.number = cart.number + 1
            if goods.storenums < cart.number:
                cart.number = goods.storenums
            cart.save()
            responseData['msg'] = '添加购物车成功!'


# 购物车删减
def subToCart(request):
    token = request.session.get('token')
    user = User.objects.get(token=token)
    goodsid = request.GET.get('goodsid')
    goods = Goods.objects.get(pk=goodsid)
    carts = Cart.objects.filter(user=user).filter(goods=goods)
    cart = carts.first()
    cart.number = cart.number - 1
    responseData = {
        'msg': '删减成功!',
        'status': '1',
        'numer': cart.number
    }
    return JsonResponse(responseData)


# 修改选中状态
def changeCartStatus(request):
    cartid = request.GET.get('cartid')
    cart = Cart.objects.get(pk=cartid)
    cart.isselect = not cart.isselect
    cart.save()
    responseData = {
        'msg': '修改状态成功!',
        'status': '1',
        'isselect': cart.isselect
    }
    return JsonResponse(responseData)


# 全选/取消全选
def changeCartSelect(request):
    isall = request.GET.get('isall')
    if isall == 'true':
        isall = True
    else:
        isall = False
    token = request.session.get('token')
    user = User.objects.get(token=token)
    carts = Cart.objects.filter(user=user)
    for cart in carts:
        cart.isselect = isall
        cart.save()
    responseData = {
        'msg': '全选/取消全选 操作成功',
        'status': '1'
    }
    return JsonResponse(responseData)