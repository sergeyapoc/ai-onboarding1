# Policy & Runbook: Privileged Access Management (PAM)
## Privileged Session Duration Rules
Standard privileged checkout sessions (e.g., access to `SRV-APP-02` or `DB-PROD-01`) are strictly limited to **120 minutes**. Any session exceeding this threshold triggers a `WARN` event and requires manager approval to extend.

## Failed MFA Verification
Multiple `ERROR` events regarding failed MFA verification on `pam-vault` nodes indicate potential credential stuffing or compromised service accounts.
**Action Required:** Immediately lock the target `user_id` session, rotate credentials in `VAULT-PROD-01`, and open a P1 security incident.