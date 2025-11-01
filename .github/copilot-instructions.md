# Project: Nails Salon Booking (Django)

## Purpose
Provide a booking system for a nails salon: clients, technicians, services, schedules, appointments, payments, and reviews.

## Tech stack
- Python 3.10+
- Django 5+ (or latest LTS)
- Django REST Framework (API) (TODO: not implemented yet)
- PostgreSQL (recommended) (TODO: currently using SQLite)
- Celery + Redis (async tasks / notifications) (TODO: not implemented yet)
- pytest + pytest-django (tests)

## High-level architecture
- apps/
    - booking (Appointment model, availability logic, Service catalog, durations, prices, Clients(admin module users group), Technicians(admin module users group))
    - notifications (email/SMS tasks)
    - google_calendar_integration (Sync with Google Calendar)
- API: ViewSets + Routers, versioned (api/v1) (TODO: not implemented yet)
- Frontend: separate SPA or Django templates (TODO: not implemented yet, maybe not needed and will use django admin for now)

## Data model guidance (core)
- Users: admins, clients, technicians (use Django's built-in User model with groups/permissions)
- Service: title, duration (minutes), price, category
- Booking/Appointment:
    - client (FK), technician (FK), service (FK)
    - start (timezone-aware), end (computed), status (choices: pending, confirmed, canceled, completed)
    - created_at, updated_at
    - constraints to prevent overlapping bookings per technician
- Schedule/Availability: model or computed service to represent daily availability per technician

## Booking rules / invariants
- All datetimes timezone-aware. Store in UTC, localize in UI.
- Validate: start + service.duration -> end
- Prevent double-booking: use transaction + select_for_update or DB constraints where possible.
- Minimum and maximum booking window configurable.
- Cancellation policy.

## API patterns (TODO: not implemented yet)
- Use serializers with validate() to enforce business rules.
- Keep views thin. Put logic in services/use-cases.
- Endpoints:
    - GET /api/v1/services/
    - GET /api/v1/technicians/{id}/availability?date=YYYY-MM-DD
    - POST /api/v1/appointments/
    - PATCH /api/v1/appointments/{id}/cancel
    - POST /api/v1/payments/webhook

## Concurrency
- When creating appointments:
    - lock technician availability rows: select_for_update()
    - re-check overlapping appointments
    - create appointment and commit
- Consider optimistic locking with a version field if needed.

## Testing
- Unit tests for availability algorithm and serializer validation.
- Integration tests for appointment flow and payment webhooks.
- Use factories (factory_boy) for fixtures.

## Security & Privacy
- Authenticate APIs with JWT or token auth.
- Validate user inputs, limit rate for booking endpoints.

## Dev tools / style
- Use type hints, docstrings, and small functions.
- Format: Black + isort.
- Lint: flake8.
- Add pre-commit hooks.

## Example Copilot prompts (quick)
- "Create a Django model for Appointment with client, technician, service, start, end, status choices and a clean method that prevents overlapping bookings for a technician."
- "Write a DRF serializer for Appointment that computes end from start + service.duration and validates no overlap."
- "Implement a service function to calculate a technician's available slots for a given date considering working hours, breaks, existing appointments, and service duration."

Keep prompts focused and include required inputs (models, fields, validations, and expected behavior). Use tests to lock behavior.