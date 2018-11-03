from django.conf.urls import url
from app import views

urlpatterns = [
    url(r'^$', views.home, name='home'),  # 首页

    url(r'^home/$', views.home, name='home'),  # 首页
    url(r'^market/(\d+)/(\d+)/(\d+)/$', views.market, name='market'), # 闪购超市
    url(r'^cart/$', views.cart, name='cart'),  # 购物车
    url(r'^mine/$', views.mine, name='mine'),  # 我的

    url(r'^register/$', views.register, name='register'),  # 注册
    url(r'^login/$', views.login, name='login'),  # 登录
    url(r'^quit/$', views.quit, name='quit'),  # 退出登录
    url(r'^check_user/$', views.check_user, name='check_user'),  # 用户名验证

    url(r'^addToCart/$', views.addToCart, name='addToCart'),  # 添加到购物车
    url(r'^subToCart/$', views.subToCart, name='subToCart'),  # 购物车删减
    url(r'^changeCartStatus/$', views.changeCartStatus, name='changeCartStatus'),  # 修改选中状态
    url(r'^changeCartSelect/$', views.changeCartSelect, name='changeCartSelect'),  # 全选/取消全选
]