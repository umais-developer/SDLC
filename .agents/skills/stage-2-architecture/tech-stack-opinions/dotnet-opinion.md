# .NET Tech Stack Opinion

## Stack Profile

| Aspect | Recommendation |
|--------|-----------------|
| **Runtime** | .NET 8.0+ |
| **Pattern** | MVC / Clean Architecture |
| **Web Framework** | ASP.NET Core 8.0+ |
| **ORM** | Entity Framework Core 8.0+ |
| **Dependency Injection** | Built-in `IServiceCollection` |
| **Testing** | xUnit + Moq |
| **API Style** | RESTful with OpenAPI/Swagger |
| **Logging** | Serilog |
| **Validation** | FluentValidation |
| **Database** | SQL Server / PostgreSQL |
| **Deployment** | Docker + Azure App Service or AWS |

---

## Architectural Pattern: Clean Architecture + MVC

### Layered Architecture

```
┌─────────────────────────────────────────┐
│          Presentation Layer             │
│    (ASP.NET Core Controllers)           │
│         WebAPI / Pages / Endpoints      │
└────────────────┬────────────────────────┘
                 │ (DTO contracts)
┌────────────────▼────────────────────────┐
│           Application Layer             │
│    (Business Logic, Use Cases)          │
│      Services, Commands, Queries        │
└────────────────┬────────────────────────┘
                 │ (Interface contracts)
┌────────────────▼────────────────────────┐
│             Domain Layer                │
│         Entities, Interfaces            │
│        Business Rules (SOLID)           │
└────────────────┬────────────────────────┘
                 │ (Repository interface)
┌────────────────▼────────────────────────┐
│         Infrastructure Layer            │
│    (Database, External Services)        │
│        EF Core, Repositories            │
└─────────────────────────────────────────┘
```

### Directory Structure

```
src/
├── ProjectName.Presentation/          # ASP.NET Core WebAPI
│   ├── Controllers/
│   │   ├── UsersController.cs
│   │   └── ProductsController.cs
│   ├── Filters/
│   ├── Middleware/
│   ├── Program.cs
│   └── appsettings.json
├── ProjectName.Application/           # Business Logic
│   ├── Services/
│   │   ├── UserService.cs
│   │   └── IUserService.cs
│   ├── Commands/                      # CQRS
│   │   └── CreateUserCommand.cs
│   ├── Queries/
│   │   └── GetUserQuery.cs
│   ├── DTOs/
│   │   └── UserDto.cs
│   └── Validators/
│       └── CreateUserValidator.cs
├── ProjectName.Domain/                # Domain Logic
│   ├── Entities/
│   │   └── User.cs
│   ├── Interfaces/
│   │   ├── IUserRepository.cs
│   │   └── IUnitOfWork.cs
│   └── ValueObjects/
│       └── Email.cs
├── ProjectName.Infrastructure/        # Data Access
│   ├── Data/
│   │   ├── AppDbContext.cs
│   │   └── Migrations/
│   ├── Repositories/
│   │   └── UserRepository.cs
│   └── ExternalServices/
│       └── EmailService.cs
└── ProjectName.Tests/                 # Unit & Integration Tests
    ├── Unit/
    ├── Integration/
    └── Fixtures/
```

---

## SOLID Principles in .NET

### S - Single Responsibility Principle

```csharp
// ❌ BAD - Multiple responsibilities
public class UserService
{
    public void CreateUser(UserDto dto)
    {
        // Validates
        // Creates entity
        // Saves to DB
        // Sends email
        // Logs
    }
}

// ✅ GOOD - Each class has one responsibility
public interface IUserService
{
    Task<User> CreateAsync(CreateUserCommand cmd);
}

public interface IEmailService
{
    Task SendWelcomeEmailAsync(User user);
}

public interface ILogger
{
    void LogUserCreated(User user);
}

public class UserService : IUserService
{
    private readonly IUserRepository _repository;
    private readonly IEmailService _emailService;
    private readonly ILogger _logger;

    public UserService(
        IUserRepository repository,
        IEmailService emailService,
        ILogger logger)
    {
        _repository = repository;
        _emailService = emailService;
        _logger = logger;
    }

    public async Task<User> CreateAsync(CreateUserCommand cmd)
    {
        var user = new User(cmd.Name, cmd.Email);
        await _repository.AddAsync(user);
        
        await _emailService.SendWelcomeEmailAsync(user);
        _logger.LogUserCreated(user);

        return user;
    }
}
```

### O - Open/Closed Principle

```csharp
// ❌ BAD - Must modify to add new discount type
public class OrderService
{
    public decimal CalculateDiscount(Order order)
    {
        if (order.Type == "VIP")
            return order.Total * 0.2m;
        else if (order.Type == "Loyalty")
            return order.Total * 0.1m;
        else if (order.Type == "Bulk")
            return order.Total * 0.15m;
        // Adding new type requires code change
    }
}

// ✅ GOOD - Open for extension, closed for modification
public interface IDiscountStrategy
{
    decimal Calculate(Order order);
}

public class VIPDiscountStrategy : IDiscountStrategy
{
    public decimal Calculate(Order order) => order.Total * 0.2m;
}

public class LoyaltyDiscountStrategy : IDiscountStrategy
{
    public decimal Calculate(Order order) => order.Total * 0.1m;
}

public class BulkDiscountStrategy : IDiscountStrategy
{
    public decimal Calculate(Order order) => order.Total * 0.15m;
}

// New discounts added without modifying existing code
public class OrderService
{
    private readonly IDiscountStrategy _discountStrategy;

    public OrderService(IDiscountStrategy discountStrategy)
    {
        _discountStrategy = discountStrategy;
    }

    public decimal CalculateDiscount(Order order) 
        => _discountStrategy.Calculate(order);
}
```

### L - Liskov Substitution Principle

```csharp
// ✅ GOOD - All implementations honor the contract
public interface IRepository<T> where T : class
{
    Task<T> GetByIdAsync(int id);
    Task AddAsync(T entity);
    Task UpdateAsync(T entity);
    Task DeleteAsync(T entity);
}

public class UserRepository : IRepository<User>
{
    public async Task<User> GetByIdAsync(int id) 
        => await _context.Users.FindAsync(id);
    
    public async Task AddAsync(User entity) 
        => _context.Users.Add(entity);
    
    public async Task UpdateAsync(User entity) 
        => _context.Users.Update(entity);
    
    public async Task DeleteAsync(User entity) 
        => _context.Users.Remove(entity);
}

// Can substitute UserRepository for IRepository<User>
public class UserService
{
    private readonly IRepository<User> _repository;

    public UserService(IRepository<User> repository) 
        => _repository = repository;

    // Works with any IRepository<User> implementation
}
```

### I - Interface Segregation Principle

```csharp
// ❌ BAD - Fat interface
public interface IUserManager
{
    Task CreateUserAsync(User user);
    Task DeleteUserAsync(int id);
    Task SendEmailAsync(User user, string message);
    Task LogAuditAsync(string action);
    Task UpdateRoleAsync(User user, Role role);
    Task GenerateReportAsync(DateTime start, DateTime end);
}

// ✅ GOOD - Segregated interfaces
public interface IUserRepository
{
    Task CreateAsync(User user);
    Task DeleteAsync(int id);
    Task UpdateAsync(User user);
}

public interface IEmailService
{
    Task SendAsync(User user, string message);
}

public interface IAuditLogger
{
    Task LogAsync(string action);
}

public interface IRoleService
{
    Task AssignRoleAsync(User user, Role role);
}

// Only implement what you need
public class UserController : ControllerBase
{
    private readonly IUserRepository _userRepository;
    private readonly IEmailService _emailService;

    public UserController(IUserRepository userRepo, IEmailService emailSvc)
    {
        _userRepository = userRepo;
        _emailService = emailSvc;
    }
}
```

### D - Dependency Inversion Principle

```csharp
// ❌ BAD - Depends on concrete implementation
public class UserService
{
    private readonly SqlServerUserRepository _repository;

    public UserService()
    {
        _repository = new SqlServerUserRepository();
    }
}

// ✅ GOOD - Depends on abstraction
public interface IUserRepository
{
    Task<User> GetByIdAsync(int id);
}

public class UserService
{
    private readonly IUserRepository _repository;

    // Injected, not created
    public UserService(IUserRepository repository)
    {
        _repository = repository;
    }
}

// Can inject different implementations
services.AddScoped<IUserRepository, SqlServerUserRepository>();
// Or for testing:
services.AddScoped<IUserRepository, MockUserRepository>();
```

---

## Dependency Injection & Configuration

### Service Registration (Program.cs)

```csharp
var builder = WebApplication.CreateBuilder(args);

// Add services to the container
builder.Services.AddScoped<IUserService, UserService>();
builder.Services.AddScoped<IUserRepository, UserRepository>();
builder.Services.AddScoped<IEmailService, EmailService>();

// DbContext
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseSqlServer(builder.Configuration.GetConnectionString("DefaultConnection")));

// Controllers
builder.Services.AddControllers();

// Swagger/OpenAPI
builder.Services.AddSwaggerGen();

var app = builder.Build();

// Configure the HTTP request pipeline
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();
app.UseAuthorization();
app.MapControllers();

app.Run();
```

---

## MVC Pattern in Controllers

```csharp
[ApiController]
[Route("api/[controller]")]
public class UsersController : ControllerBase
{
    private readonly IUserService _userService;

    public UsersController(IUserService userService) 
        => _userService = userService;

    // GET /api/users/{id}
    [HttpGet("{id}")]
    public async Task<ActionResult<UserDto>> GetUserAsync(int id)
    {
        try
        {
            var user = await _userService.GetUserAsync(id);
            if (user == null)
                return NotFound();

            return Ok(new UserDto { Id = user.Id, Name = user.Name });
        }
        catch (Exception ex)
        {
            return BadRequest(ex.Message);
        }
    }

    // POST /api/users
    [HttpPost]
    public async Task<ActionResult<UserDto>> CreateUserAsync([FromBody] CreateUserRequest request)
    {
        var command = new CreateUserCommand(request.Name, request.Email);
        var user = await _userService.CreateUserAsync(command);
        
        return CreatedAtAction(nameof(GetUserAsync), new { id = user.Id }, user);
    }
}
```

---

## Testing Strategy

### Unit Tests with xUnit & Moq

```csharp
public class UserServiceTests
{
    private readonly Mock<IUserRepository> _mockRepository;
    private readonly Mock<IEmailService> _mockEmailService;
    private readonly UserService _service;

    public UserServiceTests()
    {
        _mockRepository = new Mock<IUserRepository>();
        _mockEmailService = new Mock<IEmailService>();
        _service = new UserService(_mockRepository.Object, _mockEmailService.Object);
    }

    [Fact]
    public async Task CreateUserAsync_WithValidData_ReturnsUser()
    {
        // Arrange
        var command = new CreateUserCommand("John", "john@example.com");
        var expectedUser = new User("John", "john@example.com");

        _mockRepository
            .Setup(r => r.AddAsync(It.IsAny<User>()))
            .Returns(Task.CompletedTask);

        // Act
        var result = await _service.CreateUserAsync(command);

        // Assert
        Assert.NotNull(result);
        Assert.Equal("John", result.Name);
        _mockRepository.Verify(r => r.AddAsync(It.IsAny<User>()), Times.Once);
        _mockEmailService.Verify(e => e.SendWelcomeEmailAsync(It.IsAny<User>()), Times.Once);
    }

    [Fact]
    public async Task CreateUserAsync_WithInvalidEmail_ThrowsException()
    {
        // Arrange
        var command = new CreateUserCommand("John", "invalid-email");

        // Act & Assert
        await Assert.ThrowsAsync<ArgumentException>(() => _service.CreateUserAsync(command));
    }
}
```

### Integration Tests

```csharp
public class UserRepositoryIntegrationTests : IAsyncLifetime
{
    private readonly AppDbContext _context;
    private readonly UserRepository _repository;

    public async Task InitializeAsync()
    {
        var options = new DbContextOptionsBuilder<AppDbContext>()
            .UseInMemoryDatabase(databaseName: Guid.NewGuid().ToString())
            .Options;

        _context = new AppDbContext(options);
        await _context.Database.EnsureCreatedAsync();
        _repository = new UserRepository(_context);
    }

    [Fact]
    public async Task AddAsync_WithValidUser_SavesSuccessfully()
    {
        // Arrange
        var user = new User("John", "john@example.com");

        // Act
        await _repository.AddAsync(user);
        await _context.SaveChangesAsync();

        // Assert
        var savedUser = await _context.Users.FirstOrDefaultAsync(u => u.Email == "john@example.com");
        Assert.NotNull(savedUser);
    }

    public async Task DisposeAsync()
    {
        await _context.DisposeAsync();
    }
}
```

---

## Validation with FluentValidation

```csharp
public class CreateUserCommandValidator : AbstractValidator<CreateUserCommand>
{
    public CreateUserCommandValidator()
    {
        RuleFor(x => x.Name)
            .NotEmpty()
            .MinimumLength(3)
            .MaximumLength(100);

        RuleFor(x => x.Email)
            .NotEmpty()
            .EmailAddress();
    }
}

// Register in DI
services.AddValidatorsFromAssembly(typeof(Program).Assembly);

// Use in controller
[HttpPost]
public async Task<ActionResult<UserDto>> CreateUserAsync([FromBody] CreateUserRequest request)
{
    var command = new CreateUserCommand(request.Name, request.Email);
    var validator = new CreateUserCommandValidator();
    var result = await validator.ValidateAsync(command);

    if (!result.IsValid)
        return BadRequest(result.Errors);

    return Ok(await _userService.CreateUserAsync(command));
}
```

---

## Loose Coupling Strategy

### Repository Pattern

```csharp
public interface IUserRepository
{
    Task<User> GetByIdAsync(int id);
    Task AddAsync(User user);
    Task UpdateAsync(User user);
    Task DeleteAsync(User user);
    IQueryable<User> GetAll();
}

public class UserRepository : IUserRepository
{
    private readonly AppDbContext _context;

    public UserRepository(AppDbContext context) => _context = context;

    public async Task<User> GetByIdAsync(int id) 
        => await _context.Users.FindAsync(id);
    
    public async Task AddAsync(User user)
    {
        _context.Users.Add(user);
        await _context.SaveChangesAsync();
    }

    public IQueryable<User> GetAll() => _context.Users;
}

// Decouples business logic from EF Core
public class UserService
{
    private readonly IUserRepository _repository;

    public UserService(IUserRepository repository) => _repository = repository;

    public async Task<User> GetUserAsync(int id) => await _repository.GetByIdAsync(id);
}
```

### Specification Pattern (for complex queries)

```csharp
public abstract class Specification<T> where T : class
{
    public Expression<Func<T, bool>> Criteria { get; protected set; }
    public List<Expression<Func<T, object>>> Includes { get; } = new();

    protected virtual void AddInclude(Expression<Func<T, object>> include) 
        => Includes.Add(include);
}

public class GetActiveUsersSpecification : Specification<User>
{
    public GetActiveUsersSpecification()
    {
        Criteria = u => u.IsActive;
        AddInclude(u => u.Orders);
    }
}

// Repository can evaluate specification
public class SpecificationRepository<T> : IRepository<T> where T : class
{
    public IQueryable<T> ApplySpecification(Specification<T> spec)
    {
        var query = _context.Set<T>();
        return spec.Includes.Aggregate(query, (q, include) => q.Include(include))
            .Where(spec.Criteria);
    }
}
```

---

## Build & Performance

### Pre-Deployment Checklist
- [ ] Build succeeds without warnings (`dotnet build`)
- [ ] Code analysis passes (`dotnet build /p:TreatWarningsAsErrors=true`)
- [ ] All unit tests pass (>80% coverage)
- [ ] Integration tests pass
- [ ] Swagger/OpenAPI documented
- [ ] Database migrations applied
- [ ] appsettings.Production.json configured
- [ ] Secrets not in code (use Secrets Manager)

### Release Build
```bash
dotnet publish -c Release -o ./publish
```

---

## Deployment

### Docker
```dockerfile
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
WORKDIR /app
COPY --from=build /app/publish .
ENTRYPOINT ["dotnet", "ProjectName.Presentation.dll"]
```

### Azure App Service
```bash
az webapp deployment source config-zip --resource-group myGroup \
  --name myApp --src publish.zip
```

---

## Common Pitfalls & Solutions

| Pitfall | Problem | Solution |
|---------|---------|----------|
| **Service Locator** | Hard to test, hidden dependencies | Use constructor injection only |
| **Circular dependencies** | Compile error, design issue | Refactor to break cycle |
| **Entity Framework N+1 queries** | Performance degradation | Use `.Include()`, `AsNoTracking()` |
| **Tight coupling to EF** | Hard to test, swap data stores | Use repositories + interfaces |
| **Missing validation** | Invalid data in database | Use FluentValidation + Model state |
| **Synchronous blocking calls** | Scalability issues | Use async/await throughout |

---

## Revision Notes

**Version:** 1.0  
**Last Updated:** May 8, 2026  
**Maintainer:** Solutions Architecture Team

