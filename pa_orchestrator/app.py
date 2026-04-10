import os
from a2a.types import AgentSkill
from shared.app_factory import create_a2a_app
from .agent import root_agent

a2a_app = create_a2a_app(
    agent=root_agent,
    name="pa_orchestrator",
    description=(
        "PA Orchestration Hub — automates the complete prior authorization lifecycle "
        "by coordinating specialist agents for coverage checks, clinical trial matching, "
        "justification letters, appeal generation, and documentation completeness."
    ),
    url=os.getenv("PA_ORCHESTRATOR_URL", os.getenv("BASE_URL", "http://localhost:8003")),
    port=8003,
    fhir_extension_uri=f"{os.getenv('PO_PLATFORM_BASE_URL', 'http://localhost:5139')}/schemas/a2a/v1/fhir-context",
    skills=[
        AgentSkill(
            id="prior-authorization-orchestration",
            name="prior-authorization-orchestration",
            description="Complete PA lifecycle — coverage check, clinical trials, justification letter, appeal generation, documentation completeness.",
            tags=["prior-authorization", "orchestration", "fhir", "clinical-trials"],
        ),
    ],
)
