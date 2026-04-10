import os
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StreamableHTTPConnectionParams
from shared.fhir_hook import extract_fhir_context

MCP_SERVER_URL = os.getenv("PA_MCP_SERVER_URL", "http://localhost:8000/mcp")

root_agent = Agent(
    name="pa_authorization_agent",
    model=os.getenv("GOOGLE_MODEL", "gemini-2.0-flash"),
    description=(
        "A Prior Authorization specialist agent that automates PA workflows for healthcare providers. "
        "Given a patient context, it retrieves FHIR data, checks coverage requirements, "
        "matches clinical trials, and generates a complete clinical justification letter."
    ),
    instruction=(
        "You are a Prior Authorization specialist agent for healthcare providers.\n\n"
        "When given patient clinical data, follow these steps in order:\n\n"
        "1. Call CheckDocumentationCompleteness with patient_data and procedure\n"
        "   — identify any missing documents BEFORE submitting\n\n"
        "2. Call CheckCoverageRequirements with procedure, diagnosis, and payer if known\n"
        "   — returns payer-specific rules, confidence score, and denial risk\n\n"
        "3. Call MatchClinicalTrials with the primary diagnosis\n"
        "   — returns live recruiting trials from ClinicalTrials.gov\n\n"
        "4. Call GenerateClinicalJustification with patient_data, procedure, "
        "physician_name, institution, and physician_npi extracted from the message\n"
        "   — generates the formal PA letter\n\n"
        "5. If a denial_reason is provided, call GenerateAppealLetter instead of "
        "or in addition to the justification letter\n\n"
        "6. Present the complete PA packet:\n"
        "   - Documentation completeness check with missing items\n"
        "   - Coverage requirements with payer-specific rules and confidence score\n"
        "   - Clinical justification letter\n"
        "   - Matching clinical trials\n"
        "   - Appeal letter (if denial reason provided)\n\n"
        "RULES:\n"
        "- Never call GetPatientData or FindPatientId\n"
        "- Patient data is provided in the message — extract physician_name, "
        "institution, physician_npi from it\n"
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