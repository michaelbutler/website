# pylint: disable=missing-docstring
from django.shortcuts import render
from django.http import HttpResponseForbidden, HttpResponseRedirect, JsonResponse
from django.contrib.syndication.views import Feed
from django.conf import settings
from django.views.generic import DetailView, TemplateView
from django.urls import reverse

from common.forms import UploadForm
from common.models import News
from games.models import Game, Installer
import random
import datetime as dt


def home(request):
    """Homepage view"""
    new_games = Game.objects.with_installer().order_by('-created')[:6]
    updated_games = [
        installer.game for installer in (
            Installer
            .objects
            .prefetch_related('game')
            .filter(published=True)
            .order_by('-updated_at')
        )[:6]
    ]
    samples = [
        {
            "image": "images/carousel/overwatch.jpg",
            "href": "/games/overwatch",
            "text": "Play Overwatch on Battle.net",
        },
        {
            "image": "images/carousel/the-witcher.jpg",
            "href": "/games/the-witcher-3-wild-hunt",
            "text": "Install The Witcher 3 from GOG or Steam",
        },
        {
            "image": "images/carousel/warframe.jpg",
            "href": "/games/warframe",
            "text": "Play Warframe",
        },
        {
            "image": "images/carousel/battlefield5.jpg",
            "href": "/games/battlefield-v",
            "text": "Play Battlefield V on Origin",
        },
        {
            "image": "images/carousel/eso.jpg",
            "href": "/games/the-elder-scrolls-online-tamriel-unlimited",
            "text": "Play The Elders Scrolls: Online",
        },
        {
            "image": "images/carousel/warcraft.jpg",
            "href": "/games/world-of-warcraft",
            "text": "Play World of Warcraft",
        }
    ]
    random.shuffle(samples, shuffle_by_hour)
    return render(request, 'home.html', {
        "new_games": new_games,
        "updated_games": updated_games,
        "sample_banners": samples
    })


def shuffle_by_hour():
    """
    Converts the current hour into a float between 0.0 and 1.0 for use in shuffling arrays.
    """
    return dt.datetime.now().hour / 24


class Downloads(TemplateView):
    template_name = "common/downloads.html"

    def get_context_data(self, **kwargs):
        context = super(Downloads, self).get_context_data(**kwargs)
        context['version'] = settings.CLIENT_VERSION
        context['download_url'] = 'https://lutris.net/releases/'
        return context


def news_archives(request):
    news = News.objects.all()
    return render(request, 'news.html', {'news': news})


class NewsDetails(DetailView):
    queryset = News.objects.all()
    template_name = 'common/news_details.html'
    context_object_name = 'news'

    def get_object(self, queryset=None):
        return super(NewsDetails, self).get_object()


class NewsFeed(Feed):
    title = "Lutris news"
    link = '/news/'
    description = u"Latest news about Lutris"
    feed_size = 20

    def items(self):
        return News.objects.order_by("-publish_date")[:self.feed_size]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.content.rendered

    def item_link(self, item):
        return item.get_absolute_url()


def upload_file(request):
    if not request.user.is_staff:
        return HttpResponseForbidden()
    form = UploadForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        upload = form.save(commit=False)
        upload.uploaded_by = request.user
        upload.save()
        return HttpResponseRedirect(reverse('upload_file'))
    return render(request, 'common/upload.html', {'form': form})


def server_status(_request):
    """Simple availability check"""
    return JsonResponse({"status": "ok"})
