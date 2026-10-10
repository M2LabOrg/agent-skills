## Threat model

### Assets

- <What is protected: data, credentials, availability, integrity of X>

### Actors and trust boundaries

- <Who interacts with the system: authenticated users, the public, internal services, third parties>
- <Where the trust boundaries are; mark them on the architecture diagram with a subgraph>

### Threats (STRIDE)

| Category | Threat | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| **S**poofing | <e.g. forged token> | Low / Med / High | Low / Med / High | <e.g. signature, audience and expiry checks> |
| **T**ampering | <data modified in transit or at rest> | | | |
| **R**epudiation | <action cannot be attributed> | | | |
| **I**nformation disclosure | <PII in logs, verbose errors> | | | |
| **D**enial of service | <unbounded input, expensive operation> | | | |
| **E**levation of privilege | <user reaches admin function> | | | |

### Residual risks

- <Risks accepted rather than mitigated, and why that is acceptable>

### Secrets and PII

- <Secrets needed; where stored; how rotated>
- <PII that flows through; where it is logged and persisted; retention>
