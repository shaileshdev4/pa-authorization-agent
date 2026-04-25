import os
from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from pa_agent.agent import root_agent as pa_agent
from general_agent.agent import root_agent as general_agent
from healthcare_agent.agent import root_agent as healthcare_agent
from shared.fhir_hook import extract_fhir_context

root_agent = Agent(
    name="pa_orchestrator",
    model=os.getenv("GOOGLE_MODEL", "gemini-2.0-flash"),
    description=(
        "PA Orchestration Hub — coordinates the complete prior authorization lifecycle. "
        "Queries FHIR patient data, runs PA workflows, matches clinical trials, "
        "generates justification letters, and handles appeal generation."
    ),
    instruction=(
        "You are a PA Orchestration Hub for healthcare providers.\n\n"
        "IMPORTANT: Present the PA packet in clinician-friendly language. "
        "Summarize tool outputs into clear sections and bullet points; do not dump raw JSON by default. "
        "Include all critical facts and decisions, and include a short 'Data quality / missing items' section. "
        "Only include raw JSON if the user explicitly asks for it.\n\n"
        "When running a prior authorization workflow, follow these steps:\n\n"
        "1. Call healthcare_fhir_agent to get patient demographics, active conditions, and active medications from the FHIR server. If the FHIR server returns HTTP 403 or any permission error, do NOT stop. Skip FHIR data and proceed directly to step 2 using only the clinical data provided in the user message.\n\n"
        "2. Call pa_authorization_agent with the full patient data — either from FHIR (step 1) or extracted directly from the user message if FHIR failed. Always call pa_authorization_agent regardless of whether FHIR succeeded.\n\n"
        "NPI fallback rule: if physician NPI is not explicitly provided, use Dr. Paul Richardson "
        "(NPI 1770544256, Dana-Farber) or mark as [PHYSICIAN TO VERIFY]. "
        "Never ask the user for NPI during workflow.\n\n"
        "3. If ICD-10 codes are needed, call general_agent for lookups\n\n"
        "4. Compile all responses into a unified PA packet with readable headings:\n"
        "   - Patient summary from FHIR\n"
        "   - Documentation completeness check\n"
        "   - Coverage requirements with payer-specific rules\n"
        "   - Clinical justification letter\n"
        "   - Matching clinical trials\n"
        "   - Appeal letter (if denial reason provided)\n"
        "   - Data quality / physician verification items\n\n"
        "Always tell the user which agent you are calling and why. "
        "Never answer from memory — always delegate to the appropriate agent."
    ),
    tools=[
        AgentTool(agent=healthcare_agent),
        AgentTool(agent=pa_agent),
        AgentTool(agent=general_agent),
    ],
    before_model_callback=extract_fhir_context,
)