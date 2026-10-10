# Mermaid diagram types: examples

## Contents

- [Flowchart](#flowchart)
- [Sequence](#sequence)
- [State](#state)
- [Entity-relationship](#entity-relationship)
- [Class](#class)
- [Gantt](#gantt)
- [Trust boundaries with subgraph](#trust-boundaries-with-subgraph)

## Flowchart

Components and data flow. `LR` reads left to right; `TB` top to bottom.

```mermaid
flowchart LR
    User((User)) -->|HTTPS| CDN[CDN]
    CDN -->|/api/*| API[API service]
    API -->|SQL| DB[(Database)]
    API -->|enqueue| Q[(Job queue)]
    Q --> Worker[Worker]
    Worker -->|writes| Store[(Object storage)]
```

## Sequence

Use when order matters. `autonumber` helps in long sequences.

```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant A as API
    participant Q as Queue
    participant W as Worker
    U->>A: POST /jobs
    A->>Q: enqueue(jobId)
    A-->>U: 202 Accepted {jobId}
    Q->>W: deliver(jobId)
    W->>A: PATCH /jobs/{id} status=done
```

## State

Lifecycles and retries.

```mermaid
stateDiagram-v2
    [*] --> Queued
    Queued --> Running
    Running --> Succeeded
    Running --> Failed
    Failed --> Queued: retry < 3
    Failed --> DeadLetter: retry >= 3
    Succeeded --> [*]
    DeadLetter --> [*]
```

## Entity-relationship

```mermaid
erDiagram
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ ORDER_LINE : contains
    PRODUCT ||--o{ ORDER_LINE : "appears in"
    CUSTOMER {
        uuid id PK
        string email
    }
    ORDER {
        uuid id PK
        uuid customer_id FK
        string status
    }
```

## Class

```mermaid
classDiagram
    class Handler {
        <<interface>>
        +handle(event) Result
    }
    class EmailHandler
    class WebhookHandler
    Handler <|.. EmailHandler
    Handler <|.. WebhookHandler
```

## Gantt

Use sparingly; plans change faster than diagrams.

```mermaid
gantt
    title Release plan
    dateFormat YYYY-MM-DD
    section Build
    Implement feature   :a1, 2026-01-05, 5d
    Evaluate and iterate:a2, after a1, 4d
    section Ship
    Staged rollout      :after a2, 3d
```

## Trust boundaries with subgraph

```mermaid
flowchart LR
    User((User)) -->|HTTPS| API
    subgraph Cloud[Cloud account]
        API[API service] --> DB[(Database)]
    end
```
