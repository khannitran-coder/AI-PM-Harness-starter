# Usage Guide

## Purpose

Use this harness to create first-draft PM outputs from approved, anonymized project evidence.

## Supported tasks

### Risk & Issue Analysis

Input: RAID/project updates.

Output: structured risks/issues with evidence, response and owner.

### Executive Status Report

Input: status, milestones, risks, issues and decisions.

Output: draft RAG report and decisions required.

### Meeting -> Actions & Decisions

Input: meeting notes/transcript.

Output: actions, decisions and open questions.

## Data handling rules

| Data class | Use in AI workflow |
|---|---|
| Public | Allowed |
| Internal | Allowed only if approved for the selected tool |
| Confidential | Do not send unless policy explicitly allows it |
| PII / credentials | Must be removed before model submission |

## Review checklist

Before approving any AI output, the PM should verify:

- [ ] Every material fact has evidence.
- [ ] Owner names are sourced, not guessed.
- [ ] Dates are sourced or explicitly marked as unknown.
- [ ] Risk/issue classification is reasonable.
- [ ] The model did not invent project status.
- [ ] No confidential data is present.
- [ ] Important caveats are preserved.
- [ ] Final decisions remain human-owned.

## Golden rule

**AI drafts; PM decides.**

The model must not approve a risk, change project scope, commit a deadline, terminate a vendor or publish an external report.

## Safe failure behavior

When evidence is insufficient, the preferred answer is:

`UNKNOWN - insufficient evidence`

not a guessed value.

## Incident handling

If the validator flags a confidentiality or unsupported-claim issue:

1. do not publish the output;
2. identify the offending field;
3. remove or correct the source data;
4. rerun the task;
5. log the incident in the evaluation sheet.
