# Incident Post-Mortem: May 1, 2025 CASB Outage
**Summary:** Between 00:45 and 04:15 UTC on May 1, 2025, `casb-proxy-02` and `casb-proxy-01` experienced intermittent failures reaching the Threat Score enrichment service.
**Impact:** 15 CASB proxy decisions were processed without Threat Intelligence (TI) context using fallback rules.
**Root Cause:** A misconfigured TLS certificate rotation on the internal TI microservice caused handshake timeouts after 5000ms.
**Preventive Actions:** Added automated certificate expiration alerts 14 days prior to expiry and implemented circuit-breaker caching on CASB proxies.