# SPA (Single Page Application) Tech Stack Opinion

## Stack Profile

| Aspect | Recommendation |
|--------|-----------------|
| **Language** | TypeScript (strict mode) |
| **Framework** | React 18+ or Vue 3+ |
| **Build Tool** | Vite 5.x |
| **State Management** | Zustand or Pinia (for large apps) |
| **Styling** | Tailwind CSS or CSS Modules |
| **Testing** | Vitest (unit) + Playwright (e2e) |
| **Linting** | ESLint + Prettier |
| **API Client** | React Query / TanStack Query |
| **Deployment** | Vercel, Netlify, or GitHub Pages |

---

## Architectural Principles

### 1. **Component Architecture (MVC-inspired)**

#### Model (Business Logic)
```typescript
// hooks/useUserStore.ts - Centralized state management
import { create } from 'zustand';

interface UserState {
  user: User | null;
  fetchUser: (id: string) => Promise<void>;
  updateUser: (user: User) => void;
}

export const useUserStore = create<UserState>((set) => ({
  user: null,
  fetchUser: async (id) => {
    const data = await api.getUser(id);
    set({ user: data });
  },
  updateUser: (user) => set({ user }),
}));
```

#### View (UI Components)
```typescript
// components/UserProfile.tsx - Pure presentation component
interface UserProfileProps {
  user: User;
  onUpdate: (user: User) => void;
}

export const UserProfile: React.FC<UserProfileProps> = ({ user, onUpdate }) => {
  return (
    <div className="user-profile">
      <h1>{user.name}</h1>
      <button onClick={() => onUpdate(user)}>Update</button>
    </div>
  );
};
```

#### Controller (Container Component)
```typescript
// pages/UserPage.tsx - Orchestrates state and UI
export const UserPage: React.FC = () => {
  const { user, fetchUser, updateUser } = useUserStore();

  React.useEffect(() => {
    fetchUser('123');
  }, []);

  return <UserProfile user={user} onUpdate={updateUser} />;
};
```

---

### 2. **SOLID Principles Application**

#### S - Single Responsibility
Each component/hook does **one thing**:
- `useUserStore` → User state management
- `UserProfile` → User display
- `UserPage` → Page orchestration

```typescript
// ❌ BAD - Component doing too much
function UserComponent() {
  // Fetches, displays, formats, validates, exports data
}

// ✅ GOOD - Single concern
function UserProfile() {
  // Only displays user data
}
```

#### O - Open/Closed
Components should be **open for extension, closed for modification**:

```typescript
// ✅ GOOD - Extensible through props
interface ButtonProps {
  variant?: 'primary' | 'secondary';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({ 
  variant = 'primary', 
  size = 'md', 
  children 
}) => (
  <button className={`btn-${variant} btn-${size}`}>
    {children}
  </button>
);
```

#### L - Liskov Substitution
Derived components must be substitutable for base components:

```typescript
// Base interface
interface InputProps {
  value: string;
  onChange: (value: string) => void;
}

// ✅ GOOD - Implements contract
export const TextInput: React.FC<InputProps> = ({ value, onChange }) => (
  <input value={value} onChange={(e) => onChange(e.target.value)} />
);

// ✅ GOOD - Also implements contract
export const TextArea: React.FC<InputProps> = ({ value, onChange }) => (
  <textarea value={value} onChange={(e) => onChange(e.target.value)} />
);

// ✅ These are interchangeable
type AnyInput = React.FC<InputProps>;
```

#### I - Interface Segregation
Components accept **only what they need**:

```typescript
// ❌ BAD - Passes entire user object
interface UserCardProps {
  user: User; // User has 50 fields
}

// ✅ GOOD - Passes only needed fields
interface UserCardProps {
  name: string;
  email: string;
  avatar: string;
}
```

#### D - Dependency Inversion
Depend on abstractions, not concrete implementations:

```typescript
// ❌ BAD - Tightly coupled to HTTP client
function useUserData() {
  const [user, setUser] = useState(null);
  
  useEffect(() => {
    fetch('/api/user').then(setUser);
  }, []);
  
  return user;
}

// ✅ GOOD - Depends on abstraction
interface UserAPI {
  getUser(): Promise<User>;
}

function useUserData(api: UserAPI) {
  const [user, setUser] = useState(null);
  
  useEffect(() => {
    api.getUser().then(setUser);
  }, [api]);
  
  return user;
}
```

---

### 3. **Loose Coupling & Testability**

#### Dependency Injection Pattern
```typescript
// services/userService.ts
export class UserService {
  constructor(private api: HttpClient) {}

  async getUser(id: string): Promise<User> {
    return this.api.get(`/users/${id}`);
  }
}

// pages/UserPage.tsx
export const UserPage: React.FC = () => {
  // Inject real API in production, mock in tests
  const userService = new UserService(httpClient);
  
  // Use userService...
};
```

#### Custom Hooks for Logic Extraction
```typescript
// hooks/useFormValidation.ts
export function useFormValidation<T>(initialData: T) {
  const [data, setData] = useState(initialData);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validate = (schema: ValidationSchema) => {
    // Validation logic
  };

  return { data, errors, validate };
}

// ✅ Testable - hook logic is pure and isolated
```

#### Mocking & Testing
```typescript
// __tests__/useUserStore.test.ts
import { renderHook, act } from '@testing-library/react';
import { useUserStore } from '../hooks/useUserStore';
import * as api from '../api/user';

jest.mock('../api/user');

test('fetches user data', async () => {
  (api.getUser as jest.Mock).mockResolvedValue({ 
    id: '1', 
    name: 'John' 
  });

  const { result } = renderHook(() => useUserStore());

  await act(() => result.current.fetchUser('1'));

  expect(result.current.user).toEqual({ id: '1', name: 'John' });
});
```

---

## Directory Structure

```
src/
  ├── components/          # UI components (presentation)
  │   ├── Button.tsx
  │   ├── UserProfile.tsx
  │   └── __tests__/
  ├── hooks/               # Business logic (hooks)
  │   ├── useUserStore.ts
  │   ├── useFormValidation.ts
  │   └── __tests__/
  ├── services/            # External API calls
  │   ├── userService.ts
  │   ├── authService.ts
  │   └── __tests__/
  ├── pages/               # Page components (orchestrators)
  │   ├── UserPage.tsx
  │   └── __tests__/
  ├── types/               # TypeScript interfaces
  │   └── index.ts
  ├── utils/               # Utilities
  │   └── __tests__/
  └── main.tsx
```

---

## Testing Strategy

### Unit Tests (>80% target)
- Test individual hooks in isolation
- Mock API calls
- Test component prop handling

```bash
npm run test:unit
```

### Integration Tests
- Test multiple components together
- Test store + component interactions

```bash
npm run test:integration
```

### E2E Tests
- Real browser, full workflow
- Use Playwright

```bash
npm run test:e2e
```

---

## Build & Performance Optimization

### Code Splitting
```typescript
// vite.config.ts
export default {
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor': ['react', 'react-dom'],
          'utils': ['lodash', 'date-fns'],
        }
      }
    }
  }
};
```

### Lazy Loading Components
```typescript
import { lazy, Suspense } from 'react';

const UserPage = lazy(() => import('./pages/UserPage'));

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <UserPage />
    </Suspense>
  );
}
```

### CSS-in-JS vs Utility CSS
- **Tailwind CSS** (recommended): Fast, predictable, great for large projects
- **CSS Modules**: Good isolation, zero-runtime overhead
- **Styled Components**: Flexible but runtime cost

---

## Deployment Best Practices

### Pre-Deployment Checklist
- [ ] TypeScript strict mode passes
- [ ] ESLint warnings = 0
- [ ] Unit test coverage ≥ 80%
- [ ] E2E tests pass
- [ ] Bundle size analyzed (`npm run analyze`)
- [ ] Lighthouse score ≥ 90

### Environment Management
```typescript
// config/env.ts
export const config = {
  api: {
    baseURL: process.env.REACT_APP_API_URL,
    timeout: 5000,
  },
  auth: {
    provider: process.env.REACT_APP_AUTH_PROVIDER,
  },
};
```

---

## Common Pitfalls & How to Avoid Them

| Pitfall | Problem | Solution |
|---------|---------|----------|
| **Over-fetching** | Component renders before data loads | Use React Query with stale-while-revalidate |
| **Prop drilling** | Pass props through many layers | Use context or store (Zustand) |
| **Unnecessary re-renders** | Performance degradation | Use `useMemo`, `useCallback`, `React.memo` |
| **Tight coupling** | Hard to test, modify | Use dependency injection, interfaces |
| **State in multiple places** | Inconsistent data | Single source of truth (store) |
| **Missing error handling** | App crashes on API failure | Try-catch, error boundaries, fallbacks |

---

## Stack Decisions Chart

```
Is the app static (no dynamic state)?
  ├─ YES → Plain TypeScript + Vite + HTML5 Canvas (if rendering-heavy)
  └─ NO → React 18+ with Zustand
  
Is state shared across many components?
  ├─ YES → Zustand or Pinia
  └─ NO → Local useState in component
  
Do you need server-side rendering?
  ├─ YES → Next.js (not a pure SPA anymore)
  └─ NO → Vite + React/Vue
  
Is performance critical (>100k items)?
  ├─ YES → Canvas or WebGL
  └─ NO → React with Tailwind
```

---

## Revision Notes

**Version:** 1.0  
**Last Updated:** May 8, 2026  
**Maintainer:** Solutions Architecture Team

