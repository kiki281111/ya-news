import pytest
from django.test.client import Client
from django.contrib.auth import get_user_model
from news.models import News, Comment

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