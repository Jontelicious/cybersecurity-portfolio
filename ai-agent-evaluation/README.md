# Cross-Agent Code Review: Testing Reusable AI Agent Skills

**Project type:** AI-assisted software engineering · Security tooling · Software testing  
**Date:** October 2026  
**Status:** Completed controlled evaluation

## Overview

I evaluated how six reusable programming Agent Skills coordinate during software development, testing, review, and defect correction. I used two coding agents—Codex CLI and OpenCode—to independently implement a Python command-line utility that summarizes **synthetic Nmap XML**. Both agents worked to shared, frozen fixture expectations and were prohibited from running Nmap, scanning live targets, or accessing networks.

The objective was not to compare raw coding speed or declare a winning model. I wanted to find out whether reusable instructions could support disciplined handoffs, whether passing tests provided meaningful confidence, and whether independent cross-review would uncover defects missed by an agent's own review.

## Skills and methodology

The six Skills covered project architecture, CLI engineering, code review, security-tool development, debugging/root-cause investigation, and test automation. Each agent selected relevant Skills rather than loading all six. The benchmark exercised a defined cycle: **independent implementation → automated tests → same-agent read-only review → reciprocal cross-agent review → targeted repairs → independent verification**.

The CLI parsed only explicitly named local XML files. Its requirements included deterministic JSON, malformed-input handling, DTD/entity rejection, parser limits, and truthful error reporting. Each implementation used Python's standard library and synthetic files. The agents retained their own source trees, with repair work isolated from the original benchmark snapshots.

## Results

| Stage | Recorded result |
|---|---|
| Codex initial implementation | 17 tests passed |
| OpenCode initial implementation | 13 tests passed |
| Codex reviewing OpenCode | Two medium-severity application defects and one test-portability issue identified |
| OpenCode reviewing Codex | No confirmed product defect; two low-severity test gaps identified |
| OpenCode repair, first iteration | 19 tests passed |
| Independent verification of first repair | Identified an additional unsupported-encoding classification defect |
| OpenCode repair, second iteration | 20 tests passed |
| Final independent verification | 20 tests passed; all nine frozen fixture outcomes passed |

The initial green suites did not catch everything. Cross-review exposed problems with **XML element ancestry** and **unsupported encoding exceptions**. In one case, unexpected nested XML could cause observations to be attributed to the wrong port. In another, an unsupported encoding could escape structured parser handling and produce the wrong error classification. A later verification caught additional encoding variants that the first fix had missed.

The final targeted checks distinguished XML parse errors from genuine filesystem input errors and verified consistent JSON error responses for four unsupported encoding declarations. Final verification ran against a different Python/Expat combination from the repair environment.

## What I learned

**Green tests are evidence, not proof.** The additional defects appeared even after successful automated testing and same-agent review. Stronger negative tests and a second reviewer made the error handling more robust.

**Review-only is a meaningful safety boundary.** Cross-reviews were conducted against preserved copies, with integrity comparisons used to check that reviewed source and fixture files had not changed. Corrections happened later, in separately authorized working copies.

**Agent coordination does not require loading every Skill.** The two agents selected different subsets of the six Skills while satisfying the same overall development contract. Responsibilities and authorization limits were maintained across implementation, testing, and review phases in the reported runs.

**Cross-runtime verification matters.** A fix validated in one environment needed retesting with another Python/Expat version, where related exceptions behaved differently.

## Scope and limitations

This was a controlled offline exercise with synthetic Nmap XML—not a penetration test or live scanning activity. The resulting utilities are not claimed to be production-ready vulnerability scanners, complete Nmap XML implementations, or comprehensively security-audited software. Testing did not include broad fuzzing, production-scale resource benchmarks, or arbitrary hostile-process containment. Test counts from the two agents are not directly comparable because the implementations and suites differed.

The findings reflect recorded agent runs, review reports, and integrity checks. One experiment is insufficient to rank either agent generally.

## Technical competencies demonstrated

Python CLI design; XML parsing and defensive input handling; automated regression testing; negative controls; structured error contracts; reproducibility; evidence preservation; independent code review; cross-runtime debugging; scoped AI-agent collaboration.
