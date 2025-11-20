"""
Unit tests for the base Simulation class.
"""

import pytest

from src.simulation.base import Simulation, Agent, SimulationContext, SimulationEvent


class TestAgent(Agent):
    """Concrete test agent for testing."""

    def __init__(self):
        super().__init__()
        self.step_count = 0

    def step(self, context: SimulationContext) -> None:
        """Count steps."""
        self.step_count += 1


class TestSimulation:
    """Test base Simulation class."""

    def test_simulation_creation(self):
        """Test creating a simulation."""
        sim = Simulation(name="Test Sim")

        assert sim.name == "Test Sim"
        assert sim.current_timestep == 0
        assert len(sim.agents) == 0
        assert not sim.is_running

    def test_add_agent(self):
        """Test adding an agent to the simulation."""
        sim = Simulation()
        agent = TestAgent()

        sim.add_agent(agent)

        assert len(sim.agents) == 1
        assert agent.created_at == 0
        assert len(sim.events) == 1  # agent_added event

    def test_remove_agent(self):
        """Test removing an agent."""
        sim = Simulation()
        agent = TestAgent()

        sim.add_agent(agent)
        sim.remove_agent(agent)

        assert len(sim.agents) == 0
        assert len(sim.events) == 2  # agent_added + agent_removed

    def test_step(self):
        """Test stepping the simulation."""
        sim = Simulation()
        agent1 = TestAgent()
        agent2 = TestAgent()

        sim.add_agent(agent1)
        sim.add_agent(agent2)

        sim.step()

        assert sim.current_timestep == 1
        assert agent1.step_count == 1
        assert agent2.step_count == 1

    def test_run(self):
        """Test running the simulation for multiple steps."""
        sim = Simulation()
        agent = TestAgent()

        sim.add_agent(agent)
        sim.run(10)

        assert sim.current_timestep == 10
        assert agent.step_count == 10
        assert not sim.is_running

    def test_reset(self):
        """Test resetting the simulation."""
        sim = Simulation()
        agent = TestAgent()

        sim.add_agent(agent)
        sim.run(5)

        sim.reset()

        assert sim.current_timestep == 0
        assert len(sim.agents) == 0
        assert len(sim.events) == 0

    def test_log_event(self):
        """Test logging events."""
        sim = Simulation()
        event = sim.log_event(
            event_type="test_event",
            agent_id="agent123",
            data={"key": "value"}
        )

        assert event.event_type == "test_event"
        assert event.agent_id == "agent123"
        assert event.data["key"] == "value"
        assert len(sim.events) == 1

    def test_get_events_by_type(self):
        """Test filtering events by type."""
        sim = Simulation()

        sim.log_event("type_a", data={"num": 1})
        sim.log_event("type_b", data={"num": 2})
        sim.log_event("type_a", data={"num": 3})

        type_a_events = sim.get_events_by_type("type_a")

        assert len(type_a_events) == 2
        assert all(e.event_type == "type_a" for e in type_a_events)

    def test_get_events_by_agent(self):
        """Test filtering events by agent."""
        sim = Simulation()

        sim.log_event("event", agent_id="agent1")
        sim.log_event("event", agent_id="agent2")
        sim.log_event("event", agent_id="agent1")

        agent1_events = sim.get_events_by_agent("agent1")

        assert len(agent1_events) == 2
        assert all(e.agent_id == "agent1" for e in agent1_events)


class TestSimulationContext:
    """Test SimulationContext."""

    def test_context_creation(self):
        """Test creating a simulation context."""
        context = SimulationContext(
            current_day=42,
            current_week=6,
            random_seed=123
        )

        assert context.current_day == 42
        assert context.current_week == 6
        assert context.current_timestep == 42
        assert context.random_seed == 123

    def test_timestep_alias(self):
        """Test that current_timestep is an alias for current_day."""
        context = SimulationContext(current_day=10, current_week=1)

        assert context.current_timestep == context.current_day


class TestSimulationEvent:
    """Test SimulationEvent."""

    def test_event_creation(self):
        """Test creating a simulation event."""
        event = SimulationEvent(
            event_type="pr_created",
            timestep=5,
            agent_id="dev123",
            data={"pr_id": "pr456"}
        )

        assert event.event_type == "pr_created"
        assert event.timestep == 5
        assert event.agent_id == "dev123"
        assert event.data["pr_id"] == "pr456"
        assert event.event_id is not None
