create-infra:
    @echo "Creating infra for integration tests"
    uv run python tests/integration/infra.py --operation create

destroy-infra:
    @echo "Destroying infra used for integration tests"
    uv run python tests/integration/infra.py --operation destroy

populate-table: create-infra
    @echo "Populating table for integration tests"
    uv run python tests/integration/populate_table.py

test-export: populate-table
    @echo "Running export integration test"
    uv run python tests/integration/export.py

test-download:
    @echo "Running download integration test"
    uv run python tests/integration/download.py
