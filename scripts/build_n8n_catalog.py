import os
import json
import re

TEMPLATES_RAW = [
    # 1-18 Featured
    ("seo_audit_openai", "Analyze Any Website with OpenAI And Get On-Page SEO Audit", "SEO & Marketing", "Instantly find and fix technical and on-page SEO issues to improve search visibility.", "Webhook", 4, ["SEO", "OpenAI", "Audit", "Website"]),
    ("telegram_memory_chatbot", "AI Agent Chatbot + LONG TERM Memory + Note Storage + Telegram", "AI Chatbots & Agents", "Builds an AI agent chatbot equipped with long-term memory and Google Docs/Telegram integration.", "Webhook", 5, ["Chatbot", "Telegram", "Memory", "GoogleDocs"]),
    ("hacker_news_to_video", "Hacker News to Video Content", "Video & Media", "Automatically converts trending tech articles from Hacker News into engaging video content using AI.", "Schedule", 4, ["HackerNews", "Video", "Content", "AI"]),
    ("wordpress_seo_autopost", "Automate SEO-Optimized WordPress Posts with AI & Google Sheets", "SEO & Marketing", "Streamlines blog creation from content generation and metadata optimization to publishing on WordPress.", "Schedule", 5, ["WordPress", "SEO", "GoogleSheets", "Blogging"]),
    ("sql_query_from_schema", "Generate SQL queries from schema only - AI-powered", "Database & SQL", "Allows an AI agent to build and run SQL queries based strictly on database schemas without exposing underlying row data.", "Webhook", 3, ["SQL", "Database", "Schema", "Security"]),
    ("ultimate_scraper_workflow", "Ultimate Scraper Workflow for n8n", "Web Scraping", "Combines Selenium and AI to scrape any webpage element or handle custom login sessions securely.", "Webhook", 4, ["Scraping", "Selenium", "Browser", "Extraction"]),
    ("clinic_management_multiagent", "Multi-Agent AI Clinic Management with WhatsApp, Telegram, and Google Calendar", "Productivity & Operations", "A modular system managing patient communication, appointment scheduling, and confirmations via chat.", "Webhook", 6, ["Clinic", "WhatsApp", "Telegram", "Calendar"]),
    ("stock_technical_analysis", "Technical stock analysis with Telegram, Airtable and a GPT-powered AI Agent", "Finance & Crypto", "Performs technical market analysis using indicators like RSI and MACD, delivering reports via Telegram.", "Schedule", 4, ["Finance", "Stocks", "Telegram", "Airtable"]),
    ("retell_lead_qualification", "Automate Lead Qualification with RetellAI Phone Agent, OpenAI GPT & Google Sheet", "Sales & Outreach", "Handles outbound and inbound sales calls to qualify prospects and log details into Google Sheets.", "Webhook", 4, ["Sales", "VoiceAI", "RetellAI", "Leads"]),
    ("timesheet_generator_ai", "AI Timesheet Generator with Gmail, Calendar & GitHub to Google Sheets", "Productivity & Operations", "Tracks work activities across platforms to automatically log hours and update timesheets.", "Schedule", 5, ["Timesheet", "GitHub", "Gmail", "Productivity"]),
    ("sales_cold_calling_pipeline", "Automate Sales Cold Calling Pipeline with Apify, GPT-4o, and WhatsApp", "Sales & Outreach", "Scales outbound sales pipelines by finding prospects and sending tailored chat outreach.", "Webhook", 5, ["ColdCalling", "Apify", "WhatsApp", "Sales"]),
    ("financial_reports_gemini", "Generate Monthly Financial Reports with Gemini AI, SQL, and Outlook", "Finance & Crypto", "Pulls financial metrics, synthesizes insights with Gemini, and emails formatted reports to stakeholders.", "Schedule", 4, ["Finance", "Gemini", "SQL", "Outlook"]),
    ("telegram_menu_bot", "Telegram Bot with Menu-Driven Commands", "AI Chatbots & Agents", "Sets up an interactive menu system inside Telegram for seamless command execution.", "Webhook", 3, ["Telegram", "Bot", "Commands", "Interactive"]),
    ("social_videos_kling_ai", "Generate & Auto-Post Social Videos to Multiple Platforms with GPT-4 and Kling AI", "Video & Media", "End-to-end automation for creating short-form videos and distributing them across channels.", "Schedule", 5, ["Video", "SocialMedia", "KlingAI", "Shorts"]),
    ("carousels_tiktok_instagram", "Generate and publish carousels for TikTok and Instagram with GPT-Image-1", "Social Media", "Dynamically builds and schedules image-based carousel posts for social reach.", "Schedule", 4, ["Carousels", "Instagram", "TikTok", "Images"]),
    ("web_monitoring_slack", "AI-Powered Information Monitoring with OpenAI, Google Sheets, Jina AI and Slack", "DevOps & Monitoring", "Scrapes web pages on a schedule and notifies teams in Slack regarding important updates.", "Schedule", 4, ["Monitoring", "Slack", "JinaAI", "Sheets"]),
    ("dental_voice_agent", "Voice Agent for Dental Appointment Booking with Gemini AI", "Productivity & Operations", "Handles voice inquiries for dental offices and checks live calendar availability.", "Webhook", 4, ["Voice", "Booking", "Dental", "Gemini"]),
    ("supabase_postgres_chat", "AI Agent to chat with Supabase/PostgreSQL DB", "Database & SQL", "Enables natural language querying of SQL database tables through an interactive chat interface.", "Webhook", 3, ["PostgreSQL", "Supabase", "SQL", "Chatbot"]),

    # 19-35
    ("youtube_summarizer_chatbot", "Ultimate AI-Powered Chatbot for YouTube Summarization & Analysis", "Video & Media", "Transcribes, extracts, and answers questions about any YouTube video link provided.", "Webhook", 4, ["YouTube", "Transcribe", "Summarizer", "Chatbot"]),
    ("telegram_research_assistant", "AI Research Assistant via Telegram (GPT-4o mini + DeepSeek R1 + SerpAPI)", "AI Chatbots & Agents", "Comprehensive multi-model assistant executing web searches and deep syntheses on demand.", "Webhook", 5, ["Research", "DeepSeek", "SerpAPI", "Telegram"]),
    ("invoice_email_to_sheets", "Extract Invoice Data from Email to Google Sheets using GPT-4o AI Automation", "Productivity & Operations", "Monitors mailboxes for invoice PDFs, extracts totals and dates, and logs them into accounting sheets.", "Webhook", 4, ["Invoices", "PDF", "Email", "Accounting"]),
    ("llama_parse_documents", "Advanced AI Powered Document Parsing & Text Extraction with Llama Parse", "Database & SQL", "Handles complex layout parsing across unstructured documents for cleaner downstream data manipulation.", "Webhook", 3, ["LlamaParse", "Documents", "Extraction", "OCR"]),
    ("security_compliance_digest", "Intelligent AI Digest for Security, Privacy, and Compliance Feeds", "DevOps & Monitoring", "Aggregates and filters security advisories into a single daily summary update.", "Schedule", 3, ["Security", "Compliance", "Advisories", "Digest"]),
    ("document_qa_gemini_supabase", "Document Q&A Chatbot with Gemini AI and Supabase Vector Search for Telegram", "Database & SQL", "Implements a RAG pipeline backed by vector search for robust file querying over Telegram.", "Webhook", 4, ["RAG", "VectorSearch", "Supabase", "Gemini"]),
    ("linkedin_job_signals", "Scrape LinkedIn Job Listings for Hiring Signals & Prospecting with Bright Data", "Sales & Outreach", "Automated lead discovery parsing open job postings to identify active corporate hiring needs.", "Schedule", 4, ["LinkedIn", "Hiring", "Prospecting", "BrightData"]),
    ("heygen_video_voice_clone", "Generate AI Videos from Text with HeyGen and Voice Cloning", "Video & Media", "Creates talking-head presentation assets and personalized video segments automatically.", "Webhook", 4, ["HeyGen", "Video", "Avatar", "VoiceCloning"]),
    ("image_optimizer_cdn", "Convert Image Files (JPG, PNG) to URLs and Reduce File Size for FREE", "DevOps & Monitoring", "Utility workflow for optimizing user-uploaded visual media assets in automation pipelines.", "Webhook", 3, ["Images", "Optimization", "CDN", "Storage"]),
    ("pdf_rag_mistral_qdrant", "Build a PDF Document RAG System with Mistral OCR, Qdrant and Gemini AI", "Database & SQL", "Advanced OCR parsing combined with vector storage to build precise document query systems.", "Webhook", 4, ["MistralOCR", "Qdrant", "RAG", "Gemini"]),
    ("youtube_shorts_generator", "YouTube Shorts Automation Tool", "Video & Media", "Fully automates idea generation, scriptwriting, video rendering, and uploading workflows.", "Schedule", 5, ["YouTubeShorts", "Social", "Rendering", "Automation"]),
    ("telegram_mcp_task_manager", "AI-Powered Telegram Task Manager with MCP Server", "MCP Protocols", "Leverages Model Context Protocol servers to route tasks seamlessly from a chat window.", "Webhook", 4, ["MCP", "Telegram", "TaskManager", "Tools"]),
    ("viral_trends_social_poster", "Extract Trends, Auto-Generate Social Content with AI, Reddit, Google & Post", "Social Media", "Surfaces trending topics from search and social platforms to draft viral marketing posts.", "Schedule", 4, ["Reddit", "Trends", "SocialMedia", "Marketing"]),
    ("gemini_multimodal_telegram", "Conversational AI Chatbot with Google Gemini for Text & Image | Telegram", "AI Chatbots & Agents", "Multimodal assistant capable of reviewing images and responding contextually in text.", "Webhook", 3, ["Gemini", "Multimodal", "Vision", "Telegram"]),
    ("rag_starter_template", "RAG Starter Template using Simple Vector Stores, Form trigger and OpenAI", "Database & SQL", "Minimalist beginner guide for setting up Retrieval-Augmented Generation workflows.", "Webhook", 3, ["RAG", "VectorStore", "OpenAI", "Starter"]),
    ("infranodus_graph_rag", "Telegram AI Chatbot Agent with InfraNodus GraphRAG Knowledge Base", "AI Chatbots & Agents", "Graph-based knowledge retrieval tool replacing heavy vector stores with semantic network structures.", "Webhook", 4, ["GraphRAG", "KnowledgeGraph", "Telegram", "Semantic"]),
    ("gmail_smart_organization", "Intelligent Email Organization with AI-Powered Content Classification for Gmail", "Productivity & Operations", "Automatically categorizes, prioritizes, and labels incoming messages in Gmail.", "Schedule", 4, ["Gmail", "Classification", "Productivity", "Labels"]),

    # 36-50
    ("linkedin_dalle_poster", "Automated LinkedIn Content Creation with GPT-4 and DALL-E for Scheduled Posts", "Social Media", "Generates text hooks and matching custom brand visuals for professional network distribution.", "Schedule", 4, ["LinkedIn", "DALLE", "Scheduling", "Branding"]),
    ("linkedin_lead_scoring_sheets", "Search LinkedIn companies, Score with AI and add them to Google Sheet CRM", "Sales & Outreach", "Discovers business leads, evaluates their fitness score using LLMs, and stores them neatly in Google Sheets.", "Schedule", 4, ["LinkedIn", "LeadScoring", "CRM", "GoogleSheets"]),
    ("perplexity_search_pipeline", "Query Perplexity AI from your n8n workflows", "AI Chatbots & Agents", "Integrates Perplexity's real-time conversational search engines directly into custom steps.", "Webhook", 3, ["Perplexity", "Search", "Web", "AI"]),
    ("seo_seed_keywords_generator", "Generate SEO Seed Keywords Using AI", "SEO & Marketing", "Analyzes ideal customer profiles to formulate comprehensive lists of high-value search keywords.", "Webhook", 3, ["Keywords", "SEO", "Strategy", "CustomerProfile"]),
    ("coinmarketcap_data_analyst", "Analyze Crypto Markets with the AI-Powered CoinMarketCap Data Analyst", "Finance & Crypto", "Multi-agent pipeline fetching centralized and decentralized crypto trends for market tracking.", "Schedule", 4, ["Crypto", "CoinMarketCap", "Analytics", "Trading"]),
    ("gemini_pdf_image_processor", "5 Ways to Process Images & PDFs with Gemini AI in n8n", "Database & SQL", "Educational blueprint highlighting different architectural approaches for multimodal AI tasks.", "Webhook", 3, ["Gemini", "PDF", "Vision", "Processing"]),
    ("tavily_web_researcher", "The Ultimate Free AI-Powered Researcher with Tavily Web Search & Extract", "AI Chatbots & Agents", "Autonomous web search agent filtering relevant sources to draft comprehensive summaries.", "Webhook", 4, ["Tavily", "Research", "WebSearch", "Synthesis"]),
    ("auto_service_social_marketing", "AI content generation for Auto Service - Automate your social media!", "Social Media", "Specialized marketing automation tailored for automotive repair shops and mechanics.", "Schedule", 4, ["AutoService", "Niche", "Marketing", "Social"]),
    ("ai_vision_image_validator", "Automate Image Validation Tasks using AI Vision", "DevOps & Monitoring", "Uses vision-language models to verify whether user-uploaded photos meet specific criteria.", "Webhook", 3, ["Vision", "ImageValidation", "QC", "Moderation"]),
    ("brand_voice_blog_creator", "Automate Blog Creation in Brand Voice with AI", "SEO & Marketing", "Quick-training pipeline adapting standard LLM outputs to match a company's specific style guide.", "Webhook", 4, ["BrandVoice", "Blogging", "StyleGuide", "Content"]),
    ("youtube_insights_extractor", "Turn YouTube Videos into Summaries, Transcripts, and Visual Insights", "Video & Media", "Comprehensive media analyzer extracting text transcripts and action moments from videos.", "Webhook", 4, ["YouTube", "Transcripts", "Insights", "Video"]),
    ("fal_ai_image_generator", "AI image generator from text built on fal.ai", "Video & Media", "Secure API endpoint template translating prompts into stylized images with safety filters.", "Webhook", 3, ["FalAI", "ImageGen", "Diffusion", "API"]),
    ("outlook_email_autoresponder", "Reply to Outlook Emails with OpenAI", "Productivity & Operations", "Learns personal writing tones to draft context-aware replies for Microsoft Outlook users.", "Schedule", 4, ["Outlook", "Email", "AutoReply", "ToneMatching"]),
    ("retell_phone_calendar_agent", "Build an AI Powered Phone Agent with Retell, Google Calendar and RAG", "Sales & Outreach", "Voice-interactive assistant handling scheduling and policy queries over phone networks.", "Webhook", 5, ["RetellAI", "Voice", "Calendar", "RAG"]),
    ("n8n_expressions_tutorial", "Learn n8n Expressions with an Interactive Step-by-Step Tutorial for Beginners", "DevOps & Monitoring", "Hands-on canvas guide teaching data navigation and expression syntax.", "Webhook", 3, ["Tutorial", "Expressions", "Beginner", "Canvas"]),

    # 51-68
    ("linkedin_post_approval_flow", "AI-Generated LinkedIn Posts with OpenAI, Google Sheets & Email Approval Workflow", "Social Media", "Drafts social content and triggers an email review prompt before final publishing.", "Schedule", 5, ["ApprovalFlow", "HumanInTheLoop", "LinkedIn", "Email"]),
    ("email_attachment_archiver", "AI Email Analyzer: Process PDFs, Images & Save to Google Drive + Telegram", "Productivity & Operations", "Consolidates attachment processing, cloud archiving, and summary messaging.", "Webhook", 4, ["Email", "Attachments", "GoogleDrive", "Telegram"]),
    ("baserow_telegram_assistant", "All-in-One Telegram/Baserow AI Assistant (Voice/Photo/Save Notes/Long Term Mem)", "AI Chatbots & Agents", "Comprehensive life-management assistant processing voice notes and persistent memory.", "Webhook", 5, ["Baserow", "VoiceNotes", "Memory", "Telegram"]),
    ("langchain_telegram_bot", "Agentic Telegram AI bot with LangChain nodes and new tools", "AI Chatbots & Agents", "Advanced tool-calling agent framework using native LangChain components.", "Webhook", 4, ["LangChain", "Tools", "Agentic", "Telegram"]),
    ("daily_news_digest_whatsapp", "Daily News Digest: Summarize RSS Feeds with OpenAI and Deliver to WhatsApp", "Social Media", "Collects multi-source RSS content, compiles brief digests, and messages them directly.", "Schedule", 4, ["RSS", "News", "WhatsApp", "Digest"]),
    ("brave_search_mcp_chatbot", "Build a Web Search Chatbot with GPT-4o and MCP Brave Search", "MCP Protocols", "Integrates Model Context Protocol tools to enhance web retrieval accuracy.", "Webhook", 4, ["MCP", "BraveSearch", "Web", "Chatbot"]),
    ("asmr_shorts_generator", "Create & Upload AI-Generated ASMR YouTube Shorts with Seedance, Fal AI, and GPT-4", "Video & Media", "Fully automated pipeline for generating and publishing satisfying short-form videos.", "Schedule", 5, ["YouTubeShorts", "ASMR", "FalAI", "Video"]),
    ("apollo_lead_enricher", "Generate & Enrich LinkedIn Leads with Apollo.io, LinkedIn API, Mail.so & GPT-3.5", "Sales & Outreach", "Streamlines outreach list building with multi-source contact validation.", "Webhook", 5, ["Apollo", "Enrichment", "Leads", "Validation"]),
    ("blog_creation_approval_flow", "Automate Blog Content Creation with OpenAI, Google Sheets & Email Approval Flow", "SEO & Marketing", "Scales SEO article production while keeping a human-in-the-loop review step.", "Schedule", 5, ["Editorial", "Approval", "SEO", "Blogging"]),
    ("imagen_brand_logo_generator", "Generate Logos and Images with Consistent Visual Styles using Imagen 3.0", "Social Media", "Remixes brand assets and generates stylistic design variants using Google Imagen.", "Webhook", 3, ["Imagen", "Branding", "Logos", "Design"]),
    ("tiktok_watermarkless_downloader", "Download TikTok Videos without Watermarks and Upload to Google Drive", "Video & Media", "Clean archiving utility bypassing typical ad-heavy third-party conversion websites.", "Webhook", 3, ["TikTok", "Archiving", "GoogleDrive", "Media"]),
    ("bright_data_job_finder", "LinkedIn Job Finder Automation using Bright Data API & Google Sheets", "Productivity & Operations", "Structured tracking workflow for matching open professional recruitment listings.", "Schedule", 4, ["JobHunt", "LinkedIn", "BrightData", "Sheets"]),
    ("audio_transcribe_drive_summary", "Use OpenAI to Transcribe Audio + Summarize with AI + Save to Google Drive", "Productivity & Operations", "Converts voice recordings into organized text files for searchable archiving.", "Webhook", 4, ["Audio", "Transcription", "Whisper", "Drive"]),
    ("content_scraper_airtable_seo", "Website Content Scraper & SEO Keyword Extractor with GPT-5-mini and Airtable", "SEO & Marketing", "Cleans HTML parsing output to store target keyword metrics directly into Airtable bases.", "Webhook", 4, ["SEO", "Airtable", "Scraper", "Keywords"]),
    ("omnichannel_social_publisher", "Social Media Content Generator And Publisher | X, LinkedIn", "Social Media", "Synchronized multi-platform publishing engine for professional accounts.", "Schedule", 4, ["X", "Twitter", "LinkedIn", "Omnichannel"]),
    ("google_trends_insights_sheets", "Extract Google Trends Keywords & Summarize Articles in Google Sheets", "SEO & Marketing", "Monitors emerging search topics and organizes content insights automatically.", "Schedule", 4, ["GoogleTrends", "Trends", "Sheets", "Insights"]),
    ("custom_api_mcp_server", "Build your own CUSTOM API MCP server", "MCP Protocols", "Technical template demonstrating how to turn existing workflows into reusable MCP servers.", "Webhook", 4, ["MCP", "CustomAPI", "Server", "Protocol"]),
    ("meeting_insights_agent", "AI Agent for realtime insights on meetings", "Productivity & Operations", "Processes conference audio to extract action items and decision metrics instantly.", "Webhook", 4, ["Meetings", "Insights", "ActionItems", "Transcripts"]),

    # 69-82
    ("outlook_invoice_parser", "Parse Incoming Invoices From Outlook using AI Document Understanding", "Productivity & Operations", "Automated extraction parser designed for Microsoft email ecosystems.", "Schedule", 4, ["Outlook", "Invoices", "Accounting", "Microsoft"]),
    ("platform_qa_mcp_assistant", "AI-Powered Research Assistant for Platform Questions with GPT-4o and MCP", "MCP Protocols", "Specialized documentation support assistant answering complex platform logic questions.", "Webhook", 4, ["MCP", "Documentation", "Support", "Architecture"]),
    ("social_media_amplifier", "AI-Powered Social Media Amplifier", "Social Media", "Repurposes core marketing pieces into varied platform-optimized post formats.", "Webhook", 4, ["Amplifier", "Repurposing", "SocialMedia", "Marketing"]),
    ("documentation_expert_gemini_rag", "Build a Documentation Expert Chatbot with Gemini RAG Pipeline", "Database & SQL", "Trains LLMs on custom technical documentation directories for accurate answers.", "Webhook", 4, ["Gemini", "RAG", "Documentation", "Chatbot"]),
    ("jina_multipage_scraper", "Essential Multipage Website Scraper with Jina.ai", "Web Scraping", "Turns complex target sites into clean LLM-friendly text blocks.", "Webhook", 3, ["JinaAI", "Scraper", "Markdown", "Web"]),
    ("structured_prompt_maker", "AI Prompt Maker", "AI Chatbots & Agents", "Interactive utility for designing, refining, and testing structured prompt templates.", "Webhook", 3, ["PromptEngineering", "Prompts", "Templates", "Refinement"]),
    ("cloud_spend_optimizer", "Cloud Spend Optimizer", "DevOps & Monitoring", "Analyzes infrastructure metrics to suggest cost-saving opportunities.", "Schedule", 4, ["CloudCost", "DevOps", "FinOps", "AWS"]),
    ("nps_score_aggregator", "NPS Score Aggregator", "Productivity & Operations", "Collects and visualizes customer satisfaction scores from multiple sources.", "Webhook", 3, ["NPS", "Feedback", "CustomerExperience", "Metrics"]),
    ("autoscaling_trigger", "Auto-Scaling Trigger", "DevOps & Monitoring", "Monitors server performance anomalies to trigger automated scaling operations.", "Webhook", 3, ["AutoScaling", "Kubernetes", "DevOps", "Infrastructure"]),
    ("powerbi_embed_updater", "Power BI Embed Updater", "Database & SQL", "Keeps data dashboards synchronized across reporting environments.", "Schedule", 3, ["PowerBI", "BI", "Dashboards", "Reporting"]),
    ("device_breakout_reporter", "Device Breakout Reporter", "DevOps & Monitoring", "Tracks hardware and client performance metrics in real-time.", "Schedule", 3, ["DeviceAnalytics", "Clients", "Hardware", "Telemetry"]),
    ("session_replay_tagger", "Session Replay Tagger", "DevOps & Monitoring", "Analyzes user interaction patterns to tag usability bottlenecks.", "Webhook", 3, ["SessionReplay", "UX", "Bottlenecks", "Analytics"]),
    ("release_notes_generator", "Release Notes Generator", "DevOps & Monitoring", "Synthesizes changelogs and pull requests into structured release summaries.", "Webhook", 3, ["ReleaseNotes", "Changelog", "GitHub", "DevOps"]),
    ("opsgenie_alert_router", "OpsGenie Alert Router", "DevOps & Monitoring", "Manages operational alerts and streamlines incident response routing.", "Webhook", 3, ["OpsGenie", "IncidentResponse", "Alerting", "DevOps"]),

    # #83+ Additional Highlights
    ("sheets_chatgpt5_assistant", "Talk to Your Google Sheets Using ChatGPT-5", "Database & SQL", "Enables natural language queries to interact directly with spreadsheet data rows.", "Webhook", 3, ["GoogleSheets", "ChatGPT5", "Spreadsheets", "Data"]),
    ("tech_radar_advisor_rag", "Build an AI-Powered Tech Radar Advisor with SQL DB, RAG, and Routing Agents", "Database & SQL", "Combines vector search with structured databases to route and advise on technology trends.", "Webhook", 5, ["TechRadar", "RAG", "Routing", "Architecture"]),
    ("deep_research_lead_magnet", "Deep Research - Sales Lead Magnet Agent", "Sales & Outreach", "Automated autonomous research agent tailored for prospecting and generating custom lead assets.", "Webhook", 5, ["DeepResearch", "LeadMagnet", "Sales", "Prospecting"]),
    ("veo3_video_generator", "AI Video Generator with Google Veo3 API (Veo 3 Fast)", "Video & Media", "Generates quick-turnaround video files using advanced text-to-video API models.", "Webhook", 3, ["Veo3", "GoogleAI", "Video", "TextToVideo"]),
    ("animated_stories_creatomate", "Create Animated Stories using GPT-4o-mini, Midjourney, Kling and Creatomate API", "Video & Media", "End-to-end media pipeline connecting script generation, image creation, and video assembly.", "Webhook", 5, ["Stories", "Animation", "Creatomate", "Midjourney"]),
    ("gmail_human_followup_reminder", "Automatic Reminders For Follow-ups with AI and Human in the loop Gmail", "Sales & Outreach", "Tracks client follow-up dates and drafts email check-ins requiring manual approval.", "Schedule", 4, ["FollowUps", "Gmail", "HumanInTheLoop", "CRM"]),
    ("dexscreener_token_insights", "Get Real-time Crypto Token Insights via Telegram with DexScreener and GPT-4o", "Finance & Crypto", "Pulls live token data from DexScreener and translates metrics into readable summaries on Telegram.", "Schedule", 4, ["DexScreener", "Crypto", "Telegram", "GPT4o"]),
    ("supabase_rag_crud_mcp", "MCP Supabase Server for AI Agent with RAG & Multi-Tenant CRUD", "MCP Protocols", "Implements a Model Context Protocol server exposing database query tools to LLMs.", "Webhook", 4, ["MCP", "Supabase", "CRUD", "MultiTenant"]),
    ("siem_mitre_incident_enrichment", "Automate SIEM Alert Enrichment with MITRE ATT&CK, Qdrant & Zendesk in n8n", "DevOps & Monitoring", "Cross-references security incident logs with threat intel vectors and opens ticketing records.", "Webhook", 5, ["SIEM", "Cybersecurity", "MITRE", "Zendesk"]),
    ("apollo_airtable_lead_pipeline", "Get Qualified Leads in One Click from Apollo to Airtable", "Sales & Outreach", "Scrapes and filters professional contact data directly into relational databases.", "Webhook", 3, ["Apollo", "Airtable", "Leads", "OneClick"]),
    ("notion_article_summarizer", "AI Agent: Scrape, Summarize & Save Articles to Notion (Gemini, Browserless)", "Productivity & Operations", "Fetches external URL contents, condenses key points, and commits pages to Notion.", "Webhook", 4, ["Notion", "Gemini", "Browserless", "Summarizer"]),
    ("legal_assistant_rag", "AI Legal Assistant Agent — AI-Powered Legal Q&A with Document Retrieval", "AI Chatbots & Agents", "Specialized RAG setup indexing regulatory texts for precise question answering.", "Webhook", 4, ["Legal", "Regulatory", "RAG", "Compliance"]),
    ("strava_ai_fitness_coach", "AI Fitness Coach Strava Data Analysis and Personalized Training Insights", "Productivity & Operations", "Pulls workout telemetry from fitness trackers to generate coaching feedback.", "Schedule", 4, ["Strava", "Fitness", "Coach", "Telemetry"]),
    ("sap_erp_invoice_pipeline", "Automated Invoice Processing with Telegram, GPT-4o, OCR and SAP Integration", "Finance & Crypto", "Enterprise-grade document routing connecting chat interfaces with ERP backends.", "Webhook", 5, ["SAP", "ERP", "Invoices", "Enterprise"]),
    ("trustpilot_sentiment_analyzer", "Scrape Trustpilot Reviews with DeepSeek, Analyze Sentiment with OpenAI", "Web Scraping", "Extracts customer feedback pages and compiles product sentiment reports.", "Schedule", 4, ["Trustpilot", "Reviews", "Sentiment", "DeepSeek"]),
    ("gmail_mcp_toolkit", "Gmail MCP Server – Your All-in-One AI Email Toolkit", "MCP Protocols", "Exposes mail operations as an MCP server for agentic interaction.", "Webhook", 4, ["MCP", "Gmail", "Toolkit", "Server"]),
    ("firecrawl_competitor_monitor", "Monitor competitors' websites for changes with OpenAI and Firecrawl", "SEO & Marketing", "Scrapes competitor landing pages periodically and summarizes structural updates.", "Schedule", 4, ["Firecrawl", "Competitors", "Monitoring", "SEO"]),
    ("google_calendar_whatsapp_agent", "Manage Google Calendar via WhatsApp with GPT-4 Virtual Assistant", "Productivity & Operations", "Schedules and updates calendar events through WhatsApp messaging.", "Webhook", 4, ["WhatsApp", "GoogleCalendar", "Scheduling", "Assistant"]),
    ("gmaps_lead_extractor", "Extract Business Leads from Google Maps with Dumpling AI to Google Sheets", "Sales & Outreach", "Gathers local business information for sales prospecting.", "Schedule", 4, ["GoogleMaps", "LocalLeads", "Scraping", "GoogleSheets"])
]

def main():
    target_path = os.path.join(os.path.dirname(__file__), "..", "apps", "engine_broker", "src", "templates", "n8n_markets_library.json")
    os.makedirs(os.path.dirname(target_path), exist_ok=True)

    catalog = []
    for item in TEMPLATES_RAW:
        t_id, name, cat, desc, trig, nodes_cnt, tags = item
        catalog.append({
            "id": t_id,
            "name": name,
            "category": cat,
            "description": desc,
            "trigger_type": trig,
            "nodes_count": nodes_cnt,
            "tags": tags
        })

    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2)

    print(f"Successfully generated n8n_markets_library.json with {len(catalog)} template definitions at {target_path}")

if __name__ == "__main__":
    main()
