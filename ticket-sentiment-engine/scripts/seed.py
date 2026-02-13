#!/usr/bin/env python3
"""Seed script — sends sample tickets to the ingest endpoint for testing."""

import httpx
import sys

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"

SAMPLE_TICKETS = [
    {
        "title": "Order not received — very frustrated",
        "content": (
            "I placed an order two weeks ago and it still hasn't arrived. "
            "I've been waiting forever and this is unacceptable. I'm a busy "
            "mom with two kids (ages 5 and 8) and I needed this for my "
            "daughter's birthday party. I live in Texas and shipping should "
            "NOT take this long. I want a full refund or the item shipped "
            "overnight immediately."
        ),
        "customer_email": "angry.parent@example.com",
        "status": "open",
    },
    {
        "title": "Loving the new product!",
        "content": (
            "Just wanted to say I absolutely love the new light therapy lamp! "
            "I'm a grad student and I've been dealing with seasonal depression. "
            "This has made such a huge difference in my daily routine. "
            "My roommate wants one too. Keep up the great work!"
        ),
        "customer_email": "happy.student@example.com",
        "status": "open",
    },
    {
        "title": "Billing issue — double charged",
        "content": (
            "I was charged twice for order #4521. I'm a software developer "
            "and I checked my bank statement carefully — there are definitely "
            "two charges for $49.99. I'm in my 30s and I've never had this "
            "issue with any other company. Please resolve ASAP. "
            "I'm in Portland, Oregon."
        ),
        "customer_email": "dev.billing@example.com",
        "status": "open",
    },
    {
        "title": "Question about product for TBI recovery",
        "content": (
            "Hi there, I suffered a traumatic brain injury last year and my "
            "neurologist recommended light therapy as part of my recovery. "
            "I'm a 45-year-old writer based in Colorado. Can you tell me "
            "which product would be best suited for TBI recovery? I'd also "
            "love to know if you offer any medical discounts. Thank you!"
        ),
        "customer_email": "tbi.recovery@example.com",
        "status": "open",
    },
    {
        "title": "VIP customer — urgent replacement needed",
        "content": (
            "This is my third purchase from you and I'm one of your biggest "
            "fans, but the lamp I received is defective — it flickers every "
            "few minutes. I have chronic migraines and the flickering is "
            "making things worse. I'm a nurse who works night shifts so I "
            "really depend on this. Please send a replacement urgently. "
            "I'm in Florida."
        ),
        "customer_email": "vip.nurse@example.com",
        "status": "open",
    },
]


def main():
    print(f"Seeding {len(SAMPLE_TICKETS)} tickets to {BASE_URL}/api/v1/ingest ...")

    response = httpx.post(
        f"{BASE_URL}/api/v1/ingest",
        json={"tickets": SAMPLE_TICKETS},
        timeout=30.0,
    )
    response.raise_for_status()

    data = response.json()
    print(f"Response: {data}")
    print("Done! Tickets are being processed in the background.")


if __name__ == "__main__":
    main()
