"""
AI Call Summarizer and Sales Status Classification Engine (Python)
Extracts:
1. Executive Summary
2. Customer Requirements
3. Objections Raised
4. Next Steps
5. Sales Status (strictly one of the 6 required categories):
   - Converted
   - Interested
   - Follow-up Required
   - Not Interested
   - Demo Requested
   - No Response
"""

import json
import os
import re
from dotenv import load_dotenv
load_dotenv()

VALID_STATUSES = [
    "Converted",
    "Interested",
    "Follow-up Required",
    "Not Interested",
    "Demo Requested",
    "No Response"
]


class CallSummarizer:
    def __init__(self, api_key=None):
        if api_key is False or api_key == "":
            self.api_key = None
        elif api_key is not None:
            self.api_key = api_key
        else:
            self.api_key = os.environ.get("OPENAI_API_KEY")

    def analyze_call(self, transcript_messages, product_name="NexusPulse AI", language="en"):
        if not transcript_messages or len(transcript_messages) == 0:
            return self._build_no_response_result(product_name)

        user_messages = [m.get("text", "").strip() for m in transcript_messages if m.get("sender") == "user"]
        user_text_combined = " ".join(user_messages).lower()

        if not user_messages or len(user_text_combined.strip()) < 3:
            return self._build_no_response_result(product_name)

        if self.api_key and self.api_key.strip():
            try:
                llm_result = self._analyze_with_llm(transcript_messages, product_name)
                if llm_result:
                    return llm_result
            except Exception as e:
                print(f"[CallSummarizer] LLM error, falling back to rule engine: {e}")

        return self._analyze_with_rules(transcript_messages, user_messages, user_text_combined, product_name, language)

    def _build_no_response_result(self, product_name):
        return {
            "summary": f"Call initiated with {product_name} sales bot, but no audible response or engagement was received from the customer before the call ended.",
            "customer_requirements": ["None identified - call was unanswered or terminated prematurely."],
            "objections": ["No engagement from customer."],
            "next_steps": ["Retry outbound call during business hours or send introductory email."],
            "sales_status": "No Response",
            "status_reason": "No response was recorded from the customer during the session.",
            "sentiment": "Neutral"
        }

    def _analyze_with_rules(self, transcript_messages, user_messages, user_text_combined, product_name, language):
        """High-precision pattern matcher for sales qualification and analysis."""
        turn_count = len(transcript_messages)
        user_turn_count = len(user_messages)

        objections = []
        if any(w in user_text_combined for w in ["expensive", "costly", "high price", "tight budget", "too much", "no budget", "महंगा", "ధర ఎక్కువ"]):
            objections.append("Pricing / Budget concern: Customer mentioned pricing constraints or questioned ROI.")
        if any(w in user_text_combined for w in ["competitor", "already have", "using another", "already use", "hubspot", "salesforce", "apollo", "azure", "gcp", "google cloud", "on-prem", "on-premise", "datacenter"]):
            objections.append("Competitor / Existing Stack: Customer is currently using Azure, GCP, on-premises datacenters, or existing software.")
        if any(w in user_text_combined for w in ["busy", "later", "next month", "no time", "not now", "call back later", "बाद में", "తరువాత"]):
            objections.append("Timing: Customer indicated they are busy or not ready to evaluate currently.")
        if any(w in user_text_combined for w in ["boss", "manager", "team", "colleagues", "partner", "permission", "discuss", "cto"]):
            objections.append("Authority / Consensus: Customer needs buy-in from leadership, CTO, or internal engineering team.")

        if not objections:
            objections.append("No major objections raised during the conversation.")

        requirements = []
        if any(w in user_text_combined for w in ["cloud", "aws", "migration", "migrate", "server", "ec2", "s3", "bedrock", "database", "rds", "lambda", "infrastructure", "devops", "hosting"]):
            requirements.append("Cloud infrastructure modernization, AWS workload migration, or Generative AI adoption via Amazon Bedrock.")
        if any(w in user_text_combined for w in ["lead", "conversion", "sales", "inbound", "outreach"]):
            requirements.append("Automated lead conversion and accelerating inbound response times.")
        if any(w in user_text_combined for w in ["crm", "hubspot", "salesforce", "integration", "sync"]):
            requirements.append("Seamless integration with existing CRM and software workflow.")
        if any(w in user_text_combined for w in ["price", "cost", "plan", "trial", "starter", "tier", "savings", "budget"]):
            requirements.append("Transparent pricing models, cost optimization, and Proof-of-Concept credit availability.")
        if any(w in user_text_combined for w in ["voice", "call", "agent", "ai", "speech", "realistic"]):
            requirements.append("High quality, human-like voice AI capable of natural conversations.")

        if not requirements:
            requirements.append("General exploration of technology solutions.")

        status = "Interested"
        reason = ""

        has_signed_up = any(w in user_text_combined for w in ["signed up", "sign up now", "take my card", "buy now", "purchase", "let's do the trial", "start trial now", "activate plan"])
        has_demo = any(w in user_text_combined for w in ["demo", "schedule", "book", "meeting", "calendar", "tomorrow", "afternoon", "morning", "show me", "15 minute", "30 minute", "assessment", "consultation", "डेमो", "డెమో"])
        bot_booked_demo = any("booked" in m.get("text", "").lower() or "reserved" in m.get("text", "").lower() for m in transcript_messages if m.get("sender") == "bot")
        has_not_interested = any(w in user_text_combined for w in ["not interested", "no thanks", "don't call", "stop", "never", "remove me", "don't want", "dont want", "रुचि नहीं", "వద్దు"])
        has_followup = any(w in user_text_combined for w in ["call later", "email me", "send details", "discuss with team", "check with boss", "next week", "later", "बाद में", "తరువాత", "ईमेल"])
        has_interested = any(w in user_text_combined for w in ["interested", "sounds good", "tell me more", "how does it work", "pricing", "features", "yes", "yeah", "sure", "हाँ", "అవును"])

        if has_signed_up:
            status = "Converted"
            reason = "Customer agreed to immediate trial onboarding or subscription purchase."
        elif has_demo or bot_booked_demo or (has_interested and ("demo" in user_text_combined or "trial" in user_text_combined or "assessment" in user_text_combined)):
            status = "Demo Requested"
            reason = "Customer agreed to or requested a live technical demonstration or architecture assessment."
        elif has_not_interested and not has_demo:
            status = "Not Interested"
            reason = "Customer explicitly declined the product offering and indicated no interest at this time."
        elif has_followup or any("Timing" in o or "Authority" in o for o in objections):
            status = "Follow-up Required"
            reason = "Customer requested a later callback, additional materials via email, or needs internal alignment."
        elif has_interested or user_turn_count >= 2:
            status = "Interested"
            reason = "Customer actively engaged with questions regarding product capabilities, pricing, and features."
        else:
            status = "No Response"
            reason = "Conversation was inconclusive with insufficient customer input."

        is_aws_prod = ("aws" in product_name.lower())
        intro_desc = "enterprise cloud migration, infrastructure modernization, and Generative AI on Amazon Bedrock" if is_aws_prod else "automated lead conversion and revenue acceleration"
        summary = (
            f"The customer interacted with {product_name} voice sales representative over {user_turn_count} conversational turns. "
            f"The sales bot introduced the core value proposition of {intro_desc}. "
            f"Key discussion centered around {', '.join([r.lower() for r in requirements[:2]])}. "
            f"Final sentiment outcome: {status} ({reason})."
        )

        next_steps = []
        if status == "Converted":
            if is_aws_prod:
                next_steps = [
                    "Initiate AWS enterprise cloud onboarding and workload provisioning.",
                    "Assign dedicated AWS Certified Solutions Architect and Technical Account Manager.",
                    "Provision AWS Proof-of-Concept credit package."
                ]
            else:
                next_steps = [
                    "Trigger automated welcome onboarding sequence via email.",
                    "Assign dedicated customer success manager.",
                    "Send 14-day enterprise trial credentials and API documentation."
                ]
        elif status == "Demo Requested":
            if is_aws_prod:
                next_steps = [
                    "Send calendar confirmation for 30-minute Cloud Architecture & Migration Assessment with an AWS Certified Solutions Architect.",
                    "Prepare AWS Well-Architected Review checklist and TCO cost savings breakdown.",
                    "Qualify account for up to $5,000 in AWS Proof-of-Concept (POC) credits."
                ]
            else:
                next_steps = [
                    "Send calendar invite with Google Meet link for 15-minute live demo.",
                    "Prepare customized CRM integration walkthrough based on customer industry.",
                    "Send pre-demo 2-minute product showcase video."
                ]
        elif status == "Follow-up Required":
            if is_aws_prod:
                next_steps = [
                    "Send AWS Cloud Solutions enterprise architecture overview and migration whitepaper.",
                    "Schedule follow-up reminder in CRM to reconnect with engineering leadership in 3 business days.",
                    "Provide information on zero-downtime database migration tooling (AWS DMS)."
                ]
            else:
                next_steps = [
                    "Send product one-pager and pricing breakdown to customer email.",
                    "Schedule automated follow-up reminder in CRM in 3 business days.",
                    "Prepare answers to any team governance or timeline considerations."
                ]
        elif status == "Interested":
            if is_aws_prod:
                next_steps = [
                    "Send AWS Cloud Solutions tier pricing sheet and customer case study.",
                    "Offer complimentary Cloud Cost & Architecture review session.",
                    "Enroll in AWS enterprise cloud technical updates newsletter."
                ]
            else:
                next_steps = [
                    "Send comprehensive feature brochure and customer ROI case study.",
                    "Follow up via WhatsApp or SMS to offer a tailored demo slot.",
                    "Enroll in automated high-intent lead nurture email sequence."
                ]
        elif status == "Not Interested":
            next_steps = [
                "Update CRM status to 'Disqualified / Unresponsive'.",
                "Add to low-touch quarterly newsletter list.",
                "Suppress proactive outbound calls for 90 days."
            ]
        else:
            next_steps = [
                "Verify customer contact details and phone number.",
                "Schedule one alternate outbound call attempt."
            ]

        return {
            "summary": summary,
            "customer_requirements": requirements,
            "objections": objections,
            "next_steps": next_steps,
            "sales_status": status,
            "status_reason": reason,
            "sentiment": "Positive" if status in ["Converted", "Demo Requested", "Interested"] else ("Negative" if status == "Not Interested" else "Neutral")
        }

    def _analyze_with_llm(self, transcript_messages, product_name):
        import openai
        client = openai.OpenAI(api_key=self.api_key)

        transcript_text = "\n".join([
            f"{'AI Bot' if m.get('sender') == 'bot' else 'Customer'}: {m.get('text', '')}"
            for m in transcript_messages
        ])

        system_prompt = f"""You are an executive Sales Intelligence Analyzer evaluating an AI voice sales call for {product_name}.
Evaluate the conversation transcript and output a JSON object with:
1. "summary": A concise, factual description of the discussion, topics covered, and outcome. Do NOT invent customer information.
2. "customer_requirements": A list of strings describing the customer's explicitly stated needs, current workflow, and pain points (or ["None explicitly stated"]).
3. "objections": A list of strings describing concerns or hesitations raised (or ["No major objections identified"]).
4. "next_steps": A list of strings with concrete action items. Clearly distinguish agreed actions (e.g. "[Agreed] Live demo booked for tomorrow at 10 AM") from suggested actions (e.g. "[Suggested] Send pricing brochure").
5. "sales_status": MUST strictly be one of:
   - "Converted": Only if customer completed a verified purchase, signup, or activated trial.
   - "Demo Requested": Customer explicitly requested or agreed to a product demonstration/walkthrough.
   - "Not Interested": Customer clearly declined or stated they do not want the solution.
   - "Follow-up Required": Customer asked to be contacted later, requested email information, or needs manager alignment.
   - "Interested": Customer expressed genuine engagement, questions about pricing/features, but didn't request a demo or convert.
   - "No Response": Customer provided no meaningful engagement / silent.
6. "status_reason": A short explanation of why that specific status was chosen based on evidence.
7. "sentiment": "Positive", "Neutral", or "Negative".

Ensure output is strictly valid JSON without markdown formatting.
"""
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Transcript:\n{transcript_text}"}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        content = response.choices[0].message.content
        data = json.loads(content)
        # Ensure status is valid
        if data.get("sales_status") not in VALID_STATUSES:
            data["sales_status"] = "Interested"
        return data
