# Entity Merge Service

## Entities
- Company: id, name, address (line_1, line_2, state, city, postal_code)
- User: id, first_name, last_name, company_id
- Branch: id, name, company_id

## Problem
Sometimes two Company records are duplicates. We need an HTTP API to merge them into one company, resolve data conflicts, and re-link all Users and Branches to the merged company.

## Simple Solution (Python + SQLite)
- Frontend sends:
	- source_company_1_id
	- source_company_2_id
	- resolved_company (user-chosen final values)
- Backend creates a new merged company with a new id.
- Backend updates all Users and Branches from both source company ids to the new company id.
- Backend deduplicates Branch records when needed.
- Backend soft-deletes source companies (recommended for audit/history).
- SQLite is file-based, so it is easy to run and review in an interview repo.

## API
- POST /v1/company-merges

## Quick Demo Script
Run this to seed two duplicate companies, send a merge request, and verify the result:

```powershell
python scripts/demo_merge.py
```

Expected output includes:
- HTTP 200
- merged_company_id in response
- users/branches reassigned to merged company
- source companies soft-deleted

## Maintainability
- Keep API models separate from database models.
- Keep merge rules in the service layer and SQLite logic in the repository layer.
- Add new fields (like credit_limit) in one place and reuse the same merge flow.