import os
import sqlite3

# 1. Создаем папку data для хранения базы и документов
os.makedirs("data/docs", exist_ok=True)
db_path = "data/security_logs.db"

# 2. Создаем и наполняем SQLite базу данных (Structured Data)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS system_logs")
cursor.execute("""
CREATE TABLE system_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    system_name TEXT NOT NULL,
    component TEXT NOT NULL,
    log_level TEXT NOT NULL,
    corr_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    message TEXT NOT NULL
)
""")

# Реалистичный датасет логов (включая примеры из task2 + дополнительные записи для аналитики)
logs_data = [
    ("2025-05-01T00:04:59+00:00", "casb-proxy-01", "CASB", "WARN", "7de471bf-f865-4d61-8515-5381e4dc6680", "SUPERUSER", "Inactive Box OAuth grant for eroberts not revoked — 5 days since last use"),
    ("2025-05-01T00:11:57+00:00", "vuln-scan-01", "Vulnerability_Scanner", "INFO", "ad6853c6-4cd3-46a4-9fc0-8086228ba68a", "ADMIN", "Asset WKSTN-117 (172.16.254.3) added to scan scope — first scan scheduled"),
    ("2025-05-01T00:34:30+00:00", "pam-vault-01", "PAM", "INFO", "caf3c094-b61e-48af-8ad7-6a0d52194d62", "STANDARDUSER", "User glopez checked out credentials for SRV-APP-02 from VAULT-PROD-01 — session initiated"),
    ("2025-05-01T00:49:26+00:00", "casb-proxy-02", "CASB", "ERROR", "31286dc8-40b1-4b20-99eb-b4955d7ecb5f", "ADMIN", "Threat score enrichment service unreachable — 15 CASB decisions made without TI context"),
    ("2025-05-01T01:15:10+00:00", "casb-proxy-02", "CASB", "ERROR", "9a182bc1-11c4-4e11-88aa-12904d7ecb11", "SYSTEM", "Threat score enrichment service unreachable — fallback allow policy triggered"),
    ("2025-05-01T02:05:44+00:00", "pam-vault-01", "PAM", "WARN", "44120ac9-99b1-4a20-91eb-c4955d71112a", "STANDARDUSER", "Session duration exceeded 120 minutes for SRV-APP-02 by user glopez"),
    ("2025-05-01T03:22:19+00:00", "pam-vault-02", "PAM", "ERROR", "88219dc8-30b1-4b20-77eb-a4955d7ecb99", "SUPERUSER", "Failed MFA verification during privileged checkout for DB-PROD-01"),
    ("2025-05-01T04:10:05+00:00", "casb-proxy-01", "CASB", "ERROR", "55123dc8-40b1-4b20-99eb-b4955d7ecb00", "ADMIN", "Threat score enrichment service timeout after 5000ms"),
    ("2025-05-01T05:00:00+00:00", "vuln-scan-01", "Vulnerability_Scanner", "WARN", "112233c6-4cd3-46a4-9fc0-8086228ba68a", "ADMIN", "High severity CVE-2025-1042 detected on asset SRV-APP-02"),
    ("2025-05-01T06:18:33+00:00", "casb-proxy-02", "CASB", "INFO", "778899bf-f865-4d61-8515-5381e4dc6680", "SYSTEM", "Threat intelligence feed synchronized successfully")
]

cursor.executemany("""
INSERT INTO system_logs (timestamp, system_name, component, log_level, corr_id, user_id, message)
VALUES (?, ?, ?, ?, ?, ?, ?)
""", logs_data)

conn.commit()
conn.close()

# 3. Создаем неструктурированные документы для RAG (Runbooks & Policies)
docs = {
    "data/docs/casb_runbook.md": """# Runbook: CASB Proxy & Threat Score Service Issues
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
""",
    "data/docs/pam_vault_policy.md": """# Policy & Runbook: Privileged Access Management (PAM)
## Privileged Session Duration Rules
Standard privileged checkout sessions (e.g., access to `SRV-APP-02` or `DB-PROD-01`) are strictly limited to **120 minutes**. Any session exceeding this threshold triggers a `WARN` event and requires manager approval to extend.

## Failed MFA Verification
Multiple `ERROR` events regarding failed MFA verification on `pam-vault` nodes indicate potential credential stuffing or compromised service accounts.
**Action Required:** Immediately lock the target `user_id` session, rotate credentials in `VAULT-PROD-01`, and open a P1 security incident.
""",
    "data/docs/postmortem_may2025.md": """# Incident Post-Mortem: May 1, 2025 CASB Outage
**Summary:** Between 00:45 and 04:15 UTC on May 1, 2025, `casb-proxy-02` and `casb-proxy-01` experienced intermittent failures reaching the Threat Score enrichment service.
**Impact:** 15 CASB proxy decisions were processed without Threat Intelligence (TI) context using fallback rules.
**Root Cause:** A misconfigured TLS certificate rotation on the internal TI microservice caused handshake timeouts after 5000ms.
**Preventive Actions:** Added automated certificate expiration alerts 14 days prior to expiry and implemented circuit-breaker caching on CASB proxies.
"""
}

for filepath, content in docs.items():
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content.strip())

print("Успешно! База данных data/security_logs.db и 3 документа в data/docs/ созданы.")
