# 3-5 Minute Demo Script

## 0:00-0:30 - Problem

Show a simple before workflow:

```text
RAID + meeting notes + status sheet
        -> manual reading
        -> manual reconciliation
        -> manual report
```

Say: "The goal is not to let AI make project decisions. The goal is to reduce PM preparation time while preserving evidence, confidentiality and human accountability."

## 0:30-1:00 - Architecture

Show `docs/architecture.md` diagram.

Point to:

- anonymization;
- task schema;
- validator;
- human review.

## 1:00-2:00 - Live risk demo

Run Risk & Issue Analysis.

Show two correct items with evidence IDs.

Then feed a hallucination trap: ask for an owner that is not in the evidence.

Expected behavior: `UNKNOWN` or validator warning/block.

## 2:00-2:40 - Meeting demo

Show the phrase "expected to finish next Friday".

The system should **not** convert this into a committed due date.

Show output with `due_date: UNKNOWN`.

## 2:40-3:30 - Safety demo

Open the synthetic sensitive file and show the sanitizer transforming:

- email;
- phone;
- account number;
- demo secret;
- known names.

Run tests.

## 3:30-4:20 - Benchmark

Show the final benchmark dashboard after you have real measurements.

Suggested order:

1. F1 / quality
2. unsupported claim rate
3. leakage rate
4. median time saved
5. correction count

## 4:20-4:50 - Recommendation

Say:

"The output is a controlled augmentation workflow. AI drafts the PM artifact, the harness checks it against project evidence, and the PM remains accountable for the final decision."

## Recording notes

Do not show API keys, private company data, personal data or production credentials. Use only the included synthetic project package or approved anonymized data.
