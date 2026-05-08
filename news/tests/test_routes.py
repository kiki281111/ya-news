from http import HTTPStatus
import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects

@pytest.mark.django_db
def test_home_availability_for_anonymous_user(client):
    """The main page is accessible to an anonymous user."""
    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:home', 'users:login', 'users:signup')
)
def test_pages_availability_for_anonymous_user(client, name):
    """Pages that are accessible to everyone (including anonymous users)."""
    url = reverse(name)

    if name == 'users:logout':
        response = client.post(url)
        assert response.status_code == HTTPStatus.FOUND
        return
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:detail',)
)
def test_pages_availability_for_auth_user(not_author_client, name, news):
    """Pages accessible to any authorized user."""
    url = reverse(name, args=(news.id,))
    response = not_author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_pages_availability_for_different_users(
        parametrized_client, name, comment, expected_status
):
    """The edit/delete comment pages are only accessible to the author."""
    url = reverse(name, args=(comment.id,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('comment_id_for_args')),
        ('news:delete', pytest.lazy_fixture('comment_id_for_args')),
    ),
)
def test_redirects(client, name, args):
    """
    An anonymous user is redirected to the login page
    when they try to edit or delete a comment.
    """
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)