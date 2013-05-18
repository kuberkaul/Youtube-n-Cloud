from django.conf.urls import patterns,url

from gallery import views

urlpatterns=patterns('',
		url(r'^$',views.index,name='index'),
		url(r'^player.html/',views.play,name='play'),
		url(r'^delete.html/',views.delete,name='delete'),
		)


