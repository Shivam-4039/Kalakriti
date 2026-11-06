# Kalakriti

Kalakriti is an AI-driven market linkage and smart cataloging platform designed to empower traditional Indian artisans. The platform simplifies product onboarding by enabling voice-first cataloging in vernacular languages, automated image background cleanup, fair pricing guidance, Geographical Indication (GI) mapping, and integration with digital commerce networks such as the Open Network for Digital Commerce (ONDC).

---

## Architecture Overview

The system consists of two primary layers:

- **Backend**: A high-performance asynchronous REST API built with FastAPI, PostgreSQL, and SQLAlchemy. It handles business logic, speech and voice processing, image enhancement pipelines, catalog persistence, and commerce integrations.
- **Frontend**: A cross-platform mobile application developed with React Native and Expo. It provides an intuitive, voice-assisted user experience tailored for low-literacy contexts, complete with offline-first data caching and vernacular audio feedback.

---

## Key Features

- **Voice-Driven Cataloging**: Allows artisans to describe products in their native language, converting spoken input into structured product listings.
- **Automated Image Optimization**: Cleans and standardizes product photos by removing cluttered backgrounds to meet e-commerce catalog standards.
- **Fair Pricing Guidance**: Assists artisans in calculating competitive and sustainable selling prices based on materials, effort, and dimensions.
- **GI Craft Verification & Tagging**: Maps products to certified Geographical Indications to safeguard authentic craft heritage.
- **ONDC and B2B Connectivity**: Prepares catalog data for distribution across decentralized digital commerce networks and wholesale buyers.
- **Offline Resilience**: Supports local draft storage via SQLite on the mobile app, enabling uninterrupted workflows in areas with intermittent connectivity.
- **QR Code Traceability**: Generates distinct QR codes linking physical handicraft items to verified artisan profiles and product narratives.

---

## Repository Structure

```text
Kalakriti/
├── Backend/
│   ├── alembic/              # Database migration scripts
│   ├── app/
│   │   ├── models/           # SQLAlchemy database models
│   │   ├── routers/          # FastAPI API route controllers
│   │   ├── schemas/          # Pydantic data validation schemas
│   │   ├── services/         # Business logic and external service integrations
│   │   ├── utils/            # Shared utilities for audio, image, and logging
│   │   ├── config.py         # Application configuration and environment parsing
│   │   ├── database.py       # Async database session management
│   │   └── main.py           # FastAPI application entrypoint
│   ├── .env.example          # Sample environment configuration for backend
│   ├── alembic.ini           # Alembic configuration
│   ├── docker-compose.yml    # Docker services orchestration
│   ├── dockerfile            # Backend container specification
│   └── requirements.txt      # Python dependencies
│
└── Frontend/
    ├── app/                  # Expo Router file-based application screens
    │   ├── (auth)/           # Authentication screens (Login, OTP)
    │   ├── (tabs)/           # Core application tabs (Dashboard, Catalog, Profile)
    │   └── listing/          # Multi-step product listing workflow
    ├── assets/               # Static assets, fonts, and icons
    ├── components/           # Reusable UI components and voice widgets
    ├── constants/            # Application constants and locale mappings
    ├── hooks/                # Custom React hooks
    ├── services/             # HTTP client and API integration services
    ├── stores/               # Zustand state management stores
    ├── theme/                # UI styling and design tokens
    ├── utils/                # Helper functions
    ├── app.json              # Expo application manifest
    ├── package.json          # Node.js dependencies and scripts
    └── tsconfig.json         # TypeScript compiler configuration
```

---

## Prerequisites

Ensure the following runtimes and tools are installed on your machine before setting up the project:

- **Python**: Version 3.11 or later
- **Node.js**: Version 18 LTS or 20 LTS
- **Package Manager**: npm (bundled with Node.js)
- **Database**: PostgreSQL 16 (or access to a running PostgreSQL instance / Docker)
- **Media Utilities**: FFmpeg (required for backend audio processing and normalization)
- **Mobile Development**: Expo Go mobile application (on Android/iOS), or Android Studio / Xcode emulators

---

## Backend Setup

### 1. Navigate to the Backend Directory

```bash
cd Backend
```

### 2. Create and Activate a Virtual Environment

On Windows (PowerShell):

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

On macOS / Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the `Backend` directory by copying the example template:

```bash
cp .env.example .env
```

Open `.env` and configure the required settings:

- `DATABASE_URL`: PostgreSQL connection string with asyncpg (for example, `postgresql+asyncpg://postgres:postgres@localhost:5432/kalakriti`).
- `SUPABASE_URL`: Supabase project endpoint.
- `SUPABASE_SERVICE_ROLE_KEY`: Supabase service role secret key for storage and auth.
- `SARVAM_API_KEY`: API key for voice recognition and synthesis.
- `GROQ_API_KEYS`: API keys for speech fallback and text processing.

### 5. Run Database Migrations

Apply database migrations to set up the schema:

```bash
alembic upgrade head
```

### 6. Start the Backend Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Once running, the interactive API documentation will be accessible at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Alternative: Run Backend via Docker

If Docker and Docker Compose are installed:

```bash
docker compose up --build
```

---

## Frontend Setup

### 1. Navigate to the Frontend Directory

```bash
cd Frontend
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Configure Environment Variables

Create a `.env` file in the `Frontend` directory:

```bash
# For Android Studio Emulator:
EXPO_PUBLIC_API_URL=http://10.0.2.2:8000/api/v1

# For physical devices running Expo Go (replace with your machine's local IP address):
# EXPO_PUBLIC_API_URL=http://192.168.1.100:8000/api/v1

# For Web / iOS Simulator:
# EXPO_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### 4. Start the Development Server

```bash
npm start
```

You can then run the application on your target platform:

- Press `a` in the terminal to launch on an connected Android device or emulator.
- Press `i` to launch on the iOS simulator.
- Scan the displayed QR code using the Expo Go mobile application on your physical device.

---

## Verification

To confirm both layers are functioning properly:

1. Send a request to the backend health endpoint:
   ```bash
   curl http://localhost:8000/health
   ```
2. Verify that the mobile application loads the login screen and can establish communication with the configured API URL.

