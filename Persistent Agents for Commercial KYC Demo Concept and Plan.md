# Persistent Agents for Commercial KYC: Demo Concept and Plan

Nov 17, 2026 · @Faisal Fareed

## Bottom line

Build a demo in which one persistent agent owns a mid-market commercial client's KYC case for seven months, from onboarding to an event-driven re-review, with humans approving every risk decision. Commercial banking has a real agentic use case, but it is not "KYC in minutes": it is owning the slow, stateful, multi-party case that nobody owns today.

- **Lifecycle pick:** ongoing due diligence (perpetual KYC), with a short onboarding prologue. US rules now make beneficial ownership re-verification event-driven (FinCEN, Feb 2026), and the federal BOI registry is gone for US companies (Aug 2026).
- **The moments that land:** the agent resumes after days of silence with full context; links four weak signals into one ownership change; asks the client only for what changed; quarantines a prompt injection; survives a live kill-and-resume.
- **What makes it credible:** deterministic rules where rules work, a citation on every fact, an independent control agent, a named human manager, and consistency and cost measured on stage.
- **What to avoid:** speed claims for mid-market onboarding, autonomous approval, headcount claims.
- **Effort:** about seven weeks with four to five people (my estimate).

## Scope and assumptions

Four inputs were confirmed by Faisal; the rest are my assumptions and are marked as such. Change any of them and the recommendation may shift.

| Topic | Position | Status | Why it matters |
| --- | --- | --- | --- |
| Audience | Mixed room: business execs plus CTO/architects | Confirmed | Demo needs an exec narrative and a 10-minute technical deep-dive |
| Stack | Vendor-neutral; components mapped to OpenAI, AWS, Google Cloud and Microsoft equivalents | Confirmed | Argue the pattern, not a product |
| Lifecycle stage | Chosen by me from the evidence | Delegated | See the critical take and demo sections |
| Deliverable | This concept and plan doc | Confirmed | Prototype is a later step |
| Segment | US mid-market commercial clients, roughly $10M to $1B revenue: operating companies, holdcos, multi-layer LLCs | Assumption | Excludes small business (mostly digital eKYB already) and large corporate/institutional (closer to CIB) |
| Jurisdiction | US: BSA, FinCEN CDD rule (25% beneficial owners plus one control person), OFAC screening, bank risk-based EDD policy | Assumption | EU AMLR and UK rules only as a sidebar |
| "Persistent agent" | An agent that owns a case or client for weeks to months, with durable state and memory, woken by events (document arrives, registry change, adverse media, deadline), acting under its own identity, permissions and human manager | Assumption | This is the property the demo has to prove; a chat session or a 5-minute pipeline does not qualify |
| Data | Synthetic clients, but real public sources where possible (state business registries, GLEIF, OFAC SDN list) | Assumption | Realism without production data or PII |
| Format | 20-minute storyline plus 10-minute architecture segment | Assumption | Fits a typical exec briefing slot |
| Presenter | A technology provider or advisor showing a bank, not the bank showing a regulator | Assumption | Claims must be defensible to a BSA Officer in the room |

## The critical take: is there a real use case?

Yes, but it is narrower than most agentic KYC demos suggest. The real value is in the long tail of a case, not the first pass. In mid-market commercial banking, assembling a file in minutes speeds up the part of the process that was already shortest.

### Where today's demos overreach

- **"KYC in minutes."** The [AWS/IBM reference architecture](https://aws.amazon.com/blogs/architecture/modernizing-kyc-with-aws-serverless-solutions-and-agentic-ai-for-financial-services/) (Apr 2026) claims under 5 minutes against 3 to 5 days for standard cases, with no published benchmark. [JPMorgan](https://www.risk.net/risk-management/7963378/banks-eye-agentic-ai-to-streamline-kyc-workflows) targets up to five days cut to under a minute. Both measure one automated pass, while a mid-market file is slow because it waits on the client, on handoffs and on QC.
- **The bottleneck just moves.** JPMorgan's Derek Waldron [warned](https://www.artificialintelligence-news.com/news/jpmorgan-chase-ai-strategy-2025/) that hours saved in individual steps "often just shift bottlenecks" in end-to-end processes.
- **"An agent factory replaces the analyst team."** [McKinsey](https://www.mckinsey.com/capabilities/risk-and-resilience/our-insights/agentic-ai-in-financial-crime-prevention-lessons-from-winners) (Oct 2026) saw about 2x productivity at the agent-assistant level across European bank deployments. It calls the fully supervised agent factory untested, and found human oversight was 70 to 75% of variable run cost in one banking task.
- **"Autonomous approval."** The AWS design auto-approves above 95% model confidence. A BSA Officer will push back: model confidence is not a calibrated risk rating. Bank-side examples ([KPMG](https://kpmg.com/kpmg-us/content/dam/kpmg/pdf/2026/kyc-operations-governed-ai-agents.pdf), [Incore Bank with Kyndryl and Google Cloud](https://fintech.global/2026/09/07/incore-bank-trials-gemini-powered-kyc-with-kyndryl/)) keep humans at the risk decision.
- **"Agents for everything."** McKinsey found rule-based question routing beat agent-chosen follow-ups. A structured third-party API also beat agentic web search on speed and accuracy. Ownership math, sanctions matching and policy rules should stay deterministic.
- **Onboarding is relationship work.** [Deloitte](https://www.deloitte.com/us/en/insights/industry/financial-services/agentic-ai-banking.html) (Aug 2025) expects agentic impact "could remain lower" in relationship-heavy areas like client onboarding. The demo should make the RM's ask smaller and better timed, not replace the RM.

### Where agents are a genuine game changer

1. **Owning a case across weeks.** Chasing the client, reconciling partial answers, remembering what was asked and why. Today that lives in email, the CLM queue and one analyst's head; KPMG lists outreach loops, siloed handoffs and poor status visibility as core pain points.
2. **Event-driven ongoing due diligence (perpetual KYC).** Watching for material change, filtering noise, and scoping a targeted re-review instead of a full refresh.
3. **Judgment-heavy drafting with evidence.** Reconciling documents against registries and writing the memo with every claim cited. [Deutsche Bank's private bank](https://www.renascence.io/news/76165/deutsche-banks-kyc-ai-lifts-client-onboarding-efficiency-30) estimates about a 30% onboarding efficiency gain from agentic source-of-wealth checks.

### My pick: anchor on ongoing due diligence

- **US regulation now points there.** FinCEN's [February 2026 exceptive relief](https://www.dlapiper.com/en/insights/publications/2026/03/fincen-issues-exceptive-relief-from-cdd-rule-requirements) drops re-verifying beneficial owners at every new account. Banks verify at the first account, then when facts reasonably call the information into question, and as their risk-based ongoing CDD requires. That is an event-driven obligation.
- **The federal registry backstop is gone.** FinCEN's [August 2026 final rule](https://corpgov.law.harvard.edu/2026/08/27/fincen-permanently-eliminates-boi-reporting-requirements-for-us-companies-and-us-persons/) permanently removed BOI reporting for US companies. Banks have to notice ownership changes themselves.
- **Model risk guidance does not cover agents.** SR 26-2 (Apr 2026) replaced SR 11-7 and the BSA/AML model risk statement, and [EY notes](https://www.ey.com/content/dam/ey-unified-site/ey-com/en-us/insights/banking-capital-markets/documents/ey-model-risk-management-guidance.pdf) generative and agentic AI are out of its scope. Banks govern agents under their own frameworks, so the demo must show governance, not assert it.
- **Buyers are already there.** A [Fenergo and Chartis survey](https://thefintechtimes.com/?p=128098) found KYC maintenance is the second most cited reason for adopting agentic AI, after fraud.
- **Persistence is the point.** A review that spans months and reuses prior reviews cannot be done by a stateless pipeline.

**Verdict:** anchor the demo on ongoing due diligence for the existing commercial book. Add a short onboarding prologue so the room sees the agent build the memory it uses later. Pure onboarding speed is the weaker story for persistence and the riskier claim in front of a BSA Officer.

## What is actually happening in market

Every hyperscaler and several G-SIBs now treat KYC as a flagship agent use case. Almost none of the public examples show an agent that owns a case for weeks. That gap is the opening for this demo.

### Banks and platforms

| Who | What was announced or shipped | What it proves | Long-running and event-driven? |
| --- | --- | --- | --- |
| [JPMorgan](https://www.risk.net/risk-management/7963378/banks-eye-agentic-ai-to-streamline-kyc-workflows) | "Agentic-first" client onboarding, targeted for production by end of April 2026; up to 5 days cut to under a minute (Apr 2026) | A G-SIB redesigning onboarding with agents as orchestrator, not add-on | Not disclosed; the headline is a single fast pass |
| [Goldman Sachs](https://www.investmentnews.com/wirehouses/bny-goldman-double-down-on-tech-with-digital-employees-and-ai-agents/265198) | About six months with embedded Anthropic engineers building Claude-based agents for client vetting and onboarding (reported Feb 2026) | Onboarding and vetting are a top target at a G-SIB | Not disclosed; early stage |
| [BNY](https://www.axios.com/2025/10/17/ai-wall-street-digital-workers) | Over 100 "digital employees" with logins, email addresses, human managers and performance reviews (Oct 2025); [134](https://www.investmentnews.com/wirehouses/bny-goldman-double-down-on-tech-with-digital-employees-and-ai-agents/265198) by Feb 2026 | The operating model a persistent agent needs: identity, manager, scope | Yes, but in payments, reconciliation and code repair, not KYC |
| [Deutsche Bank Private Bank](https://www.renascence.io/news/76165/deutsche-banks-kyc-ai-lifts-client-onboarding-efficiency-30) | Agentic source-of-wealth checks in Singapore and Hong Kong; about 30% efficiency estimate (Sep 2026) | Agents can carry the judgment-heavy memo step | Not disclosed; private bank, not commercial |
| [Standard Chartered Hong Kong](https://www.silenteight.com/blog/ing-standard-chartered-and-hsbc-are-making-perpetual-kyc-work-thanks-to-better-data) | Company data pulled automatically through the HKMA Commercial Data Interchange (2025) | A registry change can arrive as an event, the precondition for perpetual KYC | Event-driven data feed, no agent |
| [HSBC with Google Cloud](https://cloud.google.com/blog/topics/financial-services/how-hsbc-fights-money-launderers-with-artificial-intelligence) | AML AI finds 2 to 4x more suspicious activity with 60% fewer alerts; twice as much financial crime identified in commercial banking | AI can run at scale in a G-SIB's financial crime stack | Transaction monitoring, not KYC |
| [Incore Bank, Kyndryl, Google Cloud](https://fintech.global/2026/09/07/incore-bank-trials-gemini-powered-kyc-with-kyndryl/) | Gemini multi-agent KYC with policy-as-code and guardrail agents, human oversight throughout (Sep 2026) | Policy-as-code plus guardrail agents is a credible control pattern | Proof of concept only |
| [AWS with IBM](https://aws.amazon.com/blogs/architecture/modernizing-kyc-with-aws-serverless-solutions-and-agentic-ai-for-financial-services/) | AgentCore supervisor plus five sub-agents on an Amazon MSK event stream; confidence-banded escalation (Apr 2026) | Event-driven plumbing for KYC agents is mature | Per application; agents act on events but do not own a case |
| [Google Cloud](https://cloud.google.com/blog/products/ai-machine-learning/build-kyc-agentic-workflows-with-googles-adk) | Multi-agent KYC sample on ADK (Jun 2025); [Gemini Enterprise for Financial Services](https://fstech.co.uk/fst/Google_Cloud_Launches_Gemini_Enterprise_For_Financial_Services.php) with partner KYC agents such as D&B Business Verification (Aug 2026) | KYC is a showcase for every hyperscaler | Per request |
| [OpenAI Frontier](https://openai.com/index/introducing-openai-frontier/) and [Microsoft Entra Agent ID](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/agent-identity) | Agent identities with explicit permissions as first-class enterprise objects (2025 to 2026) | The identity layer a case-owning agent needs now exists off the shelf | Platform capability, not a KYC product |

### Advisors and research

| Source | Main finding | What it means for the demo |
| --- | --- | --- |
| [McKinsey](https://www.mckinsey.com/capabilities/risk-and-resilience/our-insights/agentic-ai-in-financial-crime-prevention-lessons-from-winners) (Oct 2026) | Banks put 10 to 15% of staff on KYC and AML. AI cuts KYC handling time 30 to 70%. Run-to-run consistency ranged 72 to 100%. Agents were near-perfect on checkable facts and weaker on adverse media matching and narrative coherence | Show consistency testing live; keep judgment calls behind human gates |
| [BCG](https://www.bcg.com/publications/2025/know-your-customer-agentic-ai-revolution) (Oct 2025) | Financial crime compliance can reach 5% of total bank costs; KYC is the most resource-intensive part and the ripest for change | Frame value in cost per file and analyst capacity |
| [KPMG](https://kpmg.com/kpmg-us/content/dam/kpmg/pdf/2026/kyc-operations-governed-ai-agents.pdf) (2026) | Pain points: repetitive outreach, siloed handoffs, poor status visibility, resource-intensive refresh. Human checkpoints stay at key risk decisions | These are persistence problems; demo them directly |
| [Deloitte](https://www.deloitte.com/us/en/insights/industry/financial-services/agentic-ai-banking.html) (Aug 2025) | Describes continuous KYC maintenance by cooperating agents. Recommends an agent registry with owners, scope and risk limits | Show the registry entry for the demo agent |
| [PwC with Microsoft](https://www.techuk.org/resource/agentic-ai-is-moving-fast-in-financial-services-governance-has-to-move-faster.html) (2026) | Firms need a central control plane that is both system of record and system of control for agent workflows | The architecture segment should be that control plane |
| [Accenture](https://bankingblog.accenture.com/?p=27775) | A European bank started with document classification, extraction, and validating and remediating missing data | Credible starting scope is mundane; say so |
| [EY](https://www.ey.com/content/dam/ey-unified-site/ey-com/en-ca/services/ai/documents/ey-how-agentic-ai-can-improve-anti-money-laundering-investigations.pdf) | Agentic AI for AML investigations, with standardized outputs that reduce review cycles | Adjacent; keep AML investigations out of scope |

No source found shows a production KYC agent that holds a commercial case open across weeks of client outreach and later re-reviews. That is either white space or a sign of how hard it is; the demo has to prove it is the former.

## Why persistence is the game changer

A commercial KYC case is a long-lived, multi-party object; today nobody owns it end to end, so it stalls in queues and inboxes. A persistent agent changes who moves the case forward. Workflow tools and copilots do not.

| Dimension | Workflow or RPA (today's CLM) | Copilot | Persistent case agent |
| --- | --- | --- | --- |
| Time horizon | A task at a time; the case waits in a queue | One analyst session | Weeks to years; wakes on events and timers |
| Who moves the case | Humans pushing tickets | A human, with suggestions | The agent, with humans at gates |
| Memory | Fields in the CLM; context lost at each handoff | The session only | Case record with sources, plus what was asked, answered and decided, and why |
| Triggers | Calendar refresh (1, 3 or 5 years) or manual | A human opens it | Registry changes, client replies, documents, adverse media, transaction signals, expiry dates |
| Handling the unexpected | Exception queue | Depends on the analyst | Reasons about the change, scopes targeted work, escalates when unsure |
| Identity | Shared bot service account | The user's identity | Its own identity, scoped permissions, a named human manager |
| Typical failure | Stalls silently | Inconsistent across analysts | Drift, overreach, prompt injection; must be governed |

### Five capabilities the demo must make visible

1. **Durable time.** The case survives days of silence, restarts and deploys. Even long-running agent runtimes are measured in hours: [AgentCore Runtime](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-how-it-works.html) supports operations up to 8 hours. Weeks-long ownership needs a durable workflow engine that holds state, timers and human tasks and wakes the agent on each event; [Temporal](https://docs.temporal.io/ai) and [Azure Durable Functions](https://techcommunity.microsoft.com/blog/appsonazureblog/-/4453402) both integrate with the OpenAI Agents SDK.
2. **Memory as a record, not a recollection.** Managed agent memory such as [Vertex AI Memory Bank](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/memory-bank/overview?hl=en) extracts facts from conversations automatically. For KYC every fact needs a source, a timestamp and who confirmed it. The KYC profile and evidence store are the memory; LLM summaries are working notes derived from them.
3. **Event triage.** Perpetual KYC can flood analysts with alerts; [WorkFusion](https://www.workfusion.com/wp-content/uploads/2026/03/pKYC-Avert-the-Alerts-Avalanche.pdf) frames the job as separating non-material events, such as minor filings and address changes, from material ones. The agent must show its reasoning for each.
4. **Accountable identity.** The BNY model: a login, a manager, a defined scope. In the demo the agent reads core banking and screening results but writes only to case management and draft outreach.
5. **Learning under change control.** Analyst corrections and QC findings improve the agent over time. Prompt and policy changes still go through change control and a regression evaluation run before release.

## The recommended demo: "One client, seven months, one case owner"

The demo follows one mid-market client from onboarding to an event-driven re-review seven months later, compressed into 20 minutes, with one persistent agent owning the case throughout. A 6-minute architecture segment then proves the persistence is real, not animation.

### The client (fictional)

**Tidewater Cold Chain Holdings LLC**: a New Jersey refrigerated logistics operator with about $140M revenue, owned through a Delaware holding company. Owners: the founder (40%), a private equity fund's SPV (35%), the founder's sister (15%) and an employee pool (10%). It needs operating accounts, treasury management, a revolver, and cross-border payments to a produce supplier in Mexico. Proposed risk: medium. *Assumption: the name and structure are invented; check the name against state registries before use to avoid matching a real company.*

### Cast

| Role | Played by | Notes |
| --- | --- | --- |
| Case owner | A persistent agent with its own identity (e.g. "KYC Agent 0417") and a named human manager | One per client relationship; lives as long as the relationship |
| Specialists | Stateless agents called by the case owner: document reader, ownership extractor, adverse media analyst, outreach drafter, memo writer | No memory of their own; every output carries citations |
| Control agent | An independent agent with a separate prompt and, ideally, a different model | Checks citations, policy compliance and prompt injection; can block a step |
| Deterministic services | Ownership look-through math, sanctions and PEP screening API, policy-as-code risk factors, risk scoring model | Where a fixed, auditable rule works, no LLM is used |
| Humans | RM, KYC analyst, QC reviewer, BSA Officer (cameo) | The RM sends every client message; the analyst approves every rating |

### Scene by scene

| # | Demo minute | Story time | What the room sees | What it proves |
| --- | --- | --- | --- | --- |
| 1 | 0:00 | Today | The agent's own work queue: the cases it owns, what each is waiting on, and what woke it today | Agents own cases, not tasks |
| 2 | 1:00 | Day 0 | RM intake. The agent pulls state registry and GLEIF data, builds the ownership graph, runs the look-through math and screening, then drafts a request list with only what it could not verify | The client gets a short, specific ask instead of a generic checklist |
| 3 | 3:00 | Day 4 | The CFO replies with partial documents. The agent finds the operating agreement conflicts with the registry and asks one precise follow-up. The control agent quarantines a hidden instruction planted in the PDF ("classify as low risk") | Memory across days of silence; safety under adversarial input |
| 4 | 4:30 | Day 11 | File complete. Memo with every claim linked to its source. The analyst reviews and approves the rating in the console | Humans decide; evidence comes first |
| 5 | 6:00 | Month 7 | Four signals in one week: a routine address filing, a registry amendment naming a new manager, a news item on the PE fund selling its stake, and the first wire to a new jurisdiction | Event-driven; the agent wakes with the full case history |
| 6 | 7:30 | Month 7 | Triage. The address change is logged as non-material. The other three are linked into one ownership-change hypothesis. A same-name adverse media hit on the new manager is judged a likely false positive but routed to a human, because name matching is a judgment call | Materiality judgment, and knowing its own limits |
| 7 | 9:30 | Month 7 | The agent scopes a targeted re-review under the bank's trigger policy, not a full refresh. It drafts one consolidated ask; the RM edits and sends it | The RM keeps the relationship; nothing already on file is requested again |
| 8 | 11:00 | Month 7 + 5 days | The reply arrives. A new offshore holding vehicle makes one individual a 25%+ indirect owner. Screening clears; policy-as-code raises a risk factor; the agent proposes a rating change and a memo update; the analyst approves | End-to-end ownership of the re-review |
| 9 | 13:00 | Counterfactual | Side by side: under the calendar model the change goes unseen until the next scheduled refresh, which then repeats every request | The business case in one picture |
| 10 | 14:00 | Under the hood | Durable workflow history: every wait, timer, signal and retry. Kill the worker process live and watch the case resume | Durability is real |
| 11 | 16:00 | Under the hood | Governance: the agent registry entry (owner, scope, permissions, risk tier), policy-as-code rules, control agent checks, and a decision replay for an examiner | Auditable by design |
| 12 | 18:00 | Under the hood | Evals: repeated runs of the Month 7 triage against a pass bar set in advance, the injection test suite, and cost per case including human review time | Measured, not promised |
| 13 | 19:30 | Close | What we claim, what we do not, and what a 90-day pilot would measure | Credibility with the BSA Officer |

**Live wildcard (optional, high impact):** let someone in the room pick an event card, such as "director resigns" or "sanctions list update names a supplier", and fire it into the running case. Pre-test every card. Nothing proves the agent is not scripted faster.

&#91;embedded content: demo storyline · 6 moments over 7 months\]

The agent's line never breaks: it works in bursts and watches in between. Bank staff act only to send messages and approve decisions, and the client is contacted three times in seven months.

## Vendor-neutral reference architecture

The workflow owns time, the agent owns judgment, and the KYC system owns the record. Keeping those three apart is what makes a weeks-long agent both durable and auditable.

&#91;embedded content: reference architecture · 8 layers\]

Events wake a durable workflow, which rebuilds the case owner from the record. The agent proposes; humans approve through workflow gates.

### Components and example products

| Layer | Job in the demo | Example products (any one works) |
| --- | --- | --- |
| Event intake and watcher | Normalizes registry filings, client replies, screening hits, transaction signals and expiry timers; drops obvious noise with rules before any LLM sees it | Kafka or Amazon MSK (used in the [AWS reference design](https://aws.amazon.com/blogs/architecture/modernizing-kyc-with-aws-serverless-solutions-and-agentic-ai-for-financial-services/)), Google Pub/Sub, Azure Event Hubs |
| Durable case workflow | One workflow per client: timers, waits, human tasks, retries; survives restarts | [Temporal](https://docs.temporal.io/ai), AWS Step Functions, [Azure Durable Functions](https://techcommunity.microsoft.com/blog/appsonazureblog/-/4453402) |
| Agent runtime | Runs the case owner and the stateless specialists through a model gateway | OpenAI Agents SDK or [Frontier](https://openai.com/index/introducing-openai-frontier/), [Amazon Bedrock AgentCore](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-how-it-works.html), Vertex AI Agent Engine with ADK, Microsoft Foundry Agent Service |
| Case record (the memory) | KYC profile, evidence with sources and timestamps, every request and reply, every decision and approver | The bank's CLM (e.g. Fenergo, nCino, Pega) or a purpose-built case store. Managed agent memory (AgentCore Memory, Vertex AI Memory Bank) only for working notes |
| Deterministic services | Ownership look-through math, sanctions and PEP screening, policy-as-code risk factors, risk scoring | OPA or Cedar for policy; the bank's existing screening vendor and risk model |
| Control plane | Control agent, human approval gates, agent registry, kill switch | Built in the demo; the PwC and Microsoft "system of record and system of control" idea |
| Identity and access | One identity per agent, least privilege, delegated tokens when acting for the RM | [Microsoft Entra Agent ID](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/agent-identity), AgentCore Identity, Frontier agent identities |
| Observability and audit | Immutable trace, decision replay, eval results | Workflow event history, OpenTelemetry traces, cloud audit logs |

### Design rules to state out loud in the demo

- **The agent proposes; a workflow gate disposes.** Risk ratings, account approvals and exits are human tasks in the workflow, not agent actions.
- **No citation, no fact.** Any model output that becomes part of the file must point to a document page or registry record. The control agent blocks uncited claims.
- **Wake from the record, not the chat.** On every event the case owner is rebuilt from the case record and a short structured summary. Context stays small, current and auditable.
- **Confidence bands, not confidence scores.** Following one bank in the McKinsey research: grade source authority and entity-match strength into bands, use only the top band without review, and suppress ungrounded answers instead of caveating them.
- **Read-only by default.** The agent reads core banking and screening results. It writes only to case management and to draft outreach, which a human sends.

## What to measure and what to claim

Lead with client touches and time-to-detect material change, not raw speed. Those are the numbers persistence moves, and the ones a BSA Officer will not dispute. The pilot targets below are my assumptions for discussion, not benchmarks.

| KPI | Industry baseline | How the demo shows it | Pilot target (assumption) |
| --- | --- | --- | --- |
| Client contacts per onboarding | Banks say 4, corporates count 8 ([Thomson Reuters, 2017](https://www.theglobaltreasurer.com/?p=1598)); Forrester estimates about 10 ([via Moody's](https://moodys.com/web/en/us/kyc/resources/insights/customer-onboarding-best-practices-financial-institutions.html)). Dated, but no newer public figure found | Counter on the case: asks sent versus items verified without asking | 2 or fewer for a standard file |
| Repeat requests for data already held | 92% of corporate treasurers asked for the same information more than once ([Encompass, 2025](https://www.encompasscorporation.com/blog/why-kyc-for-corporates-is-broken-and-how-to-fix-it/)) | Scene 7: the ask lists only what changed | Zero |
| Onboarding elapsed time | UK corporate banks often take more than six weeks; 70% of firms lost clients to slow onboarding; about 10% abandonment ([Fenergo, 2025](https://fintech.global/?p=217350)) | Split the clock: bank-controlled time versus waiting on the client | Bank-controlled time down by half |
| Periodic review effort | KYC reviews average 90 days and $2,300 each ([Fenergo](https://go.fenergo.com/agentic-ai-operations-efficiency-global)); only about a third of periodic reviews are automated ([Fenergo, 2025](https://fintech.global/?p=217350)) | Scene 9 counterfactual: targeted re-review versus full refresh | Material events reviewed within 5 business days of the trigger |
| Analyst handling time per file | 30 to 70% reduction estimated ([McKinsey, 2026](https://www.mckinsey.com/capabilities/risk-and-resilience/our-insights/agentic-ai-in-financial-crime-prevention-lessons-from-winners)) | Timer on the analyst review step | 30% reduction, the low end of the range |
| Consistency of judgment | One bank's sign-off bar: 80% accuracy and 70% run-to-run consistency (McKinsey) | Scene 12: repeated runs of the Month 7 triage | Meet or beat the bank's own bar, set before the demo |
| Evidence coverage | No industry baseline | Every memo claim links to its source | 100% |
| Cost per case | McKinsey found human oversight, not tokens, dominates variable run cost | Scene 12: token cost plus human review minutes | Lower than today's fully loaded cost per file |

### Claims to make

- Fewer, better-timed client asks, and no repeated requests for data already on file.
- Material changes caught between scheduled reviews, with the reasoning shown.
- Every fact traceable to a source; every decision replayable for an examiner.
- Less bank-controlled time per case, with client waiting time made visible.

### Claims to avoid

- "Onboarding in minutes" for mid-market commercial clients.
- "Replaces analysts", or any headcount figure.
- Autonomous approval or straight-through risk ratings.
- "Regulator approved" or "SR 26-2 compliant"; agentic AI is outside its scope.
- Vendor productivity multiples presented as measured results.
- "The agent learns on its own" without change control.

## Data, realism and the skeptic test

Use synthetic clients and real public reference data, and design every scene to survive a hostile question. A mixed room will contain at least one person paid to find the hole.

### Data plan

| Data | Source | Real or synthetic |
| --- | --- | --- |
| Entity registration and amendments | Mock API that serves records in the format of a state business registry | Synthetic |
| Sanctions screening (clears) | OFAC SDN list | Real public list |
| Sanctions and PEP hits used in scenes | Purpose-built entries, clearly labeled | Synthetic; never make a fictional person resemble a real listed person |
| Corporate documents | Operating agreement, certificate of formation, beneficial ownership certification, specimen IDs | Synthetic, one with a planted injection |
| Adverse media | Short news articles written for the demo, including the same-name false positive | Synthetic |
| Transactions | Wire history, including the first payment to a new jurisdiction | Synthetic |
| Bank policy | A written demo-bank KYC policy: risk factors, review triggers, EDD thresholds, encoded as policy-as-code | Written for the demo, reviewed by a KYC SME |

### The skeptic test

| Question | Likely asker | How the demo answers |
| --- | --- | --- |
| "Isn't this our CLM workflow with an LLM bolted on?" | CTO | Scenes 5 to 8: the CLM routes tasks, while the agent decides what work an event requires and does it. Show the CLM as the record underneath |
| "What if it invents an owner?" | Head of KYC | Ownership math is deterministic, extraction is cited, and the control agent blocks uncited claims (scenes 3 and 4) |
| "Who is accountable when it is wrong?" | BSA Officer | Registry entry with a named human manager; humans approve ratings; full trace |
| "Can an examiner reconstruct this decision in two years?" | BSA Officer, internal audit | Scene 11: decision replay from the workflow history and the case record |
| "What about prompt injection through client documents?" | CISO | Scene 3 quarantines a planted instruction; scene 12 runs the injection suite |
| "Will it give the same answer twice?" | Model risk | Scene 12: repeated runs against a pass bar set in advance |
| "What does a case cost to run?" | COO, CFO | Scene 12: token cost plus human review minutes per case |
| "My RMs will not let a bot email their clients." | Head of Commercial Banking | The RM edits and sends every message; the agent only drafts |
| "Is the time-skip just a script?" | Everyone | The live wildcard event, and kill-and-resume in scene 10 |
| "SR 26-2 excludes agentic AI, so what governs this?" | Second line, model risk | The bank's own AI risk framework. Show a risk tier scored on agency, impact, data sensitivity and action surface, as McKinsey suggests |
| "Will it work on our messy data?" | Operations | Honest answer: the demo cannot prove that. The pilot measures it on a sample of the real book |

## Build plan

A credible version takes about seven weeks with four to five people. That is my estimate, assuming synthetic data and no integration with a real bank system. Build the parts that prove persistence and judgment for real; simulate the external feeds.

1. **Weeks 1 to 2: Scenario and policy.** Write the demo-bank KYC policy and trigger rules with a KYC SME. Build the synthetic client set (Tidewater plus two background clients for the queue view) and the event cards. Set eval pass bars before any build.
2. **Weeks 2 to 4: Core.** Durable case workflow, case record with sources, event watcher with a rules pre-filter, the case owner, five specialists and the control agent, and the deterministic ownership and policy services.
3. **Weeks 4 to 5: Experience.** Analyst console with case timeline, simulated clock and approvals; RM outreach view; the under-the-hood trace and replay view.
4. **Weeks 5 to 6: Hardening.** Consistency runs, injection suite, cost instrumentation, and a red team led by the KYC SME and someone playing the BSA Officer.
5. **Week 7: Rehearsal.** Three dry runs in front of a hostile panel, plus a fallback recording of every scene.

**Team:** a demo lead with KYC operations experience, two engineers (agents and workflow; front end), a part-time KYC or compliance SME, and a part-time designer.

| Element | Build or simulate | Why |
| --- | --- | --- |
| Durable workflow, timers, kill-and-resume | Build | This is the proof of persistence |
| Agent reasoning, control agent, citations | Build | This is the product |
| Ownership math and policy-as-code | Build | Shows where the LLM is deliberately not used |
| Clock | Simulate: an accelerated clock driving real workflow timers | Seven months in 20 minutes |
| Registry, screening and transaction feeds | Simulate: mock APIs replaying synthetic events | No vendor contracts or real PII |
| Client email and portal | Simulate: a demo inbox | Keeps the RM-sends-everything rule visible |
| CLM system of record | Simulate with a light mock, or use a bank sandbox if offered | Shows the agent sits on top of the record, not in place of it |

## Risks and decisions needed

The biggest risk is not technical: it is a demo that overclaims in front of the one person whose sign-off matters. Most of the plan above exists to prevent that.

| Risk | Effect | Mitigation |
| --- | --- | --- |
| Overclaiming | The BSA Officer disengages and the room follows | Use the claims list; rehearse with a hostile panel |
| Persistence looks like slides | Time-skips read as scripted animation | Kill-and-resume in scene 10; the live wildcard event |
| Live non-determinism | An odd answer on stage | Pre-run each scene; show real consistency results; keep fallback recordings |
| Name collisions | A fictional client or person matches a real one | Check names against registries; label synthetic list entries |
| Wrong jurisdiction for the room | US trigger logic shown to an EU or UK bank | Rework the trigger policy for local rules before showing it |
| Scope creep into AML | Transaction monitoring becomes the story | Keep transaction data as one signal, never an investigation |
| Looks vendor-locked | A mixed room assumes a sales pitch | Show the product mapping table; keep the pattern center stage |

### Decisions for Faisal

- [ ] Confirm the segment and jurisdiction (assumed: US mid-market commercial).
- [ ] Keep or drop the transaction signal in scene 5 (more realism, more scope risk).
- [ ] Pick one reference stack for the build, while the story stays vendor-neutral.
- [ ] Recruit a KYC SME to own the demo-bank policy and lead the red team.
- [ ] Decide on the live wildcard: highest impact, highest risk.
- [ ] Track the FCA's evaluation of its eight live agentic tests, expected in Q1 2027 per [McKinsey](https://www.mckinsey.com/capabilities/risk-and-resilience/our-insights/agentic-ai-in-financial-crime-prevention-lessons-from-winners), and refresh the regulatory framing when it lands.

## Sources

Pages in the first list were opened and their figures checked. Pages in the second came from search results; open them before quoting externally.

**Opened and checked**

- [McKinsey: Agentic AI in financial-crime prevention, lessons from winners](https://www.mckinsey.com/capabilities/risk-and-resilience/our-insights/agentic-ai-in-financial-crime-prevention-lessons-from-winners) (Oct 26, 2026)
- [KPMG: KYC operations with governed AI agents](https://kpmg.com/kpmg-us/content/dam/kpmg/pdf/2026/kyc-operations-governed-ai-agents.pdf) (2026)
- [Risk.net: Banks eye agentic AI to streamline KYC workflows](https://www.risk.net/risk-management/7963378/banks-eye-agentic-ai-to-streamline-kyc-workflows) (Apr 15, 2026; paywalled beyond the intro)
- [AWS Architecture Blog: Modernizing KYC with AWS serverless solutions and agentic AI](https://aws.amazon.com/blogs/architecture/modernizing-kyc-with-aws-serverless-solutions-and-agentic-ai-for-financial-services/) (Apr 23, 2026)
- [Deloitte: Agentic AI in banking](https://www.deloitte.com/us/en/insights/industry/financial-services/agentic-ai-banking.html) (Aug 14, 2025)
- [Renascence summary of Finextra: Deutsche Bank KYC AI](https://www.renascence.io/news/76165/deutsche-banks-kyc-ai-lifts-client-onboarding-efficiency-30) (Sep 23, 2026)
- [InvestmentNews: BNY, Goldman double down on digital employees and AI agents](https://www.investmentnews.com/wirehouses/bny-goldman-double-down-on-tech-with-digital-employees-and-ai-agents/265198) (Feb 9, 2026)
- [FinTech Global: 70% of banks lose clients due to slow onboarding (Fenergo)](https://fintech.global/?p=217350) (Oct 8, 2025)
- [Fenergo and Chartis: Agentic AI operations efficiency](https://go.fenergo.com/agentic-ai-operations-efficiency-global) (undated)
- [The Fintech Times: Fenergo and Chartis agentic AI survey](https://thefintechtimes.com/?p=128098) (Jul 28, 2025)
- [Encompass: Why KYC for corporates is broken](https://www.encompasscorporation.com/blog/why-kyc-for-corporates-is-broken-and-how-to-fix-it/) (2025)
- [Google Cloud: How HSBC fights money launderers with AI](https://cloud.google.com/blog/topics/financial-services/how-hsbc-fights-money-launderers-with-artificial-intelligence) (Nov 29, 2023)
- [EY: Revised interagency model risk management guidance](https://www.ey.com/content/dam/ey-unified-site/ey-com/en-us/insights/banking-capital-markets/documents/ey-model-risk-management-guidance.pdf) (2026)
- [DLA Piper: FinCEN issues exceptive relief from CDD rule requirements](https://www.dlapiper.com/en/insights/publications/2026/03/fincen-issues-exceptive-relief-from-cdd-rule-requirements) (Mar 2, 2026)

**From search results (verify before external use)**

- [Axios: This Wall Street bank has over 100 digital employees](https://www.axios.com/2025/10/17/ai-wall-street-digital-workers) (Oct 17, 2025)
- [Harvard Law corporate governance forum: FinCEN permanently eliminates BOI reporting for US companies](https://corpgov.law.harvard.edu/2026/08/27/fincen-permanently-eliminates-boi-reporting-requirements-for-us-companies-and-us-persons/) (Aug 27, 2026)
- [FinTech Global: Incore Bank trials Gemini-powered KYC with Kyndryl](https://fintech.global/2026/09/07/incore-bank-trials-gemini-powered-kyc-with-kyndryl/) (Sep 7, 2026)
- [Google Cloud: Build a multi-agent KYC workflow with ADK](https://cloud.google.com/blog/products/ai-machine-learning/build-kyc-agentic-workflows-with-googles-adk) (Jun 2025)
- [FStech: Google Cloud launches Gemini Enterprise for Financial Services](https://fstech.co.uk/fst/Google_Cloud_Launches_Gemini_Enterprise_For_Financial_Services.php) (Aug 2026)
- [Silent Eight: ING, Standard Chartered and HSBC making perpetual KYC work](https://www.silenteight.com/blog/ing-standard-chartered-and-hsbc-are-making-perpetual-kyc-work-thanks-to-better-data)
- [OpenAI: Introducing Frontier](https://openai.com/index/introducing-openai-frontier/) (Feb 2026)
- [Microsoft Learn: Agent identity in Foundry](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/agent-identity)
- [AWS: How AgentCore Runtime works](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-how-it-works.html)
- [Temporal: Durable AI](https://docs.temporal.io/ai)
- [Microsoft: OpenAI Agents SDK integration with Azure Durable Functions](https://techcommunity.microsoft.com/blog/appsonazureblog/-/4453402)
- [Google Cloud: Vertex AI Agent Engine Memory Bank overview](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/memory-bank/overview?hl=en)
- [WorkFusion: pKYC, avert the alerts avalanche](https://www.workfusion.com/wp-content/uploads/2026/03/pKYC-Avert-the-Alerts-Avalanche.pdf) (2026)
- [BCG: The KYC agentic AI revolution](https://www.bcg.com/publications/2025/know-your-customer-agentic-ai-revolution) (Oct 2025)
- [techUK, PwC guest blog: Agentic AI governance in financial services](https://www.techuk.org/resource/agentic-ai-is-moving-fast-in-financial-services-governance-has-to-move-faster.html)
- [Accenture Banking Blog: agentic AI in KYC](https://bankingblog.accenture.com/?p=27775)
- [EY: How agentic AI can improve AML investigations](https://www.ey.com/content/dam/ey-unified-site/ey-com/en-ca/services/ai/documents/ey-how-agentic-ai-can-improve-anti-money-laundering-investigations.pdf)
- [AI News: JPMorgan Chase AI strategy (Derek Waldron)](https://www.artificialintelligence-news.com/news/jpmorgan-chase-ai-strategy-2025/)
- [The Global Treasurer: Thomson Reuters KYC survey](https://www.theglobaltreasurer.com/?p=1598) (2017)
- [Moody's: Customer onboarding best practices (cites Forrester)](https://moodys.com/web/en/us/kyc/resources/insights/customer-onboarding-best-practices-financial-institutions.html)
