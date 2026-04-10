import os
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StreamableHTTPConnectionParams
from shared.fhir_hook import extract_fhir_context

MCP_SERVER_URL = os.getenv("PA_MCP_SERVER_URL", "http://localhost:8000/mcp")

root_agent = Agent(
    name="pa_authorization_agent",
    model=os.getenv("GOOGLE_MODEL", "gemini-2.5-flash-preview-04-17"),
    description=(
        "A Prior Authorization specialist agent that automates PA workflows for healthcare providers. "
        "Given a patient context, it retrieves FHIR data, checks coverage requirements, "
        "matches clinical trials, and generates a complete clinical justification letter."
    ),
    instruction=(
        "You are a Prior Authorization specialist agent. "
        "When given patient clinical data in the message, follow these steps:\n\n"
        "1. Call CheckCoverageRequirements with the procedure and diagnosis from the message\n"
        "2. Call MatchClinicalTrials with the primary diagnosis\n"
        "3. Call GenerateClinicalJustification with the patient_data as a JSON string "
        "constructed from the message content, and the procedure name\n"
        "4. Present the complete PA packet with all results\n\n"
        "IMPORTANT: Do NOT call GetPatientData — patient data is provided in the message. "
        "Extract patient name, DOB, diagnosis, procedure, labs, and physician from the message "
        "and pass them directly to GenerateClinicalJustification as a JSON string.\n"
        "Never skip the justification letter step."
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