```markdown
# 🚨 Emergency Dispatch Simulation System

This project simulates an emergency response system that:

- Identifies emergency needs.
- Calculates the optimal resource dispatch strategy.
- Dynamically allocates services like police, fire, rescue, and utilities.
- Works with data retrieved via API and optionally integrates with a database.

It is fully containerized with Docker and prepared for deployment in environments like AWS Lambda, ECS, or traditional server infrastructure.

---

## 📁 Project Structure

```bash
.
├── main.py         # Entrypoint for the simulation logic
├── api_service.py           # Handles HTTP interactions with the dispatch/emulator API
├── utils.py        # Contains distance logic and emergency solver classes
├── models.py                # Pydantic models for locations and services
├── config.py                # Loads environment variables using Pydantic
├── requirements.txt         # Python dependencies
├── docker-compose.yaml      # Docker compose for local testing
├── alembic.ini              # Database migration tool settings
├── database/                # Folder which contains database migration script and database versions
├── .env.template            # Template Environment configuration
├── Dockerfile               # Docker build instructions
├── .dockerignore            # Files ignored by Docker
├── .env                     # Environment configuration
```

---

## ⚙️ Environment Variables (`.env`)

| Variable                     | Description                                                                |
|-----------------------------|-----------------------------------------------------------------------------|
| `ALGORITHM_API_HOST`        | The base URL of the simulation/emulator API                                 |
| `ALGORITHM_SEED`            | Seed for the simulation — keeps runs consistent if needed                   |
| `ALGORITHM_TARGET_DISPATCHES` | Total number of dispatches to aim for during the simulation               |
| `ALGORITHM_MAX_ACTIVE_CALLS`  | Maximum number of calls the simulation can handle at once                 |
| `ALGORITHM_RETRY_COUNT`     | How many times to retry a failed request to the simulation API              |
| `ALGORITHM_TIMEOUT`         | Timeout (in seconds) for each API call                                      |
| `ALGORITHM_PRIORITY_COUNTY` | Priority county for which the algorithm is optimized for solving            |
| `DB_HOST`                   | Hostname of the PostgreSQL database                                         |
| `DB_PORT`                   | Port the database is exposed on (default: 5432)                             |
| `DB_USERNAME`               | Database username                                                           |
| `DB_PASSWORD`               | Database password                                                           |
| `DB_DATABASE`               | Name of the database                                                        |

---

## 🚀 Running Locally

### 1. Install dependencies (if not using Docker)

```bash
cd algorithm # make sure you run these from inside the algorithm directory
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

Make sure you have a `.env` file in your root directory with the variables listed above.

---

## 🐳 Running in Docker

### 1. Build the Docker image

```bash
docker build -t emergency-algorithm .
```

### 2. Run the container

```bash
docker run --env-file .env emergency-algorithm
```

---

## 🧪 Sample `.env`

```env
ALGORITHM_API_HOST=http://localhost:5000
ALGORITHM_SEED=default
ALGORITHM_TARGET_DISPATCHES=1000
ALGORITHM_MAX_ACTIVE_CALLS=100
ALGORITHM_RETRY_COUNT=3
ALGORITHM_TIMEOUT=5.0

DB_HOST=localhost
DB_PORT=5432
DB_USERNAME=postgres
DB_PASSWORD=postgres
DB_DATABASE=entity-management-api
```

---

## 🧱 Preparing for Deployment (Lambda, ECS, etc.)

### Option 1: As a Lambda Function
- Use AWS Lambda Containers (just deploy the Docker image).
- Ensure the entrypoint function is defined and returns results per Lambda format.

### Option 2: As a Server Process
- Run the container in ECS/Fargate or EC2 with `.env` passed as environment variables or secret manager.

---

## ✅ Future Improvements

- Add health checks and monitoring endpoints.
- Unit testing with 100% coverage
- Connect simulation results to dashboards (e.g. Grafana or frontend).

---

## 📄 License

MIT License. Feel free to use, extend, and contribute back!