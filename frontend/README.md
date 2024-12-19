# LearnLab Frontend Service

## Overview
Next.js-based frontend application providing the user interface for the LearnLab platform.

## Technical Stack
- **Framework**: Next.js 15.0.3
- **Language**: TypeScript
- **Styling**: TailwindCSS
- **Node Version**: 18.x
- **Docker Image**: node:18-alpine

## Project Structure
```
frontend/
├── app/                    # Next.js 13+ app directory
│   ├── fonts/             # Custom fonts (Geist)
│   ├── layout.tsx         # Root layout component
│   └── page.tsx           # Home page component
├── public/                # Static assets
├── .env                   # Environment variables
├── .env.example           # Example environment file
├── Dockerfile            # Docker configuration
├── next.config.ts        # Next.js configuration
├── package.json          # Project dependencies
├── postcss.config.mjs    # PostCSS configuration
└── tailwind.config.ts    # Tailwind configuration
```

## Dependencies
```json
{
  "dependencies": {
    "react": "19.0.0-rc-66855b96-20241106",
    "react-dom": "19.0.0-rc-66855b96-20241106",
    "next": "15.0.3"
  },
  "devDependencies": {
    "typescript": "^5",
    "tailwindcss": "^3.4.1",
    "eslint": "^8"
  }
}
```

## Docker Configuration
- Development stage with hot-reload
- Production stage with optimized build
- Node modules volume mounting
- Runs on port 3000

## Environment Variables
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_STREAMLIT_URL=http://localhost:8501
```

## Features
Current implementations:
- Next.js App Router setup
- TypeScript integration
- TailwindCSS configuration
- Custom font setup (Geist)
- Docker development environment
- Hot reload support

## Development
1. Local Setup:
```bash
npm install
```

2. Run Development Server:
```bash
npm run dev
```

3. Build for Production:
```bash
npm run build
```

## Docker Commands
```bash
# Build the service
docker-compose build frontend

# Run the service
docker-compose up frontend

# View logs
docker-compose logs -f frontend
```

## Font System
- Uses Geist Sans as primary font
- Uses Geist Mono for code and monospace text
- Fonts are locally hosted and optimized

## Development Progress
Current implementation includes:
- Basic Next.js setup
- Docker configuration
- TailwindCSS integration
- Custom font setup
- Development environment

Next planned implementations:
- API integration with backend
- Authentication system
- Core UI components
- Data visualization components