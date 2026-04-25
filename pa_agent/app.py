import os
from a2a.types import AgentSkill
from shared.app_factory import create_a2a_app
from .agent import root_agent
from starlette.requests import Request
from starlette.responses import JSONResponse

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


# Patch agent card to include Prompt Opinion-compatible A2A 1.0 shape.
@a2a_app.route("/.well-known/agent-card.json", methods=["GET"])
async def patched_agent_card(request: Request):
    agent_url = os.getenv("PA_AGENT_URL", os.getenv("BASE_URL", "http://localhost:8001"))
    card = {
        "name": "pa_authorization_agent",
        "description": (
            "Automates prior authorization for healthcare providers. Retrieves patient FHIR data, "
            "checks payer coverage requirements, matches active clinical trials, and generates "
            "AI-written clinical justification letters."
        ),
        "version": "1.0.0",
        "protocolVersion": "1.0",
        "url": agent_url,
        "preferredTransport": "JSONRPC",
        "defaultInputModes": ["text/plain"],
        "defaultOutputModes": ["text/plain"],
        "supportedInterfaces": [
            {
                "url": agent_url,
                "protocolBinding": "JSONRPC",
                "protocolVersion": "1.0",
            },
            {
                "url": f"{agent_url}/a2a-http-json",
                "protocolBinding": "HTTP+JSON",
                "protocolVersion": "1.0",
            },
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
                "id": "prior-authorization",
                "name": "prior-authorization",
                "description": (
                    "Generates a complete prior authorization packet including coverage check, "
                    "clinical trial matching, and AI-written clinical justification letter."
                ),
                "tags": [],
                "examples": [],
            }
        ],
        "securitySchemes": {
            "prompt-opinion-api-key": {
                "apiKeySecurityScheme": {
                    "name": "X-API-Key",
                    "location": "header",
                }
            }
        },
    }
    return JSONResponse(card)


# Ensure this patched route takes precedence over the SDK-provided card route.
if a2a_app.router.routes:
    a2a_app.router.routes.insert(0, a2a_app.router.routes.pop())