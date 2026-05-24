# DMN Rule Specification

> Current alignment note - 2026-05-24:
> The raw Kogito runtime exposes generated decision-service endpoints such as
> `/CampaignStrategy/EvaluateCampaignStrategy`, not `/rules/*` paths. Friendly
> product names live in the FastAPI adapter and internal tool routes. Raw Kogito
> responses do not own `rule_decision_id` or `evaluated_at`; FastAPI supplies
> those defaults when normalizing responses.

## Overview

This document describes the decision logic implemented in the rule-service DMN assets for the `content_creator` project. The goal is to explain what each file accepts as input, how the rules behave, what they return, and how the FastAPI layer uses the results at runtime.

The current rule set is deterministic. It does not perform machine learning or probabilistic inference. Instead, it applies explicit FEEL expressions and decision tables to produce stable, auditable marketing recommendations and risk flags.

## Rule-Service Scope

The rule service currently exposes four DMN files:

| File | Purpose | Main Output |
|---|---|---|
| `CampaignStrategy.dmn` | Derive campaign strategy recommendations | objective, CTA, KPI band, approval flag, constraints, rationale |
| `CampaignPlan.dmn` | Calculate planning bands and cadence estimates | budget bands, KPI forecast bands, duration, cadence, confidence |
| `ClaimRisk.dmn` | Flag risky marketing claims in draft text | risk flags and approval requirement |
| `SegmentConstraints.dmn` | Return segment-specific content constraints | constraint notes by property segment and format |

## Runtime Integration

The FastAPI layer is the product boundary. The browser does not talk to the rule service directly.

### Runtime Flow

1. The application receives a product request through FastAPI.
2. `api/app/services/kogito_rule_client.py` maps the request into the shape expected by the DMN service.
3. If `KOGITO_RULE_SERVICE_URL` is configured, FastAPI sends the request to the Quarkus rule service.
4. If the rule service is not configured, the API falls back to local deterministic rules through `LocalRules()`.
5. The response is validated against the Pydantic model in `api/app/models/rules.py`.
6. `api/app/services/rule_service.py` stores the rule decision record with:
   - `rule_decision_id`
   - `project_id`
   - `decision_type`
   - `rule_version`
   - request input
   - response output
   - timestamp

### Actual Kogito Endpoints

FastAPI calls these generated Kogito decision-service paths when `KOGITO_RULE_SERVICE_URL` is configured:

| Product intent | Kogito endpoint |
|---|---|
| Campaign strategy | `POST /CampaignStrategy/EvaluateCampaignStrategy` |
| Campaign plan | `POST /CampaignPlan/EvaluateCampaignPlan` |
| Budget forecast | `POST /CampaignPlan/CalculateBudgetForecast` |
| Campaign timeline | `POST /CampaignPlan/RecommendCampaignTimeline` |
| Segment constraints | `POST /SegmentConstraints/CheckSegmentConstraints` |
| Claim risk | `POST /ClaimRisk/AssessClaimRisk` |

FastAPI exposes product/internal-tool friendly paths separately under `/internal/tools`.

### LocalRules Fallback Parity

When `KOGITO_RULE_SERVICE_URL` is unset, `api/app/services/local_rules.py` evaluates deterministic fallback rules in Python. The fallback is intended for local resilience and tests, but it must be reviewed for parity with the DMN assets before being treated as identical production behavior.

Known parity watch item:

- Campaign strategy confidence/approval logic should be checked against `CampaignStrategy.dmn`, especially where the DMN uses source-backed signal counts and unavailable signal counts.

### Important Runtime Defaults

The API currently injects a few fallback values when constructing DMN payloads:

| Value | Default |
|---|---|
| `source_backed_signal_count` | `3` |
| `total_budget_vnd` | `120000000` |
| `target_leads` | `240` |
| `campaign_days` | `30` |
| `launch_phase` | empty string |

These defaults matter because they influence the actual branch selected by the DMN logic.

## 1. `CampaignStrategy.dmn`

### Purpose

This DMN derives the high-level campaign strategy. It decides what the campaign should optimize for, which CTA to recommend, how confident the system should be, and which review constraints apply.

### Input Model

#### `brief`

| Field | Type | Meaning |
|---|---|---|
| `property_segment` | string | Property category such as apartments, land plots, or commercial real estate |
| `campaign_objective` | string | User-provided objective for the campaign |
| `buyer_profile` | string | Target audience description |
| `promotion_details` | string | Offer or promotion context, if any |

#### `insight_context`

| Field | Type | Meaning |
|---|---|---|
| `summary` | string | Short market-insight summary |
| `source_backed_signal_count` | number | Number of insight signals supported by sources |
| `unavailable_signal_count` | number | Number of signals that were not available or not verified |

### Decision Tables

#### Recommended Objective

| F | Input: `brief.campaign_objective` | Output: `Recommended Objective` | Description |
|---|---|---|---|
| 1 | `null`, `""` | `lead_generation` | Default objective when the brief does not provide one. |
| 2 | `-` | `brief.campaign_objective` | Pass through the provided objective unchanged. |

#### Recommended CTA

| F | Input: `brief.promotion_details` | Output: `Recommended CTA` | Description |
|---|---|---|---|
| 1 | `null`, `""` | `Register for consultation` | Use a consultative CTA when no promotion details are available. |
| 2 | `-` | `Book a consultation for offer details` | Use a stronger CTA when promotion details are present. |

#### KPI Expectation Band

| F | Input: `brief.campaign_objective` | Input: `insight_context.source_backed_signal_count` | Output: `KPI Expectation Band` | Description |
|---|---|---|---|---|
| 1 | `"awareness"` | `-` | `reach_engagement_medium` | Awareness campaigns bias toward reach and engagement outcomes. |
| 2 | `-` | `>= 3` | `lead_volume_medium` | Strong source-backed signal coverage supports a medium lead-volume expectation. |
| 3 | `-` | `-` | `lead_volume_cautious` | Conservative fallback when the evidence is weaker. |

#### Approval Required

| F | Input: `insight_context.unavailable_signal_count` | Output: `Approval Required` | Description |
|---|---|---|---|
| 1 | `> 0` | `true` | Missing signals require human review before downstream use. |
| 2 | `-` | `false` | No missing signals, so approval is not forced by this rule. |

#### Constraint Profile

| F | Input: `brief.property_segment` | Output: `Constraint Profile` | Description |
|---|---|---|---|
| 1 | `"commercial_real_estate"` | `commercial` | Commercial real estate gets commercial-specific guardrails. |
| 2 | `"land_plots"` | `land` | Land plots get land-specific guardrails. |
| 3 | `-` | `default` | Default fallback for all other segments. |

#### Segment Constraints Notes

| F | Input: `Constraint Profile` | Output: `constraint_1` | Output: `constraint_2` | Output: `constraint_3` | Description |
|---|---|---|---|---|---|
| 1 | `commercial` | `Avoid guaranteed investment-return claims.` | `Use verified project facts for legal, price, handover, and financing claims.` | `Avoid implying guaranteed tenant demand or rental yield.` | Guardrails for commercial property marketing copy. |
| 2 | `land` | `Avoid guaranteed investment-return claims.` | `Use verified project facts for legal, price, handover, and financing claims.` | `Highlight planning/legal clarity only when source-backed.` | Guardrails for land plot marketing copy. |
| 3 | `default` | `Avoid guaranteed investment-return claims.` | `Use verified project facts for legal, price, handover, and financing claims.` | `null` | Generic fallback guardrails. |

#### Rationale Notes

| F | Input: `Recommended Objective` | Input: `Approval Required` | Output: `note_1` | Output: `note_2` | Output: `note_3` | Description |
|---|---|---|---|---|---|---|
| 1 | `"awareness"` | `-` | `Objective emphasizes awareness and reach outcomes.` | `CTA remains consultative to fit real estate discovery behavior.` | `Buyer profile and insight availability influence planning confidence.` | Rationale for awareness-oriented strategy. |
| 2 | `-` | `true` | `Objective follows provided campaign intent when present.` | `CTA prioritizes consultative lead capture for real estate campaigns.` | `Missing insight signals increase review requirements before downstream use.` | Rationale when review is forced by unavailable signals. |
| 3 | `-` | `-` | `Objective follows provided campaign intent when present.` | `CTA prioritizes consultative lead capture for real estate campaigns.` | `Buyer profile and insight availability influence planning confidence.` | Default rationale fallback. |

#### Planning Assumptions

| F | Input: `Approval Required` | Output: `assumption_1` | Output: `assumption_2` | Description |
|---|---|---|---|---|
| 1 | `true` | `Strategy recommendations are intended to guide downstream planning and copy generation.` | `Missing insight signals may require human review before draft approval.` | Review-focused planning assumptions. |
| 2 | `-` | `Strategy recommendations are intended to guide downstream planning and copy generation.` | `Human review is still required before generated content is treated as final.` | Default planning assumptions. |

### Output Model

| Field | Type | Meaning |
|---|---|---|
| `rule_version` | string | Version label for the strategy rule set |
| `recommended_objective` | string | Final objective recommendation |
| `recommended_cta` | string | Final CTA recommendation |
| `kpi_expectation_band` | string | KPI band label |
| `approval_required` | boolean | Whether review is required before downstream use |
| `segment_constraints` | string[] | Constraint notes for the selected segment |
| `rationale_notes` | string[] | Short explanation notes for the decision |
| `planning_assumptions` | string[] | Assumption notes for downstream planning |

### What It Actually Does

This DMN does not calculate a complex strategy model. It mainly:

- normalizes the requested objective,
- picks a CTA based on promotion availability,
- maps limited insight confidence into a KPI band,
- flags missing signals for review,
- returns segment-specific guardrails.

## 2. `CampaignPlan.dmn`

### Purpose

This DMN converts the campaign brief and planning constraints into planning ranges. It produces budget bands, KPI forecast bands, a recommended campaign duration, cadence guidance, and a confidence label.

### Input Model

#### `brief`

| Field | Type | Meaning |
|---|---|---|
| `property_segment` | string | Property category |
| `campaign_objective` | string | Objective used for planning context |

#### `planning_constraints`

| Field | Type | Meaning |
|---|---|---|
| `total_budget_vnd` | number | Total campaign budget |
| `target_leads` | number | Lead target |
| `campaign_days` | number | Planned duration in days |
| `launch_phase` | string | Launch phase label such as `launch` |

#### `insight_context`

| Field | Type | Meaning |
|---|---|---|
| `summary` | string | Insight summary |
| `source_backed_signal_count` | number | Count of source-backed signals |
| `unavailable_inputs` | string[] | Inputs that are unavailable or unverified |

### Decision Logic

This DMN is mostly a literal-expression calculation, not a table-driven branching model.

### Planning Formulae

| Output | Formula |
|---|---|
| `budget_band.min` | `total_budget_vnd * 0.85` |
| `budget_band.max` | `total_budget_vnd * 1.15` |
| `daily_budget_band.min` | `(total_budget_vnd / campaign_days) * 0.85` |
| `daily_budget_band.max` | `(total_budget_vnd / campaign_days) * 1.15` |
| `kpi_forecast_band.leads.min` | `target_leads * 0.8` |
| `kpi_forecast_band.leads.max` | `target_leads * 1.2` |
| `kpi_forecast_band.cpl.min` | `(total_budget_vnd / target_leads) * 0.85` |
| `kpi_forecast_band.cpl.max` | `(total_budget_vnd / target_leads) * 1.15` |
| `kpi_forecast_band.clicks.min` | `target_leads * 12 * 0.8` |
| `kpi_forecast_band.clicks.max` | `target_leads * 12 * 1.2` |
| `kpi_forecast_band.reach.min` | `target_leads * 180 * 0.8` |
| `kpi_forecast_band.reach.max` | `target_leads * 180 * 1.2` |

### Cadence Rules

| Condition | `posts_per_week` |
|---|---|
| `property_segment = commercial_real_estate` | `3` |
| `launch_phase = launch` | `5` |
| Otherwise | `4` |

Additional fixed cadence values:

| Field | Value |
|---|---|
| `creative_variants_per_week` | `3` |
| `review_checkpoint_days` | `[7, 14, 21]` |

### Confidence and Approval Rules

| F | Input: `insight_context.unavailable_inputs` | Input: `insight_context.source_backed_signal_count` | Output: `confidence_level` | Output: `approval_required` | Description |
|---|---|---|---|---|---|
| 1 | not empty | `-` | `low` | `true` | Missing inputs lower confidence and force approval. |
| 2 | empty | `>= 3` | `medium` | `false` | Enough source-backed signals produce medium confidence. |
| 3 | empty | `-` | `cautious` | `false` | Conservative fallback when signal coverage is weaker. |

### Output Model

| Field | Type | Meaning |
|---|---|---|
| `rule_version` | string | Rule-set version label |
| `formula_version` | string | Formula version label |
| `budget_band` | object | Budget range with min/max/unit |
| `daily_budget_band` | object | Daily budget range with min/max/unit |
| `kpi_forecast_band` | object | KPI range object for leads, CPL, clicks, reach |
| `recommended_duration_days` | number | Duration recommendation |
| `content_cadence` | object | Posts per week, variants, and review checkpoints |
| `confidence_level` | string | Planning confidence label |
| `unavailable_inputs` | string[] | Inputs that could not be confirmed |
| `planning_assumptions` | string[] | Fixed planning assumptions |
| `estimate_disclaimer` | string | Warning that results are estimates only |
| `approval_required` | boolean | Whether human approval is required |

### What It Actually Does

This DMN does not optimize media spend or predict real campaign performance. It only:

- converts a budget into conservative bands,
- transforms lead targets into rough KPI ranges,
- sets a simple weekly content cadence,
- lowers confidence when inputs are missing,
- marks the plan as an estimate, not a guarantee.

## 3. `ClaimRisk.dmn`

### Purpose

This DMN scans draft text for risky real-estate claims and returns structured risk flags.

### Input Model

#### `draft_text`

| Field | Type | Meaning |
|---|---|---|
| `draft_text` | string | Draft copy to inspect for risky claims |

#### `project_facts`

| Field | Type | Meaning |
|---|---|---|
| `handover_status` | string | Current handover status from project facts |
| `ownership_status` | string | Ownership status from project facts |

### Decision Tables

#### Discount Risk

| F | Input: `draft_text` | Output: `risk_flag` | Description |
|---|---|---|---|
| 1 | contains `discount`, `% off`, or `ưu đãi` | `{ category: "discount", severity: "medium", reason: "Discount or promotion claim needs offer verification.", suggested_review_note: "Verify promotion terms before approval." }` | Flag discount-related promotion language. |
| 2 | `-` | `null` | No discount-related trigger detected. |

#### Ownership Risk

| F | Input: `draft_text` | Output: `risk_flag` | Description |
|---|---|---|---|
| 1 | contains `ownership`, `instant ownership`, or `sổ` | `{ category: "ownership", severity: "high", reason: "Ownership/legal status claim needs factual support.", suggested_review_note: "Confirm legal and ownership documents before approval." }` | Flag ownership and legal-status claims. |
| 2 | `-` | `null` | No ownership-related trigger detected. |

#### Handover Risk

| F | Input: `draft_text` | Input: `project_facts.handover_status` | Output: `risk_flag` | Description |
|---|---|---|---|---|
| 1 | contains `handover` or `bàn giao` | `-` | `{ category: "handover_timing", severity: "medium", reason: "Handover timing claim needs project schedule support.", suggested_review_note: "Check official handover timeline." }` | Text mentions handover timing directly. |
| 2 | `-` | `"planned"` | `{ category: "handover_timing", severity: "medium", reason: "Handover timing claim needs project schedule support.", suggested_review_note: "Check official handover timeline." }` | Planned handover status also requires review. |
| 3 | `-` | `-` | `null` | No handover risk detected. |

#### Financing Risk

| F | Input: `draft_text` | Output: `risk_flag` | Description |
|---|---|---|---|
| 1 | contains `financing`, `loan`, or `vay` | `{ category: "financing", severity: "medium", reason: "Financing claim needs lender/program verification.", suggested_review_note: "Verify financing terms." }` | Flag financing-related claims. |
| 2 | `-` | `null` | No financing risk detected. |

#### Rental Yield Risk

| F | Input: `draft_text` | Output: `risk_flag` | Description |
|---|---|---|---|
| 1 | contains `rental yield`, `yield`, or `cho thuê` | `{ category: "rental_yield", severity: "high", reason: "Rental yield claim can imply investment performance.", suggested_review_note: "Remove guarantee language or add verified basis." }` | Flag rental-yield or investment-performance language. |
| 2 | `-` | `null` | No rental-yield risk detected. |

#### Investment Potential Risk

| F | Input: `draft_text` | Output: `risk_flag` | Description |
|---|---|---|---|
| 1 | contains `guaranteed`, `cam kết`, or `profit` | `{ category: "investment_potential", severity: "high", reason: "Guaranteed return or profit claim is risk-sensitive.", suggested_review_note: "Avoid guaranteed investment performance claims." }` | Flag guaranteed-return or profit claims. |
| 2 | `-` | `null` | No investment-potential risk detected. |

#### Combined Risk Flags

| F | Input: individual risk flags | Output: `RiskFlags` | Description |
|---|---|---|---|
| 1 | At least one non-null flag exists | A list of all non-null risk flags | Collect every triggered risk flag. |
| 2 | All flags are null | Empty list | No risks detected. |

#### Approval Requirement

| F | Input: `count(RiskFlags)` | Output: `Approval Required` | Description |
|---|---|---|---|
| 1 | `> 0` | `true` | Any risk flag forces approval. |
| 2 | `-` | `false` | No risk flags means no forced approval from this rule. |

### Output Model

| Field | Type | Meaning |
|---|---|---|
| `rule_version` | string | Version label for claim-risk rules |
| `risk_flags` | array of objects | List of detected risk flags |
| `approval_required` | boolean | Whether the draft needs human approval |

### What It Actually Does

This DMN is a keyword-based safety gate. It does not understand semantics deeply. It:

- searches for sensitive phrases,
- creates standardized risk objects,
- requires review whenever at least one risk is found.

## 4. `SegmentConstraints.dmn`

### Purpose

This DMN returns constraint notes for a specific property segment and draft format.

### Input Model

#### `property_segment`

| Field | Type | Meaning |
|---|---|---|
| `property_segment` | string | Segment such as commercial_real_estate or land_plots |

#### `draft_context`

| Field | Type | Meaning |
|---|---|---|
| `format_type` | string | Draft format such as `promotion_offer` |

### Decision Tables

#### Constraint Profile

| F | Input: `property_segment` | Input: `draft_context.format_type` | Output: `Constraint Profile` | Description |
|---|---|---|---|---|
| 1 | `"commercial_real_estate"` | `-` | `commercial` | Commercial property profile. |
| 2 | `"land_plots"` | `-` | `land` | Land plot profile. |
| 3 | `-` | `"promotion_offer"` | `promotion_offer` | Promotion-offer format profile. |
| 4 | `-` | `-` | `default` | Fallback profile for all other cases. |

#### Constraint Notes

| F | Input: `Constraint Profile` | Output: `constraint_1` | Output: `constraint_2` | Output: `constraint_3` | Description |
|---|---|---|---|---|---|
| 1 | `commercial` | `Avoid guaranteed investment-return claims.` | `Use verified project facts for legal, price, handover, and financing claims.` | `Avoid implying guaranteed tenant demand or rental yield.` | Commercial guardrails. |
| 2 | `land` | `Avoid guaranteed investment-return claims.` | `Use verified project facts for legal, price, handover, and financing claims.` | `Highlight planning/legal clarity only when source-backed.` | Land guardrails. |
| 3 | `promotion_offer` | `Avoid guaranteed investment-return claims.` | `Use verified project facts for legal, price, handover, and financing claims.` | `Verify promotion terms, dates, and eligibility before publishing.` | Promotion-offer guardrails. |
| 4 | `default` | `Avoid guaranteed investment-return claims.` | `Use verified project facts for legal, price, handover, and financing claims.` | `null` | Generic fallback guardrails. |

### Output Model

| Field | Type | Meaning |
|---|---|---|
| `rule_version` | string | Version label for segment-constraint rules |
| `segment_constraints` | string[] | Constraint notes to apply in downstream generation or review |

### What It Actually Does

This DMN is a content guardrail helper. It does not generate copy. It only returns segment- and format-specific instructions to keep downstream drafting within safe marketing boundaries.

## Relationship Between the DMNs

The four DMN files form a layered rule system:

| Layer | Rule File | Role |
|---|---|---|
| Strategy | `CampaignStrategy.dmn` | Decide what the campaign should aim for |
| Planning | `CampaignPlan.dmn` | Turn brief + constraints into estimated bands |
| Safety | `ClaimRisk.dmn` | Detect risky claims in draft text |
| Segment guardrails | `SegmentConstraints.dmn` | Provide segment- and format-specific constraints |

## Practical Behavior Summary

In practice, the rule system does the following:

1. Normalizes missing strategy inputs into defaults.
2. Converts planning inputs into estimate bands using fixed multipliers.
3. Flags sensitive language that needs review.
4. Returns constraint notes based on segment and draft format.
5. Persists every evaluation as a traceable decision record.

## Key Limits

- The rules are deterministic and intentionally simple.
- They do not learn from past campaigns.
- They do not infer market truth from search results.
- They do not replace human review.
- They do not calculate true performance forecasts.

## Source Files

- [`rules-service/src/main/resources/CampaignStrategy.dmn`](../rules-service/src/main/resources/CampaignStrategy.dmn)
- [`rules-service/src/main/resources/CampaignPlan.dmn`](../rules-service/src/main/resources/CampaignPlan.dmn)
- [`rules-service/src/main/resources/ClaimRisk.dmn`](../rules-service/src/main/resources/ClaimRisk.dmn)
- [`rules-service/src/main/resources/SegmentConstraints.dmn`](../rules-service/src/main/resources/SegmentConstraints.dmn)
- [`api/app/models/rules.py`](../api/app/models/rules.py)
- [`api/app/services/kogito_rule_client.py`](../api/app/services/kogito_rule_client.py)
- [`api/app/services/rule_service.py`](../api/app/services/rule_service.py)
