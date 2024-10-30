"""Tests conftest file. Used to prepare to tests."""

from asyncio import get_event_loop_policy
from typing import AsyncGenerator, Generator

import aiofiles
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from python_advanced_diploma.src.config import (
    DB_HOST_TEST,
    DB_NAME_TEST,
    DB_PASSWORD_TEST,
    DB_PORT_TEST,
    DB_USER_TEST,
)
from python_advanced_diploma.src.database import Base, get_async_session
from python_advanced_diploma.src.main import app
from python_advanced_diploma.src.medias.medias_models import TweetMedia
from python_advanced_diploma.src.tweets.tweets_models import Like, Tweet
from python_advanced_diploma.src.users.users_models import Follow, User

DATABASE_URL_TEST = (
    "postgresql+asyncpg://"
    "{DB_USER_TEST}:{DB_PASSWORD_TEST}@{DB_HOST_TEST}".format(
        DB_USER_TEST=DB_USER_TEST,
        DB_PASSWORD_TEST=DB_PASSWORD_TEST,
        DB_HOST_TEST=DB_HOST_TEST,
    ) + ":{DB_PORT_TEST}/{DB_NAME_TEST}".format(
        DB_PORT_TEST=DB_PORT_TEST,
        DB_NAME_TEST=DB_NAME_TEST,
    )
)
engine_test = create_async_engine(DATABASE_URL_TEST, poolclass=NullPool)
test_async_session_maker = async_sessionmaker(
    engine_test,
    class_=AsyncSession,
    expire_on_commit=False,
)
metadata = Base.metadata
metadata.bind = engine_test

test_async_session = test_async_session_maker()


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Функция для перезаписи асинхронной сессии.

    :yield: Асинхронная сессия
    """
    async with test_async_session_maker() as test_session:
        yield test_session


app.dependency_overrides[get_async_session] = override_get_async_session


@pytest.fixture(autouse=True, scope="session")
async def prepare_database():
    """
    Фикстура для подготовки тестовой БД к проведению тестов.

    :yield: None
    """
    async with engine_test.begin() as start_conn:
        await start_conn.run_sync(metadata.create_all)
    yield
    async with engine_test.begin() as end_conn:
        await end_conn.run_sync(metadata.drop_all)


@pytest.fixture(scope="session")
# def event_loop(request) -> Generator[AbstractEventLoop]:
def event_loop(request) -> Generator:
    """
    Фикстура для получения AbstractEventLoop.

    :param request: Запрос
    :yield: AbstractEventLoop
    """
    loop = get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    """
    Фикстура асинхронного клиента.

    :yield: Асинхронный клиент.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as async_client:
        yield async_client


@pytest.fixture(autouse=True, scope="session")
async def user() -> User:
    """
    Фикстура пользователя.

    :return: Пользователь
    """
    user = User(name="Test user name", user_api_key="test_api_key")
    test_async_session.add(user)
    await test_async_session.commit()
    return user


@pytest.fixture
async def tweet_to_delete(user: User) -> Tweet:
    """
    Фикстура твита для тестирования удаления твита.

    :param user: Пользователь
    :return: Твит для удаления
    """
    tweet = Tweet(
        content="Some test tweet content to delete",
        author_id=user.id,
    )
    test_async_session.add(tweet)
    await test_async_session.commit()
    return tweet


@pytest.fixture(scope="session")
async def another_user() -> User:
    """
    Фикстура другого пользователя.

    :return: Другой пользователь
    """
    another_user = User(
        name="Test user name to like",
        user_api_key="test_api_key_to_like",
    )
    test_async_session.add(another_user)
    await test_async_session.commit()
    return another_user


@pytest.fixture()
async def tweet_to_like(another_user: User) -> Tweet:
    """
    Фикстура твита для тестирования лайка твита.

    :param another_user: Другой пользователь
    :return: Твит для лайка
    """
    tweet_to_like = Tweet(
        content="Some test tweet content to like",
        author_id=another_user.id,
    )
    test_async_session.add(tweet_to_like)
    await test_async_session.commit()
    return tweet_to_like


@pytest.fixture
async def own_tweet_to_like(user: User) -> Tweet:
    """
    Фикстура твита для тестирования лайка собственного твита.

    :param user: Пользователь
    :return: Собственный твит для лайка
    """
    own_tweet_to_like = Tweet(
        content="Some test tweet content to like own tweet",
        author_id=user.id,
    )
    test_async_session.add(own_tweet_to_like)
    await test_async_session.commit()
    return own_tweet_to_like


@pytest.fixture(scope="session")
async def user_to_like() -> User:
    """
    Фикстура пользователя для тестирования существующего лайка.

    :return: Пользователь для тестирования существующего лайка
    """
    user_to_like = User(
        name="Test user name to test like",
        user_api_key="test_api_key_to_test_like",
    )
    test_async_session.add(user_to_like)
    await test_async_session.commit()
    return user_to_like


@pytest.fixture
async def tweet_to_test_exist_like(user_to_like: User) -> Tweet:
    """
    Фикстура твита для тестирования существующего лайка.

    :param user_to_like: Пользователь для тестирования существующего лайка
    :return: Твит для тестирования существующего лайка
    """
    tweet_to_test_exist_like = Tweet(
        content="Some test tweet content to test exist like",
        author_id=user_to_like.id,
    )
    test_async_session.add(tweet_to_test_exist_like)
    await test_async_session.commit()
    return tweet_to_test_exist_like


@pytest.fixture
async def exist_like_to_test(
    user: User, tweet_to_test_exist_like: Tweet,
) -> Like:
    """
    Фикстура лайка для тестирования повторного лайка.

    :param user: Пользователь
    :param tweet_to_test_exist_like: Твит для тестирования повторного лайка
    :return: Лайк для тестирования повторного лайка
    """
    exist_like_to_test = Like(
        user_id=user.id,
        tweet_id=tweet_to_test_exist_like.id,
    )
    test_async_session.add(exist_like_to_test)
    await test_async_session.commit()
    return exist_like_to_test


@pytest.fixture
async def tweet_to_delete_like(another_user: User) -> Tweet:
    """
    Фикстура твита для тестирования удаления лайка твита.

    :param another_user: Другой пользователь
    :return: Твит для удаления лайка
    """
    tweet_to_delete_like = Tweet(
        content="Some test tweet content to delete like",
        author_id=another_user.id,
    )
    test_async_session.add(tweet_to_delete_like)
    await test_async_session.commit()
    return tweet_to_delete_like


@pytest.fixture
async def like_to_delete(user: User, tweet_to_delete_like: Tweet) -> Like:
    """
    Фикстура лайка для тестирования отмены лайка.

    :param user: Пользователь
    :param tweet_to_delete_like: Твит для удаления лайка
    :return: Лайк для удаления
    """
    like_to_delete = Like(
        user_id=user.id,
        tweet_id=tweet_to_delete_like.id,
    )
    test_async_session.add(like_to_delete)
    await test_async_session.commit()
    return like_to_delete


@pytest.fixture(scope="session")
async def user_to_follow() -> User:
    """
    Фикстура пользователя для тестирования подписки.

    :return: Пользователь для тестирования подписки
    """
    user_to_follow = User(
        name="Test user name to follow",
        user_api_key="test_api_key_to_follow",
    )
    test_async_session.add(user_to_follow)
    await test_async_session.commit()
    return user_to_follow


@pytest.fixture
async def follow_to_test(user: User, user_to_follow: User) -> Follow:
    """
    Фикстура подписки для тестирования.

    :param user: Пользователь
    :param user_to_follow: Пользователь для тестирования подписки
    :return: Подписка для тестирования
    """
    follow_to_test = Follow(
        following_user_id=user_to_follow.id,
        followed_user_id=user.id,
    )
    test_async_session.add(follow_to_test)
    await test_async_session.commit()
    return follow_to_test


@pytest.fixture
async def follow_to_delete(user: User, another_user: User) -> Follow:
    """
    Фикстура подписки для тестирования отмены подписки.

    :param user: Пользователь
    :param another_user: Другой пользователь
    :return: Подписка для удаления
    """
    follow_to_delete = Follow(
        following_user_id=user.id,
        followed_user_id=another_user.id,
    )
    test_async_session.add(follow_to_delete)
    await test_async_session.commit()
    return follow_to_delete


@pytest.fixture
async def tweets(user: User, another_user: User) -> tuple[Tweet, Tweet, Tweet]:
    """
    Фикстура твитов.

    :param user: Пользователь
    :param another_user: Другой пользователь
    :return: Кортеж твитов
    """
    tweet_one = Tweet(content="Test content1", author_id=user.id)
    tweet_two = Tweet(content="Test content2", author_id=another_user.id)
    tweet_three = Tweet(content="Test content3", author_id=another_user.id)
    test_async_session.add_all((tweet_one, tweet_two, tweet_three))
    await test_async_session.flush()
    like_one = Like(
        user_id=user.id,
        tweet_id=tweet_three.id,
    )
    like_two = Like(
        user_id=another_user.id,
        tweet_id=tweet_one.id,
    )
    test_async_session.add_all((like_one, like_two))
    await test_async_session.commit()
    return tweet_one, tweet_two, tweet_three


@pytest.fixture
async def test_image() -> bytes:
    """
    Фикстура тестового изображения для твит медиа.

    :return: тестовое изображение для твит медиа
    """
    async with aiofiles.open(
        "../../tests/images_for_tests/test_image.jpeg", "rb",
    ) as image_file:
        image = await image_file.read()
    return image


@pytest.fixture
async def tweet_media_images(test_image: bytes) -> list[str]:
    """
    Фикстура списка изображений для твит медиа.

    :param test_image: тестовое изображение для твит медиа
    :return: изображения для твит медиа
    """
    image_paths = []
    for i_num in range(1, 3):
        image_path = "../../tests/images_for_tests/{i_num}_{filename}".format(
            i_num=i_num,
            filename="test_image.jpeg",
        )
        image_paths.append(image_path)
        async with aiofiles.open(image_path, "wb") as img_file:
            await img_file.write(test_image)
    return image_paths


@pytest.fixture
async def tweet_medias(tweet_media_images: list[str]) -> list[TweetMedia]:
    """
    Фикстура списка твит медиа.

    :param tweet_media_images: изображения для твит медиа
    :return: Твит медиа
    """
    medias = [
        TweetMedia(image=image_path) for image_path in tweet_media_images
    ]
    test_async_session.add_all(medias)
    await test_async_session.commit()
    return medias
