"""
Unit and Integration Test Suite: Expert AI Sales Bot Verification
Covers the 4 Core Sales Principles:
1. Bot behaves as an expert sales person and handles customer appropriately
2. Bot asks the discovery and qualifying questions a sales expert asks
3. Bot sells the product dynamically matched to the prospect's stated needs
4. Bot maintains an empathetic, polite, and consultative tone at all times
"""

import unittest
from sales_agent import SalesAgent
from summarizer import CallSummarizer
from products import get_product


class TestRule1ExpertSalesPersonBehavior(unittest.TestCase):
    """Rule 1: Bot behaves as an expert sales person and handles customer appropriately."""

    def setUp(self):
        self.agent = SalesAgent(product_id="aws-services", language="en", api_key=False)

    def test_concise_spoken_output_for_voice(self):
        """Spoken output should be concise (1-3 sentences) and avoid markdown formatting."""
        greeting = self.agent.generate_initial_greeting()
        self.assertNotIn("*", greeting, "Spoken voice output must not contain markdown asterisks")
        self.assertNotIn("#", greeting, "Spoken voice output must not contain markdown headings")
        self.assertLessEqual(len(greeting.split(".")), 5, "Greeting should be concise for voice call")

    def test_handles_timing_objection_appropriately(self):
        """Prospect says too busy / later -> expert handles with zero downtime reassurance & low friction offer."""
        resp = self.agent.respond("We are really busy this quarter, maybe next year.")
        self.assertTrue(
            "timing" in resp.lower() or "downtime" in resp.lower() or "proof-of-concept" in resp.lower() or "overview" in resp.lower(),
            f"Expected consultative objection handling, got: {resp}"
        )

    def test_handles_authority_objection_appropriately(self):
        """Prospect needs to consult boss/CTO -> expert suggests joint architecture review."""
        resp = self.agent.respond("I need to speak to my CTO and VP of Engineering first.")
        self.assertTrue(
            "cto" in resp.lower() or "team" in resp.lower() or "architect" in resp.lower(),
            f"Expected joint stakeholder session offer, got: {resp}"
        )

    def test_graceful_handling_of_hard_no(self):
        """Definite rejection is accepted politely without being pushy or aggressive."""
        resp = self.agent.respond("No thanks, we definitely do not want this, stop calling.")
        self.assertTrue(
            "completely understand" in resp.lower() or "appreciate" in resp.lower() or "wonderful day" in resp.lower(),
            f"Expected polite signoff on definite no, got: {resp}"
        )
        self.assertNotIn("why not", resp.lower())
        self.assertNotIn("you are making a mistake", resp.lower())

    def test_handles_competitor_comparison_professionally(self):
        """Handles mention of Azure/GCP with validation, value-add and open workload question."""
        resp = self.agent.respond("We are currently looking into Microsoft Azure and Google Cloud.")
        self.assertTrue(
            "azure" in resp.lower() or "gcp" in resp.lower() or "200" in resp or "bedrock" in resp.lower(),
            f"Expected competitive differentiation, got: {resp}"
        )
        self.assertIn("?", resp, "Expert sales rep must advance the conversation with a question")


class TestRule2DiscoveryQuestions(unittest.TestCase):
    """Rule 2: Bot asks all the discovery/qualifying questions that an expert sales rep asks."""

    def setUp(self):
        self.agent = SalesAgent(product_id="aws-services", language="en", api_key=False)

    def test_asks_discovery_on_onprem_datacenter_setup(self):
        """When prospect shares current setup (on-prem), bot asks bottleneck discovery question."""
        resp = self.agent.respond("We currently host everything on our own on-premise servers in our datacenter.")
        self.assertIn("?", resp, "Must end with a discovery question")
        self.assertTrue(
            "bottleneck" in resp.lower() or "challenge" in resp.lower() or "costs" in resp.lower() or "scalability" in resp.lower(),
            f"Expected discovery question about bottlenecks/scaling, got: {resp}"
        )

    def test_asks_discovery_on_high_costs(self):
        """When prospect brings up high bills, bot explores which workloads drive the cost."""
        resp = self.agent.respond("Our hosting bill is skyrocketing and we need to cut costs.")
        self.assertIn("?", resp, "Must ask discovery question")
        self.assertTrue(
            "workloads" in resp.lower() or "compute" in resp.lower() or "database" in resp.lower(),
            f"Expected workload discovery question, got: {resp}"
        )

    def test_asks_discovery_on_downtime_and_scaling(self):
        """When prospect suffers downtime, bot asks architecture discovery question (VMs vs containers)."""
        resp = self.agent.respond("Our servers experienced major downtime during our last flash traffic spike.")
        self.assertIn("?", resp, "Must ask discovery question")
        self.assertTrue(
            "container" in resp.lower() or "docker" in resp.lower() or "kubernetes" in resp.lower() or "machines" in resp.lower() or "vm" in resp.lower(),
            f"Expected container/VM architecture question, got: {resp}"
        )

    def test_asks_discovery_on_genai_requirements(self):
        """When prospect wants AI, bot asks if it is customer-facing or internal automation."""
        resp = self.agent.respond("We want to build Generative AI features with foundation models.")
        self.assertIn("?", resp, "Must ask discovery question")
        self.assertTrue(
            "customer-facing" in resp.lower() or "internal" in resp.lower() or "workflow" in resp.lower(),
            f"Expected use-case discovery question, got: {resp}"
        )

    def test_asks_discovery_on_security_compliance(self):
        """When prospect raises security/compliance, bot asks which regulations they must meet."""
        resp = self.agent.respond("We have very strict security and compliance requirements.")
        self.assertIn("?", resp, "Must ask discovery question")
        self.assertTrue(
            "certifications" in resp.lower() or "regulations" in resp.lower() or "compliance" in resp.lower(),
            f"Expected compliance regulation discovery question, got: {resp}"
        )


class TestRule3NeedsBasedSelling(unittest.TestCase):
    """Rule 3: Bot sells the product directly tailored to the customer's stated needs."""

    def setUp(self):
        self.agent = SalesAgent(product_id="aws-services", language="en", api_key=False)

    def test_sells_cost_reduction_solution_to_cost_conscious_buyer(self):
        """Pitches TCO reduction (45%), Savings Plans (72%), and POC credits ($5,000) for high bill pain."""
        resp = self.agent.respond("Our cloud bill is skyrocketing and we desperately need cost reduction.")
        self.assertTrue(
            "45%" in resp or "72%" in resp or "savings plans" in resp.lower(),
            f"Expected specific AWS cost reduction metrics, got: {resp}"
        )

    def test_sells_high_availability_solution_to_downtime_plagued_buyer(self):
        """Pitches 99.999% SLA availability and Multi-AZ Elastic Load Balancing for downtime pain."""
        resp = self.agent.respond("We suffer frequent downtime and outages whenever traffic surges.")
        self.assertTrue(
            "99.999%" in resp or "multi-az" in resp.lower() or "auto scaling" in resp.lower() or "elastic load balancing" in resp.lower(),
            f"Expected high-availability solution, got: {resp}"
        )

    def test_sells_bedrock_foundation_models_to_genai_buyer(self):
        """Pitches Amazon Bedrock, Claude, and private VPC security for Generative AI need."""
        resp = self.agent.respond("We want to integrate foundation LLMs and Generative AI into our platform.")
        self.assertTrue(
            "bedrock" in resp.lower() and ("claude" in resp.lower() or "titan" in resp.lower() or "models" in resp.lower()),
            f"Expected Bedrock and LLM pitch, got: {resp}"
        )

    def test_sells_security_and_governance_to_enterprise_buyer(self):
        """Pitches 143 security standards, SOC 2/HIPAA, and VPC isolation for security need."""
        resp = self.agent.respond("We are in healthcare and require SOC 2 and HIPAA compliance.")
        self.assertTrue(
            "143" in resp or "soc" in resp.lower() or "hipaa" in resp.lower() or "vpc" in resp.lower(),
            f"Expected security certification and isolation details, got: {resp}"
        )

    def test_sells_nexus_ai_sdr_replacement_to_sales_team(self):
        """Validates that general SaaS product (nexus-ai) also matches needs (cost and lead drop)."""
        nexus_agent = SalesAgent(product_id="nexus-ai", language="en", api_key=False)
        resp = nexus_agent.respond("Our outbound sales team is spending too much on SDR headcount.")
        self.assertTrue(
            "70%" in resp or "cost" in resp.lower() or "spend" in resp.lower(),
            f"Expected Nexus AI cost reduction value proposition, got: {resp}"
        )


class TestRule4PoliteToneAndEtiquette(unittest.TestCase):
    """Rule 4: Tone is courteous, empathetic, and respectful at every turn."""

    def setUp(self):
        self.agent = SalesAgent(product_id="aws-services", language="en", api_key=False)

    def test_empathy_markers_present(self):
        """Checks that empathetic phrases are used when customer expresses pains or rejections."""
        test_inputs = [
            ("Our bill is high", ["completely understand", "hear you", "appreciate"]),
            ("We have too much downtime", ["hear you", "understand", "appreciate"]),
            ("Not interested right now", ["completely understand", "appreciate", "wonderful day"]),
            ("We use our own servers", ["thank you for sharing", "appreciate"]),
        ]
        for user_msg, expected_markers in test_inputs:
            agent = SalesAgent(product_id="aws-services", language="en", api_key=False)
            resp = agent.respond(user_msg)
            has_marker = any(marker in resp.lower() for marker in expected_markers)
            self.assertTrue(has_marker, f"Response to '{user_msg}' lacked polite empathy marker: {resp}")

    def test_no_combative_or_aggressive_language(self):
        """Ensures forbidden aggressive sales language never appears in responses."""
        forbidden_phrases = [
            "you are wrong",
            "you must buy",
            "why wouldn't you",
            "mistake not to",
            "don't be ridiculous",
            "stupid",
            "listen to me",
            "buy now or else"
        ]
        prompts = [
            "AWS is a ripoff, I hate it.",
            "We are happy on on-premise, cloud is a fad.",
            "Your pricing makes no sense.",
            "I'm hanging up."
        ]
        for prompt in prompts:
            agent = SalesAgent(product_id="aws-services", language="en", api_key=False)
            resp = agent.respond(prompt)
            for forbidden in forbidden_phrases:
                self.assertNotIn(forbidden, resp.lower(), f"Combative phrase '{forbidden}' found in response: {resp}")

    def test_polite_multilingual_etiquette_hindi(self):
        """Ensures polite honorifics and etiquette in Hindi (e.g., 'मैं समझता हूँ', 'धन्यवाद', 'शुभ')."""
        agent_hi = SalesAgent(product_id="aws-services", language="hi", api_key=False)
        resp_cost = agent_hi.respond("हमारा बिल बहुत ज्यादा आ रहा है और हमें खर्च कम करना है।")
        self.assertTrue(
            "समझता हूँ" in resp_cost or "धन्यवाद" in resp_cost or "AWS" in resp_cost,
            f"Expected polite Hindi response, got: {resp_cost}"
        )

    def test_polite_multilingual_etiquette_telugu(self):
        """Ensures polite honorifics and etiquette in Telugu (e.g., 'ధన్యవాదాలు', 'నమస్కారం')."""
        agent_te = SalesAgent(product_id="aws-services", language="te", api_key=False)
        greeting = agent_te.generate_initial_greeting()
        self.assertIn("నమస్కారం", greeting)


if __name__ == "__main__":
    unittest.main()
