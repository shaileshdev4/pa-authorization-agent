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
        "STEP 1: Call healthcare_fhir_agent to get patient demographics. "
        "If FHIR returns 403 or any error, skip this step and proceed immediately to Step 2.\n\n"
        "STEP 2: Call pa_authorization_agent with the COMPLETE original user message text exactly as received. "
        "Do not summarize or shorten it. Pass everything.\n\n"
        "STEP 3: Return the COMPLETE response from pa_authorization_agent to the user VERBATIM. "
        "Do NOT reformat it. Do NOT summarize it. Do NOT add section headers. "
        "Do NOT say 'did not provide' for any section. "
        "If pa_authorization_agent returned a letter, show the full letter text. "
        "If it returned trial matches, show all of them. "
        "Copy the entire pa_authorization_agent response as your final answer.\n\n"
        "NPI rule: if physician NPI is missing, mark as [PHYSICIAN TO VERIFY]. Never substitute another physician's NPI. Never ask the user.\n\n"
        "Never answer from memory — always delegate to pa_authorization_agent."
    ),
    tools=[
        AgentTool(agent=healthcare_agent),
        AgentTool(agent=pa_agent),
        AgentTool(agent=general_agent),
    ],
    before_model_callback=extract_fhir_context,
)