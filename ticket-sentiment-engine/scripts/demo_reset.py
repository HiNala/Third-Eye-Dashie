#!/usr/bin/env python3
"""Demo reset script — clears the database and re-seeds all sample tickets for
an end-to-end demo.  Combines DB truncation with both seed_real_tickets (14)
and seed_100_tickets (100) for a total of 114 tickets.
"""

import subprocess
import sys

import httpx

# ---------------------------------------------------------------------------
# Import ticket data from the sibling seed scripts
# ---------------------------------------------------------------------------
from seed_real_tickets import SAMPLE_TICKETS as REAL_TICKETS
from seed_100_tickets import SAMPLE_TICKETS as BULK_TICKETS

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
BATCH_SIZE = 25


def clear_database() -> None:
    """Truncate all ticket-related tables via docker compose exec."""
    print("Clearing database (raw_tickets, processed_tickets, ticket_embeddings)...")
    subprocess.run(
        [
            "docker", "compose", "exec", "-T", "db",
            "psql", "-U", "postgres", "-d", "tickets_db",
            "-c", "TRUNCATE ticket_embeddings, processed_tickets, raw_tickets CASCADE;",
        ],
        check=True,
    )
    print("Database cleared.\n")


def seed_tickets(tickets: list[dict], label: str) -> list[str]:
    """Ingest a list of tickets via the API, returning all created IDs."""
    print(f"Seeding {len(tickets)} {label} tickets to {BASE_URL}/api/v1/ingest ...")
    all_ids: list[str] = []

    for i in range(0, len(tickets), BATCH_SIZE):
        batch = tickets[i : i + BATCH_SIZE]
        print(f"  Batch {i // BATCH_SIZE + 1} ({len(batch)} tickets)...")

        response = httpx.post(
            f"{BASE_URL}/api/v1/ingest",
            json={"tickets": batch},
            timeout=30.0,
        )
        response.raise_for_status()

        data = response.json()
        all_ids.extend(data["ticket_ids"])
        print(f"  Accepted: {len(data['ticket_ids'])} ticket(s)")

    return all_ids


def main() -> None:
    # Step 1 — wipe existing data
    clear_database()

    # Step 2 — seed real tickets (14) + bulk tickets (100)
    real_ids = seed_tickets(REAL_TICKETS, "real")
    print()
    bulk_ids = seed_tickets(BULK_TICKETS, "generated")

    total = len(real_ids) + len(bulk_ids)
    print(f"\nDone!  {total} tickets ingested and queued for LLM processing.")
    print("Monitor progress:  docker compose logs app --follow")
    print(f"When complete:     curl {BASE_URL}/api/v1/tickets | python3 -m json.tool")


if __name__ == "__main__":
    main()
