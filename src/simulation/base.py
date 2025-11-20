"""
Base classes for the SDLC SimLab simulation engine.

This module provides the foundational abstractions for building agent-based models.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from uuid import uuid4


@dataclass
class SimulationContext:
    """
    Context object passed to agents during simulation steps.

    Contains information about the current simulation state that agents
    need to make decisions.
    """
    current_day: int
    current_week: int
    random_seed: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def current_timestep(self) -> int:
        """Alias for current_day for clarity."""
        return self.current_day


class Agent(ABC):
    """
    Abstract base class for all agents in the simulation.

    Agents are autonomous entities that make decisions and interact
    with other agents during the simulation.
    """

    def __init__(self, agent_id: Optional[str] = None):
        """
        Initialize an agent.

        Args:
            agent_id: Unique identifier for this agent. Auto-generated if not provided.
        """
        self.agent_id = agent_id or str(uuid4())
        self.created_at: Optional[int] = None  # Set when added to simulation

    @abstractmethod
    def step(self, context: SimulationContext) -> None:
        """
        Execute one time step for this agent.

        This method is called once per simulation timestep and should contain
        the agent's decision-making logic.

        Args:
            context: Current simulation context
        """
        pass

    def on_added_to_simulation(self, timestep: int) -> None:
        """
        Called when the agent is added to a simulation.

        Args:
            timestep: The current timestep when agent was added
        """
        self.created_at = timestep

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.agent_id[:8]}...)"


class SimulationEvent:
    """
    Represents an event that occurred during simulation.

    Events are used for logging, metrics calculation, and debugging.
    """

    def __init__(
        self,
        event_type: str,
        timestep: int,
        agent_id: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a simulation event.

        Args:
            event_type: Type of event (e.g., "pr_created", "pr_merged", "incident")
            timestep: When the event occurred
            agent_id: Agent that triggered the event (if applicable)
            data: Additional event data
        """
        self.event_id = str(uuid4())
        self.event_type = event_type
        self.timestep = timestep
        self.agent_id = agent_id
        self.data = data or {}

    def __repr__(self) -> str:
        return f"SimulationEvent(type={self.event_type}, timestep={self.timestep})"


class Simulation:
    """
    Core simulation engine that orchestrates agent interactions over time.

    The simulation maintains a collection of agents and advances time in
    discrete steps, calling each agent's step() method at each timestep.
    """

    def __init__(
        self,
        name: str = "SDLC Simulation",
        timestep_days: int = 1,
        random_seed: Optional[int] = None
    ):
        """
        Initialize the simulation.

        Args:
            name: Human-readable name for this simulation
            timestep_days: Number of days each timestep represents (default: 1)
            random_seed: Seed for random number generation (for reproducibility)
        """
        self.name = name
        self.timestep_days = timestep_days
        self.random_seed = random_seed

        self.agents: List[Agent] = []
        self.current_timestep: int = 0
        self.events: List[SimulationEvent] = []
        self.is_running: bool = False

    def add_agent(self, agent: Agent) -> None:
        """
        Add an agent to the simulation.

        Args:
            agent: Agent to add
        """
        agent.on_added_to_simulation(self.current_timestep)
        self.agents.append(agent)

        # Log event
        self.log_event(
            event_type="agent_added",
            agent_id=agent.agent_id,
            data={"agent_type": agent.__class__.__name__}
        )

    def remove_agent(self, agent: Agent) -> None:
        """
        Remove an agent from the simulation.

        Args:
            agent: Agent to remove
        """
        if agent in self.agents:
            self.agents.remove(agent)
            self.log_event(
                event_type="agent_removed",
                agent_id=agent.agent_id,
                data={"agent_type": agent.__class__.__name__}
            )

    def log_event(
        self,
        event_type: str,
        agent_id: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> SimulationEvent:
        """
        Log an event that occurred during simulation.

        Args:
            event_type: Type of event
            agent_id: Agent that triggered the event
            data: Additional event data

        Returns:
            The created event
        """
        event = SimulationEvent(
            event_type=event_type,
            timestep=self.current_timestep,
            agent_id=agent_id,
            data=data
        )
        self.events.append(event)
        return event

    def get_context(self) -> SimulationContext:
        """
        Create a context object for the current simulation state.

        Returns:
            Current simulation context
        """
        return SimulationContext(
            current_day=self.current_timestep,
            current_week=self.current_timestep // 7,
            random_seed=self.random_seed
        )

    def step(self) -> None:
        """
        Advance the simulation by one timestep.

        Calls step() on all agents in the simulation.
        """
        context = self.get_context()

        # Let each agent take their step
        for agent in self.agents:
            agent.step(context)

        self.current_timestep += 1

    def run(self, num_steps: int) -> None:
        """
        Run the simulation for a specified number of steps.

        Args:
            num_steps: Number of timesteps to simulate
        """
        self.is_running = True

        for _ in range(num_steps):
            if not self.is_running:
                break
            self.step()

        self.is_running = False

    def stop(self) -> None:
        """Stop the simulation early."""
        self.is_running = False

    def reset(self) -> None:
        """Reset the simulation to initial state."""
        self.current_timestep = 0
        self.events.clear()
        self.agents.clear()
        self.is_running = False

    def get_events_by_type(self, event_type: str) -> List[SimulationEvent]:
        """
        Get all events of a specific type.

        Args:
            event_type: Type of event to filter by

        Returns:
            List of matching events
        """
        return [e for e in self.events if e.event_type == event_type]

    def get_events_by_agent(self, agent_id: str) -> List[SimulationEvent]:
        """
        Get all events for a specific agent.

        Args:
            agent_id: Agent ID to filter by

        Returns:
            List of matching events
        """
        return [e for e in self.events if e.agent_id == agent_id]

    def __repr__(self) -> str:
        return (
            f"Simulation(name={self.name}, "
            f"timestep={self.current_timestep}, "
            f"agents={len(self.agents)})"
        )
