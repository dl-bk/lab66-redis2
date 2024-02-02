import redis
import bcrypt

class ShoppingCart:
    def __init__(self):
        self.redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)

    def register_user(self, username, password):
        # Перевірка, чи користувач вже існує
        if self.redis_client.hexists(username, 'password_hash'):
            print("Користувач вже існує.")
            return False
        # Зберігання хешу пароля у Redis
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        self.redis_client.hset(username, 'password_hash', password_hash)
        print("Користувач успішно зареєстрований.")
        return True

    def login(self, username, password):
        # Перевірка логіну та пароля
        stored_password_hash = self.redis_client.hget(username, 'password_hash')
        if stored_password_hash and bcrypt.checkpw(password.encode('utf-8'), stored_password_hash.encode('utf-8')):
            print(f"Ви увійшли як {username}.")
            self.current_user = username
            return True
        else:
            print("Невірний логін або пароль.")
            return False

    def add_item(self, item_id, quantity=1):
        key = f"cart:{self.current_user}:{item_id}"
        if self.redis_client.hexists(key, 'quantity'):
            self.redis_client.hincrby(key, 'quantity', quantity)
        else:
            self.redis_client.hset(key, mapping={'item_id': item_id, 'quantity': quantity})
        print(f"Товар {item_id} додано до кошика.")

    def remove_item(self, item_id):
        key = f"cart:{self.current_user}:{item_id}"
        self.redis_client.delete(key)
        print(f"Товар {item_id} видалено з кошика.")

    def update_item_quantity(self, item_id, quantity):
        key = f"cart:{self.current_user}:{item_id}"
        if self.redis_client.hexists(key, 'quantity'):
            self.redis_client.hset(key, 'quantity', quantity)
            print(f"Кількість товару {item_id} оновлено.")
        else:
            print(f"Товар {item_id} не знайдено у кошику.")

    def clear_cart(self):
        keys = self.redis_client.keys(f"cart:{self.current_user}:*")
        for key in keys:
            self.redis_client.delete(key)
        print("Кошик очищено.")

    def search_item(self, item_id):
        key = f"cart:{self.current_user}:{item_id}"
        item_data = self.redis_client.hgetall(key)
        if item_data:
            print(f"Інформація про товар: {item_data}")
        else:
            print(f"Товар {item_id} не знайдено.")

    def view_cart(self):
        keys = self.redis_client.keys(f"cart:{self.current_user}:*")
        if not keys:
            print("Кошик пустий.")
            return []
        cart_items = []
        for key in keys:
            item_data = self.redis_client.hgetall(key)
            cart_items.append(item_data)
        print("Вміст кошика:", cart_items)
        return cart_items

# Приклад використання
cart_app = ShoppingCart()

# Реєстрація та логін користувача
if cart_app.register_user("user6", "122"):
    if cart_app.login("user6", "122"):
        # Додавання товарів
        cart_app.add_item("item1", quantity=3)
        cart_app.add_item("item2", quantity=1)

        # Перегляд кошика
        cart_app.view_cart()

        # Зміна кількості товару
        cart_app.update_item_quantity("item1", quantity=5)

        # Пошук товару
        cart_app.search_item("item2")

        # Видалення товару
        cart_app.remove_item("item2")

        # Перегляд оновленого кошика
        cart_app.view_cart()

        # Повне очищення кошика
        cart_app.clear_cart()
        cart_app.view_cart()