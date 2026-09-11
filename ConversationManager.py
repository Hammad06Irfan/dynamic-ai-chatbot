import json
import instructor
from openai import OpenAI
from schemas import ChatbotResponse
from guardrails import validate_user_input
from mcp_client import MCPClientBridge

class ConversationManager:
    def __init__(
        self,
        api_key: str,
        system_prompt: str = "You are a helpful, technically rigorous engineering assistant.",
        model: str = "openai/gpt-oss-20b",
    ):
        self.raw_client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=api_key
        )
        self.instructor_client = instructor.from_openai(
            self.raw_client,
            mode=instructor.Mode.MD_JSON
        )
        self.model = model
        self.system_prompt = system_prompt
        self.messages = []
        
        # Initialize MCP Bridge
        self.mcp = MCPClientBridge("mcp_server.py")
        # Dynamically discover schemas from the MCP server
        self.tools_schema = self.mcp.get_openai_tools_schema()

    def set_system_prompt(self, new_prompt: str) -> None:
        if self.system_prompt != new_prompt:
            self.system_prompt = new_prompt
            self.clear_history()

    def add_user_message(self, content: str) -> str:
        validated_content = validate_user_input(content)
        self.messages.append({"role": "user", "content": validated_content})
        return validated_content

    def add_ai_message(self, response: ChatbotResponse) -> None:
        self.messages.append({
            "role": "assistant",
            "content": response.response_text,
            "metadata": {
                "intent": response.detected_intent,
                "confidence": response.confidence_score,
                "topics": response.key_topics,
            },
        })

    def generate_response(self, temperature: float = 0.2) -> ChatbotResponse:
        system_instruction = (
            f"{self.system_prompt}\n\n"
            "You have access to tools via an MCP Server for exact math calculations and live web search. "
            "Use them whenever accuracy requires factual verification or arithmetic."
        )

        tool_messages = [{"role": "system", "content": system_instruction}]
        for msg in self.messages:
            tool_messages.append({"role": msg["role"], "content": msg["content"]})

        tool_findings = []

        # Phase 1: Tool Resolution Loop via MCP
        for iteration in range(2):
            try:
                response = self.raw_client.chat.completions.create(
                    model=self.model,
                    messages=tool_messages,
                    tools=self.tools_schema,
                    tool_choice="auto",
                    temperature=temperature
                )
            except Exception as e:
                print(f"[DEBUG ERROR] Tool phase API call failed: {e}")
                break

            choice = response.choices[0].message
            if not choice.tool_calls:
                break

            tool_messages.append({
                "role": "assistant",
                "content": choice.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in choice.tool_calls
                ]
            })

            for tc in choice.tool_calls:
                func_name = tc.function.name
                func_args = json.loads(tc.function.arguments)
                print(f"\n[MCP CLIENT] Requesting tool execution from server: {func_name}({func_args})")

                # Invoke tool on the MCP server
                tool_result = self.mcp.call_tool(func_name, func_args)

                tool_messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "name": func_name,
                    "content": json.dumps(tool_result)
                })

                tool_findings.append(
                    f"MCP Tool `{func_name}` executed with args {func_args} returned:\n{json.dumps(tool_result, indent=2)}"
                )

        # Phase 2: Schema Enforcement with Flattened Context
        final_messages = [{"role": "system", "content": self.system_prompt}]
        for msg in self.messages:
            final_messages.append({"role": msg["role"], "content": msg["content"]})

        if tool_findings:
            context_block = (
                "\n\n---\n**Tool Execution Findings (from MCP Server):**\n"
                + "\n\n".join(tool_findings)
                + "\n---\nUse these exact tool findings to answer the query accurately."
            )
            final_messages.append({"role": "system", "content": context_block})

        try:
            return self.instructor_client.chat.completions.create(
                model=self.model,
                response_model=ChatbotResponse,
                messages=final_messages,
                temperature=temperature,
                max_retries=2
            )
        except Exception as e:
            print(f"\n[DEBUG ERROR] Final schema call failed: {e}\n")
            return ChatbotResponse(
                response_text="I encountered an issue formatting the final output. Please try again.",
                detected_intent="other",
                confidence_score=0.5,
                key_topics=["system_retry"]
            )

    def get_messages(self) -> list:
        return self.messages

    def clear_history(self) -> None:
        self.messages = []