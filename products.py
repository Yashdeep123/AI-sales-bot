"""Product catalog for sales bot."""

SAAS_PRODUCTS = {
    "nexus-ai": {
        "id": "nexus-ai",
        "name": "NexusPulse AI",
        "tagline": "Autonomous B2B Lead Conversion & Sales Pipeline Automation",
        "category": "AI Sales & Revenue Acceleration",
        "description": "NexusPulse AI is an enterprise-grade AI sales agent platform that automatically engages, qualifies, and schedules meetings with inbound and outbound leads 24/7, accelerating pipeline velocity by 300%.",
        "target_audience": "B2B SaaS companies, sales leaders, revenue operations, and agencies.",
        "pricing": [
            {"name": "Starter", "price": "$99/mo", "features": "Up to 1,000 automated lead calls, CRM integration, email follow-ups"},
            {"name": "Growth", "price": "$299/mo", "features": "Up to 5,000 calls, voice cloning, multi-language, objection auto-handling, Slack alerts"},
            {"name": "Enterprise", "price": "$799/mo", "features": "Unlimited calls, dedicated account manager, custom CRM webhooks, SOC-2 compliance, custom SLA"}
        ],
        "features": [
            "Real-time voice conversation with sub-second latency",
            "Automatic qualification using BANT (Budget, Authority, Need, Timeline)",
            "Zero-latency calendar scheduling with Google Meet & Zoom integration",
            "Native sync with HubSpot, Salesforce, Pipedrive, and Zoho",
            "Automated multi-channel follow-ups via SMS and WhatsApp"
        ],
        "pain_points": [
            "Leads going cold because sales reps take hours or days to respond",
            "High SDR hiring and training costs with high turnover rates",
            "Inconsistent pitch quality and missed objection-handling opportunities",
            "Difficulty scaling sales across different time zones and languages"
        ],
        "stats": [
            "3.4x higher conversion rate than traditional web forms",
            "Average response time under 15 seconds",
            "Over 40% reduction in customer acquisition cost (CAC)"
        ],
        "objections": {
            "price": "I completely understand budget is top of mind. Most of our clients see a 4x return on investment within the first 30 days alone because it captures high-intent leads while your team sleeps. Plus, we offer a risk-free 14-day trial.",
            "competitor": "That's great you're already leveraging sales tools! Unlike legacy tools that only send cold emails or rigid chat popups, NexusPulse conducts realistic, interactive voice calls that feel human and book meetings directly into your calendar.",
            "timing": "I completely hear you on timing. The beauty of NexusPulse is that implementation takes under 15 minutes with our 1-click CRM integrations. You can have it qualifying leads today without slowing down your current sprint.",
            "authority": "Totally understand you'd like to align with your team and leadership. How about I set up a quick 15-minute tailored live demo with our senior solution architect so your team can test it hands-on together?",
            "trust": "We are SOC-2 Type II certified and trusted by over 450 fast-growing B2B companies with 99.9% uptime."
        },
        "demo_offer": "A personalized 15-minute live interactive demo with our senior solution architect and a complimentary 14-day enterprise trial.",
        "special_offer": "Sign up this week and get your first 1,000 voice call minutes completely free!"
    },
    "cloudguard": {
        "id": "cloudguard",
        "name": "CloudGuard Security",
        "tagline": "Autonomous Cloud Compliance & Continuous Posture Management",
        "category": "Cybersecurity & Compliance",
        "description": "Automated SOC 2, ISO 27001, and HIPAA compliance monitoring that continuously audits your AWS, Azure, and GCP infrastructure.",
        "target_audience": "CTOs, CISOs, engineering leaders, and DevOps teams.",
        "pricing": [
            {"name": "Standard", "price": "$199/mo", "features": "SOC 2 & ISO compliance, 10 cloud accounts, weekly audit scans"},
            {"name": "Enterprise", "price": "$599/mo", "features": "Full multi-cloud, custom audit evidence export, 24/7 incident response"}
        ],
        "features": [
            "Continuous 24/7 cloud misconfiguration detection",
            "1-Click audit evidence generation for SOC 2 and HIPAA",
            "Automated remediation pull requests for Terraform and Kubernetes"
        ],
        "pain_points": [
            "Spending hundreds of engineering hours gathering audit screenshots",
            "Fear of failing enterprise security assessments and losing deals",
            "Hidden cloud misconfigurations exposing customer data"
        ],
        "stats": [
            "80% reduction in audit prep time",
            "Over 10,000 security misconfigurations auto-fixed"
        ],
        "objections": {
            "price": "Achieving compliance manually typically costs upwards of $40,000 in consultant fees and hundreds of engineering hours. CloudGuard cuts that cost by 80%.",
            "timing": "Audits have strict deadlines. Starting now ensures zero last-minute panic or costly non-compliance delays."
        },
        "demo_offer": "A free cloud security posture scan and report valued at $1,500."
    },
    "aws-services": {
        "id": "aws-services",
        "name": "AWS Cloud Solutions",
        "tagline": "Enterprise Cloud Migration, Scalable Infrastructure & Generative AI on Amazon Bedrock",
        "category": "Cloud Computing, Infrastructure & AI",
        "description": "Amazon Web Services (AWS) provides secure, scalable cloud compute (EC2), high-durability storage (S3), managed databases (RDS), serverless Lambda, and state-of-the-art Generative AI with Amazon Bedrock. We help businesses modernize infrastructure, reduce TCO by up to 45%, and accelerate innovation.",
        "target_audience": "CTOs, VPs of Engineering, Cloud Architects, DevOps leads, and IT Directors.",
        "pricing": [
            {"name": "Starter Cloud & Migration", "price": "$499/mo", "features": "Cloud architecture readiness review, EC2/S3 workload setup, 24/7 technical support, up to $2,000 in AWS POC credits"},
            {"name": "Business Scale & AI", "price": "$1,499/mo", "features": "Multi-region architecture, RDS & serverless migration, Amazon Bedrock Generative AI integration, automated FinOps cost optimization"},
            {"name": "Enterprise Strategic Cloud", "price": "Custom / Pay-As-You-Go", "features": "Full enterprise migration execution, dedicated AWS Solutions Architect, custom Well-Architected review, Savings Plans & EDP negotiation"}
        ],
        "features": [
            "Elastic on-demand compute with Amazon EC2 & AWS Serverless Lambda",
            "Enterprise object storage with Amazon S3 and high-availability databases with Amazon RDS & Aurora",
            "Next-generation Generative AI models (Claude, Llama, Titan) via Amazon Bedrock",
            "Zero-downtime database and VM migration using AWS Database Migration Service (DMS)",
            "Automated FinOps cost governance with AWS Cost Explorer and Savings Plans saving up to 72%",
            "Enterprise security and compliance with AWS IAM, GuardDuty, and SOC 2/HIPAA/ISO certifications"
        ],
        "pain_points": [
            "High capital expenditure and server maintenance costs of on-premises datacenters",
            "Infrastructure bottlenecks during unexpected traffic spikes leading to downtime",
            "Complexity and privacy concerns when building enterprise Generative AI applications",
            "Unpredictable cloud bills and unoptimized instance spend",
            "Fear of downtime and data loss during legacy database migration"
        ],
        "stats": [
            "Over 45% average reduction in infrastructure TCO compared to on-premises",
            "99.999% SLA availability backed by global Availability Zones",
            "Up to 72% compute savings with AWS Savings Plans and Spot Instances",
            "3x faster time-to-market for deploying cloud & AI microservices"
        ],
        "objections": {
            "price": "I completely understand cloud costs are a major consideration. With AWS pay-as-you-go pricing, Savings Plans, and Spot instances, teams routinely reduce compute bills by up to 72%. Plus, we can qualify your team for up to $5,000 in AWS Proof-of-Concept credits and conduct a free Well-Architected Cost Optimization Review.",
            "competitor": "That's great you're exploring or already on cloud platforms like Azure or GCP! AWS offers the deepest breadth of over 200 fully featured services, mature global infrastructure across 33+ geographic regions, and industry-leading enterprise AI with Amazon Bedrock. What is the primary workload you are evaluating—is it enterprise databases, microservice scalability, or Generative AI?",
            "timing": "I completely understand migration timing can feel daunting. That's why we use AWS Application Migration Service and AWS Database Migration Service for automated, zero-downtime replication. We can start with a non-critical workload or a proof-of-concept without touching production traffic.",
            "authority": "Absolutely, involving your CTO, VP of Engineering, and lead architects is critical. How about we schedule a tailored 30-minute Cloud Architecture & Strategy Session with an AWS Certified Solutions Architect so your whole technical team can review the proposed architecture together?",
            "trust": "AWS secures critical workloads for 90% of Fortune 100 enterprises, healthcare giants, and government bodies, with comprehensive SOC 1/2/3, ISO 27001, PCI-DSS, and FedRAMP certifications."
        },
        "demo_offer": "A tailored 30-minute Cloud Architecture & Migration Assessment with an AWS Certified Solutions Architect, plus a complimentary AWS Well-Architected Cost Review and up to $5,000 in AWS POC credits.",
        "special_offer": "Schedule a session this week to qualify for free migration funding and a $5,000 AWS Cloud activation credit package!"
    }
}


def get_product(product_id="nexus-ai"):
    return SAAS_PRODUCTS.get(product_id, SAAS_PRODUCTS["nexus-ai"])


def list_products():
    return [
        {
            "id": p["id"],
            "name": p["name"],
            "tagline": p["tagline"],
            "category": p["category"]
        }
        for p in SAAS_PRODUCTS.values()
    ]
