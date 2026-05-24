from uuid import uuid4

from app.models.insight import InsightLabel, MarketSignal


USER_CONTEXT_SOURCE = {
    "source_id": "user_provided_project_context",
    "source_title": "User-provided project context",
    "source_url": "internal:user-context",
}


class InsightSignalBuilder:
    def tool_signal(
        self,
        *,
        signal_type: str,
        label: str,
        summary: str,
        source_id: str | None = None,
        source_title: str | None = None,
        source_url: str | None = None,
        confidence: str = "medium",
    ) -> dict[str, object]:
        return {
            "signal_type": signal_type,
            "label": label,
            "summary": summary,
            "source_id": source_id,
            "source_title": source_title,
            "source_url": source_url,
            "confidence": confidence,
        }

    def user_context_tool_signal(
        self, signal_type: str, summary: str
    ) -> dict[str, object]:
        return self.tool_signal(
            signal_type=signal_type,
            label="user_provided",
            summary=summary,
            confidence="medium",
            **USER_CONTEXT_SOURCE,
        )

    def market_signal(
        self,
        *,
        signal_type: str,
        label: InsightLabel,
        summary: str,
        source_id: str | None = None,
        source_title: str | None = None,
        source_url: str | None = None,
        confidence: str = "medium",
    ) -> MarketSignal:
        return MarketSignal(
            signal_id=str(uuid4()),
            signal_type=signal_type,
            label=label,
            summary=summary,
            source_id=source_id,
            source_title=source_title,
            source_url=source_url,
            confidence=confidence,
        )

    def user_context_market_signal(
        self, signal_type: str, summary: str
    ) -> MarketSignal:
        return self.market_signal(
            signal_type=signal_type,
            label=InsightLabel.user_provided,
            summary=summary,
            confidence="medium",
            **USER_CONTEXT_SOURCE,
        )
