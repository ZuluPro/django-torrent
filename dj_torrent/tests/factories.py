import factory
from factory import Faker, fuzzy

TORRENT_STATUS = (
    'downloading',
    'seeding',
    'stopped',
)


class UserFactory(factory.django.DjangoModelFactory):
    username = Faker('user_name')
    password = factory.PostGenerationMethodCall('set_password', 'foobarham')
    email = Faker('email')

    is_superuser = True
    is_staff = True
    is_active = True

    class Meta:
        model = 'auth.User'
        django_get_or_create = ('username', 'email',)


class TorrentFactory(factory.django.DjangoModelFactory):
    base_id = -1
    hash = Faker('sha1')
    name = Faker('words')
    status = fuzzy.FuzzyChoice(TORRENT_STATUS)
    progress = fuzzy.FuzzyFloat(0, 100)
    deleted = False

    class Meta:
        model = 'dj_torrent.Torrent'
        django_get_or_create = ('hash',)
