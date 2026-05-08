
import pytest
from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count(client, many_news):
    """The number of news items on the homepage is limited."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    assert object_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, many_news):
    """The news is sorted from fresh to old."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, news_with_comments):
    """Comments on the news page are displayed in chronological order"""
    detail_url = reverse('news:detail', args=(news_with_comments.id,))
    response = client.get(detail_url)
    assert 'news' in response.context
    news_obj = response.context['news']
    all_comments = news_obj.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps



@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, form_expected',
    (
        (pytest.lazy_fixture('client'), False),
        (pytest.lazy_fixture('author_client'), True),
    )
)
def test_form_availability(parametrized_client, form_expected, news):
    """The comment is only available to authorized users."""
    detail_url = reverse('news:detail', args=(news.id,))
    response = parametrized_client.get(detail_url)
    has_form = 'form' in response.context
    assert has_form is form_expected
    if form_expected:
        assert isinstance(response.context['form'], CommentForm)