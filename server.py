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
    name="bigquery-kitsch",
    version="2.0.0",
    instructions=(
        "Mock BigQuery analytics platform for Kitsch, a beauty and lifestyle brand. "
        "Query inventory levels and risk, retail account performance, point-of-sale data, "
        "buyer meeting prep, revenue summaries, customer segments, channel ROI, and insight reports. "
        "Key use cases: Inventory Risk Report, Retail Account Performance & POS Analysis, "
        "and Pre-meeting Retail Buyer Presentations."
    ),
)


# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------

@mcp.tool()
def get_products(
    category: Optional[str] = Field(default=None, description="Filter by category, e.g. 'Haircare', 'Sleep & Satin', 'Hair Accessories', 'Styling', 'Gift Sets'"),
    sku: Optional[str] = Field(default=None, description="Filter by SKU (exact or partial match), e.g. 'KT-CURL-HEATLESS'"),
    hero_only: Optional[bool] = Field(default=None, description="If true, return only hero/flagship products"),
) -> list[dict]:
    """Return Kitsch product catalog. Filter by category, SKU, or hero product flag."""
    results = _db["products"]
    if category:
        results = [r for r in results if _match(r, "category", category)]
    if sku:
        results = [r for r in results if sku.lower() in r["sku"].lower()]
    if hero_only is True:
        results = [r for r in results if r.get("hero_product")]
    return results


# ---------------------------------------------------------------------------
# Inventory
# ---------------------------------------------------------------------------

@mcp.tool()
def get_inventory(
    sku: Optional[str] = Field(default=None, description="Filter by SKU (partial match), e.g. 'KT-CURL-HEATLESS'"),
    status: Optional[str] = Field(default=None, description="Filter by inventory status: 'critical' | 'at_risk' | 'healthy'"),
) -> list[dict]:
    """Return inventory levels by SKU including weeks of supply, reorder point, and status.
    Use status='critical' or status='at_risk' to identify SKUs needing immediate action."""
    results = _db["inventory"]
    if sku:
        results = [r for r in results if sku.lower() in r["sku"].lower()]
    if status:
        results = [r for r in results if _match(r, "status", status)]
    return results


@mcp.tool()
def get_inventory_risk_report() -> dict:
    """Return the full Inventory Risk Report including critical SKUs, at-risk SKUs,
    recommended actions, and summary. Use this for the Inventory Risk Report deliverable."""
    return _db["inventory_risk_report"]


# ---------------------------------------------------------------------------
# Retail Accounts
# ---------------------------------------------------------------------------

@mcp.tool()
def get_retail_accounts(
    account_name: Optional[str] = Field(default=None, description="Filter by account name (partial match), e.g. 'Target', 'Ulta', 'Walmart'"),
    channel_type: Optional[str] = Field(default=None, description="Filter by channel type: 'mass_market' | 'specialty_beauty' | 'drug_store' | 'marketplace' | 'direct_to_consumer'"),
    partnership_tier: Optional[str] = Field(default=None, description="Filter by tier: 'strategic' | 'core' | 'growth' | 'owned'"),
    underperforming_only: Optional[bool] = Field(default=None, description="If true, return only accounts below plan (ytd_gmv_vs_plan_pct < 1.0)"),
) -> list[dict]:
    """Return retail account profiles including GMV, fill rate, in-stock rate, buyer contact,
    and performance vs plan. Use this for Retail Account Performance analysis."""
    results = _db["retail_accounts"]
    if account_name:
        results = [r for r in results if _match(r, "account_name", account_name)]
    if channel_type:
        results = [r for r in results if _match(r, "channel_type", channel_type)]
    if partnership_tier:
        results = [r for r in results if _match(r, "partnership_tier", partnership_tier)]
    if underperforming_only:
        results = [r for r in results if r.get("ytd_gmv_vs_plan_pct", 1.0) < 1.0]
    return results


@mcp.tool()
def get_retail_performance_report() -> dict:
    """Return the full Retail Account Performance Report including top performers,
    underperformers, POS highlights, and strategic recommendations.
    Use this for the Retail Account Performance & POS Analysis deliverable."""
    return _db["retail_performance_report"]


# ---------------------------------------------------------------------------
# POS Data
# ---------------------------------------------------------------------------

@mcp.tool()
def get_pos_data(
    account_name: Optional[str] = Field(default=None, description="Filter by retail account name (partial match), e.g. 'Target', 'Ulta'"),
    sku: Optional[str] = Field(default=None, description="Filter by SKU (partial match)"),
    period: Optional[str] = Field(default=None, description="Filter by period (partial match), e.g. '2026-09'"),
    low_sell_through: Optional[bool] = Field(default=None, description="If true, return only records with sell_through_rate below 0.70"),
) -> list[dict]:
    """Return point-of-sale data by retail account and SKU including units sold, revenue,
    sell-through rate, in-stock rate, returns, and velocity rank."""
    results = _db["pos_data"]
    if account_name:
        results = [r for r in results if _match(r, "account_name", account_name)]
    if sku:
        results = [r for r in results if sku.lower() in r["sku"].lower()]
    if period:
        results = [r for r in results if _match(r, "period", period)]
    if low_sell_through:
        results = [r for r in results if r.get("sell_through_rate", 1.0) < 0.70]
    return results


# ---------------------------------------------------------------------------
# Buyer Meeting Prep
# ---------------------------------------------------------------------------

@mcp.tool()
def get_buyer_meeting_prep(
    account_name: Optional[str] = Field(default=None, description="Filter by account name (partial match), e.g. 'Target', 'Ulta', 'Walmart'"),
    meeting_id: Optional[str] = Field(default=None, description="Filter by meeting ID, e.g. 'mtg001'"),
) -> list[dict]:
    """Return buyer meeting preparation packages including business snapshot, talking points,
    expansion opportunities, risks to address, competitive context, and asks from the buyer.
    Use this for Pre-meeting Retail Buyer Presentation deliverables."""
    results = _db["buyer_meeting_prep"]
    if account_name:
        results = [r for r in results if _match(r, "account", account_name)]
    if meeting_id:
        results = [r for r in results if r["meeting_id"].lower() == meeting_id.lower()]
    return results


# ---------------------------------------------------------------------------
# Campaign Performance
# ---------------------------------------------------------------------------

@mcp.tool()
def get_campaign_performance(
    campaign_id: Optional[str] = Field(default=None, description="Filter by campaign ID, e.g. 'cp001'"),
    channel: Optional[str] = Field(default=None, description="Filter by channel: 'paid_social' | 'multi_channel'"),
    platform: Optional[str] = Field(default=None, description="Filter by platform (partial match), e.g. 'TikTok', 'Email', 'Pinterest'"),
    hero_sku: Optional[str] = Field(default=None, description="Filter by hero SKU (partial match), e.g. 'KT-CURL-HEATLESS'"),
) -> list[dict]:
    """Return campaign performance records including spend, impressions, clicks, CTR,
    conversions, CVR, revenue attributed, ROAS, CPA, new customer %, AOV, top creative,
    and strategic notes. Use for campaign reporting and channel analysis."""
    results = _db["campaign_performance"]
    if campaign_id:
        results = [r for r in results if r["campaign_id"].lower() == campaign_id.lower()]
    if channel:
        results = [r for r in results if _match(r, "channel", channel)]
    if platform:
        results = [r for r in results if _match(r, "platform", platform)]
    if hero_sku:
        results = [r for r in results if hero_sku.lower() in str(r.get("hero_sku", "")).lower()]
    return results


@mcp.tool()
def get_campaign_insights() -> dict:
    """Return the aggregated campaign insights report including blended ROAS, total spend,
    total attributed revenue, top-performing campaigns, key insights, and strategic recommendations
    across all Kitsch marketing campaigns. Use for executive summaries and campaign planning."""
    return _db["campaign_insights"]


# ---------------------------------------------------------------------------
# Revenue Summary
# ---------------------------------------------------------------------------

@mcp.tool()
def get_revenue_summary(
    period: Optional[str] = Field(default=None, description="Filter by period, e.g. '2026-09' (partial match)"),
) -> list[dict]:
    """Return monthly revenue summary by channel including DTC, retail, and Amazon breakdowns,
    units sold, AOV, MoM and YoY growth rates."""
    results = _db["revenue_summary"]
    if period:
        results = [r for r in results if _match(r, "period", period)]
    return results


# ---------------------------------------------------------------------------
# Channel ROI
# ---------------------------------------------------------------------------

@mcp.tool()
def get_channel_roi(
    channel: Optional[str] = Field(default=None, description="Filter by channel name (partial match), e.g. 'Amazon', 'DTC', 'Ulta'"),
) -> list[dict]:
    """Return channel-level ROI, ROAS, CAC, and contribution margin data across
    DTC, Amazon, and all retail partners."""
    results = _db["channel_roi"]
    if channel:
        results = [r for r in results if _match(r, "channel", channel)]
    return results


# ---------------------------------------------------------------------------
# Customer Segments
# ---------------------------------------------------------------------------

@mcp.tool()
def get_customer_segments(
    segment_name: Optional[str] = Field(default=None, description="Filter by segment name (partial match), e.g. 'Satin Loyalists', 'TikTok Converts', 'Eco Shoppers'"),
) -> list[dict]:
    """Return Kitsch customer segments including size, AOV, CLV, churn rate, and primary channel.
    Segments: Satin Loyalists, TikTok Converts, Eco Shoppers, Gift Buyers, Subscription Members."""
    results = _db["customer_segments"]
    if segment_name:
        results = [r for r in results if _match(r, "segment_name", segment_name)]
    return results


# ---------------------------------------------------------------------------
# Anomaly Detection
# ---------------------------------------------------------------------------

@mcp.tool()
def detect_anomalies(
    dataset: Optional[str] = Field(default=None, description="Filter by dataset name (partial match), e.g. 'inventory_ops', 'retail_pos'"),
    severity: Optional[str] = Field(default=None, description="Filter by severity: 'high' | 'medium' | 'low'"),
    metric: Optional[str] = Field(default=None, description="Filter by metric name (partial match), e.g. 'in_stock_rate', 'weeks_of_supply'"),
) -> list[dict]:
    """Return detected data anomalies across inventory, POS, and revenue datasets.
    Use to surface risks and unexpected signals."""
    results = _db["anomalies"]
    if dataset:
        results = [r for r in results if _match(r, "dataset", dataset)]
    if severity:
        results = [r for r in results if _match(r, "severity", severity)]
    if metric:
        results = [r for r in results if _match(r, "metric", metric)]
    return results


# ---------------------------------------------------------------------------
# Insight Reports
# ---------------------------------------------------------------------------

@mcp.tool()
def generate_insight_report(
    topic: Optional[str] = Field(default=None, description="Filter by topic (partial match): 'Inventory Risk' | 'Retail Account Performance' | 'Pre-Meeting Buyer Preparation'"),
    account: Optional[str] = Field(default=None, description="Filter buyer prep reports by account name, e.g. 'Target'"),
) -> list[dict]:
    """Return pre-generated insight reports. Topics available:
    - 'Inventory Risk': critical SKU analysis and action plan
    - 'Retail Account Performance': account-level POS and performance summary
    - 'Pre-Meeting Buyer Preparation': meeting-specific talking points and asks (filter by account)
    Returns all reports if no match found."""
    results = _db["insight_reports"]
    if topic:
        matched = [r for r in results if _match(r, "topic", topic)]
        results = matched if matched else results
    if account:
        results = [r for r in results if _match(r, "topic", account) or _match(r, "summary", account)]
    return results


# ---------------------------------------------------------------------------
# Datasets & Schemas
# ---------------------------------------------------------------------------

@mcp.tool()
def list_datasets(
    region: Optional[str] = Field(default=None, description="Filter by region, e.g. 'US'"),
) -> list[dict]:
    """List available Kitsch BigQuery datasets."""
    results = _db["datasets"]
    if region:
        results = [r for r in results if _match(r, "region", region)]
    return results


@mcp.tool()
def get_table_schema(
    dataset: Optional[str] = Field(default=None, description="Filter by dataset name (partial match)"),
    table: Optional[str] = Field(default=None, description="Filter by table name (partial match)"),
) -> list[dict]:
    """Return table schema definitions for Kitsch BigQuery tables."""
    results = _db["table_schemas"]
    if dataset:
        results = [r for r in results if _match(r, "dataset", dataset)]
    if table:
        results = [r for r in results if _match(r, "table", table)]
    return results


# ---------------------------------------------------------------------------
# Query History & Exports
# ---------------------------------------------------------------------------

@mcp.tool()
def run_query(
    sql: str = Field(description="SQL query to simulate. Used as keyword search against query history."),
    dataset: Optional[str] = Field(default=None, description="Target dataset name (informational)"),
) -> list[dict]:
    """Simulate running a BigQuery SQL query against Kitsch data.
    Performs keyword search across query history and returns matching records."""
    results = _db["query_history"]
    keywords = [w for w in sql.lower().split() if len(w) > 3]
    if keywords:
        matched = [r for r in results if any(kw in r["sql"].lower() for kw in keywords)]
        if matched:
            return matched
    return results


@mcp.tool()
def export_query_results(
    query_id: Optional[str] = Field(default=None, description="Filter by query ID, e.g. 'qr01'"),
    destination: Optional[str] = Field(default=None, description="Filter by destination (partial match), e.g. 'google_sheets', 'csv_download'"),
) -> list[dict]:
    """Return export job records for completed query exports."""
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
