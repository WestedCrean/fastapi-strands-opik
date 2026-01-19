from threading import Lock
from strands import Agent, tool
from strands.hooks import (
    BeforeInvocationEvent,
    BeforeToolCallEvent,
    HookProvider,
    HookRegistry,
)


class LimitSQLAgentCalls(HookProvider):
    """Limits the sqlagent tool to 3 calls per invocation"""

    def __init__(self, max_calls: int = 3):
        self.sql_call_count = 0
        self.max_calls = max_calls
        self._lock = Lock()

    def register_hooks(self, registry: HookRegistry) -> None:
        """Register the hooks for this provider"""
        registry.add_callback(BeforeInvocationEvent, self.reset_counter)
        registry.add_callback(BeforeToolCallEvent, self.check_sql_limit)

    def reset_counter(self, event: BeforeInvocationEvent) -> None:
        """Reset the counter at the start of each agent invocation"""
        with self._lock:
            self.sql_call_count = 0

    def check_sql_limit(self, event: BeforeToolCallEvent) -> None:
        """Check if sqlagent has exceeded its call limit"""
        tool_name = event.tool_use["name"]

        # Only track sqlagent tool
        if tool_name == "sqlagent":
            with self._lock:
                self.sql_call_count += 1

                if self.sql_call_count > self.max_calls:
                    event.cancel_tool = (
                        f"The sqlagent tool has reached its maximum limit of {self.max_calls} calls. "
                        f"You MUST now provide an answer based on the information already gathered. "
                        f"DO NOT attempt to call sqlagent again."
                    )
