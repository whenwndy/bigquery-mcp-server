import json
import os
from pathlib import Path
from typing import Optional
from fastmcp import FastMCP
from pydantic import Field

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

_DATA_PATH = Path(__file__).parent / "data" / "bigquery.json"
_db: dict = json.loads(_DATA_PATH.read_text())


def _match(record: dict, field: str, value: str) -> bool:
    """Case-insensitive substring match on a field."""
    return value.lower() in str(record.get(field, "")).lower()


# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------

mcp = FastMCP(
    name="bigquery-mock",
    version="1.0.0",
    instructions=(
        "Mock BigQuery analytics platform for H/L Partners. Query campaign performance, "
        "customer segments, CLV, revenue, funnel analysis, channel ROI, anomalies, and insight reports."
    ),
)

# ---------------------------------------------------------------------------
# Query History
# ---------------------------------------------------------------------------

@mcp.tool()
def run_query(
    sql: str = Field(description="SQL query string to simulate executing (mock: used as keyword search against query history)"),
    dataset: Optional[str] = Field(default=None, description="Target dataset name (optional, informational)"),
) -> list[dict]:
    """Simulate running a BigQuery SQL query. This is a mock — it performs a keyword search
    across the sql field in query_history and returns matching records. If no keywords match,
    all query_history records are returned."""
    results = _db["query_history"]
    keywords = [w for w in sql.lower().split() if len(w) > 3]
    if keywords:
        matched = [r for r in results if any(kw in r["sql"].lower() for kw in keywords)]
        if matched:
            return matched
    return results


# ---------------------------------------------------------------------------
# Datasets
# ---------------------------------------------------------------------------

@mcp.tool()
def list_datasets(
    region: Optional[str] = Field(default=None, description="Filter by region, e.g. US"),
) -> list[dict]:
    """List available BigQuery datasets. Optionally filter by region."""
    results = _db["datasets"]
    if region:
        results = [r for r in results if _match(r, "region", region)]
    return results


# ---------------------------------------------------------------------------
# Table Schemas
# ---------------------------------------------------------------------------

@mcp.tool()
def get_table_schema(
    dataset: Optional[str] = Field(default=None, description="Filter by dataset name (partial match)"),
    table: Optional[str] = Field(default=None, description="Filter by table name (partial match)"),
) -> list[dict]:
    """Return table schema definitions. Optionally filter by dataset or table name."""
    results = _db["table_schemas"]
    if dataset:
        results = [r for r in results if _match(r, "dataset", dataset)]
    if table:
        results = [r for r in results if _match(r, "table", table)]
    return results


# ---------------------------------------------------------------------------
# Campaign Performance
# ---------------------------------------------------------------------------

@mcp.tool()
def get_campaign_performance(
    campaign_id: Optional[str] = Field(default=None, description="Filter by campaign ID, e.g. cp101"),
    channel: Optional[str] = Field(default=None, description="Filter by channel: paid_search | social | email | organic"),
    period: Optional[str] = Field(default=None, description="Filter by period, e.g. 2026-04 (partial match)"),
) -> list[dict]:
    """Return campaign performance records. Optionally filter by campaign ID, channel, or period."""
    results = _db["campaign_performance"]
    if campaign_id:
        results = [r for r in results if r["campaign_id"].lower() == campaign_id.lower()]
    if channel:
        results = [r for r in results if _match(r, "channel", channel)]
    if period:
        results = [r for r in results if _match(r, "period", period)]
    return results


# ---------------------------------------------------------------------------
# Customer Segments
# ---------------------------------------------------------------------------

@mcp.tool()
def get_customer_segments(
    segment_name: Optional[str] = Field(default=None, description="Filter by segment name (partial match)"),
    primary_channel: Optional[str] = Field(default=None, description="Filter by primary channel (partial match)"),
) -> list[dict]:
    """Return customer segment records. Optionally filter by segment name or primary channel."""
    results = _db["customer_segments"]
    if segment_name:
        results = [r for r in results if _match(r, "segment_name", segment_name)]
    if primary_channel:
        results = [r for r in results if _match(r, "primary_channel", primary_channel)]
    return results


# ---------------------------------------------------------------------------
# Customer Lifetime Value
# ---------------------------------------------------------------------------

@mcp.tool()
def get_customer_lifetime_value(
    segment_id: Optional[str] = Field(default=None, description="Filter by segment ID, e.g. sg01"),
    cohort: Optional[str] = Field(default=None, description="Filter by cohort, e.g. 2024-Q1 (partial match)"),
) -> list[dict]:
    """Return customer lifetime value estimates. Optionally filter by segment ID or cohort."""
    results = _db["customer_lifetime_value"]
    if segment_id:
        results = [r for r in results if r["segment_id"].lower() == segment_id.lower()]
    if cohort:
        results = [r for r in results if _match(r, "cohort", cohort)]
    return results


# ---------------------------------------------------------------------------
# Revenue Summary
# ---------------------------------------------------------------------------

@mcp.tool()
def get_revenue_summary(
    period: Optional[str] = Field(default=None, description="Filter by period, e.g. 2026-04 (partial match)"),
) -> list[dict]:
    """Return monthly revenue summary records including MRR, ARR, and growth metrics. Optionally filter by period."""
    results = _db["revenue_summary"]
    if period:
        results = [r for r in results if _match(r, "period", period)]
    return results


# ---------------------------------------------------------------------------
# Funnel Analysis
# ---------------------------------------------------------------------------

@mcp.tool()
def get_funnel_analysis(
    stage: Optional[str] = Field(default=None, description="Filter by funnel stage name (partial match), e.g. Awareness"),
) -> list[dict]:
    """Return funnel analysis data by stage. Optionally filter by stage name."""
    results = _db["funnel_analysis"]
    if stage:
        results = [r for r in results if _match(r, "stage", stage)]
    return results


# ---------------------------------------------------------------------------
# Insight Reports
# ---------------------------------------------------------------------------

@mcp.tool()
def generate_insight_report(
    topic: Optional[str] = Field(default=None, description="Filter by report topic (partial match), e.g. Campaign Performance"),
) -> list[dict]:
    """Return insight reports. Optionally filter by topic (partial match). Returns all reports if no match found."""
    results = _db["insight_reports"]
    if topic:
        matched = [r for r in results if _match(r, "topic", topic)]
        return matched if matched else results
    return results


# ---------------------------------------------------------------------------
# Channel ROI
# ---------------------------------------------------------------------------

@mcp.tool()
def get_channel_roi(
    channel: Optional[str] = Field(default=None, description="Filter by channel name (partial match), e.g. email"),
) -> list[dict]:
    """Return channel ROI and attribution data. Optionally filter by channel name."""
    results = _db["channel_roi"]
    if channel:
        results = [r for r in results if _match(r, "channel", channel)]
    return results


# ---------------------------------------------------------------------------
# Anomaly Detection
# ---------------------------------------------------------------------------

@mcp.tool()
def detect_anomalies(
    dataset: Optional[str] = Field(default=None, description="Filter by dataset name (partial match)"),
    metric: Optional[str] = Field(default=None, description="Filter by metric name (partial match), e.g. spend_usd"),
    severity: Optional[str] = Field(default=None, description="Filter by severity: high | medium | low"),
) -> list[dict]:
    """Return detected anomalies. Optionally filter by dataset, metric, or severity."""
    results = _db["anomalies"]
    if dataset:
        results = [r for r in results if _match(r, "dataset", dataset)]
    if metric:
        results = [r for r in results if _match(r, "metric", metric)]
    if severity:
        results = [r for r in results if _match(r, "severity", severity)]
    return results


# ---------------------------------------------------------------------------
# Export Jobs
# ---------------------------------------------------------------------------

@mcp.tool()
def export_query_results(
    query_id: Optional[str] = Field(default=None, description="Filter by query ID, e.g. qr01"),
    destination: Optional[str] = Field(default=None, description="Filter by destination (partial match), e.g. google_sheets"),
) -> list[dict]:
    """Return export job records. Optionally filter by query ID or destination."""
    results = _db["export_jobs"]
    if query_id:
        results = [r for r in results if r["query_id"].lower() == query_id.lower()]
    if destination:
        results = [r for r in results if _match(r, "destination", destination)]
    return results


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
