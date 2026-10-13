from __future__ import annotations

import json
from uuid import uuid4

from .domain import Message, RunResult
from .evaluation.rules import evaluate_response
from .memory import ConversationMemory
from .prompt_loader import PromptLoader
from .providers.base import Provider
from .tools.registry import ToolRegistry
from .tracing import TraceWriter


class Harness:
    def __init__(
        self,
        *,
        provider: Provider,
        prompt_loader: PromptLoader,
        prompt_names: tuple[str, ...],
        tools: ToolRegistry,
        memory: ConversationMemory,
        tracer: TraceWriter,
        max_tool_rounds: int = 4,
    ) -> None:
        self.provider = provider
        self.prompt_loader = prompt_loader
        self.prompt_names = prompt_names
        self.tools = tools
        self.memory = memory
        self.tracer = tracer
        self.max_tool_rounds = max_tool_rounds

    def run(self, user_input: str) -> RunResult:
        if not user_input.strip():
            raise ValueError("Le message utilisateur ne peut pas être vide")
        if len(user_input) > 100_000:
            raise ValueError("Le message utilisateur dépasse 100 000 caractères")

        run_id = uuid4().hex
        instructions = self.prompt_loader.compose(self.prompt_names)
        conversation = self.memory.snapshot()
        user_message = Message(role="user", content=user_input.strip())
        conversation.append(user_message)
        self.tracer.write(
            run_id,
            "run_started",
            prompt_names=self.prompt_names,
            memory_messages=len(conversation) - 1,
        )

        continuation: str | None = None
        total_tool_calls = 0
        for round_index in range(self.max_tool_rounds + 1):
            reply = self.provider.generate(
                messages=conversation,
                instructions=instructions,
                tools=self.tools.schemas(),
                continuation_token=continuation,
            )
            self.tracer.write(
                run_id,
                "model_response",
                round=round_index,
                text=reply.text,
                tool_calls=[call.name for call in reply.tool_calls],
            )

            if not reply.tool_calls:
                final_text = reply.text.strip()
                evaluation = evaluate_response(final_text)
                self.memory.add(user_message)
                self.memory.add(Message(role="assistant", content=final_text))
                self.tracer.write(
                    run_id,
                    "run_finished",
                    score=evaluation.score,
                    tool_calls=total_tool_calls,
                )
                return RunResult(
                    run_id=run_id,
                    text=final_text,
                    tool_calls=total_tool_calls,
                    evaluation=evaluation,
                    metadata={"rounds": round_index + 1},
                )

            if round_index >= self.max_tool_rounds:
                self.tracer.write(run_id, "run_failed", reason="tool_round_limit")
                raise RuntimeError("Limite de tours d'outils atteinte")

            for call in reply.tool_calls:
                result = self.tools.execute(call.name, call.arguments)
                serialized = json.dumps(result, ensure_ascii=False, default=str)
                conversation.append(
                    Message(role="tool", content=serialized, tool_call_id=call.call_id)
                )
                total_tool_calls += 1
                self.tracer.write(
                    run_id,
                    "tool_executed",
                    tool=call.name,
                    call_id=call.call_id,
                    arguments=call.arguments,
                    result=result,
                )
            continuation = reply.continuation_token

        raise RuntimeError("Le harness s'est arrêté sans réponse finale")

