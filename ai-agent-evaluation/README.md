# Cross-Agent Code Review — AI Agent Skills Evaluation

**Project type:** Personal software engineering experiment  
**Environment:** Codex CLI on Linux Mint; OpenCode on Fedora AgentVM  
**Technologies:** Python, XML/Expat, unittest, Git, Agent Skills  
**Evidence checkpoint:** 26 October 2026  
**Status:** Completed controlled offline evaluation; broader reliability and security validation incomplete

## 1. Objective and context

This project evaluated how reusable programming Agent Skills could support a controlled software development workflow involving two AI coding agents.

Codex CLI and OpenCode independently implemented a Python command-line application for processing synthetic Nmap XML.

The experiment investigated three practical questions:

1. Could the agents select and use relevant Skills while respecting task-specific authorization boundaries?
2. Would automated tests and same-agent reviews identify the important defects?
3. Could reciprocal code review reveal issues that the original agent had missed?

The objective was to study software engineering process quality, defect discovery and reproducibility—not to rank models by coding speed or demonstrate live penetration-testing capability.

## 2. Technical environment

The experiment used two separate Linux environments.

| Component | Linux Mint | Fedora AgentVM |
| --- | --- | --- |
| Coding agent | Codex CLI | OpenCode |
| Python version | 3.12.3 | 3.14.8 |
| Expat version | 2.6.1 | 2.8.5 |
| Main responsibility | Independent implementation and reciprocal review | Independent implementation and reciprocal review |

The different Python/Expat combinations later became important when testing XML parser exception handling.

The Fedora AgentVM was a guest environment used for controlled coding-agent experiments. It was not a substitute for the primary Linux Mint homelab.

### Six reusable Agent Skills

The evaluation drew from six locally maintained Skills:

| Skill | Intended responsibility |
| --- | --- |
| `python-project-architect` | Project organization and architecture |
| `python-cli-builder` | Command-line interfaces and application contracts |
| `security-tool-developer` | Security boundaries and controlled tooling |
| `test-automation-engineer` | Test design and regression verification |
| `code-review-engineer` | Code review and targeted corrections |
| `debugging-root-cause-investigator` | Structured investigation of defects |

The agents selected Skills relevant to each phase instead of loading all six.

In the initial implementations, both loaded the CLI, security-tool and testing Skills. Codex additionally loaded the architecture Skill. The root-cause investigation Skill was not needed as a separate workflow.

These are reported Skill-loading observations, not proof of automatic activation or a controlled comparison against agents operating without Skills.

## 3. Implementation and evaluation design

### Application contract

Both agents received the same bounded task: implement a Python standard-library CLI that reads explicitly named local files containing synthetic Nmap XML and produces deterministic structured JSON.

The contract included:

- Host, port and service observation extraction.
- Input and output validation.
- Malformed XML handling.
- DTD and entity declaration rejection.
- Input-size and parser-complexity limits.
- Consistent error reporting.
- No unsupported vulnerability or scan-completeness claims.

The exercise used nine frozen fixture expectations. These supplied common behavioral requirements while allowing independent implementations and test suites.

No Nmap execution, network scanning, external target access, privilege escalation or production-system configuration changes were authorized.

### Workflow

The experiment followed a defined sequence:

1. Independent implementation by Codex and OpenCode.
2. Automated testing against local synthetic fixtures.
3. Same-agent review and targeted corrections.
4. Exchange of preserved project snapshots.
5. Reciprocal read-only code review.
6. Repair in separately authorized working copies.
7. Independent verification of the repaired implementation.

Review artifacts were maintained outside the reviewed source trees. Reported integrity checks compared directory contents and file hashes to detect changes to preserved snapshots.

These controls support the documented preservation results but do not constitute cryptographically signed attestations or comprehensive filesystem isolation.

## 4. Security considerations

The central security requirement was to treat XML input as untrusted data.

The application contract restricted access to explicitly named local files and prohibited live scanning. It also required rejection of XML declarations capable of introducing external entities or unsupported parsing behavior.

Other important boundaries included:

- Separating read-only review from authorized repair.
- Keeping original benchmark snapshots separate from modified copies.
- Preventing unexpected input from being reported as successful analysis.
- Distinguishing malformed XML from filesystem access errors.
- Using bounded execution and synthetic test data.
- Avoiding claims about vulnerabilities in real systems.

These controls were evaluated within a limited offline test environment. They do not establish that the generated applications are secure against arbitrary malicious inputs or resource-exhaustion attacks.

## 5. Testing and verification

### Initial implementation results

| Implementation | Recorded initial tests |
| --- | --- |
| Codex | 17 passed |
| OpenCode | 13 passed |

Both implementations met their respective initial automated test expectations.

The test counts are not directly comparable because the agents developed different implementations and suites.

### Same-agent reviews

Before reciprocal review, each agent inspected its own implementation.

Codex's review identified and corrected two low-severity issues involving leading-zero port input and duplicate XML state elements.

OpenCode's review identified and corrected a scan-completeness classification issue involving a failed `runstats/finished` status.

These findings demonstrate that review added value beyond the initial test suites, but same-agent inspection is not independent verification.

### Reciprocal code review

Codex reviewed a preserved copy of OpenCode's implementation and identified:

- **Medium — XML ancestry handling:** Unexpected nested XML structures could cause parsing errors or incorrect attribution of observations to ports.
- **Medium — Unsupported XML encoding:** Certain declarations could escape the intended parser error handling and produce incorrect classifications.
- **Low — Test portability:** An external-entity test depended on an absolute path from the original environment.

OpenCode reviewed Codex's implementation and reported no confirmed application defect in the reviewed scope.

It identified two low-severity test weaknesses: an output-size assertion evaluated after subprocess completion and a dash-leading filename test that did not actually exercise a relative path beginning with a dash.

The absence of a confirmed defect in one bounded review is not evidence that an implementation is defect-free.

### First repair and independent verification

OpenCode corrected the identified XML ancestry and encoding issues and improved the portability of the affected test.

Its repaired implementation passed **19 tests** on Fedora.

Codex subsequently verified the repair on Linux Mint. Despite the passing suite, that independent check identified additional unsupported-encoding declarations that raised a specific Expat `ValueError` on Python 3.12.3 / Expat 2.6.1.

Those cases were still being classified as filesystem input errors rather than malformed XML.

### Second repair and final verification

OpenCode applied a narrower fix for the parser-origin encoding exception and extended the regression tests.

The final independent verification on Mint recorded:

| Verification | Result |
| --- | --- |
| Repaired implementation tests | 20 passed |
| Frozen fixture expectations | All nine matched |
| Unsupported encoding classifications | Four investigated declarations handled correctly |
| Error output | Structured JSON without tracebacks for the checked cases |
| Filesystem input errors | Checked cases retained their separate classification |
| Unrelated injected `ValueError` cases | Propagated rather than being silently reclassified |

The four investigated declarations were `x-no-such-encoding`, `UTF-32`, `UTF-7` and `shift_jis`.

The final repair passed the documented checks on the original problematic Python/Expat combination. No further actionable finding was reported during that bounded verification.

This result does not establish complete XML parser security or cross-runtime compatibility beyond the tested versions.

### Preservation checks

The reported review process retained original projects and read-only review copies separately from the repaired implementation.

Hash and directory comparisons supported preservation of the reviewed files. The final independent verification reported that 19 directory entries were unchanged, with matching hashes for regular files.

These observations support the reported review boundary. They do not establish comprehensive protection against every possible side effect outside the checked locations.

## 6. Results and limitations

### Verified within the recorded evaluation

The documented experiment supports these conclusions:

- Both agents completed the bounded offline CLI development task.
- Relevant Skills were explicitly selected and used in the reported workflows.
- Same-agent and reciprocal reviews identified actionable defects after initially passing tests.
- A first successful repair suite did not eliminate all related parser edge cases.
- A second targeted repair passed the final recorded regression checks.
- Cross-runtime verification exposed an exception-handling issue not covered by the original Fedora tests.
- Reported integrity checks supported preservation of the reviewed project snapshots.

### Not established

The experiment does not establish:

- That either coding agent is generally more capable or reliable.
- That Agent Skills improve results compared with a controlled no-Skill baseline.
- Automatic Skill activation or independent multi-agent delegation.
- Production-grade security of either generated application.
- Complete Nmap XML specification support.
- Resistance to comprehensive fuzzing or adversarial resource exhaustion.
- Full subprocess-tree containment or streaming output-size enforcement.
- Compatibility across untested operating systems, Python versions or parser libraries.
- Absence of undiscovered defects.

Some execution, review and integrity outcomes were recorded in agent-generated reports and user-supplied terminal evidence. The underlying private project source trees were not independently re-executed as part of preparing this public case study.

## 7. Lessons learned

**Passing tests do not establish correctness.** Both initial implementations passed their suites, but subsequent reviews uncovered cases the tests had not covered.

**Independent verification can expose environment-dependent defects.** The unsupported-encoding behavior differed between Python/Expat versions, making cross-runtime testing important.

**Error classification is part of the security contract.** Malformed input should not be misreported as a filesystem error or successful analysis, and unrelated exceptions should not be hidden by overly broad handlers.

**Review and repair need separate authorization.** Preserving the original artifacts makes findings easier to reproduce and keeps the experiment's development history intact.

**Test quality matters more than raw test counts.** A green suite can contain incomplete assertions or tests that fail to exercise their intended edge cases.

**Benchmark conclusions must stay within scope.** One synthetic experiment can demonstrate a useful workflow without proving general agent superiority or production readiness.

## 8. Evidence and references

This public case study summarizes a more detailed benchmark report maintained in the private Agent Skills repository.

The internal report records the evaluation chronology, individual findings, repair iterations, runtime versions and reported preservation checks.

The private report and original working copies are not automatically authorized for public release.

Public evidence currently consists of this curated technical summary and its explicitly stated limitations.

## 9. Future improvements

Potential follow-up work includes:

- Adding stronger tests for relative filenames beginning with a dash.
- Improving subprocess output-capture enforcement.
- Repeating parser regression checks across additional Python/Expat versions.
- Adding controlled fuzzing and resource-limit tests.
- Comparing Skill-guided workflows against a defined no-Skill baseline.
- Preserving reproducible, sanitized fixture and test artifacts for public review.

These are future evaluation opportunities, not completed achievements.

## Authorization and publication

The experiment used synthetic Nmap XML and locally authorized software development environments.

No live network assessment or vulnerability exploitation was part of this benchmark.

Private repository content, raw agent execution logs and unreviewed environment details remain outside this public case study.
