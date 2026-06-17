# Security Policy

## Supported Status

HandoverGap is currently alpha software. Treat APIs and schemas as subject to change until a stable release is declared.

## Data Handling

- Do not commit `.env` files, OpenAI keys, TiDB credentials, customer data, employee data, or real support/CRM exports.
- Use synthetic, anonymized, or consented data for examples and evaluation.
- JSONL ingest is a neutral file format, not a direct Slack/GitHub/CRM connector.
- Redact personal identifiers, direct contact details, payment data, and secrets before creating source events.
- Keep user-provided datasets and reviewed labels local unless they are anonymized and approved for publication.
- `handovergap datasets export-template` intentionally omits raw memory and evidence text from the annotation CSV.

## Runtime Boundaries

- OpenAI, TiDB, Streamlit, and live database operations are optional.
- The default CLI path must run without network access or credentials.
- HandoverGap evaluates memory readiness; it must not be used for employee scoring or surveillance.

## Default Data Flow

The core package runs locally by default:

- `handovergap demo`, `detect`, `evaluate`, `report`, `ingest`, `profiles validate`, and `privacy-check` do not call OpenAI, TiDB, Slack, GitHub, or other external services.
- Optional OpenAI slot filling runs only through explicit live validation/demo paths and requires `OPENAI_API_KEY`.
- Optional TiDB persistence runs only when the `tidb`/`live` dependencies and `HANDOVERGAP_TIDB_URL` or `TIDB_HOST` / `TIDB_USER` / `TIDB_PASSWORD` are configured.
- Optional Streamlit demo mode runs locally and only enters live OpenAI + TiDB mode when the required credentials are present.

## Privacy Checklist

Before evaluating user data:

- Confirm the source file is anonymized and stored outside the repository, for example under `local/`.
- Remove real company names, customer names, employee names, channel names, direct user IDs, URLs, email addresses, phone numbers, payment details, and secrets.
- Keep `.env`, reviewed labels, generated reports, and local datasets out of git.
- Run `handovergap privacy-check` before publishing docs, examples, or packaged data.
- Treat `--reset-schema` TiDB validation commands as alpha-only and use them only on databases without user data.

## Reporting a Vulnerability

Open a private security advisory on GitHub or contact the repository owner. Include reproduction steps, affected version, and whether any secret or sensitive data exposure is involved.
