import asyncio
import random
from token_config import TOKEN_CONFIG, STABLECOINS
from my_swap_abi import MY_SWAP_ABI
from eth_price import price
from loguru import logger
from starknet_py.contract import Contract
from starknet_py.net.account.account import Account
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.signer.stark_curve_signer import KeyPair


delay = (1, 10)

amount_to_swap = random.uniform(0.0001, 0.0003)

scan = 'https://starkscan.co/tx/'

async def eth_to_stable(key, stablecoin_config, stablecoin, amount_to_swap, address):
    try:
        account = Account(address=address,
                          client=GatewayClient(net='mainnet'),
                          key_pair=KeyPair.from_private_key(int(key[2:], 16)),
                          chain=StarknetChainId.MAINNET)
        stablecoin_decimals = stablecoin_config['decimals']
        approve_address = stablecoin_config['approve_address']
        pool_id = stablecoin_config['pool_id']  # Добавляем pool_id в конфигурацию
        eth_address = TOKEN_CONFIG['ETH']['address']
        eth_abi = TOKEN_CONFIG['ETH']['abi']
        logger.info(f'Выбрал {stablecoin} стейблкоин')

        current_nonce = await account.get_nonce()

        eth_balance_wei = await account.get_balance()
        eth_balance = eth_balance_wei / 10 ** 18  # текущий баланс в эфирах

        if amount_to_swap > eth_balance:  # проверка баланса
            logger.info(
                f'Случайное количество эфиров ({amount_to_swap}) больше текущего баланса ({eth_balance}). Пропускаем кошелек.')
            return  # выход из функции, не выполняя свап

        # Рассчитываем актуальную цену на основе выбранного количества эфира
        price_eth = float(price * 0.98 * amount_to_swap)  # price ethusdc with slippage 2%
        price_eth_unit256 = int(price_eth * 10 ** stablecoin_decimals)  # price ethusdc with slippage 2% in uint256

        amount_wei = int(amount_to_swap * 10 ** 18)  # перевод в wei
        logger.info(f"Начало отправки транзакций: Свап {amount_to_swap} эфира на {price_eth} {stablecoin}")

        approve_stable = Contract(
            address=eth_address,
            abi=eth_abi,
            provider=account,
        )

        swap = Contract(
            address=approve_address,
            abi=MY_SWAP_ABI,
            provider=account,
        )

        approve_tx = approve_stable.functions["approve"].prepare(
            approve_address,
            amount_wei
        )

        swap_tx = swap.functions["swap"].prepare(
            pool_id,
            0x49d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7,
            amount_wei,
            price_eth_unit256
        )

        calls = [approve_tx, swap_tx]
        tx = await account.execute(calls=calls, auto_estimate=True,cairo_version=1,nonce=current_nonce)
        status = await account.client.wait_for_tx(tx.transaction_hash)
        if status.status.name in ['SUCCEEDED', 'ACCEPTED_ON_L1', 'ACCEPTED_ON_L2']:
            current_nonce += 1
            logger.success(
                f'{address} - транзакция подтвердилась, аккаунт успешно отправил ETH {scan}{hex(tx.transaction_hash)}')
            return 'updated'
        else:
            logger.error(f'{address} - транзакция неуспешна...')
            return 'error in tx'
    except Exception as e:
        error = str(e)
        if 'StarknetErrorCode.INSUFFICIENT_ACCOUNT_BALANCE' in error:
            logger.error(f'{address} - Не хватает баланса на деплой аккаунта...')
            return 'not balance'
        else:
            logger.error(f'{address} - ошибка {e}')
        return e

async def stable_to_eth(key,stablecoin_config, stablecoin, amount_to_swap, address):
    try:
        account = Account(address=address,
                          client=GatewayClient(net='mainnet'),
                          key_pair=KeyPair.from_private_key(int(key[2:], 16)),
                          chain=StarknetChainId.MAINNET)

        current_nonce = await account.get_nonce()

        stablecoin_address = stablecoin_config['address']
        stablecoin_abi = stablecoin_config['abi']
        stablecoin_decimals = stablecoin_config['decimals']
        approve_address = stablecoin_config['approve_address']
        pool_id = stablecoin_config['pool_id']  # Добавляем pool_id в конфигурацию

        stable_balance_wei = await account.get_balance(stablecoin_address)
        stable_balance = stable_balance_wei / 10 ** stablecoin_decimals  # текущий баланс в stable

        eth_min = float((stable_balance / price) * 0.97)
        eth_min_wei = int(eth_min * 10 ** 18)
        stable_balance_wei = int(await account.get_balance(stablecoin_address))
        logger.info(f"Начало отправки транзакций: Свап {stable_balance} {stablecoin} на {eth_min} эфир.")
        approve_stable = Contract(
            address=stablecoin_address,
            abi=stablecoin_abi,
            provider=account,
        )

        swap = Contract(
            address=approve_address,
            abi=MY_SWAP_ABI,
            provider=account,
        )

        approve_tx = approve_stable.functions["approve"].prepare(
            approve_address,  # SPENDER
            stable_balance_wei,  # AMOUNT
        )

        swap_tx = swap.functions["swap"].prepare(
            pool_id,  # POOL ID
            stablecoin_address,  # TOKEN FROM
            stable_balance_wei,  # AMOUNT FROM
            eth_min_wei,  # AMOUNT_TO_MIN
        )

        calls = [approve_tx, swap_tx]
        resp = await account.execute(calls=calls, auto_estimate=True, cairo_version=1)
        status = await account.client.wait_for_tx(resp.transaction_hash)
        if status.status.name in ['SUCCEEDED', 'ACCEPTED_ON_L1', 'ACCEPTED_ON_L2']:
            current_nonce += 1
            logger.success(
                f'{address} - транзакция подтвердилась, аккаунт успешно забрал ETH {scan}{hex(resp.transaction_hash)}')
            return 'updated'
        else:
            logger.error(f'{address} - транзакция неуспешна...')
            return 'error in tx'
    except Exception as e:
        error = str(e)
        if 'StarknetErrorCode.INSUFFICIENT_ACCOUNT_BALANCE' in error:
            logger.error(f'{address} - Не хватает баланса на деплой аккаунта...')
            return 'not balance'
        else:
            logger.error(f'{address} - ошибка {e}')
        return e


async def main():
    with open("keys.txt", "r") as f:
        keys = [row.strip() for row in f]

    with open("addresses.txt", "r") as f:
        addresses = [row.strip() for row in f]

    for address, key in zip(addresses, keys):
        logger.info('Начинаем срипт')
        chosen_stablecoin = random.choice(STABLECOINS)  # Выбираем стейблкоин один раз
        stablecoin_config = TOKEN_CONFIG[chosen_stablecoin]

        # Используйте переменную address вместо генерации адреса из ключа
        await eth_to_stable(key, stablecoin_config, chosen_stablecoin, amount_to_swap, address)

        t = random.randint(*delay)
        logger.info(f'сплю {t} секунд')
        await asyncio.sleep(t)

        # Используйте переменную address вместо генерации адреса из ключа
        await stable_to_eth(key, stablecoin_config, chosen_stablecoin, amount_to_swap, address)

        logger.info('Закончили')


asyncio.run(main())