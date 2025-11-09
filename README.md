# Discovery Agent

AI-powered conversational agent with Azure AD SSO authentication and profile-based access control.

## 🎯 Overview

Discovery Agent is a modern web application that combines:
- **Azure AD SSO Authentication** - Secure Microsoft authentication
- **Profile-based Entitlement** - User profile verification before access
- **LangGraph Backend** - Powerful AI agent framework
- **Next.js Frontend** - Modern, responsive React interface
- **MCP Integration** - Model Context Protocol for AI agent tools

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Azure AD    │  │   Profile    │  │    Terms     │     │
│  │  Sign In     │→ │   Check      │→ │  & Conditions│ →   │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Main Chat Interface                     │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│              Backend (LangGraph Agent)                      │
│  ┌────────────────────────────────────────────────────┐    │
│  │  LangGraph Chat Agent (GPT-4)                      │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│               MCP Servers (Optional)                        │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Entitlement MCP - User profile verification       │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│              External Services                              │
│  • Profile API (localhost:8080)                             │
│  • OpenAI API (GPT-4)                                       │
└─────────────────────────────────────────────────────────────┘
```

## ✨ Features

### Authentication & Authorization
- ✅ **Azure AD SSO** - Single Sign-On with Microsoft accounts
- ✅ **Profile Verification** - Automatic user profile validation
- ✅ **Terms & Conditions** - Required acceptance before access
- ✅ **Session Management** - Secure JWT-based sessions

### User Interface
- ✅ **Modern Design** - Clean, responsive UI
- ✅ **Loading States** - Beautiful loading animations
- ✅ **Error Handling** - User-friendly error messages
- ✅ **Profile Display** - User info and roles displayed

### AI Chat
- ✅ **GPT-4 Integration** - Powered by OpenAI
- ✅ **Streaming Responses** - Real-time message streaming
- ✅ **LangGraph Backend** - Sophisticated agent orchestration
- ✅ **Chat History** - Conversation persistence

### Developer Experience
- ✅ **TypeScript** - Full type safety
- ✅ **ESLint** - Code quality enforcement
- ✅ **Hot Reload** - Fast development cycles
- ✅ **Console Logging** - Detailed debugging logs

## 📁 Project Structure

```
discovery/
├── frontend/                    # Next.js application
│   ├── src/
│   │   ├── app/
│   │   │   ├── api/
│   │   │   │   ├── auth/       # NextAuth.js endpoints
│   │   │   │   └── entitlement/ # Profile check API
│   │   │   ├── profile-check/   # Profile verification page
│   │   │   ├── terms/           # Terms & conditions page
│   │   │   ├── page.tsx         # Main chat page
│   │   │   └── layout.tsx       # Root layout
│   │   ├── components/          # Reusable components
│   │   ├── lib/                 # Utilities & config
│   │   ├── providers/           # React context providers
│   │   └── types/               # TypeScript types
│   ├── package.json
│   └── .env.local               # Environment variables
│
├── backend/                     # Backend services
│   └── agent/                   # LangGraph agent
│       ├── src/
│       │   └── agent/
│       │       └── graph.py     # Main agent logic
│       ├── langgraph.json       # LangGraph config
│       └── pyproject.toml       # Python dependencies
│
├── mcp/                         # MCP servers
│   ├── entitlement_mcp.py       # Entitlement check tool
│   ├── start_mcp_server.sh      # Startup script
│   └── README.md                # MCP documentation
│
└── docs/                        # Documentation
    └── (various markdown files)
```

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+ and pnpm
- **Python** 3.8+
- **Azure AD Application** (for SSO)
- **OpenAI API Key** (for GPT-4)
- **Profile API** (running on localhost:8080)

### 1. Setup Frontend

```bash
cd frontend

# Install dependencies
pnpm install

# Copy environment template
cp env.local.example .env.local

# Edit .env.local with your credentials:
# - AZURE_AD_CLIENT_ID
# - AZURE_AD_CLIENT_SECRET
# - AZURE_AD_TENANT_ID
# - NEXTAUTH_URL
# - NEXTAUTH_SECRET
# - LANGGRAPH_API_URL

# Start development server
pnpm dev
```

Frontend will be available at: `http://localhost:3000`

### 2. Setup Backend

```bash
cd backend/agent

# Copy environment template
cp env.example .env

# Edit .env with your OpenAI API key:
# OPENAI_API_KEY=sk-...

# Start LangGraph server
langgraph dev
```

Backend will be available at: `http://localhost:8123`

### 3. Setup MCP Server (Optional)

```bash
cd mcp

# Start MCP server (automatically creates venv)
./start_mcp_server.sh
```

## 🔐 Azure AD Setup

1. **Create Azure AD App Registration**
   - Go to Azure Portal → Azure Active Directory → App registrations
   - New registration

2. **Configure Authentication**
   - Redirect URIs: `http://localhost:3000/api/auth/callback/azure-ad`
   - Front-channel logout URL: `http://localhost:3000`

3. **API Permissions**
   - Add: `openid`, `profile`, `email`, `User.Read`

4. **Create Client Secret**
   - Certificates & secrets → New client secret
   - Copy the value immediately

5. **Get IDs**
   - Application (client) ID
   - Directory (tenant) ID

## 🔧 Configuration

### Frontend Environment Variables

```bash
# Azure AD Configuration
AZURE_AD_CLIENT_ID=your-client-id-guid
AZURE_AD_CLIENT_SECRET=your-client-secret
AZURE_AD_TENANT_ID=your-tenant-id-guid

# NextAuth Configuration
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=generate-with-openssl-rand-base64-32

# Backend API
LANGGRAPH_API_URL=http://localhost:8123
```

### Backend Environment Variables

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key
```

## 📊 Authentication Flow

```
1. User visits landing page
   ↓
2. Clicks "Sign in with Microsoft"
   ↓
3. Azure AD authentication
   ↓
4. Profile verification (calls profile API)
   ↓
5. Terms & conditions acceptance
   ↓
6. Main chat interface
```

## 🧪 Testing

### Test Frontend
```bash
cd frontend
pnpm dev
# Visit http://localhost:3000
```

### Test Profile API Connection
```bash
cd frontend
./TEST_PROFILE_API.sh
```

### Test Backend
```bash
cd backend/agent
langgraph dev
# Visit http://localhost:8123
```

## 🐛 Troubleshooting

### Common Issues

**Issue:** Profile API connection refused
```bash
# Verify API is running on correct port
lsof -i :8080
curl -k https://127.0.0.1:8080/services/security/profile
```

**Issue:** Azure AD authentication fails
- Check client ID and secret are correct GUIDs
- Verify redirect URI matches exactly
- Ensure tenant ID is correct

**Issue:** Frontend won't start
```bash
# Clear cache and reinstall
rm -rf node_modules .next
pnpm install
pnpm dev
```

**Issue:** Backend agent fails
```bash
# Check OpenAI API key is set
echo $OPENAI_API_KEY

# Verify Python dependencies
pip list | grep -E "langgraph|langchain|openai"
```

## 📚 Documentation

- **Frontend:** `/frontend/README.md`
- **Backend:** `/backend/agent/README.md`
- **MCP Servers:** `/mcp/README.md`
- **Authentication Flow:** See inline documentation

## 🛠️ Tech Stack

### Frontend
- **Next.js 15** - React framework
- **TypeScript** - Type safety
- **NextAuth.js** - Authentication
- **Tailwind CSS** - Styling
- **pnpm** - Package manager

### Backend
- **LangGraph** - Agent orchestration
- **LangChain** - LLM framework
- **OpenAI GPT-4** - Language model
- **FastAPI** - API framework (via LangGraph)

### Infrastructure
- **Azure AD** - Identity provider
- **MCP** - Model Context Protocol
- **HTTPS** - Secure communication

## 🔒 Security

- ✅ Azure AD SSO authentication
- ✅ JWT-based sessions
- ✅ HTTPS communication
- ✅ Environment variable secrets
- ✅ Profile-based access control
- ✅ Terms acceptance tracking

## 📝 License

[Your License Here]

## 👥 Contributing

[Your Contributing Guidelines]

## 📧 Support

For issues and questions:
- Check documentation in `/docs`
- Review troubleshooting guides
- Contact your system administrator

---

**Built with ❤️ using Next.js, LangGraph, and Azure AD**

