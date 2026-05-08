from http import HTTPStatus
import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError
from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data, news):
    """An anonymous user cannot create a comment."""
    url = reverse('news:detail', args=(news.id,))
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    response = client.post(url, data=form_data)
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(author_client, author, form_data, news):
    """An authorized user can create a comment."""
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, form_data, news):
    """You can't use forbidden words in a comment."""
    url = reverse('news:detail', args=(news.id,))
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(url, data=bad_words_data)
    assertFormError(response.context['form'], 'text', errors=WARNING)
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(author_client, form_data, comment, news):
    """The author can edit his comment."""
    edit_url = reverse('news:edit', args=(comment.id,))
    url_to_comments = reverse('news:detail', args=(news.id,)) + '#comments'
    response = author_client.post(edit_url, data=form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_other_user_cant_edit_comment(not_author_client, form_data, comment):
    """The user cannot edit someone else's comment."""
    edit_url = reverse('news:edit', args=(comment.id,))
    response = not_author_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment_from_db.text == comment.text

def test_author_can_delete_comment(author_client, comment, news):
    """The author can delete his comment."""
    delete_url = reverse('news:delete', args=(comment.id,))
    url_to_comments = reverse('news:detail', args=(news.id,)) + '#comments'
    response = author_client.post(delete_url)
    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() == 0

def test_other_user_cant_delete_comment(not_author_client, comment):
    """The user can not delete someone comment."""
    delete_url = reverse('news:delete', args=(comment.id,))
    response = not_author_client.post(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
