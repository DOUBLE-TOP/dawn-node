import copy
import random
import asyncio

from src.dawn import DawnClient
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

    async def custom_sleep(self, account: Account, sleep: int = None):
        if sleep is None:
            sleep = random.randint(300, 310)
        self.logger_msg(account, f"💤 Sleeping for {sleep} seconds", 'success')
        await asyncio.sleep(sleep)

    async def run_account(self, accounts: list[Account], index):
        self.logger_msg(accounts[index],
                        f"Task for account {accounts[index].email} was started.", 'success')
        account = copy.deepcopy(accounts[index])
        dawn_node = DawnClient(account)
        failed_requests = 0
        while True:
            new_failures = 0
            new_failures += await dawn_node.get_points()
            new_failures += await dawn_node.keep_alive()
            if new_failures == 2:
                failed_requests += 2
                if failed_requests > 5:
                    await dawn_node.login(force=True)
                    failed_requests = 0
                    continue
                else:
                    continue
            await update_variables_in_file(self, account, await account.account_to_dict())
            await self.custom_sleep(account)

    async def run_accounts(self):
        self.logger_msg(None, "Collect accounts data", 'success')
        accounts = await self.get_accounts()
        tasks = []

        for account in accounts:
            await update_variables_in_file(self, account, await account.account_to_dict())
            await account.get_detailed_dict_for_account()
            self.logger_msg(account, f"Account details - {await account.account_to_dict()}", 'success')

            dawn_node = DawnClient(account)
            for i in range(5):
                await dawn_node.login()
                if 'None' in str(account.token) and 'None' in str(account.app_id):
                    self.logger_msg(account,
                                    f"Login was unsuccessful. Retry #{i} after 30 seconds.", 'warning')
                    await self.custom_sleep(account, 30)
                else:
                    break
            if 'None' in str(account.token) or 'None' in str(account.app_id):
                self.logger_msg(account,
                                "Unfortunately we can't get token for this user. "
                                "Please restart script to try one more time.", 'error')
                await dawn_node.session.close()
                return

            await update_variables_in_file(self, account, await account.account_to_dict())
            await dawn_node.session.close()

        self.logger_msg(None, "Create tasks for accounts", 'success')
        for index, account in enumerate(accounts):
            tasks.append(asyncio.create_task(self.run_account(accounts, index)))

        self.logger_msg(None, "Execute tasks for accounts", 'success')
        await asyncio.gather(*tasks, return_exceptions=True)
