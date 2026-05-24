"""
IntelliWealth – Mock LLM Provider
Template-based AI response generation for development and testing.

IMPORTANT: AI does NOT give investment advice.
AI ONLY explains portfolio state and risk factors.
"""

import logging
import time
from typing import Any, Dict

from app.providers.base import LLMProvider, LLMRequest, LLMResponse

logger = logging.getLogger("intelliwealth.ai.mock")


class MockProvider(LLMProvider):
    """
    Mock LLM provider using template-based response generation.
    Produces deterministic, high-quality analytical narratives
    without requiring any external API calls.
    """

    @property
    def provider_name(self) -> str:
        return "IntelliWealth Mock Provider"

    @property
    def model_id(self) -> str:
        return "mock-analyst-v1"

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate a mock analytical response based on prompt keywords."""
        start = time.perf_counter()

        content = self._route_prompt(request.prompt, request.metadata)

        latency = (time.perf_counter() - start) * 1000
        tokens = len(content.split())

        logger.info(
            "Mock generation: %d tokens in %.1fms",
            tokens, latency,
        )

        return LLMResponse(
            content=content,
            model=self.model_id,
            provider=self.provider_name,
            tokens_used=tokens,
            latency_ms=round(latency, 2),
            metadata={"mock": True},
        )

    async def health_check(self) -> Dict[str, Any]:
        return {
            "status": "healthy",
            "provider": self.provider_name,
            "model": self.model_id,
            "type": "mock",
        }

    # ================================================================
    # Response Generation
    # ================================================================

    def _route_prompt(self, prompt: str, metadata: Dict[str, Any]) -> str:
        """Route to the appropriate template based on request type."""
        request_type = metadata.get("request_type", "analyze")

        if request_type == "analyze":
            return self._generate_analysis(metadata)
        elif request_type == "risk_summary":
            return self._generate_risk_summary(metadata)
        elif request_type == "scenario_analysis":
            return self._generate_scenario(metadata)
        elif request_type == "explain_portfolio":
            return self._generate_explanation(metadata)
        else:
            return self._generate_analysis(metadata)

    def _generate_analysis(self, data: Dict[str, Any]) -> str:
        """Generate portfolio analysis narrative."""
        allocation = data.get("allocation", {})
        risk_level = data.get("risk_level", "MODERATE")
        total_value = data.get("total_value", 0)

        equity_pct = allocation.get("stocks", 0) + allocation.get("mutual_funds", 0)
        bond_pct = allocation.get("bonds", 0)
        gold_pct = allocation.get("gold", 0)
        crypto_pct = allocation.get("crypto", 0)
        cash_pct = allocation.get("cash", 0)

        sections = []

        # Portfolio composition
        sections.append(
            f"## Portfolio Analysis\n\n"
            f"The portfolio has a total estimated value of ${total_value:,.2f} "
            f"distributed across {len(allocation)} asset classes. "
            f"The current risk classification is **{risk_level}**."
        )

        # Equity analysis
        if equity_pct > 0:
            if equity_pct > 80:
                sections.append(
                    f"### Equity Concentration\n\n"
                    f"Equity instruments represent **{equity_pct:.1f}%** of the portfolio. "
                    f"This level of equity concentration exceeds the 80% threshold, "
                    f"indicating the portfolio is **heavily dependent on equity market performance**. "
                    f"Historical data shows that portfolios with equity exposure above 80% "
                    f"experience significantly higher drawdowns during market corrections."
                )
            elif equity_pct > 50:
                sections.append(
                    f"### Equity Allocation\n\n"
                    f"Equity instruments represent **{equity_pct:.1f}%** of the portfolio, "
                    f"indicating a growth-oriented allocation strategy. This level of equity "
                    f"exposure provides participation in market upside while maintaining "
                    f"some buffer through other asset classes."
                )
            else:
                sections.append(
                    f"### Equity Allocation\n\n"
                    f"Equity instruments represent **{equity_pct:.1f}%** of the portfolio, "
                    f"reflecting a balanced or conservative allocation approach."
                )

        # Fixed income
        if bond_pct > 0:
            sections.append(
                f"### Fixed Income\n\n"
                f"Bond allocation stands at **{bond_pct:.1f}%**, providing "
                f"{'strong' if bond_pct > 30 else 'moderate' if bond_pct > 15 else 'limited'} "
                f"downside protection and income generation."
            )

        # Gold
        if gold_pct > 0:
            sections.append(
                f"### Precious Metals\n\n"
                f"Gold allocation at **{gold_pct:.1f}%** serves as an inflation hedge "
                f"and portfolio stabilizer. Gold historically shows low correlation with "
                f"equity markets, contributing to overall risk reduction."
            )
        else:
            sections.append(
                "### Precious Metals\n\n"
                "The portfolio currently has **no gold allocation**. Gold can serve "
                "as an effective hedge against inflation and currency devaluation."
            )

        # Crypto
        if crypto_pct > 0:
            sections.append(
                f"### Digital Assets\n\n"
                f"Cryptocurrency allocation at **{crypto_pct:.1f}%** introduces "
                f"{'significant' if crypto_pct > 20 else 'moderate' if crypto_pct > 10 else 'limited'} "
                f"volatility to the portfolio. Digital assets exhibit the highest "
                f"annualized volatility among all asset classes tracked."
            )

        return "\n\n".join(sections)

    def _generate_risk_summary(self, data: Dict[str, Any]) -> str:
        """Generate risk narration."""
        risk_score = data.get("risk_score", 0)
        risk_level = data.get("risk_level", "MODERATE")
        concentration = data.get("concentration_score", 0)
        diversification = data.get("diversification_score", 0)
        volatility = data.get("volatility", 0)
        allocation = data.get("allocation", {})

        equity_pct = allocation.get("stocks", 0) + allocation.get("mutual_funds", 0)

        narrative = (
            f"## Risk Intelligence Summary\n\n"
            f"The portfolio carries a risk score of **{risk_score:.1f}/100** "
            f"classified as **{risk_level}** risk.\n\n"
            f"### Key Risk Factors\n\n"
            f"- **Concentration Score:** {concentration:.1f}/100 — "
            f"{'High concentration in few asset types increases vulnerability to sector-specific downturns.' if concentration > 50 else 'Moderate concentration across asset classes.' if concentration > 25 else 'Well-distributed across multiple asset classes.'}\n"
            f"- **Diversification Score:** {diversification:.1f}/100 — "
            f"{'Excellent diversification providing strong risk mitigation.' if diversification > 70 else 'Adequate diversification but room for improvement.' if diversification > 40 else 'Low diversification increases exposure to individual asset class movements.'}\n"
            f"- **Portfolio Volatility:** {volatility:.1f}% annualized — "
            f"{'Elevated volatility suggesting significant price swings are expected.' if volatility > 25 else 'Moderate volatility within typical parameters.' if volatility > 12 else 'Low volatility indicating stable value characteristics.'}\n"
        )

        if equity_pct > 80:
            narrative += (
                f"\n### ⚠️ Equity Threshold Alert\n\n"
                f"Equity exposure at **{equity_pct:.1f}%** exceeds the 80% monitoring threshold. "
                f"This means the portfolio's performance is highly correlated with equity "
                f"market movements. During a market correction of 20%, the portfolio could "
                f"experience a proportional drawdown of approximately "
                f"**{equity_pct * 0.20:.1f}%** based on equity exposure alone."
            )

        return narrative

    def _generate_scenario(self, data: Dict[str, Any]) -> str:
        """Generate scenario analysis."""
        scenario_type = data.get("scenario_type", "market_correction")
        allocation = data.get("allocation", {})
        total_value = data.get("total_value", 0)

        equity_pct = allocation.get("stocks", 0) + allocation.get("mutual_funds", 0)
        bond_pct = allocation.get("bonds", 0)
        gold_pct = allocation.get("gold", 0)
        crypto_pct = allocation.get("crypto", 0)
        cash_pct = allocation.get("cash", 0)

        scenarios = {
            "market_correction": {
                "title": "Market Correction (-20%)",
                "equity_impact": -20.0,
                "bond_impact": 3.0,
                "gold_impact": 8.0,
                "crypto_impact": -35.0,
                "cash_impact": 0.0,
            },
            "recession": {
                "title": "Economic Recession",
                "equity_impact": -35.0,
                "bond_impact": 8.0,
                "gold_impact": 15.0,
                "crypto_impact": -50.0,
                "cash_impact": 0.0,
            },
            "inflation_surge": {
                "title": "Inflation Surge (+5%)",
                "equity_impact": -8.0,
                "bond_impact": -12.0,
                "gold_impact": 20.0,
                "crypto_impact": -5.0,
                "cash_impact": -5.0,
            },
            "bull_market": {
                "title": "Bull Market (+30%)",
                "equity_impact": 30.0,
                "bond_impact": -2.0,
                "gold_impact": -5.0,
                "crypto_impact": 60.0,
                "cash_impact": 0.0,
            },
        }

        s = scenarios.get(scenario_type, scenarios["market_correction"])

        portfolio_impact = (
            (equity_pct / 100) * s["equity_impact"]
            + (bond_pct / 100) * s["bond_impact"]
            + (gold_pct / 100) * s["gold_impact"]
            + (crypto_pct / 100) * s["crypto_impact"]
            + (cash_pct / 100) * s["cash_impact"]
        )

        projected_value = total_value * (1 + portfolio_impact / 100)

        result = (
            f"## Scenario Analysis: {s['title']}\n\n"
            f"Based on current allocation, here is the projected portfolio impact:\n\n"
            f"| Asset Class | Allocation | Scenario Impact | Projected Change |\n"
            f"|-------------|-----------|-----------------|------------------|\n"
        )

        for name, pct, impact in [
            ("Equity", equity_pct, s["equity_impact"]),
            ("Bonds", bond_pct, s["bond_impact"]),
            ("Gold", gold_pct, s["gold_impact"]),
            ("Crypto", crypto_pct, s["crypto_impact"]),
            ("Cash", cash_pct, s["cash_impact"]),
        ]:
            if pct > 0:
                change = total_value * (pct / 100) * (impact / 100)
                result += f"| {name} | {pct:.1f}% | {impact:+.1f}% | ${change:+,.0f} |\n"

        result += (
            f"\n**Overall Portfolio Impact: {portfolio_impact:+.1f}%**\n\n"
            f"- Current Value: **${total_value:,.2f}**\n"
            f"- Projected Value: **${projected_value:,.2f}**\n"
            f"- Estimated Change: **${projected_value - total_value:+,.2f}**\n\n"
            f"*This scenario is based on historical correlations and does not predict future performance.*"
        )

        return result

    def _generate_explanation(self, data: Dict[str, Any]) -> str:
        """Generate portfolio explanation in plain language."""
        allocation = data.get("allocation", {})
        total_value = data.get("total_value", 0)
        asset_count = data.get("asset_count", 0)
        risk_level = data.get("risk_level", "MODERATE")

        equity_pct = allocation.get("stocks", 0) + allocation.get("mutual_funds", 0)

        explanation = (
            f"## Portfolio Explanation\n\n"
            f"Your portfolio contains **{asset_count} assets** with a combined value "
            f"of **${total_value:,.2f}**. Here is what this means:\n\n"
        )

        # Plain language breakdown
        if equity_pct > 80:
            explanation += (
                f"**Your portfolio highly depends on equity exposure.** "
                f"With {equity_pct:.0f}% in stocks and equity funds, your returns "
                f"will closely track the stock market. When the market goes up, "
                f"your portfolio benefits significantly. However, during market "
                f"downturns, you may experience substantial temporary losses.\n\n"
            )
        elif equity_pct > 50:
            explanation += (
                f"**Your portfolio has a growth-oriented mix.** "
                f"With {equity_pct:.0f}% in equities and the remainder in other "
                f"asset classes, you have a balance between growth potential "
                f"and some protective diversification.\n\n"
            )
        elif equity_pct > 0:
            explanation += (
                f"**Your portfolio takes a balanced approach.** "
                f"With {equity_pct:.0f}% in equities, you have moderate market "
                f"exposure while maintaining meaningful positions in other asset classes.\n\n"
            )

        # Asset class descriptions
        for asset_type, pct in sorted(allocation.items(), key=lambda x: x[1], reverse=True):
            if pct > 0:
                desc = {
                    "stocks": "Individual company shares that move with the stock market",
                    "mutual_funds": "Professionally managed baskets of investments",
                    "bonds": "Fixed-income instruments that provide regular interest payments",
                    "gold": "Precious metal that historically preserves value during uncertainty",
                    "crypto": "Digital currencies with high growth potential but significant price swings",
                    "cash": "Liquid reserves available for immediate use or redeployment",
                }.get(asset_type, "Other investment instruments")

                explanation += f"- **{asset_type.replace('_', ' ').title()}** ({pct:.1f}%): {desc}\n"

        explanation += (
            f"\n**Risk Classification: {risk_level}** — This reflects the overall "
            f"volatility and concentration characteristics of your current allocation."
        )

        return explanation
