# Create your views here.
from __future__ import division
from django.shortcuts import render_to_response
from django import forms
from boto.s3.key import Key
import boto
from django.conf import settings
from models import VideoUrl,VideoRating
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db.models import Avg
#from gallery.extra import ContentTypeRestrictedFileField

class UploadForm(forms.Form):
	file=forms.FileField(label='Select a video',help_text='Format : Video only')

class RatingForm(forms.Form):
	rating=forms.ChoiceField(label='Rate this video',choices=((1,1),(2,2),(3,3),(4,4),(5,5)))
	
def index(request):
	def syncs3(filename,content):
		bucket_name=settings.AWS_STORAGE_BUCKET_NAME
		conn=boto.connect_s3(settings.AWS_ACCESS_KEY_ID,settings.AWS_SECRET_ACCESS_KEY)
		bucket=conn.get_bucket(bucket_name)
		k=Key(bucket)
		k.key=filename
		k.set_metadata("Content-Type", "video/mp4")
		k.set_contents_from_string(content)
		k.set_acl('public-read')
	#videos=VideoUrl.objects.all().order_by("-uploaded_time")
	videos=VideoUrl.objects.annotate(avg_rating=Avg('videorating__rating')).order_by("-avg_rating")
	if not request.method=='POST':
		f=UploadForm()
		return render_to_response("gallery/index.html",{"form":f,"videos":videos},context_instance=RequestContext(request))

	f=UploadForm(request.POST,request.FILES)
	if not f.is_valid():
		return render_to_response("gallery/index.html",{"form":f,"videos":videos},context_instance=RequestContext(request))

	file=request.FILES['file']
	filename=file.name
	content=file.read()
	file_type = file.content_type.split('/')[0]
   	if file_type !="video":
		error=1
		return render_to_response("gallery/index.html",{"form":f,"videos":videos,"error":error},context_instance=RequestContext(request))
        	
    	else:
		syncs3(filename,content)
		v=VideoUrl(url="rtmp://smccbgx2pkn3p.cloudfront.net/cfx/st/"+filename,videoname=filename)
		v.save()
		vr=VideoRating(video=v)
		vr.save()
		videos=VideoUrl.objects.all().order_by("-uploaded_time")
		return HttpResponseRedirect(reverse('gallery.views.index'))


def play(request):

	if not request.method=='POST':
		r=RatingForm()
		id1=request.GET.get('id')
		video=VideoUrl.objects.get(id=id1)
		vo=VideoRating.objects.filter(video_id=id1)
#		if len(vo)==1 and vo[0].rating==5:
#			num_videos=1
#		else:
#			num_videos=len(vo)-1
		
		average_rating=sum([o.rating for o in vo])/len(vo)
		return render_to_response("gallery/player.html",{"video":video,"form":r,"current_rating":average_rating},context_instance=RequestContext(request))
	r=RatingForm(request.POST)
	if not r.is_valid():
		return render_to_response("gallery/player.html",{"video":video,"form":r,"current_rating":average_rating},context_instance=RequestContext(request))
	rating=request.POST['rating']
	vid=request.POST['video_id']
	v=VideoUrl.objects.get(pk=vid)
	nvr=VideoRating(video=v,rating=rating)
	nvr.save()
	vo=VideoRating.objects.filter(video_id=vid)
	average_rating=sum([o.rating for o in vo])/len(vo)
	return HttpResponseRedirect('/gallery/player.html/?id='+vid)

def delete(request):
	id1=request.GET.get('id')
	video=VideoUrl.objects.get(id=id1)
	bucket_name=settings.AWS_STORAGE_BUCKET_NAME
	conn=boto.connect_s3(settings.AWS_ACCESS_KEY_ID,settings.AWS_SECRET_ACCESS_KEY)
	bucket=conn.get_bucket(bucket_name)
	k=Key(bucket)
	k.key=video.videoname
	bucket.delete_key(k)
	videoname=video.videoname
	video.delete()
	return render_to_response("gallery/delete.html",{"videoname":videoname},context_instance=RequestContext(request))

	
