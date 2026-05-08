# Java Tech Stack Opinion

## Stack Profile

| Aspect | Recommendation |
|--------|-----------------|
| **Java Version** | 21 LTS (latest LTS) |
| **Framework** | Spring Boot 3.2+ |
| **Pattern** | MVC / Clean Architecture |
| **ORM** | JPA/Hibernate |
| **Dependency Injection** | Spring DI (built-in) |
| **Testing** | JUnit 5 + Mockito |
| **API Style** | RESTful with OpenAPI/Swagger |
| **Build Tool** | Maven or Gradle |
| **Logging** | SLF4J + Logback |
| **Validation** | Jakarta Bean Validation |
| **Database** | PostgreSQL / MySQL |
| **Deployment** | Docker + Tomcat/Undertow |
| **Async Support** | Spring Reactive (WebFlux) or Virtual Threads (Project Loom) |

---

## Architectural Pattern: Clean Architecture + MVC

### Layered Architecture

```
┌─────────────────────────────────────────┐
│       Presentation Layer                │
│    (Spring MVC Controllers)             │
│         REST Endpoints, DTOs            │
└────────────────┬────────────────────────┘
                 │ (Request/Response DTOs)
┌────────────────▼────────────────────────┐
│          Application Layer              │
│        Business Logic, Use Cases        │
│          Services, Validators           │
└────────────────┬────────────────────────┘
                 │ (Domain models)
┌────────────────▼────────────────────────┐
│            Domain Layer                 │
│      Entities, Interfaces, Rules        │
│        Business logic (SOLID)           │
└────────────────┬────────────────────────┘
                 │ (Repository interface)
┌────────────────▼────────────────────────┐
│       Infrastructure Layer              │
│   (Database, External Services)         │
│        Repositories, Adapters           │
└─────────────────────────────────────────┘
```

### Directory Structure

```
src/
├── main/
│   ├── java/com/example/app/
│   │   ├── AppApplication.java            # Main application class
│   │   ├── config/                        # Configuration
│   │   │   ├── AppConfig.java
│   │   │   └── SecurityConfig.java
│   │   ├── api/                           # Presentation layer
│   │   │   ├── controller/
│   │   │   │   ├── UserController.java
│   │   │   │   └── ProductController.java
│   │   │   └── dto/                       # Data Transfer Objects
│   │   │       ├── UserCreateRequest.java
│   │   │       └── UserResponse.java
│   │   ├── service/                       # Application layer
│   │   │   ├── UserService.java
│   │   │   ├── ProductService.java
│   │   │   └── EmailService.java
│   │   ├── domain/                        # Domain layer
│   │   │   ├── entity/
│   │   │   │   ├── User.java
│   │   │   │   └── Product.java
│   │   │   ├── exception/
│   │   │   │   └── UserNotFoundException.java
│   │   │   └── valueobject/
│   │   │       └── Email.java
│   │   ├── repository/                    # Infrastructure layer
│   │   │   ├── UserRepository.java
│   │   │   ├── ProductRepository.java
│   │   │   └── BaseRepository.java
│   │   └── util/
│   │       ├── validator/
│   │       └── mapper/
│   └── resources/
│       ├── application.properties
│       ├── application-dev.properties
│       └── application-prod.properties
└── test/java/com/example/app/
    ├── unit/
    ├── integration/
    └── fixture/
```

---

## SOLID Principles in Java

### S - Single Responsibility Principle

```java
// ❌ BAD - Multiple responsibilities
@Service
public class UserManager {
    public void createUser(UserCreateRequest request) {
        // Validates
        // Creates entity
        // Saves to DB
        // Sends email
        // Logs
    }
}

// ✅ GOOD - Each class has one responsibility
public interface IUserService {
    User createUser(CreateUserCommand cmd);
}

public interface IEmailService {
    void sendWelcomeEmail(User user);
}

public interface IAuditLogger {
    void logUserCreated(User user);
}

@Service
public class UserService implements IUserService {
    private final UserRepository repository;
    private final IEmailService emailService;
    private final IAuditLogger logger;

    public UserService(
        UserRepository repository,
        IEmailService emailService,
        IAuditLogger logger
    ) {
        this.repository = repository;
        this.emailService = emailService;
        this.logger = logger;
    }

    @Override
    @Transactional
    public User createUser(CreateUserCommand cmd) {
        User user = new User(cmd.getName(), cmd.getEmail());
        repository.save(user);
        
        emailService.sendWelcomeEmail(user);
        logger.logUserCreated(user);

        return user;
    }
}
```

### O - Open/Closed Principle

```java
// ❌ BAD - Must modify to add new discount type
@Service
public class OrderService {
    public BigDecimal calculateDiscount(Order order) {
        switch (order.getType()) {
            case VIP:
                return order.getTotal().multiply(BigDecimal.valueOf(0.2));
            case LOYALTY:
                return order.getTotal().multiply(BigDecimal.valueOf(0.1));
            case BULK:
                return order.getTotal().multiply(BigDecimal.valueOf(0.15));
            default:
                return BigDecimal.ZERO;
        }
        // Adding new type requires code change
    }
}

// ✅ GOOD - Open for extension, closed for modification
public interface DiscountStrategy {
    BigDecimal calculate(Order order);
}

@Component
public class VIPDiscountStrategy implements DiscountStrategy {
    @Override
    public BigDecimal calculate(Order order) {
        return order.getTotal().multiply(BigDecimal.valueOf(0.2));
    }
}

@Component
public class LoyaltyDiscountStrategy implements DiscountStrategy {
    @Override
    public BigDecimal calculate(Order order) {
        return order.getTotal().multiply(BigDecimal.valueOf(0.1));
    }
}

// New strategies added without modifying existing code
@Service
public class OrderService {
    private final Map<String, DiscountStrategy> strategies;

    public OrderService(List<DiscountStrategy> strategyList) {
        this.strategies = strategyList.stream()
            .collect(Collectors.toMap(s -> s.getClass().getSimpleName(), s -> s));
    }

    public BigDecimal calculateDiscount(Order order) {
        return strategies.getOrDefault(
            order.getDiscountStrategy(),
            (o) -> BigDecimal.ZERO
        ).calculate(order);
    }
}
```

### L - Liskov Substitution Principle

```java
// ✅ GOOD - All implementations honor the contract
public interface Repository<T, ID> {
    T findById(ID id);
    T save(T entity);
    void update(T entity);
    void delete(T entity);
}

@Repository
public class UserRepository implements Repository<User, Long> {
    @Autowired
    private JpaRepository<User, Long> jpaRepository;

    @Override
    public User findById(Long id) {
        return jpaRepository.findById(id).orElse(null);
    }

    @Override
    public User save(User entity) {
        return jpaRepository.save(entity);
    }

    @Override
    public void update(User entity) {
        jpaRepository.save(entity);
    }

    @Override
    public void delete(User entity) {
        jpaRepository.delete(entity);
    }
}

// Can substitute UserRepository for Repository<User, Long>
@Service
public class UserService {
    private final Repository<User, Long> repository;

    public UserService(Repository<User, Long> repository) {
        this.repository = repository;
    }

    public User getUser(Long id) {
        return repository.findById(id);
    }
}
```

### I - Interface Segregation Principle

```java
// ❌ BAD - Fat interface
public interface IUserManager {
    void createUser(User user);
    void deleteUser(Long id);
    void sendEmail(User user, String message);
    void logAudit(String action);
    void assignRole(User user, Role role);
    Report generateReport(LocalDate start, LocalDate end);
}

// ✅ GOOD - Segregated interfaces
public interface IUserRepository {
    User create(User user);
    void delete(Long id);
    User update(User user);
}

public interface IEmailService {
    void send(User user, String message);
}

public interface IAuditLogger {
    void log(String action);
}

public interface IRoleService {
    void assignRole(User user, Role role);
}

// Only inject what you need
@RestController
@RequestMapping("/users")
public class UserController {
    private final IUserRepository userRepository;
    private final IEmailService emailService;

    public UserController(
        IUserRepository userRepository,
        IEmailService emailService
    ) {
        this.userRepository = userRepository;
        this.emailService = emailService;
    }
}
```

### D - Dependency Inversion Principle

```java
// ❌ BAD - Depends on concrete implementation
@Service
public class UserService {
    private final SqlUserRepository repository;

    public UserService() {
        this.repository = new SqlUserRepository();  // Tight coupling
    }
}

// ✅ GOOD - Depends on abstraction
public interface IUserRepository {
    User findById(Long id);
}

@Service
public class UserService {
    private final IUserRepository repository;

    // Injected, not created
    public UserService(IUserRepository repository) {
        this.repository = repository;
    }
}

// Configuration injects correct implementation
@Configuration
public class PersistenceConfig {
    @Bean
    public IUserRepository userRepository(JpaRepository<User, Long> jpa) {
        return new JpaUserRepository(jpa);
    }
}
```

---

## Dependency Injection & Spring Configuration

### Service Registration

```java
// src/main/java/com/example/app/AppApplication.java
@SpringBootApplication
public class AppApplication {
    public static void main(String[] args) {
        SpringApplication.run(AppApplication.class, args);
    }
}

// src/main/java/com/example/app/config/AppConfig.java
@Configuration
public class AppConfig {
    
    @Bean
    public UserService userService(UserRepository repository, IEmailService emailService) {
        return new UserService(repository, emailService);
    }
    
    @Bean
    public IEmailService emailService() {
        return new EmailService();
    }
    
    @Bean
    public IAuditLogger auditLogger() {
        return new SlfAuditLogger();
    }
}

// In application.properties
server.port=8080
spring.datasource.url=jdbc:postgresql://localhost:5432/mydb
spring.datasource.username=admin
spring.datasource.password=${DB_PASSWORD}
spring.jpa.hibernate.ddl-auto=validate
```

---

## MVC Pattern in Controllers

```java
// src/main/java/com/example/app/api/controller/UserController.java
@RestController
@RequestMapping("/api/v1/users")
@Validated
public class UserController {
    
    private final UserService userService;
    private static final Logger logger = LoggerFactory.getLogger(UserController.class);

    public UserController(UserService userService) {
        this.userService = userService;
    }

    @GetMapping("/{id}")
    @ApiOperation("Get user by ID")
    public ResponseEntity<UserResponse> getUser(
        @PathVariable @Positive Long id
    ) {
        try {
            User user = userService.getUserById(id);
            return ResponseEntity.ok(UserResponse.from(user));
        } catch (UserNotFoundException e) {
            logger.warn("User not found: {}", id);
            return ResponseEntity.notFound().build();
        }
    }

    @PostMapping
    @ApiOperation("Create a new user")
    public ResponseEntity<UserResponse> createUser(
        @Valid @RequestBody UserCreateRequest request
    ) {
        try {
            User user = userService.createUser(
                request.getName(),
                request.getEmail()
            );
            return ResponseEntity
                .created(URI.create("/api/v1/users/" + user.getId()))
                .body(UserResponse.from(user));
        } catch (ValidationException e) {
            logger.error("Validation failed: {}", e.getMessage());
            return ResponseEntity.badRequest().build();
        }
    }

    @PutMapping("/{id}")
    @ApiOperation("Update user")
    public ResponseEntity<UserResponse> updateUser(
        @PathVariable @Positive Long id,
        @Valid @RequestBody UserUpdateRequest request
    ) {
        User user = userService.updateUser(id, request);
        return ResponseEntity.ok(UserResponse.from(user));
    }

    @DeleteMapping("/{id}")
    @ApiOperation("Delete user")
    public ResponseEntity<Void> deleteUser(@PathVariable @Positive Long id) {
        userService.deleteUser(id);
        return ResponseEntity.noContent().build();
    }
}
```

---

## Domain Entities & Validation

### JPA Entities

```java
// src/main/java/com/example/app/domain/entity/User.java
@Entity
@Table(name = "users", indexes = {
    @Index(name = "idx_email", columnList = "email", unique = true)
})
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class User {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false, length = 100)
    @NotBlank(message = "Name cannot be blank")
    @Size(min = 3, max = 100, message = "Name must be 3-100 characters")
    private String name;
    
    @Column(nullable = false, unique = true, length = 255)
    @Email(message = "Email must be valid")
    private String email;
    
    @Column(name = "created_at", nullable = false, updatable = false)
    @CreationTimestamp
    private LocalDateTime createdAt;
    
    @Column(name = "updated_at")
    @UpdateTimestamp
    private LocalDateTime updatedAt;
    
    @Version
    private Long version;  // Optimistic locking
    
    public static User create(String name, String email) {
        return User.builder()
            .name(name)
            .email(email)
            .build();
    }
}
```

### DTOs with Validation

```java
// src/main/java/com/example/app/api/dto/UserCreateRequest.java
@Data
@NoArgsConstructor
@AllArgsConstructor
public class UserCreateRequest {
    
    @NotBlank(message = "Name is required")
    @Size(min = 3, max = 100, message = "Name must be 3-100 characters")
    private String name;
    
    @NotBlank(message = "Email is required")
    @Email(message = "Email must be valid")
    private String email;
}

// src/main/java/com/example/app/api/dto/UserResponse.java
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class UserResponse {
    private Long id;
    private String name;
    private String email;
    private LocalDateTime createdAt;
    
    public static UserResponse from(User user) {
        return UserResponse.builder()
            .id(user.getId())
            .name(user.getName())
            .email(user.getEmail())
            .createdAt(user.getCreatedAt())
            .build();
    }
}
```

---

## Service Layer & Business Logic

```java
// src/main/java/com/example/app/service/UserService.java
@Service
@Slf4j
@Transactional
public class UserService {
    
    private final UserRepository userRepository;
    private final IEmailService emailService;
    private final IAuditLogger auditLogger;

    public UserService(
        UserRepository userRepository,
        IEmailService emailService,
        IAuditLogger auditLogger
    ) {
        this.userRepository = userRepository;
        this.emailService = emailService;
        this.auditLogger = auditLogger;
    }

    @Transactional(readOnly = true)
    public User getUserById(Long id) {
        return userRepository.findById(id)
            .orElseThrow(() -> new UserNotFoundException("User not found: " + id));
    }

    @Transactional
    public User createUser(String name, String email) {
        // Validate
        if (name == null || name.length() < 3) {
            throw new ValidationException("Name must be at least 3 characters");
        }
        
        if (!email.matches("^[A-Za-z0-9+_.-]+@(.+)$")) {
            throw new ValidationException("Invalid email address");
        }

        // Create entity
        User user = User.create(name, email);

        // Persist
        User savedUser = userRepository.save(user);

        // Side effects
        try {
            emailService.sendWelcomeEmail(savedUser);
            auditLogger.log("USER_CREATED: " + savedUser.getId());
        } catch (Exception e) {
            log.warn("Failed to send welcome email", e);
            // Don't fail the transaction for side effects
        }

        return savedUser;
    }

    @Transactional
    public User updateUser(Long id, UserUpdateRequest request) {
        User user = getUserById(id);
        
        if (request.getName() != null) {
            user.setName(request.getName());
        }

        User updated = userRepository.save(user);
        auditLogger.log("USER_UPDATED: " + updated.getId());
        return updated;
    }

    @Transactional
    public void deleteUser(Long id) {
        User user = getUserById(id);
        userRepository.delete(user);
        auditLogger.log("USER_DELETED: " + id);
    }

    @Transactional(readOnly = true)
    public Page<User> listUsers(int page, int size) {
        return userRepository.findAll(PageRequest.of(page, size));
    }
}
```

---

## Repository Pattern

```java
// src/main/java/com/example/app/repository/UserRepository.java
@Repository
public interface UserRepository extends JpaRepository<User, Long>, UserRepositoryCustom {
    Optional<User> findByEmail(String email);
    List<User> findByNameContainingIgnoreCase(String name);
}

// Custom repository for complex queries
public interface UserRepositoryCustom {
    List<User> findActiveUsersByRole(String role);
}

@Repository
public class UserRepositoryCustomImpl implements UserRepositoryCustom {
    
    @PersistenceContext
    private EntityManager entityManager;

    @Override
    public List<User> findActiveUsersByRole(String role) {
        CriteriaBuilder cb = entityManager.getCriteriaBuilder();
        CriteriaQuery<User> query = cb.createQuery(User.class);
        Root<User> root = query.from(User.class);
        
        query.select(root)
            .where(cb.equal(root.get("active"), true));
        
        return entityManager.createQuery(query).getResultList();
    }
}
```

---

## Testing Strategy

### Unit Tests with JUnit 5 & Mockito

```java
// src/test/java/com/example/app/unit/UserServiceTest.java
@ExtendWith(MockitoExtension.class)
class UserServiceTest {
    
    @Mock
    private UserRepository userRepository;
    
    @Mock
    private IEmailService emailService;
    
    @Mock
    private IAuditLogger auditLogger;
    
    @InjectMocks
    private UserService userService;

    @Test
    void testCreateUserSuccess() {
        // Arrange
        String name = "John Doe";
        String email = "john@example.com";
        User expectedUser = User.builder()
            .id(1L)
            .name(name)
            .email(email)
            .build();

        when(userRepository.save(any(User.class)))
            .thenReturn(expectedUser);

        // Act
        User result = userService.createUser(name, email);

        // Assert
        assertNotNull(result);
        assertEquals(name, result.getName());
        assertEquals(email, result.getEmail());
        
        verify(userRepository, times(1)).save(any(User.class));
        verify(emailService, times(1)).sendWelcomeEmail(expectedUser);
    }

    @Test
    void testCreateUserWithInvalidEmail() {
        // Act & Assert
        assertThrows(
            ValidationException.class,
            () -> userService.createUser("John", "invalid-email")
        );
    }

    @Test
    void testGetUserNotFound() {
        // Arrange
        when(userRepository.findById(999L))
            .thenReturn(Optional.empty());

        // Act & Assert
        assertThrows(
            UserNotFoundException.class,
            () -> userService.getUserById(999L)
        );
    }
}
```

### Integration Tests

```java
// src/test/java/com/example/app/integration/UserControllerIntegrationTest.java
@SpringBootTest
@AutoConfigureMockMvc
class UserControllerIntegrationTest {
    
    @Autowired
    private MockMvc mockMvc;
    
    @Autowired
    private UserRepository userRepository;

    @BeforeEach
    void setUp() {
        userRepository.deleteAll();
    }

    @Test
    void testCreateUserEndpoint() throws Exception {
        // Arrange
        UserCreateRequest request = new UserCreateRequest("John Doe", "john@example.com");

        // Act & Assert
        mockMvc.perform(post("/api/v1/users")
            .contentType(MediaType.APPLICATION_JSON)
            .content(asJsonString(request)))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.name", is("John Doe")))
            .andExpect(jsonPath("$.email", is("john@example.com")));
    }

    @Test
    void testGetUserEndpoint() throws Exception {
        // Arrange
        User user = userRepository.save(User.create("John Doe", "john@example.com"));

        // Act & Assert
        mockMvc.perform(get("/api/v1/users/" + user.getId()))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.name", is("John Doe")));
    }
}
```

---

## Pre-Deployment Checklist

- [ ] Build succeeds (`mvn clean package`)
- [ ] No compiler warnings
- [ ] Code analysis passes (`mvn sonar:sonar`)
- [ ] All unit tests pass (>80% coverage)
- [ ] All integration tests pass
- [ ] Swagger/OpenAPI generated
- [ ] Database migrations applied
- [ ] All environment variables configured
- [ ] Docker image builds successfully
- [ ] Security scan passes (OWASP dependency-check)

---

## Common Pitfalls & Solutions

| Pitfall | Problem | Solution |
|---------|---------|----------|
| **Circular bean dependency** | Spring initialization fails | Refactor to break cycle or use `@Lazy` |
| **N+1 query problem** | Excessive database queries | Use `@Fetch(FetchMode.JOIN)` or query optimization |
| **LazyInitializationException** | Accessing unloaded collection | Use eager loading or `@Transactional` on query method |
| **Tight coupling to Spring** | Hard to test outside container | Use interfaces; mock Spring beans in tests |
| **Missing @Transactional** | Data not persisted | Ensure service methods are `@Transactional` |
| **Blocking I/O operations** | Scalability issues | Consider Spring WebFlux for async |

---

## Revision Notes

**Version:** 1.0  
**Last Updated:** May 8, 2026  
**Maintainer:** Solutions Architecture Team

