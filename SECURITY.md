# Security Policy

## Supported Status

HandoverGap is currently alpha software. Treat APIs and schemas as subject to change until a stable release is declared.

## Data Handling

- Do not commit `.env` files, OpenAI keys, TiDB credentials, customer data, employee data, or real support/CRM exports.
- Use synthetic, anonymized, or consented data for examples and evaluation.
- JSONL ingest is a neutral file format, not a direct Slack/GitHub/CRM connector.
- Redact personal identifiers, direct contact details, payment data, and secrets before creating source events.

## Runtime Boundaries

- OpenAI, TiDB, Streamlit, and live database operations are optional.
- The default CLI path must run without network access or credentials.
- HandoverGap evaluates memory readiness; it must not be used for employee scoring or surveillance.

## Reporting a Vulnerability

Open a private security advisory on GitHub or contact the repository owner. Include reproduction steps, affected version, and whether any secret or sensitive data exposure is involved.
