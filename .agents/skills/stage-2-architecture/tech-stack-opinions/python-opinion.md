# Python Tech Stack Opinion

## Stack Profile

| Aspect | Recommendation |
|--------|-----------------|
| **Python Version** | 3.11+ |
| **Web Framework** | FastAPI or Django 4.2+ |
| **Pattern** | MVC-inspired (Views, Models, Services) |
| **ORM** | SQLAlchemy 2.0+ or Django ORM |
| **Dependency Injection** | Manual or Dependency Injector |
| **Testing** | pytest + unittest.mock |
| **API Style** | RESTful with auto-docs (FastAPI) or Django REST |
| **Validation** | Pydantic v2 |
| **Database** | PostgreSQL / MySQL |
| **Async Support** | async/await (FastAPI) or Celery (Django) |
| **Logging** | Python logging module + structlog |
| **Deployment** | Docker + Gunicorn/Uvicorn + Nginx |

---

## Architectural Pattern: MVC-Inspired Clean Architecture

### Layered Architecture

```
┌─────────────────────────────────────────┐
│            Presentation Layer           │
│    (FastAPI Endpoints / Django Views)   │
│         Request handlers, DTOs          │
└────────────────┬────────────────────────┘
                 │ (Pydantic models)
┌────────────────▼────────────────────────┐
│           Application Layer             │
│        Business Logic, Use Cases        │
│            Services, Handlers           │
└────────────────┬────────────────────────┘
                 │ (Domain models)
┌────────────────▼────────────────────────┐
│             Domain Layer                │
│       Entities, Interfaces, Rules       │
│         Business logic (SOLID)          │
└────────────────┬────────────────────────┘
                 │ (Repository interface)
┌────────────────▼────────────────────────┐
│         Infrastructure Layer            │
│     (Database, External Services)       │
│        Repositories, Adapters           │
└─────────────────────────────────────────┘
```

### Directory Structure

```
src/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app initialization
│   ├── config.py                  # Configuration (env, settings)
│   ├── dependencies.py            # Dependency injection
│   ├── api/                       # Presentation layer
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── users.py           # User endpoints
│   │   │   └── products.py        # Product endpoints
│   │   └── schemas/               # Request/Response DTOs (Pydantic)
│   │       ├── user_schema.py
│   │       └── product_schema.py
│   ├── services/                  # Application layer
│   │   ├── __init__.py
│   │   ├── user_service.py        # Business logic
│   │   ├── product_service.py
│   │   └── email_service.py       # External integrations
│   ├── models/                    # Domain layer
│   │   ├── __init__.py
│   │   ├── user.py                # Entity definitions
│   │   ├── product.py
│   │   └── base.py                # Base entity class
│   ├── repositories/              # Infrastructure layer
│   │   ├── __init__.py
│   │   ├── base_repository.py     # Abstract base
│   │   ├── user_repository.py     # Data access
│   │   └── product_repository.py
│   └── utils/
│       ├── __init__.py
│       ├── validators.py          # Validation helpers
│       └── exceptions.py          # Custom exceptions
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── test_user_service.py
│   │   └── test_product_service.py
│   ├── integration/
│   │   ├── test_user_endpoints.py
│   │   └── conftest.py            # Fixtures
│   └── fixtures/
│       └── sample_data.py
├── migrations/                    # Database migrations (Alembic)
│   └── versions/
├── requirements.txt
├── pytest.ini
└── docker-compose.yml
```

---

## SOLID Principles in Python

### S - Single Responsibility Principle

```python
# ❌ BAD - Multiple responsibilities
class UserManager:
    def __init__(self, db_connection):
        self.db = db_connection

    def create_user(self, name: str, email: str):
        # Validates
        # Creates entity
        # Saves to DB
        # Sends email
        # Logs
        pass

# ✅ GOOD - Each class has one responsibility
from abc import ABC, abstractmethod
from typing import Protocol

class IUserRepository(ABC):
    @abstractmethod
    async def add(self, user: 'User') -> 'User':
        pass

class IEmailService(ABC):
    @abstractmethod
    async def send_welcome_email(self, user: 'User') -> None:
        pass

class UserService:
    def __init__(
        self, 
        repository: IUserRepository,
        email_service: IEmailService
    ):
        self.repository = repository
        self.email_service = email_service

    async def create_user(self, name: str, email: str) -> User:
        user = User(name=name, email=email)
        await self.repository.add(user)
        await self.email_service.send_welcome_email(user)
        return user
```

### O - Open/Closed Principle

```python
# ❌ BAD - Must modify to add new discount type
class OrderService:
    def calculate_discount(self, order: Order) -> float:
        if order.type == "VIP":
            return order.total * 0.2
        elif order.type == "LOYALTY":
            return order.total * 0.1
        elif order.type == "BULK":
            return order.total * 0.15
        # Adding new type requires code change

# ✅ GOOD - Open for extension, closed for modification
from abc import ABC, abstractmethod

class DiscountStrategy(ABC):
    @abstractmethod
    def calculate(self, order: Order) -> float:
        pass

class VIPDiscountStrategy(DiscountStrategy):
    def calculate(self, order: Order) -> float:
        return order.total * 0.2

class LoyaltyDiscountStrategy(DiscountStrategy):
    def calculate(self, order: Order) -> float:
        return order.total * 0.1

class BulkDiscountStrategy(DiscountStrategy):
    def calculate(self, order: Order) -> float:
        return order.total * 0.15

# New discounts added without modifying existing code
class OrderService:
    def __init__(self, discount_strategy: DiscountStrategy):
        self.discount_strategy = discount_strategy

    def calculate_discount(self, order: Order) -> float:
        return self.discount_strategy.calculate(order)
```

### L - Liskov Substitution Principle

```python
# ✅ GOOD - All implementations honor the contract
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List

T = TypeVar('T')

class IRepository(ABC, Generic[T]):
    @abstractmethod
    async def get_by_id(self, id: int) -> T:
        pass
    
    @abstractmethod
    async def add(self, entity: T) -> T:
        pass
    
    @abstractmethod
    async def update(self, entity: T) -> T:
        pass
    
    @abstractmethod
    async def delete(self, entity: T) -> None:
        pass

class UserRepository(IRepository[User]):
    def __init__(self, db_session):
        self.db = db_session

    async def get_by_id(self, id: int) -> User:
        return await self.db.query(User).filter(User.id == id).first()
    
    async def add(self, entity: User) -> User:
        self.db.add(entity)
        await self.db.commit()
        return entity

# Can substitute UserRepository for IRepository[User]
class UserService:
    def __init__(self, repository: IRepository[User]):
        self.repository = repository

    async def get_user(self, id: int) -> User:
        return await self.repository.get_by_id(id)
```

### I - Interface Segregation Principle

```python
# ❌ BAD - Fat interface
class IUserManager(ABC):
    @abstractmethod
    async def create_user(self, user: User) -> None:
        pass
    
    @abstractmethod
    async def delete_user(self, id: int) -> None:
        pass
    
    @abstractmethod
    async def send_email(self, user: User, message: str) -> None:
        pass
    
    @abstractmethod
    async def log_audit(self, action: str) -> None:
        pass
    
    @abstractmethod
    async def assign_role(self, user: User, role: Role) -> None:
        pass

# ✅ GOOD - Segregated interfaces
class IUserRepository(ABC):
    @abstractmethod
    async def create(self, user: User) -> None:
        pass
    
    @abstractmethod
    async def delete(self, id: int) -> None:
        pass

class IEmailService(ABC):
    @abstractmethod
    async def send(self, user: User, message: str) -> None:
        pass

class IAuditLogger(ABC):
    @abstractmethod
    async def log(self, action: str) -> None:
        pass

class IRoleService(ABC):
    @abstractmethod
    async def assign_role(self, user: User, role: Role) -> None:
        pass

# Only inject what you need
class UserController:
    def __init__(
        self, 
        user_repo: IUserRepository,
        email_service: IEmailService
    ):
        self.user_repo = user_repo
        self.email_service = email_service
```

### D - Dependency Inversion Principle

```python
# ❌ BAD - Depends on concrete implementation
class UserService:
    def __init__(self):
        self.repository = PostgresUserRepository()  # Tight coupling

# ✅ GOOD - Depends on abstraction
from abc import ABC, abstractmethod

class IUserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: int) -> User:
        pass

class UserService:
    def __init__(self, repository: IUserRepository):
        self.repository = repository  # Decoupled

# Different implementations for different environments
# Production
services.register(IUserRepository, PostgresUserRepository())

# Testing
services.register(IUserRepository, MockUserRepository())
```

---

## Dependency Injection Setup

### Using Dependency Injector library

```python
# app/config.py
from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

class Container(containers.DeclarativeContainer):
    
    # Configuration
    config = providers.Configuration()
    
    # Database
    engine = providers.Singleton(
        create_async_engine,
        url=config.database.url,
        echo=False
    )
    
    session_factory = providers.Singleton(
        sessionmaker,
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    # Repositories
    user_repository = providers.Factory(
        UserRepository,
        session_factory=session_factory
    )
    
    # Services
    user_service = providers.Factory(
        UserService,
        repository=user_repository
    )
    
    # External services
    email_service = providers.Singleton(EmailService)

# app/main.py
from fastapi import FastAPI
from app.config import Container

container = Container()
container.config.from_yaml("config.yaml")

app = FastAPI()

@app.post("/users/")
async def create_user(request: CreateUserRequest):
    user_service = container.user_service()
    user = await user_service.create_user(
        name=request.name,
        email=request.email
    )
    return user
```

---

## FastAPI Implementation

### Routes with Dependency Injection

```python
# app/api/routes/users.py
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.user_schema import UserCreate, UserResponse
from app.services.user_service import UserService
from app.dependencies import get_user_service

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserResponse)
async def create_user(
    user_create: UserCreate,
    service: UserService = Depends(get_user_service)
):
    try:
        user = await service.create_user(
            name=user_create.name,
            email=user_create.email
        )
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service)
):
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

### Dependency Functions

```python
# app/dependencies.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository
from app.database import get_db_session

async def get_user_repository(
    session: AsyncSession = Depends(get_db_session)
) -> UserRepository:
    return UserRepository(session)

async def get_user_service(
    repository: UserRepository = Depends(get_user_repository)
) -> UserService:
    return UserService(repository)
```

---

## MVC Pattern in Services

```python
# app/services/user_service.py
from typing import Optional, List
from app.models.user import User
from app.repositories.user_repository import IUserRepository
from app.schemas.user_schema import UserCreate, UserResponse

class UserService:
    """Business logic for user operations"""
    
    def __init__(self, repository: IUserRepository):
        self.repository = repository
    
    async def create_user(self, name: str, email: str) -> User:
        # Validate input
        if not name or len(name) < 3:
            raise ValueError("Name must be at least 3 characters")
        
        if "@" not in email:
            raise ValueError("Invalid email address")
        
        # Create entity
        user = User(name=name, email=email)
        
        # Persist
        await self.repository.add(user)
        
        return user
    
    async def get_user(self, user_id: int) -> Optional[User]:
        return await self.repository.get_by_id(user_id)
    
    async def list_users(self, skip: int = 0, limit: int = 10) -> List[User]:
        return await self.repository.list(skip=skip, limit=limit)
    
    async def update_user(self, user_id: int, **kwargs) -> User:
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        await self.repository.update(user)
        return user
    
    async def delete_user(self, user_id: int) -> None:
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        await self.repository.delete(user)
```

---

## Data Models & Validation

### SQLAlchemy Models (Domain)

```python
# app/models/user.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, name={self.name}, email={self.email})>"
```

### Pydantic Schemas (DTOs)

```python
# app/schemas/user_schema.py
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class UserCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    email: EmailStr

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    email: Optional[EmailStr] = None

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True  # Convert ORM to dict
```

---

## Testing Strategy

### Unit Tests with pytest

```python
# tests/unit/test_user_service.py
import pytest
from unittest.mock import AsyncMock, Mock
from app.services.user_service import UserService
from app.models.user import User

@pytest.fixture
def mock_repository():
    return AsyncMock()

@pytest.fixture
def user_service(mock_repository):
    return UserService(repository=mock_repository)

@pytest.mark.asyncio
async def test_create_user_success(user_service, mock_repository):
    # Arrange
    mock_repository.add.return_value = User(
        id=1, 
        name="John", 
        email="john@example.com"
    )
    
    # Act
    result = await user_service.create_user(
        name="John", 
        email="john@example.com"
    )
    
    # Assert
    assert result.name == "John"
    assert result.email == "john@example.com"
    mock_repository.add.assert_called_once()

@pytest.mark.asyncio
async def test_create_user_invalid_email(user_service):
    # Act & Assert
    with pytest.raises(ValueError, match="Invalid email"):
        await user_service.create_user(
            name="John", 
            email="invalid-email"
        )
```

### Integration Tests

```python
# tests/integration/test_user_endpoints.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import override_get_db_session

@pytest.fixture
def client():
    return TestClient(app)

def test_create_user_endpoint(client):
    # Act
    response = client.post(
        "/users/",
        json={"name": "John", "email": "john@example.com"}
    )
    
    # Assert
    assert response.status_code == 200
    assert response.json()["name"] == "John"

def test_get_user_endpoint(client):
    # Arrange
    client.post(
        "/users/",
        json={"name": "John", "email": "john@example.com"}
    )
    
    # Act
    response = client.get("/users/1")
    
    # Assert
    assert response.status_code == 200
    assert response.json()["email"] == "john@example.com"
```

---

## Loose Coupling & Repository Pattern

```python
# app/repositories/base_repository.py
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar('T')

class IRepository(ABC, Generic[T]):
    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[T]:
        pass
    
    @abstractmethod
    async def add(self, entity: T) -> T:
        pass
    
    @abstractmethod
    async def update(self, entity: T) -> T:
        pass
    
    @abstractmethod
    async def delete(self, entity: T) -> None:
        pass
    
    @abstractmethod
    async def list(self, skip: int = 0, limit: int = 10) -> List[T]:
        pass

# app/repositories/user_repository.py
from app.models.user import User

class UserRepository(IRepository[User]):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, id: int) -> Optional[User]:
        return await self.session.get(User, id)
    
    async def add(self, entity: User) -> User:
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity
    
    async def update(self, entity: User) -> User:
        await self.session.merge(entity)
        await self.session.commit()
        return entity
    
    async def delete(self, entity: User) -> None:
        await self.session.delete(entity)
        await self.session.commit()
    
    async def list(self, skip: int = 0, limit: int = 10) -> List[User]:
        result = await self.session.execute(
            select(User).offset(skip).limit(limit)
        )
        return result.scalars().all()
```

---

## Pre-Deployment Checklist

- [ ] Code passes `pylint` (`pylint src/`)
- [ ] Code passes `black` formatter (`black --check src/`)
- [ ] Type hints pass `mypy` (`mypy src/`)
- [ ] All unit tests pass (>80% coverage)
- [ ] All integration tests pass
- [ ] API documentation generated (FastAPI auto-docs)
- [ ] Environment variables documented
- [ ] Database migrations tested
- [ ] Docker image builds successfully

---

## Common Pitfalls & Solutions

| Pitfall | Problem | Solution |
|---------|---------|----------|
| **Circular imports** | Module A imports B, B imports A | Restructure to break cycle |
| **Blocking I/O in async** | Defeats async benefits | Use `async/await` consistently |
| **Hard-coded DB connection** | Can't test, not portable | Inject connection string |
| **No request validation** | Invalid data reaches services | Use Pydantic models |
| **Missing error handling** | Unhandled exceptions crash app | Use try-catch, custom exceptions |
| **Tight coupling to ORM** | Hard to swap database | Use repositories + interfaces |
| **Incorrect Graph SDK package** | `microsoft-graph-core` is deprecated | Use `msgraph-core` and `msgraph-sdk` |
| **APScheduler Pickling Error** | `SQLAlchemyJobStore` fails to serialize objects with DB sessions | Use `MemoryJobStore` locally or schedule static/class methods |
| **Windows compatibility** | `signal.pause()` causes `AttributeError` | Use `while True: time.sleep(1)` for main thread blocking |
| **Indentation Errors** | Mixed spaces/tabs or rogue spaces crash on load | Ensure strict adherence to PEP8 indentation |

---

## Revision Notes

**Version:** 1.0  
**Last Updated:** May 8, 2026  
**Maintainer:** Solutions Architecture Team

