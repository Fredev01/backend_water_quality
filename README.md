# 🌊 Water Quality - Backend

## ⚙️ Getting Started

### Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Environment variables

This variables setup services like Firebase, weather, notifications, etc.

```env
# Firebase Realtime Database
FIREBASE_ADMIN_CREDENTIALS=''
FIREBASE_API_KEY=''
FIREBASE_REALTIME_URL=''

SECRET_KEY=''

# Weather API
WEATHER_API_KEY=''

# OneSignal API
ONESIGNAL_APP_ID=''
ONESIGNAL_API_KEY=''

# Firebase Admin SDK
FIREBASE_TYPE='...'
FIREBASE_PROJECT_ID='...'
FIREBASE_PRIVATE_KEY_ID='...'
FIREBASE_PRIVATE_KEY='...'
FIREBASE_CLIENT_EMAIL='...'
FIREBASE_CLIENT_ID='...'
FIREBASE_AUTH_URI='...'
FIREBASE_TOKEN_URI='...'
FIREBASE_AUTH_PROVIDER_X509_CERT_URL='...'
FIREBASE_CLIENT_X509_CERT_URL='...'
FIREBASE_UNIVERSE_DOMAIN='...'
```

> 🛡️ _Never push your `.env` file. Use `.env.example` as a secure template._

### Create a secret key

```bash
python -c 'import secrets; print(secrets.token_hex(32))'
```

### Run the app dev

```bash
fastapi dev app
```

### Run the app prod

```bash
python main.py
```

## 🧩 Project structure

```plaintext
app/
├── features/                  # Each functionality follows the Vertical Slice pattern
│   ├── ai/                    # AI-related features
│   ├── alerts/                # Alerts about water quality
│   ├── auth/                  # Authentication logic
│   ├── meters/                # Manage meters and their data
│   ├── users/                 # Manage users and their data
│   └── workspaces/           # Manage workspaces and their data
│       ├── domain/            # Entities and rules of business
│       ├── infrastructure/    # Implementation of repositories, integrations, etc.
│       ├── presentation/      # Routes, and dependencies
│       │   ├── depends.py
│       │   └── routes.py
│       └── services/          # Integration external services
│
├── share/                    # Configuration files and utilities shared across the project
│   ├── config.py
│   └── __init__.py
│
├── test/                     # Unit tests
├── utils/                    # Utilities
├── main.py                   # FastAPI entrypoint
└── requirements.txt          # Python dependencies
```

### 📦 Internal structure of each module (`features/`)

Cada módulo como `auth`, `meters`, `users`, `workspaces`, etc., tiene la siguiente organización:

Each module (`auth`, `meters`, `users`, `workspaces`, etc.) has the following organization:

| Folder/File       | Description                                              |
| ----------------- | -------------------------------------------------------- |
| `domain/`         | Contains models, repositories, and rules of business.    |
| `infrastructure/` | Implementation of repositories, integrations, etc.       |
| `presentation/`   | Endpoints (`routes.py`) and dependencies (`depends.py`). |
| `services/`       | External services integrations.                          |

---

## 🌱 Branch Flow

This flow allows working on small and controlled branches that are integrated into `main` through Pull Requests.

### Branch types and allowed commit types

| Base branch       | Example                        | Allowed commit types                | Main usage                                                            |
| ----------------- | ------------------------------ | ----------------------------------- | --------------------------------------------------------------------- |
| `main`            | `main`                         | `build`, `release`, `chore`, `docs` | Stable branch. Only merged from other branches.                       |
| `feature/<name>`  | `feature/workspace-crud`       | `feat`, `test`, `docs`, `style`     | New functionality. E.g., CRUD, endpoints, validations.                |
| `refactor/<name>` | `refactor/meter-service-clean` | `refactor`, `style`, `test`         | Internal improvements without changing behavior.                      |
| `hotfix/<name>`   | `hotfix/firebase-urgent`       | `fix`, `style`, `chore`             | Urgent fix in production.                                             |
| `bugfix/<name>`   | `bugfix/token-missing-guard`   | `fix`, `test`                       | Non-urgent fix (detected before going to production).                 |
| `docs/<name>`     | `docs/api-reference-update`    | `docs`                              | Documentation-only changes, e.g., README, docstrings, usage examples. |

---

## ✍️ Commit types (Conventional Commits)

We use the [Conventional Commits](https://www.conventionalcommits.org/) format to improve readability of history.

| Type       | Main usage                                            | Example                                            |
| ---------- | ----------------------------------------------------- | -------------------------------------------------- |
| `feat`     | New functionality or endpoint                         | `feat: add meter registration endpoint`            |
| `fix`      | Bug fix                                               | `fix: correct firebase auth payload error`         |
| `refactor` | Internal code improvement (without changing behavior) | `refactor: optimize alert notification generation` |
| `docs`     | Documentation updates                                 | `docs: update README with OneFlow structure`       |
| `test`     | Add or modify tests                                   | `test: add unit tests for user service`            |
| `style`    | Code formatting or styling (no logic changes)         | `style: apply black formatting`                    |
| `chore`    | Maintenance tasks that do not affect code logic       | `chore: update requirements.txt`                   |
| `build`    | Build tools or dependencies updates                   | `build: add Dockerfile for API deployment`         |
| `release`  | Release version preparation                           | `release: v1.0.0`                                  |
