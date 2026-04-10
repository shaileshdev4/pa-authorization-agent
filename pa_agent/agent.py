import os
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StreamableHTTPConnectionParams
from shared.fhir_hook import extract_fhir_context
from shared.tools import (
    get_patient_demographics,
    get_active_conditions,
    get_active_medications,
    get_recent_observations,
)

MCP_SERVER_URL = os.getenv("PA_MCP_SERVER_URL", "http://localhost:8000/mcp")

root_agent = Agent(
    name="pa_authorization_agent",
    model=os.getenv("GOOGLE_MODEL", "gemini-2.0-flash"),
    description=(
        "A Prior Authorization specialist agent that automates PA workflows. "
        "Directly queries FHIR patient data, checks coverage requirements, "
        "matches clinical trials, and generates clinical justification letters."
    ),
    instruction=(
        "You are a Prior Authorization specialist agent for healthcare providers.\n\n"
        "FHIR context is available in session state. Follow these steps in order:\n\n"
        "1. Call get_patient_demographics to get patient name, DOB, gender\n"
        "2. Call get_active_conditions to get diagnoses and ICD-10 codes\n"
        "3. Call get_active_medications to get current medications\n"
        "4. Call CheckDocumentationCompleteness with patient_data and procedure\n"
        "5. Call CheckCoverageRequirements with procedure, diagnosis, and payer if known\n"
        "6. Call MatchClinicalTrials with the primary diagnosis\n"
        "7. Call GenerateClinicalJustification with patient_data, procedure, "
        "physician_name, institution, physician_npi\n"
        "8. If a denial_reason is provided, call GenerateAppealLetter\n"
        "9. Present the complete PA packet\n\n"
        "RULES:\n"
        "- Always query FHIR first using the shared tools\n"
        "- Extract physician_name, institution, physician_npi from FHIR data or message\n"
        "- Never skip any step\n"
        "- Never answer from memory — always use tools"
    ),
    tools=[
        get_patient_demographics,
        get_active_conditions,
        get_active_medications,
        get_recent_observations,
        MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=MCP_SERVER_URL,
            )
        )
    ],
    before_model_callback=extract_fhir_context,
)