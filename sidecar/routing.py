# ipcha/routing.py
import logging
import yaml
import importlib
from typing import Dict
from ipcha.agents.base import VerificationAgent
from ipcha.models import Claim, VerificationResult

logger = logging.getLogger(__name__)

class ClaimRouter:
    """Routes claims to the appropriate verification agent."""

    def __init__(self, agent_mapping: Dict[str, VerificationAgent], default_agent: VerificationAgent):
        self._agent_mapping = agent_mapping
        self._default_agent = default_agent
        logger.info(f"ClaimRouter initialized with {len(agent_mapping)} agents and default {default_agent.__class__.__name__}")

    def route(self, claim: Claim, classification: str) -> VerificationResult:
        """
        Routes a claim to an agent based on its classification.

        Args:
            claim: The claim to verify.
            classification: The classification string determining the agent.

        Returns:
            The VerificationResult from the chosen agent.
        """
        agent = self._agent_mapping.get(classification, self._default_agent)
        logger.info(f"Routing claim '{claim.id}' with classification '{classification}' to agent '{agent.__class__.__name__}'")
        return agent.verify(claim)

def _get_class_from_string(class_path: str):
    """Dynamically imports a class from a string path."""
    module_name, class_name = class_path.rsplit('.', 1)
    module = importlib.import_module(module_name)
    return getattr(module, class_name)

def from_config(config_path: str) -> ClaimRouter:
    """Creates a ClaimRouter instance from a YAML configuration file."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    agent_mapping = {}
    for classification, class_path in config['agents'].items():
        AgentClass = _get_class_from_string(class_path)
        agent_mapping[classification] = AgentClass()

    DefaultAgentClass = _get_class_from_string(config['default_agent'])
    default_agent = DefaultAgentClass()

    return ClaimRouter(agent_mapping, default_agent)
