"""
Comprehensive Test Suite for AWS Cloud Solutions Sales Bot
Validates:
1. Product Catalog & Metadata for AWS
2. Multilingual Greetings (English, Hindi, Telugu)
3. Discovery & Value Proposition Pitching
4. Technical Objection Handling (Pricing, Azure/GCP Competitors, Zero-Downtime Migration, CTO Authority)
5. Contextual Demo / Architecture Assessment Slot Filling
6. Multi-Turn Sales Call Simulation
7. Call Summarizer, Requirements Extraction & Sales Status Classification
8. Live LLM Integration (OpenAI gpt-4o-mini)
9. Flask REST API Endpoints (/api/products, /api/greeting, /api/chat, /api/summary)
"""

import os
import unittest
from dotenv import load_dotenv

load_dotenv()

from products import get_product, list_products, SAAS_PRODUCTS
from sales_agent import SalesAgent
from summarizer import CallSummarizer
from app import app


class TestAWSProductCatalog(unittest.TestCase):
    def test_aws_product_exists(self):
        prod = get_product("aws-services")
        self.assertIsNotNone(prod)
        self.assertEqual(prod["id"], "aws-services")
        self.assertEqual(prod["name"], "AWS Cloud Solutions")
        self.assertIn("Cloud Computing", prod["category"])

    def test_aws_features_and_pricing(self):
        prod = get_product("aws-services")
        pricing_names = [p["name"] for p in prod["pricing"]]
        self.assertTrue(any("Starter" in name for name in pricing_names))
        self.assertTrue(any("Business" in name for name in pricing_names))

        feature_text = " ".join(prod["features"]).lower()
        self.assertIn("ec2", feature_text)
        self.assertIn("s3", feature_text)
        self.assertIn("bedrock", feature_text)
        self.assertIn("migration", feature_text)

    def test_aws_objection_playbook(self):
        prod = get_product("aws-services")
        self.assertIn("price", prod["objections"])
        self.assertIn("competitor", prod["objections"])
        self.assertIn("timing", prod["objections"])
        self.assertIn("authority", prod["objections"])


class TestAWSGreetings(unittest.TestCase):
    def test_initial_greeting_en(self):
        agent = SalesAgent(product_id="aws-services", language="en")
        greeting = agent.generate_initial_greeting()
        self.assertIn("Alex", greeting)
        self.assertIn("AWS Cloud Solutions", greeting)
        self.assertIn("infrastructure", greeting.lower())

    def test_initial_greeting_hi(self):
        agent = SalesAgent(product_id="aws-services", language="hi")
        greeting = agent.generate_initial_greeting()
        self.assertIn("नमस्ते", greeting)
        self.assertIn("AWS", greeting)

    def test_initial_greeting_te(self):
        agent = SalesAgent(product_id="aws-services", language="te")
        greeting = agent.generate_initial_greeting()
        self.assertIn("నమస్కారం", greeting)
        self.assertIn("AWS", greeting)


class TestAWSObjectionHandlingAndRules(unittest.TestCase):
    def setUp(self):
        # Using rule-engine mode by passing api_key=False
        self.agent = SalesAgent(product_id="aws-services", language="en", api_key=False)

    def test_pricing_inquiry(self):
        resp = self.agent.respond("How much does AWS cost and what are your plans?")
        self.assertTrue(
            "pay-as-you-go" in resp.lower() or "$499" in resp or "savings plans" in resp.lower(),
            f"Unexpected response: {resp}"
        )

    def test_objection_budget_too_expensive(self):
        resp = self.agent.respond("AWS is too expensive for our startup, we have a tight budget.")
        self.assertTrue(
            "savings plans" in resp.lower() or "credits" in resp.lower() or "72%" in resp,
            f"Unexpected response: {resp}"
        )

    def test_objection_competitor_azure_gcp(self):
        resp = self.agent.respond("We are currently considering Azure and Google Cloud.")
        self.assertTrue(
            "200" in resp or "bedrock" in resp.lower() or "azure" in resp.lower() or "regions" in resp.lower(),
            f"Unexpected response: {resp}"
        )

    def test_objection_on_premises_datacenter(self):
        resp = self.agent.respond("We already have our own on-premise datacenter.")
        self.assertTrue(
            "200" in resp or "bedrock" in resp.lower() or "cloud" in resp.lower(),
            f"Unexpected response: {resp}"
        )

    def test_objection_timing_busy(self):
        resp = self.agent.respond("We are too busy with our product release, maybe next quarter.")
        self.assertTrue(
            "downtime" in resp.lower() or "migration" in resp.lower() or "overview" in resp.lower(),
            f"Unexpected response: {resp}"
        )

    def test_objection_authority_cto(self):
        resp = self.agent.respond("I need to discuss this with our CTO and lead DevOps architect.")
        self.assertTrue(
            "cto" in resp.lower() or "architect" in resp.lower() or "team" in resp.lower(),
            f"Unexpected response: {resp}"
        )

    def test_features_inquiry_bedrock_and_compute(self):
        resp = self.agent.respond("What do you provide for serverless and generative AI?")
        self.assertTrue(
            "ec2" in resp.lower() or "bedrock" in resp.lower() or "s3" in resp.lower(),
            f"Unexpected response: {resp}"
        )

    def test_small_talk_handling(self):
        resp = self.agent.respond("I am doing fine, how are you?")
        self.assertTrue(
            "hosting" in resp.lower() or "workloads" in resp.lower() or "costs" in resp.lower(),
            f"Unexpected response: {resp}"
        )

    def test_definite_decline(self):
        resp = self.agent.respond("Not interested at all, please stop.")
        self.assertIn("understand", resp.lower())


class TestAWSSlotFillingDemoBooking(unittest.TestCase):
    def setUp(self):
        self.agent = SalesAgent(product_id="aws-services", language="en", api_key=False)

    def test_demo_intent_asks_slot(self):
        resp = self.agent.respond("I'd like to book a consultation session with your architect.")
        self.assertIn("morning or afternoon", resp.lower())

    def test_slot_selection_morning_confirms_booking(self):
        history = [
            {"sender": "bot", "text": "Does tomorrow morning or afternoon work better for your calendar?"}
        ]
        resp = self.agent.respond("Tomorrow morning works great", conversation_history=history)
        self.assertIn("tomorrow morning at 10:00 am", resp.lower())
        self.assertIn("reserved", resp.lower())
        self.assertIn("solutions architect", resp.lower())

    def test_slot_selection_afternoon_confirms_booking(self):
        history = [
            {"sender": "bot", "text": "Does tomorrow morning or afternoon suit you better?"}
        ]
        resp = self.agent.respond("Afternoon is better for me", conversation_history=history)
        self.assertIn("tomorrow afternoon at 2:00 pm", resp.lower())
        self.assertIn("reserved", resp.lower())


class TestAWSMultiTurnConversation(unittest.TestCase):
    def setUp(self):
        self.agent = SalesAgent(product_id="aws-services", language="en", api_key=False)

    def test_full_aws_sales_dialogue(self):
        history = []
        
        # Turn 1: Bot greets
        greeting = self.agent.generate_initial_greeting()
        history.append({"sender": "bot", "text": greeting})
        self.assertIn("AWS Cloud Solutions", greeting)

        # Turn 2: Customer shares pain point
        user_msg1 = "We run high-traffic servers on-premise and our datacenter bill is skyrocketing."
        resp1 = self.agent.respond(user_msg1, conversation_history=history)
        history.append({"sender": "user", "text": user_msg1})
        history.append({"sender": "bot", "text": resp1})
        self.assertTrue(len(resp1) > 20)

        # Turn 3: Customer raises competitor / existing tech concern
        user_msg2 = "Our team is also evaluating Microsoft Azure."
        resp2 = self.agent.respond(user_msg2, conversation_history=history)
        history.append({"sender": "user", "text": user_msg2})
        history.append({"sender": "bot", "text": resp2})
        self.assertTrue("azure" in resp2.lower() or "200" in resp2 or "bedrock" in resp2.lower())

        # Turn 4: Customer asks about demo/assessment
        user_msg3 = "Can we schedule a live architecture assessment?"
        resp3 = self.agent.respond(user_msg3, conversation_history=history)
        history.append({"sender": "user", "text": user_msg3})
        history.append({"sender": "bot", "text": resp3})
        self.assertIn("morning or afternoon", resp3.lower())

        # Turn 5: Customer chooses morning slot
        user_msg4 = "Morning works best for us."
        resp4 = self.agent.respond(user_msg4, conversation_history=history)
        history.append({"sender": "user", "text": user_msg4})
        history.append({"sender": "bot", "text": resp4})
        self.assertIn("reserved", resp4.lower())
        self.assertIn("10:00 am", resp4.lower())


class TestAWSSummarizerAndClassification(unittest.TestCase):
    def setUp(self):
        self.summarizer = CallSummarizer(api_key=False)

    def test_summary_demo_requested(self):
        transcript = [
            {"sender": "bot", "text": "Hi there! This is Alex from AWS Cloud Solutions. How are you doing today?"},
            {"sender": "user", "text": "We are looking to migrate our database to AWS RDS and want to reduce cloud costs."},
            {"sender": "bot", "text": "Would you like to schedule a 30-minute Cloud Architecture Assessment with an AWS Certified Solutions Architect?"},
            {"sender": "user", "text": "Yes, please book it for tomorrow morning."},
            {"sender": "bot", "text": "Perfect! I have reserved tomorrow morning at 10:00 AM for your assessment and AWS credits."}
        ]
        result = self.summarizer.analyze_call(transcript, product_name="AWS Cloud Solutions")

        self.assertEqual(result["sales_status"], "Demo Requested")
        self.assertEqual(result["sentiment"], "Positive")
        self.assertTrue(any("cloud" in req.lower() or "migration" in req.lower() for req in result["customer_requirements"]))
        self.assertTrue(any("assessment" in s.lower() or "solutions architect" in s.lower() or "credits" in s.lower() for s in result["next_steps"]))

    def test_summary_objection_followup_required(self):
        transcript = [
            {"sender": "bot", "text": "Hi, this is Alex from AWS Cloud Solutions."},
            {"sender": "user", "text": "We are currently very busy with a major sprint, please call back next week or email me the architecture whitepaper."}
        ]
        result = self.summarizer.analyze_call(transcript, product_name="AWS Cloud Solutions")
        self.assertEqual(result["sales_status"], "Follow-up Required")
        self.assertTrue(any("Timing" in obj or "busy" in obj.lower() for obj in result["objections"]))

    def test_summary_not_interested(self):
        transcript = [
            {"sender": "bot", "text": "Hi, this is Alex from AWS Cloud Solutions."},
            {"sender": "user", "text": "We are not interested in cloud migration, no thanks, do not call."}
        ]
        result = self.summarizer.analyze_call(transcript, product_name="AWS Cloud Solutions")
        self.assertEqual(result["sales_status"], "Not Interested")
        self.assertEqual(result["sentiment"], "Negative")


class TestAWSLiveLLMIntegration(unittest.TestCase):
    def setUp(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")

    def test_live_openai_sales_response(self):
        if not self.api_key:
            self.skipTest("No OPENAI_API_KEY found in environment")

        agent = SalesAgent(product_id="aws-services", language="en", api_key=self.api_key)
        resp = agent.respond(
            "We run PostgreSQL and MongoDB on premises and our monthly hosting is $20,000. How can AWS help us migrate and cut costs?"
        )
        self.assertIsNotNone(resp)
        self.assertTrue(len(resp) > 20)
        # Verify tone & relevance to AWS
        resp_lower = resp.lower()
        self.assertTrue(
            any(k in resp_lower for k in ["aws", "rds", "migrate", "migration", "cost", "cloud", "tco", "credits", "assessment", "dms"]),
            f"Response did not mention AWS migration/cloud concepts: {resp}"
        )

    def test_live_openai_summarizer(self):
        if not self.api_key:
            self.skipTest("No OPENAI_API_KEY found in environment")

        summarizer = CallSummarizer(api_key=self.api_key)
        transcript = [
            {"sender": "bot", "text": "Hi there! This is Alex from AWS Cloud Solutions. How are you doing today?"},
            {"sender": "user", "text": "We want to migrate our Kubernetes cluster to AWS EKS and explore Amazon Bedrock for generative AI."},
            {"sender": "bot", "text": "Does tomorrow afternoon work better for an architecture assessment?"},
            {"sender": "user", "text": "Tomorrow afternoon at 2 PM is perfect, let's schedule that."}
        ]
        result = summarizer.analyze_call(transcript, product_name="AWS Cloud Solutions")
        self.assertIn(result["sales_status"], ["Demo Requested", "Interested", "Converted"])
        self.assertTrue(len(result["summary"]) > 20)
        self.assertTrue(len(result["customer_requirements"]) > 0)


class TestAWSFlaskAPI(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_api_products_includes_aws(self):
        res = self.client.get("/api/products")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        prod_ids = [p["id"] for p in data["products"]]
        self.assertIn("aws-services", prod_ids)
        self.assertIn("aws-services", data["catalog"])

    def test_api_greeting_aws(self):
        res = self.client.post("/api/greeting", json={"product_id": "aws-services", "language": "en"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("AWS Cloud Solutions", data["product"])
        self.assertIn("Alex", data["greeting"])

    def test_api_chat_aws(self):
        res = self.client.post("/api/chat", json={
            "product_id": "aws-services",
            "language": "en",
            "user_message": "Can you tell me about AWS pricing?"
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(len(data["response"]) > 10)

    def test_api_summary_aws(self):
        transcript = [
            {"sender": "bot", "text": "Hi from AWS Cloud Solutions."},
            {"sender": "user", "text": "I'd love a demo tomorrow morning at 10 AM."}
        ]
        res = self.client.post("/api/summary", json={
            "product_id": "aws-services",
            "transcript": transcript
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("sales_status", data)
        self.assertEqual(data["sales_status"], "Demo Requested")


if __name__ == "__main__":
    unittest.main(verbosity=2)
