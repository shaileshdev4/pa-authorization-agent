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
        "IMPORTANT: When presenting the PA packet from pa_authorization_agent, "
        "reproduce the FULL output including all sections — do not summarize or truncate. "
        "The clinician needs to see every detail before approving.\n\n"
        "When running a prior authorization workflow, follow these steps:\n\n"
        "1. Call healthcare_fhir_agent to get patient demographics, active conditions, "
        "and active medications from the FHIR server\n\n"
        "2. Call pa_authorization_agent with the full patient data collected in step 1. "
        "Include diagnosis, procedure, payer (if known), physician name and NPI\n\n"
        "3. If ICD-10 codes are needed, call general_agent for lookups\n\n"
        "4. Compile all responses into a unified PA packet:\n"
        "   - Patient summary from FHIR\n"
        "   - Documentation completeness check\n"
        "   - Coverage requirements with payer-specific rules\n"
        "   - Clinical justification letter\n"
        "   - Matching clinical trials\n"
        "   - Appeal letter (if denial reason provided)\n\n"
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