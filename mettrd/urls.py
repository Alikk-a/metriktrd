"""metriktrd URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('change/', views.change, name='change'),
    path('change_activ/', views.change_activ, name='change_activ'),
    path('change_activ2/', views.change_activ2, name='change_activ2'),
    path('change_ex/', views.change_ex, name='change_ex'),
    path('change_adr/', views.change_adr, name='change_adr'),
    path('addresses.html', views.addresses, name='addresses.html'),
    path('activity.html', views.activity, name='activity.html'),
    path('profloss.html', views.profloss, name='profloss.html'),
    path('exchange.html', views.exchange, name='exchange.html'),
    path('bigtrans.html', views.bigtrans, name='bigtrans.html'),
    path('bigtrans_filter.html', views.bigtrans_filter, name='bigtrans_filter.html'),
    path('bigtrans_agr.html', views.bigtrans_agr, name='bigtrans_agr.html'),
    path('bigtrans_full.html', views.bigtrans_full, name='bigtrans_full.html'),
    path('bigtransavg_btc', views.bigtrans_szn, name='bigtransavg_btc'),
    path('bigtransavg_eth', views.bigtranseth_szn, name='bigtransavg_eth'),
    path('bigtrans_sum.html', views.bigtrans_sum, name='bigtrans_sum.html'),
    path('o120522.html', views.o120522, name='o120522.html'),
    path('o170522.html', views.o170522, name='o170522.html'),
    path('posts/', views.posts, name='posts'),
    path('proto/', views.proto, name='proto'),
    path('proto_bd_adr/', views.proto_bd_adr, name='proto_bd_adr'),
    path('alert/', views.alert, name='alert'),
    path('proto_bd_pl/', views.proto_bd_pl, name='proto_bd_pl'),
    path('pos/<int:post_id>/', views.specific_post, name='specific_post'),
    path('chartsecharts.html', views.chartsecharts, name='chartsecharts.html'),
    path('chartsapexcharts.html', views.chartsapexcharts, name='chartsapexcharts.html'),
    path('chartschartjs', views.chartschartjs, name='chartschartjs.html'),
    path('iconsbootstrap/', views.iconsbootstrap, name='iconsbootstrap'),
    path('iconsboxicons/', views.iconsboxicons, name='iconsboxicons'),
    path('iconsremix/', views.iconsremix, name='iconsremix'),
    path('tablesdata/', views.tablesdata, name='tablesdata'),
    path('tablesgeneral/', views.tablesgeneral, name='tablesgeneral'),
    path('pagesblank.html', views.pagesblank, name='pagesblank.html'),
    path('testbot/', views.sendBottest, name='testbot'),
]
