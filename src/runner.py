import copy
import random
import asyncio

from src.dawn import DawnClient
from src.models.exceptions import TokenException
from src.utils.logger import Logger


from src.models.account import Account, default_dict_to_account
from src.utils.file_manager import read_accounts, update_variables_in_file


class Runner(Logger):

    @staticmethod
    async def get_accounts() -> list[Account]:
        accounts = []
        accounts_data = await read_accounts()
        for account in accounts_data:
            accounts.append(await default_dict_to_account(account))

        return accounts

    async def custom_sleep(self, account: Account):
        duration = random.randint(300, 310)
        self.logger_msg(account, f"💤 Sleeping for {duration} seconds", 'success')
        await asyncio.sleep(duration)

    async def run_account(self, accounts: list[Account], index):
        self.logger_msg(accounts[index],
                        f"Task for account {accounts[index].email} was started.", 'success')
        account = copy.deepcopy(accounts[index])
        await account.get_detailed_dict_for_account()
        await update_variables_in_file(self, account, await account.account_to_dict())
        self.logger_msg(account, f"Account details - {await account.account_to_dict()}", 'success')

        dawn_node = DawnClient(account)
        await dawn_node.login()
        await update_variables_in_file(self, account, await account.account_to_dict())
        while True:
            try:
                await dawn_node.get_points()
                await dawn_node.keep_alive()
                await update_variables_in_file(self, account, await account.account_to_dict())
                await self.custom_sleep(account)
            except TokenException:
                await dawn_node.login(force=True)

    async def run_accounts(self):
        self.logger_msg(None, "Collect accounts data", 'success')
        accounts = await self.get_accounts()
        tasks = []

        self.logger_msg(None, "Create tasks for accounts", 'success')
        for index, account in enumerate(accounts):
            tasks.append(asyncio.create_task(self.run_account(accounts, index)))

        self.logger_msg(None, "Execute tasks for accounts", 'success')
        await asyncio.gather(*tasks, return_exceptions=True)
