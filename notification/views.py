from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.syndication.views import feed

from .models import *
from .decorators import basic_auth_required, simple_basic_auth_callback
from .forms import NoticeSettingFormSet
from .feeds import NoticeUserFeed

@basic_auth_required(realm='Notices Feed', callback_func=simple_basic_auth_callback)
def feed_for_user(request):
    url = "feed/%s" % request.user.username
    return feed(request, url, {
        "feed": NoticeUserFeed,
    })

from core.forms import UniFormNoticeSettingFormSet
#def notices(request, formset_class=NoticeSettingFormSet):
@login_required
def notices(request, formset_class=UniFormNoticeSettingFormSet):
    formset = formset_class(user=request.user, data=request.POST or None)

    if request.method == "POST":
        if formset.is_valid():
            formset.save()

    return render_to_response("notification/notices.html", {
        "formset": formset,
    }, context_instance=RequestContext(request))

@login_required
def single(request, id):
    notice = get_object_or_404(Notice, id=id)
    if request.user == notice.user:
        return render_to_response("notification/single.html", {
            "notice": notice,
        }, context_instance=RequestContext(request))
    raise Http404

@login_required
def archive(request, noticeid=None, next_page=None):
    if noticeid:
        try:
            notice = Notice.objects.get(id=noticeid)
            if request.user == notice.user or request.user.is_superuser:
                notice.archive()
            else:   # you can archive other users' notices
                    # only if you are superuser.
                return HttpResponseRedirect(next_page)
        except Notice.DoesNotExist:
            return HttpResponseRedirect(next_page)
    return HttpResponseRedirect(next_page)

@login_required
def delete(request, noticeid=None, next_page=None):
    if noticeid:
        try:
            notice = Notice.objects.get(id=noticeid)
            if request.user == notice.user or request.user.is_superuser:
                notice.delete()
            else:   # you can delete other users' notices
                    # only if you are superuser.
                return HttpResponseRedirect(next_page)
        except Notice.DoesNotExist:
            return HttpResponseRedirect(next_page)
    return HttpResponseRedirect(next_page)

@login_required
def mark_all_seen(request):
    for notice in Notice.objects.notices_for(request.user, unseen=True):
        notice.unseen = False
        notice.save()
    return HttpResponseRedirect(reverse("notification_notices"))
    
