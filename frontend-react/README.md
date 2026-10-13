# InvoiceShield Frontend (React + TypeScript)

Modern web interface built with React, TypeScript, Vite, and Tailwind CSS.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Run Development Server
```bash
npm run dev
```

**Frontend:** http://localhost:5173

### 3. Build for Production
```bash
npm run build
```

## 📋 Prerequisites

- Node.js 18+ installed
- Backend running at http://localhost:8000

## 🎨 Features

- Modern React with TypeScript
- Tailwind CSS for styling
- Vite for fast development
- Real-time document verification
- Visual risk assessment
- Responsive design

## 🔧 Tech Stack

- **Framework:** React 18
- **Language:** TypeScript
- **Build Tool:** Vite
- **Styling:** Tailwind CSS
- **HTTP Client:** Axios/Fetch API

## 📁 Structure

```
frontend-react/
├── src/
│   ├── components/    # React components
│   ├── pages/         # Page components
│   ├── lib/           # Utilities
│   └── types.ts       # TypeScript types
├── package.json
└── vite.config.ts
```

## 🌐 API Configuration

Backend API URL is configured in the source files. Update if backend is on a different port:

```typescript
const API_BASE_URL = 'http://localhost:8000';
```

## 🎯 Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint (if configured)
