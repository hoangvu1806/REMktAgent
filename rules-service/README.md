# rules-service

Quarkus/Kogito decision service for deterministic marketing rules.

## Stack

- JDK 17
- Quarkus 2.16.10.Final
- Kogito 1.44.0.Final
- DMN decision services

## Current DMN Assets

| File | Decision service | FastAPI adapter method |
|---|---|---|
| `CampaignStrategy.dmn` | `EvaluateCampaignStrategy` | `campaign_strategy()` |
| `CampaignPlan.dmn` | `EvaluateCampaignPlan` | `campaign_plan()` |
| `CampaignPlan.dmn` | `CalculateBudgetForecast` | `budget_forecast()` |
| `CampaignPlan.dmn` | `RecommendCampaignTimeline` | `campaign_timeline()` |
| `SegmentConstraints.dmn` | `CheckSegmentConstraints` | `segment_constraints()` |
| `ClaimRisk.dmn` | `AssessClaimRisk` | `claim_risk()` |

Generated Kogito endpoints are consumed by `api/app/services/kogito_rule_client.py`:

- `POST /CampaignStrategy/EvaluateCampaignStrategy`
- `POST /CampaignPlan/EvaluateCampaignPlan`
- `POST /CampaignPlan/CalculateBudgetForecast`
- `POST /CampaignPlan/RecommendCampaignTimeline`
- `POST /SegmentConstraints/CheckSegmentConstraints`
- `POST /ClaimRisk/AssessClaimRisk`

The browser does not call this service directly. FastAPI wraps rule calls as Product Server internal tools and persists `RuleDecisionRecord` rows.

## Local Run

```powershell
mvn quarkus:dev
```

Default local URL:

```txt
http://localhost:8080
```

Quarkus Dev UI:

```txt
http://localhost:8080/q/dev/
```

## Build

```powershell
mvn package
```

Runnable output:

```powershell
java -jar target\quarkus-app\quarkus-run.jar
```

## Validation

```powershell
mvn test
```

## Runtime Fallback

If `KOGITO_RULE_SERVICE_URL` is not configured in the FastAPI Product Server, `KogitoRuleClient` uses `LocalRules` in Python instead of this Quarkus service. That fallback is intentional for local MVP resilience and tests.
