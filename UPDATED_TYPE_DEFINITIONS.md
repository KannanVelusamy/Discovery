# Updated Type Definitions

## ✅ Changes to `profile.d.ts`

Updated the TypeScript type definitions to reflect the simplified entitlement flow.

---

## 📋 New Type Structure

### 1. **`BasicUserData`** - Frontend Only
```typescript
export interface BasicUserData {
  username: string;
  email: string;
  name?: string;
}
```

**Used by:**
- `/api/entitlement` response
- `profile-check` page
- `localStorage` storage
- Frontend → Agent communication

**Purpose:** Minimal user info extracted from SSO session

---

### 2. **`EntitlementApiResponse`** - Frontend API
```typescript
export interface EntitlementApiResponse {
  data: BasicUserData;
}
```

**Used by:**
- `/api/entitlement` route response
- `profile-check` page fetch

**Purpose:** Type-safe API response structure

---

### 3. **`FullUserProfile`** - Agent/Backend Only
```typescript
export interface FullUserProfile {
  username: string;
  email: string;
  employeeId: string;
  firstName: string;
  lastName: string;
  role: string[];
  status: string;
}
```

**Used by:**
- Backend agent (via MCP)
- Documentation/reference

**Purpose:** Complete profile data from entitlement_mcp

---

### 4. **`EntitlementMcpResponse`** - MCP Response
```typescript
export interface EntitlementMcpResponse {
  data: {
    profile: FullUserProfile;
  };
}
```

**Used by:**
- Backend agent tool responses
- Documentation/reference

**Purpose:** Type definition for MCP server responses

---

## 🔄 Before vs After

### Before (Old Structure):
```typescript
// Single profile type for everything
export interface UserProfile {
  email: string;
  employeeId: string;
  firstName: string;
  lastName: string;
  role: string[];
  status: string;
  username: string;
}

export interface ProfileApiResponse {
  data: {
    profile: UserProfile;
  };
}
```

**Problems:**
- ❌ Implied frontend has full profile
- ❌ No distinction between frontend/backend data
- ❌ Misleading - frontend doesn't fetch full profile anymore

---

### After (New Structure):
```typescript
// Separate types for different contexts

// Frontend: Basic data only
export interface BasicUserData {
  username: string;
  email: string;
  name?: string;
}

// Backend: Full profile data
export interface FullUserProfile {
  username: string;
  email: string;
  employeeId: string;
  firstName: string;
  lastName: string;
  role: string[];
  status: string;
}
```

**Benefits:**
- ✅ Clear separation of concerns
- ✅ Frontend types match actual data
- ✅ Backend types documented for reference
- ✅ Type-safe at every level

---

## 📊 Type Usage Map

```
Frontend:
  ├── BasicUserData ← localStorage
  ├── BasicUserData ← profile-check page
  └── EntitlementApiResponse ← API response

Backend Agent:
  ├── BasicUserData ← receives from frontend (username)
  ├── FullUserProfile ← receives from MCP
  └── EntitlementMcpResponse ← MCP tool response

MCP Server:
  └── EntitlementMcpResponse ← returns to agent
```

---

## 💡 Key Insights

### 1. **Frontend Never Sees Full Profile**
```typescript
// Frontend only has:
{ username: "kannan.velusamy", email: "...", name: "..." }

// NOT:
{ username, email, firstName, lastName, role, status, employeeId }
```

### 2. **Agent Gets Full Profile When Needed**
```typescript
// Agent calls entitlement_mcp tool
// Receives FullUserProfile with all fields
// Frontend never needs this data
```

### 3. **Type Safety Everywhere**
```typescript
// profile-check page
const [userData, setUserData] = useState<BasicUserData | null>(null);

// API route
return NextResponse.json<EntitlementApiResponse>({
  data: { username, email, name }
});
```

---

## ✅ Documentation Benefits

Each type now has clear JSDoc comments explaining:
- **What** it represents
- **Where** it's used
- **Who** uses it (frontend/backend/MCP)

Example:
```typescript
/**
 * Basic user data extracted from SSO session.
 * This is stored in localStorage for the frontend to pass to the agent.
 */
export interface BasicUserData { ... }
```

---

## 🎯 Summary

| Type | Scope | Data Level | Used By |
|------|-------|------------|---------|
| `BasicUserData` | Frontend | Minimal | profile-check, localStorage, Thread |
| `EntitlementApiResponse` | Frontend | Minimal | /api/entitlement response |
| `FullUserProfile` | Backend | Complete | Agent, MCP |
| `EntitlementMcpResponse` | Backend | Complete | MCP tool responses |

---

## 🚀 Result

The type definitions now accurately reflect:
- ✅ The simplified entitlement flow
- ✅ Frontend/backend separation
- ✅ What data exists where
- ✅ Clear documentation for developers

Perfect alignment with the simplified architecture! 🎉

