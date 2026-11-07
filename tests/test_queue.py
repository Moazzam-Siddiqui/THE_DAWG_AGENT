import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from dawg_agent.db import Base
from dawg_agent.schemas import PostCreate
from dawg_agent.services.queue import QueueError, approve_post, create_post

@pytest.fixture
def db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine, expire_on_commit=False)()
    yield session
    session.close()

def sample():
    return PostCreate(id="dawg-001", image_path="dog.jpg", caption="Good dog")

def test_create_draft(db):
    post = create_post(db, sample())
    assert post.status == "draft"
    assert post.approved is False

def test_duplicate_rejected(db):
    create_post(db, sample())
    with pytest.raises(QueueError):
        create_post(db, sample())

def test_approval_gate(db):
    post = create_post(db, sample())
    approve_post(db, post)
    assert post.approved is True
    assert post.status == "approved"
