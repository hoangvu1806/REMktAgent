from datetime import UTC, datetime
from uuid import uuid4

from app.models.insight import (
    InsightCollectionRequest,
    InsightLabel,
    InsightStatus,
    MarketInsightSnapshot,
    MarketSignal,
    UpdateAssumptionsRequest,
)
from app.models.project import Project
from app.services.insight_signals import InsightSignalBuilder
from app.services.project_service import ProjectService
from app.storage.insight_store import InsightStore


class InsightNotFoundError(Exception):
    pass


class InsightService:
    def __init__(
        self,
        *,
        store: InsightStore | None = None,
        project_service: ProjectService | None = None,
    ) -> None:
        self.store = store or InsightStore()
        self.project_service = project_service or ProjectService()
        self.signals = InsightSignalBuilder()

    def collect_snapshot(
        self, project_id: str, request: InsightCollectionRequest
    ) -> MarketInsightSnapshot:
        project = self.project_service.get_project(project_id)
        now = _utc_now()
        signals = self._collect_signals(project, request)
        unavailable: list[str] = []
        status = InsightStatus.ready if signals else InsightStatus.partial
        snapshot = MarketInsightSnapshot(
            snapshot_id=str(uuid4()),
            project_id=project.project_id,
            status=status,
            summary=self._summary(project, signals, unavailable),
            signals=signals,
            assumptions=[],
            unavailable_signals=unavailable,
            confirmed=False,
            created_at=now,
            updated_at=now,
        )
        return self.store.save_snapshot(snapshot)

    def list_snapshots(self, project_id: str) -> list[MarketInsightSnapshot]:
        self.project_service.get_project(project_id)
        return self.store.list_snapshots(project_id)

    def update_assumptions(
        self,
        project_id: str,
        snapshot_id: str,
        request: UpdateAssumptionsRequest,
    ) -> MarketInsightSnapshot:
        self.project_service.get_project(project_id)
        snapshot = self.store.get_snapshot(project_id, snapshot_id)
        if snapshot is None:
            raise InsightNotFoundError(snapshot_id)
        assumption_signals = [
            MarketSignal(
                signal_id=str(uuid4()),
                signal_type="assumption",
                label=InsightLabel.user_provided,
                summary=f"{item.question}: {item.answer}",
                source_id="user_provided_project_context",
                source_title="User-provided project context",
                source_url="internal:user-context",
                confidence="medium",
            )
            for item in request.assumptions
        ]
        snapshot.assumptions = request.assumptions
        snapshot.confirmed = request.confirmed
        snapshot.signals = [
            signal
            for signal in snapshot.signals
            if signal.signal_type != "assumption"
        ] + assumption_signals
        snapshot.updated_at = _utc_now()
        return self.store.save_snapshot(snapshot)

    def collect_project_facts(
        self,
        *,
        project_id: str,
        brief: dict[str, object],
        user_material_refs: list[str],
        official_project_url: str | None,
        resolve_external_content: bool = True,
    ) -> dict[str, object]:
        project_name = str(brief.get("project_name", project_id))
        signals = [
            self.signals.user_context_tool_signal(
                "project_fact", f"Project facts supplied for {project_name}."
            )
        ]
        if official_project_url:
            signals.append(
                self.signals.tool_signal(
                    signal_type="project_fact",
                    label="source_backed",
                    summary="Official project URL was provided for agent verification.",
                    source_id="official_project_website",
                    source_title="Official project or developer website",
                    source_url=official_project_url,
                    confidence="high",
                )
            )
        return {"signals": signals, "user_material_refs": user_material_refs}

    def collect_local_context(
        self,
        *,
        project_id: str,
        location: str,
        property_segment: str,
        approved_source_ids: list[str],
        resolve_external_content: bool = True,
    ) -> dict[str, object]:
        return {
            "signals": [
                self.signals.tool_signal(
                    signal_type="local_context",
                    label="unavailable",
                    summary=(
                        f"Google Search is still required to verify planning, infrastructure, "
                        f"transport, amenities, and location context for {location} "
                        f"and {property_segment} before insight confirmation."
                    ),
                    confidence="cautious",
                )
            ]
        }

    def collect_market_signals(
        self,
        *,
        project_id: str,
        questions: list[str],
        user_context: str | None,
        resolve_external_content: bool = True,
    ) -> dict[str, object]:
        signals = []
        for question in questions:
            signals.append(
                self.signals.tool_signal(
                    signal_type="market_signal",
                    label="unavailable",
                    summary=f"Google Search is still required for market question: {question}",
                    confidence="cautious",
                )
            )
        if user_context:
            signals.append(
                self.signals.user_context_tool_signal("market_signal", user_context)
            )
        return {"signals": signals}

    def collect_competitor_positioning(
        self,
        *,
        project_id: str,
        location: str,
        property_segment: str,
        price_range: str | None,
        approved_source_ids: list[str],
        resolve_external_content: bool = True,
    ) -> dict[str, object]:
        signals = [
            self.signals.tool_signal(
                signal_type="competitor_positioning",
                label="unavailable",
                summary=(
                    f"Google Search is still required to compare competitor "
                    f"positioning for {property_segment} in {location} before planning."
                ),
                confidence="cautious",
            )
        ]
        if price_range:
            signals.append(
                self.signals.user_context_tool_signal(
                    "competitor_positioning",
                    f"Competitor scan constrained to price range {price_range}.",
                )
            )
        return {"signals": signals}

    def _collect_signals(
        self, project: Project, request: InsightCollectionRequest
    ) -> list[MarketSignal]:
        signals = [
            self.signals.market_signal(
                signal_type="project_fact",
                label=InsightLabel.user_provided,
                summary=(
                    f"{project.project_name} is a {project.brief.property_segment.value} "
                    f"project in {project.brief.location}."
                ),
                source_id="user_provided_project_context",
                source_title="User-provided project context",
                source_url="internal:user-context",
                confidence="medium",
            )
        ]
        if request.user_context:
            signals.append(
                self.signals.user_context_market_signal(
                    "market_signal", request.user_context
                )
        )
        return signals

    def _summary(
        self,
        project: Project,
        signals: list[MarketSignal],
        unavailable: list[str],
    ) -> str:
        return (
            f"Collected {len(signals)} insight signals for {project.project_name}. "
            f"Unavailable signals: {len(unavailable)}."
        )


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
