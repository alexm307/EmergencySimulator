psql -h localhost -p 5432 -U postgres -d entity-management-api

PYTHONPATH=. alembic revision --autogenerate -m "locations"
PYTHONPATH=. alembic upgrade head