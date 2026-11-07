"""Small tests for the post waiting list."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from dawg_agent.db import Base
from dawg_agent.schemas import PostCreate
from dawg_agent.services.queue import QueueError, approve_post, create_post


@pytest.fixture
def database():
    """Give each test a fresh, empty database."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    test_session = sessionmaker(bind=engine, expire_on_commit=False)()

    yield test_session

    test_session.close()


def example_post() -> PostCreate:
    """Make a tiny example post for our tests."""
    return PostCreate(
        id="dog-test-001",
        image_path="assets/inbox/dog.jpg",
        caption="Hello, dog!",
    )


def test_new_post_starts_as_a_draft(database):
    post = create_post(database, example_post())

    assert post.status == "draft"
    assert post.approved is False


def test_same_post_id_cannot_be_added_twice(database):
    create_post(database, example_post())

    with pytest.raises(QueueError):
        create_post(database, example_post())


def test_a_person_can_approve_a_post(database):
    post = create_post(database, example_post())

    approved_post = approve_post(database, post)

    assert approved_post.approved is True
    assert approved_post.status == "approved"
