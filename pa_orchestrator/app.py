import os
from a2a.types import AgentSkill
from shared.app_factory import create_a2a_app
from .agent import root_agent
from starlette.requests import Request
from starlette.responses import JSONResponse
import json

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


# Patch agent card to include supportedInterfaces for A2A 1.0 platform compatibility
@a2a_app.route("/.well-known/agent-card.json", methods=["GET"])
async def patched_agent_card(request: Request):
    # Get original card from the app
    original_route = None
    for route in a2a_app.routes:
        if hasattr(route, "path") and "agent-card" in str(route.path) and route != request.scope.get("route"):
            original_route = route
            break

    agent_url = os.getenv("PA_ORCHESTRATOR_URL", os.getenv("BASE_URL", "http://localhost:8003"))

    card = {
        "name": "pa_orchestrator",
        "description": "PA Orchestration Hub — automates the complete prior authorization lifecycle by coordinating specialist agents for coverage checks, clinical trial matching, justification letters, appeal generation, and documentation completeness.",
        "version": "1.0.0",
        "protocolVersion": "0.3.0",
        "url": agent_url,
        "preferredTransport": "JSONRPC",
        "defaultInputModes": ["text/plain"],
        "defaultOutputModes": ["text/plain"],
        "supportedInterfaces": [
            {
                "url": agent_url,
                "protocolBinding": "JSONRPC",
                "protocolVersion": "0.3.0",
            }
        ],
        "additionalInterfaces": [
            {
                "transport": "HTTP+JSON",
                "uri": f"{agent_url}/a2a-http-json",
            }
        ],
        "capabilities": {
            "streaming": True,
            "pushNotifications": False,
            "stateTransitionHistory": True,
            "extensions": [
                {
                    "uri": f"{os.getenv('PO_PLATFORM_BASE_URL', 'http://localhost:5139')}/schemas/a2a/v1/fhir-context",
                    "description": "FHIR R4 context — allows the agent to query the patient's FHIR server.",
                    "required": True,
                }
            ],
        },
        "skills": [
            {
                "id": "prior-authorization-orchestration",
                "name": "prior-authorization-orchestration",
                "description": "Complete PA lifecycle — coverage check, clinical trials, justification letter, appeal generation, documentation completeness.",
            }
        ],
        "securitySchemes": {
            "apiKey": {
                "type": "apiKey",
                "name": "X-API-Key",
                "in": "header",
            }
        },
        "security": [{"apiKey": []}],
    }
    return JSONResponse(card)


# Ensure this patched route takes precedence over the SDK-provided card route.
if a2a_app.router.routes:
    a2a_app.router.routes.insert(0, a2a_app.router.routes.pop())
