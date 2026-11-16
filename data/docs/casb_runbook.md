# Runbook: CASB Proxy & Threat Score Service Issues
## Issue: Threat score enrichment service unreachable / timeout
**Severity:** High (ERROR)
**Root Cause:** Usually caused by expired API tokens on the Threat Intelligence (TI) gateway or network firewall blocks on port 8443 between `casb-proxy` nodes and the TI microservice.
**Remediation Steps:**
1. Check connectivity from `casb-proxy-01` and `casb-proxy-02` to `ti-enrichment.internal:8443`.
2. Verify that the TI service API key has not expired in the secrets manager.
3. If the outage lasts longer than 10 minutes, switch CASB policy from `fallback-allow` to `strict-block` for unverified external uploads.

## Issue: Inactive Box OAuth grant not revoked
**Severity:** Medium (WARN)
**Policy:** OAuth tokens inactive for more than 5 days must be automatically revoked by the IAM cleanup job. If a warning appears, the SecOps engineer must manually revoke the token via the Admin Console.