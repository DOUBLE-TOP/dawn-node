import asyncio

from src.runner import Runner

if __name__ == "__main__":
    runner = Runner()
    asyncio.run(runner.run_accounts())
