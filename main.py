import asyncio

from src.runner import Runner

if __name__ == "__main__":
    try:
        runner = Runner()
        asyncio.run(runner.run_accounts())
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
