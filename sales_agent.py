import re
import os
from dotenv import load_dotenv
load_dotenv()

from products import get_product

GREETINGS = {
    "en": {
        "intro": "Hi there! This is Alex, your AI sales assistant from {product_name}. We help B2B teams automate lead follow-ups and 3x their sales pipeline with autonomous AI voice agents. How are you doing today?",
        "closing": "Fantastic! I've booked your 15-minute live demo for tomorrow with our senior solution architect, along with a free 14-day trial. Thank you so much for your time today, and have an awesome day ahead!",
        "declined": "I completely understand! We'll keep you on our monthly product update list. Thank you so much for your time today, and feel free to check us out at any time. Have a great day!"
    },
    "hi": {
        "intro": "नमस्ते! मैं {product_name} से एलेक्स बात कर रहा हूँ। हम बी2बी कंपनियों के लिए एआई वॉयस एजेंट्स के ज़रिए लीड्स को कन्वर्ट करने में मदद करते हैं। आप आज कैसे हैं?",
        "closing": "शानदार! हमने आपका 15 मिनट का लाइव डेमो और 14 दिन का फ्री ट्रायल बुक कर लिया है। आपके कीमती समय के लिए बहुत-बहुत धन्यवाद, आपका दिन शुभ हो!",
        "declined": "मैं आपकी बात पूरी तरह समझता हूँ। समय देने के लिए बहुत धन्यवाद। अगर भविष्य में आपको ज़रूरत लगे, तो हमें ज़रूर याद कीजिएगा। धन्यवाद!"
    },
    "te": {
        "intro": "నమస్కారం! నేను {product_name} నుండి అలెక్స్ మాట్లాడుతున్నాను. మేము వ్యాపారాలకు ఆటోమేటెడ్ AI వాయిస్ ఏజెంట్ల ద్వారా అమ్మకాలను పెంచడంలో సహాయం చేస్తాము. మీరు ఎలా ఉన్నారు?",
        "closing": "అద్భుతం! మీ కోసం 15 నిమిషాల లైవ్ డెమో మరియు 14 రోజుల ఉచిత ట్రయల్ సిద్ధం చేశాము. మీ అమూల్యమైన సమయానికి చాలా ధన్యవాదాలు!",
        "declined": "నేను మీ పరిస్థితిని అర్థం చేసుకున్నాను. సమయం ఇచ్చినందుకు ధన్యవాదాలు. భవిష్యత్తులో అవసరమైతే మమ్మల్ని సంప్రదించండి. నమస్కారం!"
    }
}

AWS_GREETINGS = {
    "en": {
        "intro": "Hi there! This is Alex, your Cloud Solutions Advisor from {product_name}. We help engineering and business leaders modernize their infrastructure, cut cloud TCO by up to 45%, and build secure Generative AI solutions with Amazon Bedrock. How are you doing today?",
        "closing": "Fantastic! I've reserved tomorrow for your 30-minute Cloud Architecture & Migration Assessment with our AWS Certified Solutions Architect, along with your AWS Proof-of-Concept credits. Thank you so much for your time today, and have an awesome day ahead!",
        "declined": "I completely understand! We'll keep you updated on upcoming AWS architecture workshops and migration programs. Thank you for your time today, and have a wonderful day ahead!"
    },
    "hi": {
        "intro": "नमस्ते! मैं {product_name} से एलेक्स बात कर रहा हूँ। हम कंपनियों को क्लाउड इंफ्रास्ट्रक्चर मॉडर्नाइज़ करने, सर्वर लागत 45% तक घटाने और अमेज़ॅन बेडरॉक के ज़रिए जेनरेटिव एआई लागू करने में मदद करते हैं। आप आज कैसे हैं?",
        "closing": "शानदार! हमने कल के लिए आपका 30 मिनट का एडवांस्ड क्लाउड आर्किटेक्चर असेसमेंट और एडब्ल्यूएस पीओसी क्रेडिट्स बुक कर लिया है। आपके कीमती समय के लिए बहुत धन्यवाद, आपका दिन शुभ हो!",
        "declined": "मैं आपकी बात पूरी तरह समझता हूँ। समय देने के लिए बहुत धन्यवाद। भविष्य में यदि आपको क्लाउड या एआई समाधान की आवश्यकता हो, तो हमें ज़रूर याद कीजिएगा। धन्यवाद!"
    },
    "te": {
        "intro": "నమస్కారం! నేను {product_name} నుండి అలెక్స్ మాట్లాడుతున్నాను. మేము వ్యాపారాలకు క్లౌడ్ మైగ్రేషన్, ఇన్ఫ్రాస్ట్రక్చర్ ఖర్చుల తగ్గింపు మరియు Amazon Bedrock తో జెనరేటివ్ AI సొల్యూషన్స్ అందించడంలో సహాయం చేస్తాము. మీరు ఎలా ఉన్నారు?",
        "closing": "అద్భుతం! మీ కోసం రేపు 30 నిమిషాల AWS క్లౌడ్ ఆర్కిటెక్చర్ సెషన్ మరియు POC క్రెడిట్లను షెడ్యూల్ చేశాము. సమయం ఇచ్చినందుకు చాలా ధన్యవాదాలు!",
        "declined": "నేను మీ పరిస్థితిని అర్థం చేసుకున్నాను. సమయం ఇచ్చినందుకు ధన్యవాదాలు. భవిష్యత్తులో క్లౌడ్ అవసరాలు ఉంటే మమ్మల్ని సంప్రదించండి. నమస్కారం!"
    }
}


class SalesAgent:
    def __init__(self, product_id="nexus-ai", language="en", api_key=None):
        self.product = get_product(product_id)
        self.language = language if language in ["en", "hi", "te"] else "en"
        if api_key is False or api_key == "":
            self.api_key = None
        elif api_key is not None:
            self.api_key = api_key
        else:
            self.api_key = os.environ.get("OPENAI_API_KEY")

    def generate_initial_greeting(self):
        """Returns the opening greeting for the sales bot."""
        if self.product.get("id") == "aws-services":
            lang_dict = AWS_GREETINGS.get(self.language, AWS_GREETINGS["en"])
        else:
            lang_dict = GREETINGS.get(self.language, GREETINGS["en"])
        return lang_dict["intro"].format(product_name=self.product["name"])

    def respond(self, user_message, conversation_history=None):
        """
        Main response generator.
        Uses OpenAI if api_key is present, otherwise uses built-in smart conversational sales brain.
        """
        if not user_message or not user_message.strip():
            if self.language == "hi":
                return "माफ़ कीजिए, मुझे आपकी आवाज़ सुनाई नहीं दी। क्या आप दोहरा सकते हैं?"
            elif self.language == "te":
                return "క్షమించండి, మీ మాటలు వినపడలేదు. దయచేసి మళ్ళీ చెప్పగలరా?"
            return "I'm sorry, I couldn't hear that clearly. Could you please repeat?"

        # If API key is provided and OpenAI is installed, attempt LLM call
        if self.api_key and self.api_key.strip():
            try:
                import openai
                client = openai.OpenAI(api_key=self.api_key)
                system_prompt = self._build_system_prompt()
                messages = [{"role": "system", "content": system_prompt}]
                if conversation_history:
                    for turn in conversation_history[-8:]:
                        role = "assistant" if turn.get("sender") == "bot" else "user"
                        messages.append({"role": role, "content": turn.get("text", "")})
                messages.append({"role": "user", "content": user_message})

                completion = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    max_tokens=140,
                    temperature=0.6
                )
                return completion.choices[0].message.content.strip()
            except Exception as e:
                print(f"[SalesAgent] LLM error, falling back to rule engine: {e}")

        # Intelligent Context-Aware Rule & Intent State Machine
        return self._rule_based_response(user_message, conversation_history)

    def _build_system_prompt(self):
        lang_instruction = {
            "en": "Respond in natural, persuasive English.",
            "hi": "Respond in polite, conversational Hindi (Devanagari or Romanized Hindi).",
            "te": "Respond in polite, conversational Telugu."
        }.get(self.language, "Respond in English.")

        pricing_list = self.product.get("pricing", [])
        pricing_text = ", ".join([f"{p['name']} ({p['price']}: {p.get('features', '')})" for p in pricing_list])
        features_text = "; ".join(self.product.get("features", []))
        pain_points_text = "; ".join(self.product.get("pain_points", []))
        stats_text = "; ".join(self.product.get("stats", []))
        objections_text = "\n".join([f"- {k.capitalize()}: {v}" for k, v in self.product.get("objections", {}).items()])

        return f"""You are Alex, an elite, consultative Enterprise Sales & Solutions Advisor representing {self.product['name']}.
Product: {self.product['name']}
Tagline: {self.product['tagline']}
Category: {self.product['category']}
Description: {self.product['description']}
Target Audience: {self.product.get('target_audience', 'Technology and business decision makers')}
Pricing & Packages: {pricing_text}
Core Capabilities / Features: {features_text}
Customer Pain Points: {pain_points_text}
Key Metrics / Value Proof: {stats_text}
Primary Demo Offer: {self.product.get('demo_offer', '')}
Special Incentive: {self.product.get('special_offer', '')}

OBJECTION HANDLING PLAYBOOK:
{objections_text}

EXPERT SALESPERSON CORE PRINCIPLES (MUST FOLLOW ALL 4):
1. EXPERT & EMPATHETIC HANDLING:
   - Act as a trusted strategic advisor, not a transactional pusher.
   - Always validate and warmly acknowledge the customer's input first ("I completely appreciate that...", "That makes total sense...", "Thank you for sharing that context...").
2. PROACTIVE SALES DISCOVERY:
   - A great salesperson diagnoses before prescribing.
   - During the discovery phase, ALWAYS conclude your response with ONE insightful, consultative question to uncover their situation, bottlenecks, scale, or decision timeline.
   - Example discovery questions:
     * "How is your team currently hosting your critical workloads today?"
     * "What is the single biggest bottleneck you're experiencing—is it infrastructure cost, scalability during peak loads, or deployment speed?"
     * "What timeline is your engineering team targeting for this modernization?"
3. NEEDS-BASED CONSULTATIVE SELLING:
   - Sell strictly based on the customer's stated needs:
     * If they focus on COST/BILLS: Highlight AWS Savings Plans (up to 72% compute savings), 45% lower TCO, and up to $5,000 in POC credits.
     * If they focus on DOWNTIME/SCALABILITY: Highlight 99.999% SLA availability across multi-AZs, automated auto-scaling, and zero-downtime DMS migration.
     * If they focus on GENERATIVE AI/INNOVATION: Highlight Amazon Bedrock foundation models (Claude, Llama) with private enterprise VPC data protection.
     * If they focus on SECURITY/COMPLIANCE: Highlight SOC 2, HIPAA, ISO certifications, IAM, and continuous GuardDuty monitoring.
4. CONSISTENTLY POLITE & RESPECTFUL TONE:
   - Maintain an impeccably courteous, respectful, and friendly tone at all times.
   - Never argue, interrupt, or sound defensive.
   - If the prospect politely declines, respect their decision gracefully and thank them warmly for their time.

CLOSING METHODOLOGY:
- Offer a tailored 30-minute Cloud Architecture & Migration Assessment with an AWS Certified Solutions Architect and up to $5,000 in POC credits.
- Prompt for their preference: "Does tomorrow morning or afternoon work better for your calendar?"
- If customer picks a time (e.g. morning, 10 AM, afternoon, 2 PM), warmly confirm the reservation and conclude gracefully.

VOICE GUIDELINES:
- Output MUST be conversational spoken English (or the chosen language), 1 to 3 punchy sentences max (under 120 words).
- NEVER use markdown symbols (no asterisks, bullet points, hashes, or bold text).
- Language: {lang_instruction}
"""

    def _rule_based_response(self, user_msg, conversation_history=None):
        msg_clean = user_msg.strip()
        msg_lower = msg_clean.lower()
        history = conversation_history or []
        turn_count = len(history)
        is_aws = (self.product.get("id") == "aws-services")

        # 0. Check for gibberish / extremely short invalid input
        is_gibberish = False
        words = re.findall(r'[a-zA-Z0-9\u0900-\u097F\u0C00-\u0C7F]+', msg_clean)
        valid_short_words = {"hi", "ok", "yes", "no", "bye", "hey", "10", "11", "12", "1", "2", "3", "am", "pm", "हाँ", "సరే", "aws"}
        if len(msg_clean) <= 3 and msg_lower not in valid_short_words:
            is_gibberish = True
        elif len(words) == 1 and len(words[0]) >= 3 and not any(v in words[0].lower() for v in "aeiouy") and not any('\u0900' <= c <= '\u097F' or '\u0C00' <= c <= '\u0C7F' for c in words[0]):
            is_gibberish = True

        if is_gibberish:
            if self.language == "hi":
                return "माफ़ कीजिए, मुझे आपकी बात समझ नहीं आई। क्या आप दोहरा सकते हैं?"
            elif self.language == "te":
                return "క్షమించండి, మీ మాటలు అర్థం కాలేదు. దయచేసి మళ్ళీ చెప్పగలరా?"
            return "I didn't quite catch that. Could you please repeat?"

        # Identify last bot statement
        last_bot_msg = ""
        for turn in reversed(history):
            if turn.get("sender") == "bot":
                last_bot_msg = turn.get("text", "").lower()
                break

        # Check conversation flags
        demo_already_booked = any("booked your" in turn.get("text", "").lower() or "reserved" in turn.get("text", "").lower() for turn in history if turn.get("sender") == "bot")

        # If demo was already booked earlier, handle wrap-up gracefully
        if demo_already_booked:
            if any(w in msg_lower for w in ["thank", "thanks", "bye", "ok", "okay", "great", "cool", "see you", "yes", "sure", "afternoon", "morning", "perfect", "sounds good", "धन्यवाद", "ధన్యవాదాలు"]):
                if self.language == "hi":
                    return "आपका बहुत-बहुत धन्यवाद! कल मिलते हैं, अपना ख्याल रखिएगा।"
                elif self.language == "te":
                    return "చాలా ధన్యవాదాలు! రేపు కలుద్దాం, సెలవు!"
                return "You're all confirmed on our calendar! If you have any questions before our session, feel free to review your invite. Thanks again, and we look forward to speaking soon!"

        bot_asked_demo_time = (
            any(p in last_bot_msg for p in [
                "morning or afternoon", "suit you better", "which time", "what time",
                "schedule a tailored", "which one works", "schedule a quick", "architecture assessment", "live demo"
            ])
        ) and not demo_already_booked

        # ================= CONTEXTUAL SLOT FILLING =================
        time_slot_words = [
            "morning", "afternoon", "evening", "tomorrow", "today", "tomorrow morning", "tomorrow afternoon",
            "10", "11", "12", "1", "2", "3", "4", "5", "am", "pm", "monday", "tuesday", "wednesday", "thursday", "friday",
            "works better", "anytime", "morning works", "afternoon works", "either", "सुबह", "दोपहर", "कल", "ఉదయం", "మధ్యాహ్నం", "రేపు"
        ]
        user_picked_time = any(w in msg_lower for w in time_slot_words)
        user_proposed_direct_time = any(p in msg_lower for p in ["tomorrow morning", "tomorrow afternoon", "morning at 10", "afternoon at 2", "10 am", "2 pm", "10am", "2pm"])

        if (bot_asked_demo_time and user_picked_time) or (user_proposed_direct_time and not demo_already_booked):
            slot_name = "tomorrow morning at 10:00 AM" if ("morning" in msg_lower or "सुबह" in msg_lower or "ఉదయం" in msg_lower or "10" in msg_lower) else "tomorrow afternoon at 2:00 PM"
            if self.language == "hi":
                if is_aws:
                    return f"शानदार! मैंने आपके लिए {slot_name} का 30 मिनट का एडवांस्ड क्लाउड आर्किटेक्चर असेसमेंट और एडब्ल्यूएस क्रेडिट्स बुक कर दिया है। आपको ईमेल पर कैलेंडर लिंक मिल जाएगा। बातचीत के लिए बहुत धन्यवाद, आपका दिन शुभ हो!"
                return f"शानदार! मैंने आपके लिए {slot_name} का 15 मिनट का लाइव डेमो बुक कर दिया है। आपको ईमेल पर कैलेंडर लिंक मिल जाएगा। बातचीत के लिए बहुत धन्यवाद, आपका दिन शुभ हो!"
            elif self.language == "te":
                if is_aws:
                    return f"అద్భుతం! మీ కోసం {slot_name} న 30 నిమిషాల AWS క్లౌడ్ ఆర్కిటెక్చర్ సెషన్ సిద్ధం చేశాము. మీకు ఆహ్వానం అందుతుంది. చాలా ధన్యవాదాలు!"
                return f"అద్భుతం! మీ కోసం {slot_name} న లైవ్ డెమో సిద్ధం చేశాము. మీకు క్యాలెండర్ ఆహ్వానం అందుతుంది. చాలా ధన్యవాదాలు!"
            
            if is_aws:
                return f"Perfect! I have reserved {slot_name} for your Cloud Architecture & Migration Assessment with our AWS Certified Solutions Architect, along with your AWS Proof-of-Concept credits. You'll receive the calendar invite shortly. Thank you so much for your time today, and have an awesome day ahead!"
            return f"Perfect! I have reserved {slot_name} for your live demo with our senior solution architect, along with your 14-day enterprise trial. You'll receive the calendar invite shortly. Thank you so much for your time today, and have an awesome day ahead!"

        # ================= OBJECTIONS =================
        # 1. Too expensive / Budget issues
        if any(w in msg_lower for w in ["too expensive", "expensive", "costs too much", "cannot afford", "no budget", "tight budget", "costly", "price is high", "महंगा", "बजट नहीं", "ధర ఎక్కువ", "బడ్జెట్ లేదు"]):
            if self.language == "hi":
                if is_aws:
                    return "मैं बजट की बात पूरी तरह समझता हूँ। एडब्ल्यूएस सेविंग्स प्लान्स और स्पॉट इंस्टेंस से 72% तक लागत कम हो जाती है। क्या हम एक निःशुल्क आर्किटेक्चर कॉस्ट असेसमेंट और $5,000 क्रेडिट्स के साथ शुरुआत करें?"
                return "मैं बजट की बात पूरी तरह समझता हूँ। हमारे क्लाइंट्स पहले 30 दिनों में ही 4 गुना ROI देखते हैं क्योंकि यह तब भी लीड्स कन्वर्ट करता है जब आपकी टीम सो रही हो। क्या हम 14 दिन के रिस्क-फ्री ट्रायल से शुरुआत करें?"
            return self.product["objections"]["price"]

        # 2. Competitor / Already using something
        if any(w in msg_lower for w in ["competitor", "already have", "using another", "already using", "hubspot", "salesforce", "outreach", "apollo", "zoominfo", "azure", "gcp", "google cloud", "digitalocean", "rackspace"]):
            if self.language == "hi":
                if is_aws:
                    return "बहुत अच्छी बात है कि आप Azure या GCP पर विचार कर रहे हैं! AWS 200 से अधिक सेवाएं और सुरक्षित Amazon Bedrock AI प्रदान करता है। क्या आप प्राथमिक रूप से डेटाबेस या AI मॉडल्स का मूल्यांकन कर रहे हैं?"
                return f"बहुत अच्छी बात है कि आप पहले से टूल्स इस्तेमाल कर रहे हैं! {self.product['name']} साधारण ईमेल या बॉट्स के बजाय वास्तविक इंसानी आवाज़ में बात करके सीधे आपके कैलेंडर में मीटिंग बुक करता है। क्या आप 15 मिनट का डेमो देखना चाहेंगे?"
            return self.product["objections"]["competitor"]

        # 3. Timing / Busy / Later
        if any(w in msg_lower for w in ["busy", "later", "next month", "next quarter", "no time", "not now", "call later", "बाद में", "తరువాత"]):
            if self.language == "hi":
                if is_aws:
                    return "मैं समझ सकता हूँ कि आप व्यस्त हैं! एडब्ल्यूएस डेटाबेस माइग्रेशन सर्विस के साथ माइग्रेशन में कोई डाउनटाइम नहीं होता। क्या मैं आपके ईमेल पर एक संक्षिप्त ओवरव्यू भेज दूँ?"
                return "मैं समझ सकता हूँ कि आप व्यस्त हैं! इसका सेटअप 15 मिनट में हो जाता है। क्या मैं आपके ईमेल पर एक संक्षिप्त 2-मिनट का वीडियो ओवरव्यू भेज दूँ ताकि आप जब चाहें देख सकें?"
            return self.product["objections"]["timing"]

        # 4. Authority / Need to discuss with boss/team
        if any(w in msg_lower for w in ["boss", "manager", "discuss with", "discuss this", "check with", "talk to my", "speak to my", "ask my", "colleagues", "partner", "permission", "cto", "leadership"]):
            if self.language == "hi":
                if is_aws:
                    return "बिल्कुल, सीटीओ और इंजीनियरिंग टीम के साथ चर्चा बहुत महत्वपूर्ण है! क्यों न हम आपकी टीम के साथ 30 मिनट का कस्टमाइज़्ड AWS आर्किटेक्चर सेशन रख लें? कल या परसों में कौन सा समय सही रहेगा?"
                return "बिल्कुल, टीम के साथ विचार-विमर्श करना बहुत ज़रूरी है! क्यों न हम आपकी टीम के साथ 15 मिनट का एक लाइव कस्टमाइज़्ड डेमो रख लें ताकि सभी इसे एक साथ देख सकें? कल या परसों में कौन सा समय सही रहेगा?"
            return self.product["objections"]["authority"]

        # ================= BUYING SIGNALS & DEMO REQUESTS =================
        if any(w in msg_lower for w in ["demo", "book", "schedule", "sign up", "try it", "assessment", "consultation", "डेमो", "డెమో"]):
            if self.language == "hi":
                if is_aws:
                    return "शानदार! मैं आपके लिए 30 मिनट का AWS क्लाउड आर्किटेक्चर असेसमेंट बुक कर सकता हूँ। क्या कल सुबह का समय बेहतर रहेगा या दोपहर का?"
                return "शानदार! मैं आपके लिए 15 मिनट का लाइव डेमो बुक कर सकता हूँ। क्या आपके कैलेंडर के लिए कल सुबह का समय बेहतर रहेगा या दोपहर का?"
            elif self.language == "te":
                return "అద్భుతం! నేను మీ కోసం 30 నిమిషాల సెషన్‌ను షెడ్యూల్ చేయగలను. మీ క్యాలెండర్‌కు రేపు ఉదయం అనుకూలమా లేదా మధ్యాహ్నమా?"
            
            if is_aws:
                return "That sounds amazing! I can schedule a tailored 30-minute Cloud Architecture & Migration Assessment with our AWS Certified Solutions Architect and allocate up to $5,000 in AWS POC credits. Does tomorrow morning or afternoon work better for your calendar?"
            return "That sounds amazing! I can schedule a tailored 15-minute live demo with our senior solution architect and activate your 14-day free trial right away. Does tomorrow morning or afternoon work better for your calendar?"

        # ================= DEFINITE NO =================
        definite_no_phrases = ["not interested", "no thanks", "don't want", "dont want", "ruchi nahi", "दिलचस्पी नहीं", "వద్దు", "not looking"]
        single_words = set(re.findall(r'\b\w+\b', msg_lower))
        if any(w in msg_lower for w in definite_no_phrases) or "never" in single_words or "stop" in single_words:
            if self.language == "hi":
                if is_aws:
                    return AWS_GREETINGS["hi"]["declined"]
                return GREETINGS["hi"]["declined"]
            elif self.language == "te":
                if is_aws:
                    return AWS_GREETINGS["te"]["declined"]
                return GREETINGS["te"]["declined"]
            
            if is_aws:
                return "I completely understand! We appreciate you being upfront. If your team looks into cloud modernization, migration funding, or Amazon Bedrock AI in the future, we're always ready to help. Have a wonderful day!"
            return "I completely understand! We appreciate you being upfront. If your sales workflow needs an AI boost in the future, we're always here at nexuspulse.ai. Thank you for your time and have a wonderful day!"

        # ================= NEEDS-BASED SELLING & DISCOVERY QUESTIONS =================
        # 1. Cost & Overspending Need
        if any(w in msg_lower for w in ["bill is high", "skyrocketing", "expensive hosting", "cut costs", "reduce cost", "reduce costs", "save money", "spend too much", "spending too much", "reduce our bill", "cost optimization", "reduce spend", "reduce spending", "hosting costs", "cloud bill"]):
            if self.language == "hi":
                if is_aws:
                    return "मैं आपकी बात पूरी तरह समझता हूँ। AWS इंफ्रास्ट्रक्चर लागत को 45% तक कम करने और सेविंग्स प्लान्स के ज़रिए 72% तक छूट दिलाने में मदद करता है। क्या आपकी टीम मुख्य रूप से सर्वर या डेटाबेस की लागत कम करना चाहती है?"
                return "मैं आपकी चिंता समझता हूँ। हमारा AI प्लेटफॉर्म मैन्युअल सेल्स की लागत को 70% तक घटा देता है। वर्तमान में आपकी टीम का मासिक आउटबाउंड खर्च कितना है?"
            elif self.language == "te":
                if is_aws:
                    return "నేను మీ పరిస్థితిని అర్థం చేసుకోగలను. AWS ద్వారా క్లౌడ్ ఖర్చులను 45% వరకు తగ్గించుకోవచ్చు. మీరు ప్రధానంగా కంప్యూట్ ఖర్చులను తగ్గించాలనుకుంటున్నారా?"
                return "నేను అర్థం చేసుకోగలను. మా AI ప్లాట్‌ఫారమ్ ఖర్చులను 70% వరకు తగ్గిస్తుంది. ప్రస్తుతం మీ సేల్స్ ఖర్చు ఎంత ఉంది?"
            
            if is_aws:
                return "I completely understand—unpredictable infrastructure bills are a top concern for engineering teams. With AWS, we routinely help companies reduce their infrastructure TCO by up to 45% through auto-scaling and AWS Savings Plans offering up to 72% discounts. What are your primary workloads driving the highest costs right now—compute instances, databases, or data transfer?"
            return f"I completely understand—controlling sales overhead is crucial. {self.product['name']} typically reduces lead acquisition and qualification costs by up to 70% compared to traditional outbound SDRs. What is your current monthly spend on outbound lead generation?"

        # 2. Downtime, Outages & Scalability Need
        if any(w in msg_lower for w in ["downtime", "crashes", "crashing", "traffic spike", "outages", "outage", "slow performance", "unreliable", "server down", "scaling issues", "scalability"]):
            if self.language == "hi":
                if is_aws:
                    return "डाउनटाइम वास्तव में व्यापार और ग्राहकों के विश्वास को प्रभावित करता है। AWS 99.999% SLA विश्वसनीयता और ऑटो-स्केलिंग प्रदान करता है। क्या आपके ऍप्लिकेशन्स वर्चुअल मशीन्स पर चल रहे हैं या कंटेनर्स पर?"
                return "लीड्स का छूटना सीधे राजस्व को प्रभावित करता है। हमारा AI बिना किसी डाउनटाइम के 24/7 तुरंत कॉल्स संभालता है। क्या आपके पास ऑफ-आवर्स में आने वाले लीड्स मिस हो रहे हैं?"
            elif self.language == "te":
                if is_aws:
                    return "డౌన్‌టైమ్ వ్యాపారానికి చాలా నష్టం కలిగిస్తుంది. AWS 99.999% లభ్యతను అందిస్తుంది. మీ అప్లికేషన్లు వర్చువల్ మెషీన్లపై నడుస్తున్నాయా లేక కంటైనర్లలోనా?"
                return "కస్టమర్లను కోల్పోవడం వ్యాపారాన్ని దెబ్బతీస్తుంది. మా AI 24/7 అందుబాటులో ఉంటుంది. మీకు ఈ సమస్య ఎదురవుతోందా?"
            
            if is_aws:
                return "I hear you—downtime directly impacts revenue and user trust. AWS delivers industry-leading 99.999% SLA availability across Multi-AZ architectures with Elastic Load Balancing to absorb traffic spikes seamlessly. Are your current applications containerized on Docker or Kubernetes, or running on traditional virtual machines?"
            return f"I hear you—slow response times and missed calls directly hurt conversions. {self.product['name']} handles thousands of simultaneous calls 24/7 with zero hold time and 99.9% uptime. How many inbound inquiries are currently getting delayed or missed after hours?"

        # 3. Generative AI & Foundation Models Need
        if any(w in msg_lower for w in ["generative ai", "genai", "llm", "bedrock", "claude", "foundation models", "ai features", "ai models", "custom models", "gpt"]):
            if self.language == "hi":
                if is_aws:
                    return "यह सुनकर बहुत अच्छा लगा! Amazon Bedrock के ज़रिए आप Claude 3.5 और Titan जैसे शीर्ष मॉडल्स को सुरक्षित रूप से उपयोग कर सकते हैं। क्या आप कस्टमर-फेसिंग AI बना रहे हैं या इंटरनल वर्कफ़्लो के लिए?"
                return "शानदार! हमारा AI प्लेटफॉर्म अत्याधुनिक LLMs का उपयोग करके प्राकृतिक बातचीत करता है। आप विशेष रूप से किस प्रकार के सेल्स कॉल्स को ऑटोमेट करना चाहते हैं?"
            elif self.language == "te":
                if is_aws:
                    return "చాలా సంతోషం! Amazon Bedrock ద్వారా మీరు Claude మరియు Titan మోడళ్లను సురక్షితంగా ఉపయోగించవచ్చు. మీరు కస్టమర్ AI లేదా అంతర్గత ఆటోమేషన్ కోసం చూస్తున్నారా?"
                return "అద్భుతం! మా ప్లాట్‌ఫారమ్ తాజా AI మోడళ్లను ఉపయోగిస్తుంది. మీరు ఏ వర్క్‌ఫ్లోను ఆటోమేట్ చేయాలనుకుంటున్నారు?"
            
            if is_aws:
                return "That's exciting! Amazon Bedrock provides fully managed access to leading foundation models like Claude 3.5 Sonnet and Amazon Titan through a single API, with enterprise privacy where your data is never used to train base models. Are you planning to build customer-facing AI applications or internal workflow automation?"
            return f"That's great! {self.product['name']} utilizes state-of-the-art conversational LLMs and ultra-low latency voice models to deliver human-like sales conversations. What specific customer touchpoints are you most eager to automate with AI?"

        # 4. Security, Compliance & Governance Need
        if any(w in msg_lower for w in ["security", "compliance", "soc 2", "soc2", "hipaa", "gdpr", "pci", "data privacy", "isolated", "encryption"]):
            if self.language == "hi":
                if is_aws:
                    return "सुरक्षा AWS की सर्वोच्च प्राथमिकता है। AWS SOC 2, HIPAA, और PCI-DSS सहित 143 सुरक्षा मानकों का समर्थन करता है। आपकी संस्था को मुख्य रूप से कौन से अनुपालन नियमों को पूरा करना है?"
                return "सुरक्षा हमारी सर्वोच्च प्राथमिकता है। हमारा प्लेटफ़ॉर्म SOC 2 और GDPR अनुरूप है और सभी कॉल्स एन्क्रिप्टेड हैं। क्या आपकी कंपनी की कोई विशेष सुरक्षा आवश्यकताएं हैं?"
            elif self.language == "te":
                if is_aws:
                    return "భద్రత AWS అత్యంత ప్రాధాన్యత. AWS SOC 2, HIPAA వంటి 143 భద్రతా ప్రమాణాలకు మద్దతు ఇస్తుంది. మీకు ఏ సర్టిఫికేషన్లు అవసరం?"
                return "భద్రత మా మొదటి ప్రాధాన్యత. మా ప్లాట్‌ఫారమ్ పూర్తిగా సురక్షితం. మీ సంస్థకు నిర్దిష్ట డేటా నిబంధనలు ఉన్నాయా?"
            
            if is_aws:
                return "Security is job zero at AWS. The AWS Cloud supports 143 security standards including SOC 1/2/3, HIPAA, PCI-DSS, and FedRAMP, with fine-grained IAM controls and end-to-end encryption in private VPCs. Which specific compliance certifications or data residency regulations does your organization need to meet?"
            return f"Security is our top priority. {self.product['name']} is SOC 2 compliant, fully GDPR ready, and all call transcripts and audio streams are encrypted end-to-end. Does your company require specific data retention or compliance policies for customer conversations?"

        # 5. Current Setup / Discovery Trigger (On-premise / Datacenter / Manual workflow)
        if any(w in msg_lower for w in ["on-premise", "on-prem", "our own servers", "bare metal", "colocation", "datacenter", "private datacenter", "local servers", "manage our own"]):
            if self.language == "hi":
                if is_aws:
                    return "यह साझा करने के लिए बहुत धन्यवाद! अपने स्वयं के सर्वर प्रबंधित करने में काफी रखरखाव लगता है। आपके वर्तमान ऑन-प्रिमाइसेस सेटअप में सबसे बड़ी चुनौती क्या है — हार्डवेयर लागत, पीक लोड पर स्केलिंग, या डिप्लॉयमेंट की गति?"
                return "यह साझा करने के लिए धन्यवाद! आपके वर्तमान वर्कफ़्लो में सबसे बड़ी बाधा क्या है — फॉलो-अप का समय या कॉल वॉल्यूम?"
            elif self.language == "te":
                if is_aws:
                    return "చెప్పినందుకు ధన్యవాదాలు! మీ ప్రస్తుత సెటప్‌లో అతిపెద్ద సమస్య నిర్వహణ ఖర్చా లేక ట్రాఫిక్ పెరిగినప్పుడు స్కేల్ చేయడమా?"
                return "చెప్పినందుకు ధన్యవాదాలు! మీ ప్రస్తుత విధానంలో అతిపెద్ద సవాలు ఏమిటి?"
            
            if is_aws:
                return "Thank you for sharing that! Managing your own infrastructure gives you control, but hardware refreshes and maintenance can become a heavy lift. What is the single biggest bottleneck with your on-premise setup today—is it hardware maintenance costs, scalability during peak traffic, or deployment speed?"
            return f"Thank you for sharing that! Relying on manual workflows gives you hands-on control, but can bottleneck your team's growth. What is the biggest challenge your team faces today—follow-up speed, call volume, or lead qualification accuracy?"

        # ================= PRICING INQUIRY =================
        if any(w in msg_lower for w in ["price", "cost", "pricing", "how much", "charges", "rate", "plans", "plan", "budget", "billing", "कीमत", "दाम", "लागत", "ధర", "ఖర్చు"]):
            if self.language == "hi":
                if is_aws:
                    return "AWS फ्लेक्सिबल पे-एज़-यू-गो मॉडल पर काम करता है। हमारे स्टार्टर माइग्रेशन प्लान $499 प्रति माह से शुरू होते हैं और इसमें $5,000 तक के AWS POC क्रेडिट्स शामिल हैं। क्या आप एक फ्री कॉस्ट असेसमेंट आज़माना चाहेंगे?"
                return f"हमारा स्टार्टर प्लान सिर्फ $99 प्रति माह से शुरू होता है और ग्रोथ प्लान $299 है। साथ ही अभी हम 14 दिन का फ्री ट्रायल और 1000 फ्री मिनट्स दे रहे हैं। क्या आप इसका फ्री ट्रायल आज़माना चाहेंगे?"
            elif self.language == "te":
                if is_aws:
                    return "AWS పే-యాజ్-యు-గో మోడల్‌లో పనిచేస్తుంది. మా మైగ్రేషన్ ప్లాన్లు నెలకు $499 నుండి ప్రారంభమవుతాయి మరియు $5,000 వరకు POC క్రెడిట్లను అందిస్తాయి. మీరు ఉచిత ఖర్చుల అంచనాను చూడాలనుకుంటున్నారా?"
                return f"మా స్టార్టర్ ప్లాన్ కేవలం $99 నెలకు ప్రారంభమవుతుంది. అలాగే ప్రస్తుతం 14 రోజుల ఉచిత ట్రయల్ లభిస్తుంది. మీరు ఒకసారి దీన్ని ప్రయత్నించి చూడాలనుకుంటున్నారా?"
            
            if is_aws:
                return "AWS operates on a flexible pay-as-you-go model with Savings Plans that reduce compute spend by up to 72%. Our managed Starter Migration packages start at $499 per month, backed by up to $5,000 in AWS POC credits. Would you like to explore a free Cloud Cost & Architecture Assessment?"
            return f"Our plans start at just $99 per month for Starter, and $299 for our popular Growth tier with full voice cloning and CRM sync. Plus, we offer a risk-free 14-day free trial. Would you like me to set you up with the trial?"

        # ================= GENERIC YES / SURE / SOUNDS GOOD =================
        yes_phrases = ["yes", "yeah", "yep", "sure", "sounds good", "interested", "okay", "i am interested", "definitely", "हाँ", "जरूर", "అవును", "సరే"]
        if any(w in msg_lower for w in yes_phrases) or "ok" in single_words:
            if bot_asked_demo_time:
                if self.language == "hi":
                    return "बहुत बढ़िया! आपके लिए कौन सा समय बेहतर रहेगा — सुबह 10 बजे या दोपहर 2 बजे?"
                elif self.language == "te":
                    return "చాలా మంచిది! మీకు ఏ సమయం అనుకూలంగా ఉంటుంది — ఉదయం 10 గంటలకా లేదా మధ్యాహ్నం 2 గంటలకా?"
                return "Awesome! Which one works better for you — 10:00 AM in the morning or 2:00 PM in the afternoon?"
            else:
                if self.language == "hi":
                    if is_aws:
                        return "बहुत खूब! क्या आप कल एक 30 मिनट का AWS आर्किटेक्चर असेसमेंट देखना चाहेंगे जहां हम आपके क्लाउड माइग्रेशन और लागत बचत पर चर्चा कर सकें?"
                    return "बहुत खूब! क्या आप कल एक 15 मिनट का लाइव डेमो देखना चाहेंगे जहां हम आपके लीड्स को कन्वर्ट करना दिखा सकें?"
                elif self.language == "te":
                    return "చాలా బాగుంది! రేపు 30 నిమిషాల AWS క్లౌడ్ ఆర్కిటెక్చర్ సెషన్ చూడాలనుకుంటున్నారా?"
                
                if is_aws:
                    return "That sounds great! I'd love to set up a quick 30-minute Cloud Architecture & Migration Assessment with our AWS Certified Solutions Architect to review your infrastructure. Does tomorrow morning or afternoon suit you better?"
                return "That sounds great! I'd love to set up a quick 15-minute live demo with our senior solution architect to show you how it works hands-on. Does tomorrow morning or afternoon suit you better?"

        # ================= FEATURES / HOW IT WORKS / CLOUD / MIGRATION =================
        if any(w in msg_lower for w in ["how it works", "features", "what does it do", "how does it work", "integration", "crm", "zapier", "what is it", "cloud", "aws", "migration", "server", "ec2", "s3", "bedrock", "ai", "database", "rds", "lambda", "kubernetes", "hosting", "infrastructure", "काम कैसे करता है", "ఎలా పనిచేస్తుంది"]):
            if self.language == "hi":
                if is_aws:
                    return "शानदार तकनीक! AWS इलास्टिक EC2 कंप्यूट, S3 स्टोरेज, RDS डेटाबेस और अमेज़ॅन बेडरॉक के ज़रिए उन्नत जेनरेटिव एआई प्रदान करता है। क्या आप 30 मिनट का लाइव आर्किटेक्चर सेशन देखना चाहेंगे?"
                return f"शानदार! {self.product['name']} आपकी वेबसाइट और विज्ञापनों से आने वाले ग्राहकों को तुरंत कॉल करता है, उनके सवालों के जवाब देता है और मीटिंग बुक करता है। क्या आप इसका लाइव डेमो देखना चाहेंगे?"
            
            if is_aws:
                return "That sounds like a great architecture direction! AWS provides enterprise compute with Amazon EC2 and Lambda, durable S3 storage, managed RDS databases, and cutting-edge Generative AI on Amazon Bedrock, all backed by 99.999% SLA reliability. Would you like to schedule a quick 30-minute Cloud Architecture Assessment to see how it fits your stack?"
            return f"That's great! {self.product['name']} instantly engages your inbound leads with natural sub-second voice AI, answers their queries, qualifies their budget, and directly schedules qualified calls on your sales calendar. Would you like to see a quick 15-minute live demo of it in action?"

        # ================= GREETINGS / SMALL TALK =================
        greeting_words = [
            "good", "doing good", "doing well", "fine", "great", "im good", "i am good", "i'm good", "all good",
            "pretty good", "not bad", "awesome", "nice", "hello", "hi", "hey", "good morning", "good afternoon",
            "doing fine", "who are you", "नमस्ते", "బాగున్నాను", "బాగుంది"
        ]
        if any(w in msg_lower for w in greeting_words):
            if self.language == "hi":
                if is_aws:
                    return f"यह सुनकर बहुत खुशी हुई! मैं AWS क्लाउड सॉल्यूशंस से हूँ। क्या आपकी टीम वर्तमान इंफ्रास्ट्रक्चर की लागत घटाने या एडब्ल्यूएस पर क्लाउड माइग्रेशन में रुचि रखती है?"
                return f"यह सुनकर बहुत खुशी हुई! मैं {self.product['name']} से हूँ। क्या आप अपनी कंपनी में नए ग्राहकों को आकर्षित करने और सेल्स बढ़ाने के नए तरीकों में रुचि रखते हैं?"
            elif self.language == "te":
                if is_aws:
                    return "చాలా సంతోషం! నేను AWS నుండి మాట్లాడుతున్నాను. మీ కంపెనీ క్లౌడ్ ఖర్చులను తగ్గించుకోవడంలో మరియు ఆధునీకరించడంలో ఆసక్తి కలిగి ఉన్నారా?"
                return f"చాలా సంతోషం! నేను {self.product['name']} నుండి మాట్లాడుతున్నాను. మీ అమ్మకాలను 3 రెట్లు పెంచే AI టెక్నాలజీ గురించి తెలుసుకోవాలనుకుంటున్నారా?"
            
            if is_aws:
                return "Glad to hear that! The reason I'm reaching out is that many engineering teams face high on-prem datacenter costs and are looking to modernize with AWS cloud infrastructure and Generative AI on Bedrock. How is your team currently hosting your workloads?"
            return f"Glad to hear that! The reason I'm reaching out is that many B2B teams lose up to 60% of their inbound leads because reps take hours to respond. How is your team currently handling inbound lead follow-up times?"

        # ================= DYNAMIC ROTATING FALLBACKS (ANTI-REPETITION) =================
        fallback_options_aws = [
            f"That's a great point! With AWS Cloud Solutions, our certified architects can help reduce your infrastructure TCO by up to 45% and migrate workloads with zero downtime using AWS DMS. Would you be open to a quick 30-minute architecture review this week?",
            f"I hear you! Many engineering leaders choose AWS to eliminate hardware bottlenecks and accelerate deployment of Generative AI microservices using Amazon Bedrock. Are you looking to modernize your cloud or AI architecture this quarter?",
            f"Understood! We make cloud adoption effortless with automated replication and up to $5,000 in AWS POC credits. Would it be helpful to schedule a brief session with an AWS Solutions Architect, or would you prefer a quick overview document?"
        ]

        fallback_options_en = fallback_options_aws if is_aws else [
            f"That's a great point! With {self.product['name']}, our autonomous voice platform can handle inbound leads within 15 seconds and sync directly with your CRM. Would you be open to a quick 15-minute live demo this week to see it in action?",
            f"I hear you! Many sales leaders use {self.product['name']} to eliminate manual outbound calling and accelerate revenue. Are you looking to improve your sales team's pipeline velocity this quarter?",
            f"Understood! We make it effortless to qualify leads and auto-schedule meetings 24/7. Would it be helpful if I sent you a quick 2-minute overview video, or would you prefer a live demo?"
        ]

        fallback_idx = (turn_count // 2) % len(fallback_options_en)
        if self.language == "hi":
            if is_aws:
                return "बहुत बढ़िया बात! AWS क्लाउड सॉल्यूशंस आपकी इंफ्रास्ट्रक्चर लागत को 45% तक कम कर सकता है और बेडरॉक के ज़रिए एआई मॉडल्स तैनात कर सकता है। क्या आप इस हफ्ते एक 30 मिनट का आर्किटेक्चर रिव्यू देखना चाहेंगे?"
            return f"बहुत बढ़िया बात! {self.product['name']} आपकी सेल्स को 3 गुना बढ़ा सकता है और 15 सेकंड में लीड्स को कॉल कर सकता है। क्या आप इस हफ्ते एक छोटा 15 मिनट का लाइव डेमो देखना चाहेंगे?"
        elif self.language == "te":
            if is_aws:
                return "చాలా మంచి ప్రశ్న! AWS క్లౌడ్ సొల్యూషన్స్ మీ ఇన్ఫ్రాస్ట్రక్చర్ ఖర్చులను 45% తగ్గించగలదు. ఈ వారం 30 నిమిషాల ఆర్కిటెక్చర్ రివ్యూ చూడటానికి మీకు వీలవుతుందా?"
            return f"చాలా మంచి ప్రశ్న! {self.product['name']} కేవలం 15 సెకన్లలో కస్టమర్ల కాల్స్ తీసుకొని నేరుగా మీ CRM కు కనెక్ట్ చేస్తుంది. ఈ వారం 15 నిమిషాల లైవ్ డెమో చూడటానికి మీకు వీలవుతుందా?"

        return fallback_options_en[fallback_idx]
