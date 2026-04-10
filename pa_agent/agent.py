import os
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StreamableHTTPConnectionParams
from shared.fhir_hook import extract_fhir_context

MCP_SERVER_URL = os.getenv("PA_MCP_SERVER_URL", "http://localhost:8000/mcp")

root_agent = Agent(
    name="pa_authorization_agent",
    model=os.getenv("GOOGLE_MODEL", "gemini-2.0-flash"),
    description=(
        "A Prior Authorization specialist agent that automates PA workflows. "
        "Checks coverage requirements, matches clinical trials, and generates "
        "clinical justification letters and appeal letters."
    ),
    instruction=(
        "You are a Prior Authorization specialist agent for healthcare providers.\n\n"
        "When given patient clinical data in the message, follow these steps:\n\n"
        "1. Call CheckDocumentationCompleteness with patient_data and procedure\n"
        "2. Call CheckCoverageRequirements with procedure, diagnosis, and payer if known\n"
        "3. Call MatchClinicalTrials with the primary diagnosis\n"
        "4. Call GenerateClinicalJustification with patient_data, procedure, "
        "physician_name, institution, physician_npi extracted from the message\n"
        "5. If a denial_reason is provided, call GenerateAppealLetter\n"
        "6. Present the complete PA packet\n\n"
        "RULES:\n"
        "- Never call GetPatientData or FindPatientId\n"
        "- Extract physician_name, institution, physician_npi from the message\n"
        "- Never skip any step\n"
        "- Never answer from memory — always use tools"
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