# Training Slides - AI-PM Harness

## Slide 1 - Why AI for PM?

- PM work contains repetitive analysis and reporting tasks.
- AI can accelerate drafting, but project decisions remain human-owned.
- The pilot focuses on measurable value, not novelty.

## Slide 2 - Three supported use cases

1. Risk & Issue Analysis
2. Executive Status Reporting
3. Meeting -> Actions & Decisions

## Slide 3 - The harness

Raw data -> Anonymization -> Task context -> AI -> Validation -> Human review -> Approved output

## Slide 4 - What can go wrong?

- Hallucinated owner
- Invented date
- Unsupported risk
- Confidentiality leak
- Wrong confidence / overstatement

## Slide 5 - Evidence grounding

Every material claim should carry a source identifier.

No evidence -> `UNKNOWN` or `UNSUPPORTED_CLAIM`.

## Slide 6 - Human-in-the-loop

AI creates a draft.

PM reviews:

- factual correctness;
- business interpretation;
- risk severity;
- publication decision.

## Slide 7 - How we measure value

- accuracy / F1;
- unsupported claim rate;
- confidentiality leakage;
- median time saved;
- human correction effort.

## Slide 8 - Choosing the model

Compare models on the same cases and the same schema.

Choose per task when evidence supports task-specific routing.

## Slide 9 - Safe usage rules

- Minimize data.
- Never paste credentials.
- Do not let AI make final project decisions.
- Review high-impact outputs.

## Slide 10 - Takeaway

**AI augments PM execution under controlled governance.**
