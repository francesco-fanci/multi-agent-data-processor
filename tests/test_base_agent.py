import pytest

from src.agents.base_agent import BaseAgent


def test_base_agent_cannot_be_instantiated():

    with pytest.raises(TypeError):

        BaseAgent(
            name="Test Agent",
            goal="Test goal"
        )


def test_agent_implementation():

    class TestAgent(BaseAgent):

        def run(self, context):
            return context

    agent = TestAgent(
        name="Test Agent",
        goal="Test goal"
    )

    assert agent.name == "Test Agent"
    assert agent.goal == "Test goal"

    context = {
        "value": 10
    }

    result = agent.run(context)

    assert result == {
        "value": 10
    }