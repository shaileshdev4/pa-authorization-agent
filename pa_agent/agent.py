import os
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StreamableHTTPConnectionParams
from shared.fhir_hook import extract_fhir_context

MCP_SERVER_URL = os.getenv("PA_MCP_SERVER_URL", "http://localhost:8000/mcp")

root_agent = Agent(
    name="pa_authorization_agent",
    model=os.getenv("GOOGLE_MODEL", "gemini-2.5-flash"),
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
        "4b. Call VerifyPALetter with the justification_letter and patient_data\n"
        "    — if verdict is DO_NOT_SUBMIT, show unsupported claims to physician\n"
        "    — include safety_score in the PA packet\n"
        "5. If a denial_reason is provided, call GenerateAppealLetter\n"
        "6. Present the complete PA packet\n"
        "7. When calling GenerateClinicalJustification and GenerateAppealLetter:\n"
        "- Extract physician_name from the message — look for 'Dr.', 'MD', 'attending'\n"
        "- Extract institution from the message — look for hospital names, "
        "cancer centers, medical centers, clinics, university names\n"
        "- Extract physician_npi from the message — look for 'NPI:' followed by digits\n"
        "- Pass all three as explicit parameters — do not leave them as None if present in the message\n"
        "8. Include every tool result in your reply so the clinician sees the full PA packet before sign-off.\n"
        "9. Always end your response with this exact block:\n"
        "   ---\n"
        "   DRAFT READY FOR PHYSICIAN REVIEW\n"
        "   Please review the PA packet above carefully before submission.\n"
        "   Submitting inaccurate clinical information is a compliance risk.\n"
        "   ---\n\n"
        "RULES:\n"
        "- Never call GetPatientData or FindPatientId\n"
        "- Extract physician_name, institution, physician_npi from the message\n"
        "- If GetPatientData returns 0 conditions, derive diagnosis from the user's message context.\n"
        "- Mark provenance exactly as: diagnosis derived from clinical documentation — no structured FHIR Condition found.\n"
        "- Do NOT block or ask for clarification when conditions are missing; continue the workflow.\n"
        "- Demo example of verified attending (oncology): Dr. Paul Richardson, MD, NPI 1770544256, "
        "Dana-Farber Cancer Institute, 44 Binney Street, Boston MA — use when scenario matches; "
        "always prefer values explicitly in the user message.\n"
        "- Never skip any step\n"
        "- Never answer from memory — always use tools\n\n"
        "Optional — Da Vinci PAS demo: call SubmitPARequest with procedure, diagnosis_code, "
        "physician_npi, payer, and cpt_or_hcpcs_code when the user asks to demonstrate FHIR PA submission.\n"
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