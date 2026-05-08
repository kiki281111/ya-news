from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.test.client import Client
from django.utils import timezone
from yanews import settings

from news.models import Comment, News

User = get_user_model()


@pytest.fixture
def author(db, django_user_model):
    """The user is the author of the comment."""
    return django_user_model.objects.create(username='Лев Толстой')


@pytest.fixture
def not_author(db, django_user_model):
    """Another user (not the author)."""
    return django_user_model.objects.create(username='Читатель простой')


@pytest.fixture
def author_client(db, author):
    """A client logged in as the author."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(db, not_author):
    """A client logged in as an ordinary user."""
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news(db):
    """Test news."""
    return News.objects.create(title='Заголовок', text='Текст')


@pytest.fixture
def comment(db, news, author):
    """The author's comment on the news."""
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )


@pytest.fixture
def comment_id_for_args(comment):
    """A tuple with the comment's id for use in reverse."""
    return (comment.id,)

@pytest.fixture
def many_news(db):
    """Creates NEWS_COUNT_ON_HOME_PAGE + 1 news items with different dates."""
    today = timezone.now()
    all_news = [
        News(title=f'Новость {i}', text='Текст', date=today - timedelta(days=i))
        for i in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)
    return all_news

@pytest.fixture
def news_with_comments(db, author):
    """A news article with 10 comments sorted by date."""
    news = News.objects.create(title='Тестовая новость', text='Текст')
    now = timezone.now()
    for i in range(10):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Комментарий {i}',
        )
        comment.created = now + timedelta(days=i)
        comment.save()
    return news

@pytest.fixture
def form_data():
    """A dictionary with data for creating/editing a comment."""
    return {'text': 'Текст комментария'}