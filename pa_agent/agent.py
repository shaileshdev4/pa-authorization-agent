import os
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StreamableHTTPConnectionParams
from shared.fhir_hook import extract_fhir_context

MCP_SERVER_URL = os.getenv("PA_MCP_SERVER_URL", "http://localhost:8000/mcp")

root_agent = Agent(
    name="pa_authorization_agent",
    model="gemini-2.0-flash",
    description=(
        "A Prior Authorization specialist agent that automates PA workflows for healthcare providers. "
        "Given a patient context, it retrieves FHIR data, checks coverage requirements, "
        "matches clinical trials, and generates a complete clinical justification letter."
    ),
    instruction=(
        "You are a Prior Authorization specialist agent for healthcare providers. "
        "The patient context is already loaded — you have the patient ID automatically.\n\n"
        "IMPORTANT: Do NOT call FindPatientId. It does not exist.\n\n"
        "When activated, follow these steps in exact order:\n"
        "1. Call GetPatientData (no arguments needed — patient context is automatic)\n"
        "2. Call CheckCoverageRequirements with the procedure identified from patient data\n"
        "3. Call MatchClinicalTrials with the patient's primary diagnosis\n"
        "4. Call GenerateClinicalJustification with the patient data JSON and procedure\n"
        "5. Present the complete PA packet: patient summary, coverage requirements, "
        "clinical justification letter, and matching clinical trials\n\n"
        "Never answer from memory. Always use tools."
    ),
    tools=[
        MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=MCP_SERVER_URL,
            )
        )
    ],
    before_model_callback=extract_fhir_context,
)