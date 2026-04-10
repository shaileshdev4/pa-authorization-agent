import os
from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from pa_agent.agent import root_agent as pa_agent
from general_agent.agent import root_agent as general_agent
from shared.fhir_hook import extract_fhir_context

root_agent = Agent(
    name="pa_orchestrator",
    model=os.getenv("GOOGLE_MODEL", "gemini-2.0-flash"),
    description=(
        "PA Orchestration Hub — coordinates the complete prior authorization lifecycle. "
        "Delegates PA tasks to the PA specialist agent and general queries to the general agent."
    ),
    instruction=(
        "You are a PA Orchestration Hub for healthcare providers.\n\n"
        "Use pa_authorization_agent for:\n"
        "  - Prior authorization workflows\n"
        "  - Coverage requirements checks with payer-specific rules\n"
        "  - Clinical justification letters\n"
        "  - Appeal letter generation after denials\n"
        "  - Documentation completeness checks\n"
        "  - Clinical trial matching from ClinicalTrials.gov\n\n"
        "Use general_agent for:\n"
        "  - ICD-10 code lookups\n"
        "  - Date/time queries\n\n"
        "Always tell the user which agent you are calling. "
        "Compile all sub-agent responses into a unified PA packet.\n\n"
        "When running a full PA workflow:\n"
        "1. Delegate to pa_authorization_agent with full patient context\n"
        "2. Compile coverage requirements, trials, justification letter, doc completeness\n"
        "3. Present the complete PA packet clearly"
    ),
    tools=[
        AgentTool(agent=pa_agent),
        AgentTool(agent=general_agent),
    ],
    before_model_callback=extract_fhir_context,
)
