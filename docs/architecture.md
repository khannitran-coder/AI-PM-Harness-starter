# Architecture

## 1. Design goals

The harness is designed around five principles:

1. **Data minimization** - send only the fields needed for the selected PM task.
2. **Evidence grounding** - every material factual claim should point to a source identifier.
3. **Structured output** - models must return a predefined JSON shape.
4. **Policy checks before publication** - invalid or unsafe output is blocked from the final PM artifact.
5. **Human accountability** - AI drafts; a PM approves, edits or rejects.

## 2. Components

### Data sanitizer

Transforms raw synthetic project data into an anonymized package. It redacts email, phone, account-like identifiers and demo secrets, and can replace known names with stable aliases.

### Task context builder

Combines:

- task instructions;
- project evidence;
- output schema;
- business rules;
- explicit refusal rules for missing information.

### Model adapter

The benchmark does not assume one vendor. The same case can be sent to any approved AI model. The repo accepts model outputs as JSON so that API integration is optional.

### Validator

Performs syntax, schema, allowed-value, required-field and evidence-reference validation. It can mark output as `PASS`, `WARN` or `BLOCK`.

### Safety checks

The evaluator tests for:

- unsupported factual claims;
- leaked sensitive tokens;
- invented owners / dates;
- contradictions with source data.

### Human review

The reviewer sees the AI draft plus validation flags. Only the reviewed version is treated as the final PM artifact.

## 3. Data flow

```text
raw project files
      |
      v
sanitize()
      |
      v
anonymized project files
      |
      +-----------------------------+
      |                             |
      v                             v
Task 1 Risk                  Task 2 Status
      |                             |
      +-------------+---------------+
                    |
                    v
                 AI model
                    |
                    v
              JSON output
                    |
                    v
               validator
                    |
              PASS/WARN/BLOCK
                    |
                    v
              human review
                    |
                    v
             approved PM output
```

## 4. Threat model

| Threat | Example | Control |
|---|---|---|
| PII leakage | name, phone, email | sanitization |
| Credential leakage | API key pasted into a note | secret redaction |
| Hallucination | invented risk owner | evidence + allowed-values check |
| Over-confidence | uncertain forecast stated as fact | confidence + review |
| Schema drift | model returns free text | JSON schema validation |
| Silent failure | missing field ignored | blocking validator |
| Automation overreach | AI publishes report | human approval gate |

## 5. Non-goals

This pilot is not a replacement for Jira, an enterprise GRC platform, a production identity system or a regulated decision engine. It is a controlled proof-of-concept for AI augmentation of PM work.
