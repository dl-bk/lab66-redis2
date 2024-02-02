# Реалізуйте консольний додаток «Таблиця рекордів»
# для гри. Дода-ток має дозволити працювати з таблицею
# рекордів гри. Можливості додатку:
# ■ Вхід у таблицю рекордів за логіном і паролем;
# ■ Додати результати користувача до таблиці;
# ■ Видаляти результати з таблиці;
# ■ Змінювати результат в таблиці;
# ■ Повне очищення таблиці;
# ■ Пошук даних в таблиці;
# ■ Перегляд вмісту таблиці;
# ■ Відображення найкращої десятки результатів.
# Зберігайте дані у базі даних NoSQL. Можете використовувати Redis в якості платформи.

import redis 
import hashlib



class UserManager:
    def __init__(self, redis_client) -> None:
        self.redis_client = redis_client
    
    def register_user(self, username, password):
        user_id = hashlib.sha256(username.encode()).hexdigest()

        if self.redis_client.hget('users', user_id):
            return False
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        self.redis_client.hset('users', user_id, f'{username}:{hashed_password}')

        print("successfull registration")
        return user_id

    def login_user(self, username, password):
        user_id = hashlib.sha256(username.encode()).hexdigest()
        user_data = self.redis_client.hget('users', user_id)
        if user_data is not None:
            stored_username, stored_hash_password = user_data.split(':')
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            if stored_username == username and hashed_password == stored_hash_password:
                print("Successfull login")
                return True
            else:
                print("Invalid login or password")
                return False
        else:
            print("user does not exists")
            return False

class Scoreboard:
    def __init__(self, redis_client) -> None:
        self.redis_client = redis_client
    
    def add_score(self, username, score) -> bool:
        user_id = hashlib.sha256(username.encode()).hexdigest()
        user_data = self.redis_client.hget('users', user_id)
        if user_data is not None:
            self.redis_client.zadd('users_scores', {username:score})
            return True
        else:
            print("user does not exist")
            return False

    def remove_score(self, username) -> bool:
        score_exists = self.redis_client.zscore('users_scores', username)
        if score_exists is not None:
            self.redis_client.zrem('users_scores', username)
            return True
        else:
            print(f"User '{username}' does not exist in 'users_scores'")
            return False
    
    def view_user_score(self, username):
        user_score = self.redis_client.zscore('users_scores', username)
        if user_score is not None:
            print(user_score)
    def view_scoreboard(self) -> None:
        all_scores = self.redis_client.zrevrange('users_scores', 0, -1, withscores=True)
        for username, score in all_scores:
            print(f"{username}: {score}")
    
    def clear_scoreboard(self):
        self.redis_client.zremrangebyrank('users_scores', 0, -1)
        print("Table 'users_scores' cleared successfully")


redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
usermanager = UserManager(redis_client=redis_client)
scoreboard = Scoreboard(redis_client=redis_client)


scoreboard.view_user_score('user3')

scoreboard.view_scoreboard()




