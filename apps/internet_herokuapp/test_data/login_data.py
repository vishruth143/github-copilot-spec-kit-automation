"""Non-secret sample test data for the internet_herokuapp Login flow.

Real credentials (username/password) come from environment variables via
`.env` — see
specs/001-ui-automation-framework/contracts/configuration-contract.md.
This module only holds non-secret, deliberately-invalid sample values used
to exercise the negative-path scenario.
"""

INVALID_USERNAME = "not-a-real-user"
INVALID_PASSWORD = "not-a-real-password"
