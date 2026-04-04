import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.infrastructure.database.database import get_db
from app.infrastructure.database.models import Base, Customer, Order, Payment
from app.application.services.loyalty_service import award_loyalty_for_order, get_loyalty_summary, apply_reward_to_order
from fastapi.testclient import TestClient

TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

def test_award_loyalty_earns_points():
    db = TestingSessionLocal()
    db.add(Customer(id=1, username="username", email="user@gmail.com", password_hash="P@ssword"))
    db.add(Order(combined_order_id="some-Uuid1", customer_id=1, restaurant_id=1, total_cost=50.0))
    db.commit()
    
    result = award_loyalty_for_order(db, "some-Uuid1")
    customer = db.query(Customer).filter(Customer.id == 1).first()
    assert customer.loyalty_points == 50
    db.close()

def test_loyalty_unlocks_reward_at_500_points():
    db = TestingSessionLocal()
    db.add(Customer(id=2, username="username2", email="user2@gmail.com", password_hash="P@ssword"))
    db.add(Order(combined_order_id="some-Uuid2", customer_id=2, restaurant_id=1, total_cost=500.0))
    db.commit()
    
    award_loyalty_for_order(db, "some-Uuid2")
    customer = db.query(Customer).filter(Customer.id == 2).first()
    assert customer.loyalty_rewards_available == 1
    db.close()

def test_apply_reward_gives_50_percent_discount():
    db = TestingSessionLocal()
    db.add(Customer(id=3, username="username3", email="user3@gmail.com", password_hash="P@ssword", loyalty_rewards_available=1))
    db.add(Order(combined_order_id="some-Uuid3", customer_id=3, restaurant_id=1, total_cost=80.0))
    db.commit()
    
    result = apply_reward_to_order(db, 3, "some-Uuid3")
    assert result["discount_amount"] == 40.0
    assert result["discounted_total"] == 40.0
    db.close()

def test_double_payment_no_double_award():
    db = TestingSessionLocal()
    db.add(Customer(id=4, username="username4", email="user4@gmail.com", password_hash="P@ssword"))
    db.add(Order(combined_order_id="some-Uuid4", customer_id=4, restaurant_id=1, total_cost=100.0))
    db.commit()
    
    award_loyalty_for_order(db, "some-Uuid4")
    db.add(Payment(order_id="some-Uuid4", status="success", amount=100))
    db.commit()
    result = award_loyalty_for_order(db, "some-Uuid4")
    assert result is None
    db.close()

def test_get_loyalty_summary():
    db = TestingSessionLocal()
    db.add(Customer(id=5, username="username5", email="user5@gmail.com", password_hash="P@ssword", loyalty_points=250))
    db.commit()
    
    summary = get_loyalty_summary(db, 5)
    assert summary["points"] == 250
    assert summary["reward_percent"] == 50
    db.close()

def test_500_points_unlocks_one_reward():
    db = TestingSessionLocal()
    db.add(Customer(id=6, username="username6", email="user6@gmail.com", password_hash="P@ssword"))
    db.add(Order(combined_order_id="some-Uuid6", customer_id=6, restaurant_id=1, total_cost=500.0))
    db.commit()

    award_loyalty_for_order(db, "some-Uuid6")
    customer = db.query(Customer).filter(Customer.id == 6).first()
    assert customer.loyalty_rewards_available == 1
    db.close()
