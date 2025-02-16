import copy
import random
import asyncio

from src.dawn import DawnClient
from src.models.exceptions import TokenException, SoftwareException
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
        while True:
            try:
                await dawn_node.get_points()
                await dawn_node.keep_alive()
                await update_variables_in_file(self, account, await account.account_to_dict())
                await self.custom_sleep(account)
            except TokenException:
                await dawn_node.login(force=True)
            except SoftwareException:
                continue

    async def run_accounts(self):
        self.logger_msg(None, "Collect accounts data", 'success')
        accounts = await self.get_accounts()
        tasks = []
        workable_accounts = []
        skipped_accounts = []

        for account in accounts:
            await update_variables_in_file(self, account, await account.account_to_dict())
            await account.get_detailed_dict_for_account()
            self.logger_msg(account, f"Account details - {await account.account_to_dict()}", 'success')

            dawn_node = DawnClient(account)
            await dawn_node.login()

            if 'None' in str(account.token) or 'None' in str(account.app_id):
                self.logger_msg(account,
                                "Unfortunately we can't get token for this user. "
                                "Please restart script to try one more time.", 'error')
                await dawn_node.session.close()
                skipped_accounts.append(account)
                continue

            await update_variables_in_file(self, account, await account.account_to_dict())
            await dawn_node.session.close()
            workable_accounts.append(account)

        if skipped_accounts:
            self.logger_msg(None, "The list of skipped accounts", 'error')
            for skipped_account in skipped_accounts:
                self.logger_msg(None, f"Email: {skipped_account.email}", 'error')

        self.logger_msg(None, "Create tasks for accounts", 'success')
        for index, account in enumerate(workable_accounts):
            tasks.append(asyncio.create_task(self.run_account(workable_accounts, index)))

        self.logger_msg(None, "Execute tasks for accounts", 'success')
        await asyncio.gather(*tasks, return_exceptions=True)
