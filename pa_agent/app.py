import os
from a2a.types import AgentSkill
from shared.app_factory import create_a2a_app
from .agent import root_agent

a2a_app = create_a2a_app(
    agent=root_agent,
    name="pa_authorization_agent",
    description=(
        "Automates prior authorization for healthcare providers. "
        "Retrieves patient FHIR data, checks payer coverage requirements, "
        "matches active clinical trials, and generates AI-written clinical justification letters."
    ),
    url=os.getenv("PA_AGENT_URL", os.getenv("BASE_URL", "http://localhost:8001")),
    port=8001,
    fhir_extension_uri=f"{os.getenv('PO_PLATFORM_BASE_URL', 'http://localhost:5139')}/schemas/a2a/v1/fhir-context",
    skills=[
        AgentSkill(
            id="prior-authorization",
            name="prior-authorization",
            description=(
                "Generates a complete prior authorization packet including coverage check, "
                "clinical trial matching, and AI-written clinical justification letter."
            ),
            tags=["prior-authorization", "pa", "fhir", "clinical-trials", "justification"],
        ),
    ],
)