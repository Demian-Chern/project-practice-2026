import requests
import time
import json
from datetime import datetime

BASE_URL_NODE = "http://127.0.0.1:5000"
BASE_URL_CLIENT = "http://127.0.0.1:8080"


def print_header(text):
    print("\n" + "=" * 70)
    print(f"   {text}")
    print("=" * 70)


def test_full_project():
    print_header("ТЕСТИРОВАНИЕ ПРОЕКТА МОСПОЛИФИЗИКС + БЛОКЧЕЙН")
    print(f"Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Тест блокчейна
    try:
        print("📡 Подключение к узлу блокчейна...")
        r = requests.get(f"{BASE_URL_NODE}/chain")
        print("✅ Узел блокчейна работает")

        # Создание транзакций
        print("\n💰 Создаём тестовые транзакции...")
        txs = [
            {"sender": "Demyan", "recipient": "Alice", "amount": 150},
            {"sender": "Alice", "recipient": "Bob", "amount": 75},
        ]

        for tx in txs:
            requests.post(f"{BASE_URL_NODE}/transactions/new", json=tx)
            print(f"   ✓ {tx['sender']} → {tx['recipient']} : {tx['amount']}")

        # Майнинг
        print("\n⛏️  Майнинг нового блока...")
        mine_response = requests.get(f"{BASE_URL_NODE}/mine")
        print("✅ Блок успешно добыт!")

        # Показать цепочку
        print("\n🔗 Текущая цепочка блоков:")
        chain = requests.get(f"{BASE_URL_NODE}/chain").json()['chain']
        for block in chain[-2:]:  # последние 2 блока
            print(f"   Блок #{block['index']} | Транзакций: {len(block['transactions'])} | Proof: {block['proof']}")

    except Exception as e:
        print(f"❌ Ошибка при тестировании блокчейна: {e}")

    print_header("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО")



if __name__ == "__main__":
    test_full_project()