# Evaluation Methodology

## 1. Research question

Can a controlled AI workflow reduce PM administrative effort while maintaining acceptable quality and confidentiality?

## 2. Hypotheses

- H1: AI-assisted PM tasks reduce median preparation time.
- H2: Structured output + evidence validation reduces unsupported claims compared with an unconstrained baseline.
- H3: Model choice materially changes quality across different PM tasks.
- H4: Human review remains necessary for final project decisions and external reporting.

## 3. Test corpus

The repository contains the **final 90-case curated gold-standard set** for the pilot benchmark:

- 30 normal cases;
- 20 ambiguous cases;
- 15 missing-information cases;
- 10 conflicting-information cases;
- 10 hallucination traps;
- 5 confidentiality traps.

There are 30 cases per PM use case: risk analysis, status reporting and meeting-to-actions/decisions. Each case includes its own synthetic input evidence, gold expectation and grading rules. The set defines what should be measured; it is not a performance result.

## 4. Experimental controls

For every model and every case:

1. Same anonymized input.
2. Same task instructions.
3. Same output schema.
4. Same evaluation set.
5. Same temperature/decoding policy when the vendor allows it.
6. No human editing before automated scoring.
7. Human correction measured separately after automated scoring.

## 5. Gold standard

A gold-standard case contains the expected risk/action/decision IDs, allowed owners, expected RAG values and source evidence. Gold labels should be reviewed by a second person before final reporting where practical.

## 6. Metrics

### Precision

```text
true positives / (true positives + false positives)
```

### Recall

```text
true positives / (true positives + false negatives)
```

### F1

```text
2 * precision * recall / (precision + recall)
```

### Unsupported factual claim rate

```text
unsupported factual claims / total factual claims * 100
```

### Confidentiality leakage rate

```text
sensitive tokens detected after sanitization / sensitive tokens presented to the sanitizer * 100
```

### Time saved

```text
(human baseline minutes - AI-assisted minutes) / human baseline minutes * 100
```

Use median, not only mean, because PM task duration can contain outliers.

## 7. Baseline protocol

For each use case, record a human-only baseline on 5-10 representative cases. Then repeat with AI assistance. Record:

- task start/end time;
- number of manual corrections;
- number of factual corrections;
- final approval outcome.

## 8. Model comparison

Score models separately for each task. A single overall winner is optional. The more useful outcome may be task-based routing:

```text
Risk analysis       -> Model A
Status reporting    -> Model B
Meeting extraction  -> Model C
```

The routing decision should use an explicit weighted decision matrix, not intuition alone.

## 9. Decision thresholds

Suggested starting thresholds (adjust before final experiment):

- **BLOCK** if confidentiality leakage is detected;
- **BLOCK** if required evidence is missing for a high-impact claim;
- **WARN** if confidence is low or input evidence is ambiguous;
- **PASS** when all required fields and safety checks pass.

These are governance defaults, not claims of regulatory compliance.
