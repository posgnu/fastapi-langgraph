import asyncio
import json

import httpx


async def main() -> None:
    """An asynchronous chat client for the FastAPI streaming API."""
    print("Starting chat client...")
    print("Type 'exit' or press Ctrl+C to quit.")

    async with httpx.AsyncClient(timeout=None) as client:
        while True:
            try:
                user_input = await asyncio.to_thread(input, "You: ")
                if user_input.lower() == "exit":
                    break

                request_data = {"input": user_input}

                async with client.stream(
                    "POST", "http://localhost:8000/stream", json=request_data
                ) as response:
                    print("AI: ", end="", flush=True)
                    async for line in response.aiter_lines():
                        if line:
                            try:
                                data = json.loads(line)
                                print(data.get("data", ""), end="", flush=True)
                            except json.JSONDecodeError:
                                print(f"\nCould not decode: {line}")
                    print()

            except KeyboardInterrupt:
                print("\nExiting chat.")
                break
            except httpx.RequestError as e:
                print(f"\nAn error occurred: {e}")
                break


if __name__ == "__main__":
    asyncio.run(main())
