import sqlite3
from datetime import datetime

def create_blog_database():
    """Создание базы данных и таблиц для блога"""
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()

    try:
        # Таблица пользователей
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Таблица категорий
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT
            )
        """)
        
        # Таблица постов (с внешними ключами)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                category_id INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        """)
        
        # Таблица комментариев
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                post_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Включаем поддержку внешних ключей
        cursor.execute("PRAGMA foreign_keys = ON")
        
        conn.commit()
        print("✅ База данных блога успешно создана!")
        
    except sqlite3.Error as e:
        conn.rollback()
        print(f"❌ Ошибка при создании БД: {e}")
    finally:
        conn.close()

def add_user(username, email):
    """Добавление нового пользователя"""
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO users (username, email) 
            VALUES (?, ?)
        """, (username, email))
        
        conn.commit()
        print(f"✅ Пользователь '{username}' успешно добавлен!")
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        print(f"❌ Ошибка: пользователь с таким именем или email уже существует")
        return None
    except sqlite3.Error as e:
        print(f"❌ Ошибка при добавлении пользователя: {e}")
        return None
    finally:
        conn.close()

def add_category(name, description=None):
    """Добавление новой категории"""
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO categories (name, description) 
            VALUES (?, ?)
        """, (name, description))
        
        conn.commit()
        print(f"✅ Категория '{name}' успешно добавлена!")
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        print(f"❌ Ошибка: категория с таким названием уже существует")
        return None
    except sqlite3.Error as e:
        print(f"❌ Ошибка при добавлении категории: {e}")
        return None
    finally:
        conn.close()

def create_post(title, content, user_id, category_id):
    """Создание нового поста"""
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    
    try:
        # Проверяем существование пользователя
        cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        if not cursor.fetchone():
            print(f"❌ Ошибка: пользователь с ID {user_id} не существует")
            return None
        
        # Проверяем существование категории
        cursor.execute("SELECT id FROM categories WHERE id = ?", (category_id,))
        if not cursor.fetchone():
            print(f"❌ Ошибка: категория с ID {category_id} не существует")
            return None
        
        cursor.execute("""
            INSERT INTO posts (title, content, user_id, category_id) 
            VALUES (?, ?, ?, ?)
        """, (title, content, user_id, category_id))
        
        conn.commit()
        print(f"✅ Пост '{title}' успешно создан!")
        return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"❌ Ошибка при создании поста: {e}")
        return None
    finally:
        conn.close()

def add_comment(text, post_id, user_id):
    """Добавление комментария к посту"""
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    
    try:
        # Проверяем существование поста
        cursor.execute("SELECT id FROM posts WHERE id = ?", (post_id,))
        if not cursor.fetchone():
            print(f"❌ Ошибка: пост с ID {post_id} не существует")
            return None
        
        # Проверяем существование пользователя
        cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        if not cursor.fetchone():
            print(f"❌ Ошибка: пользователь с ID {user_id} не существует")
            return None
        
        cursor.execute("""
            INSERT INTO comments (text, post_id, user_id) 
            VALUES (?, ?, ?)
        """, (text, post_id, user_id))
        
        conn.commit()
        print(f"✅ Комментарий успешно добавлен!")
        return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"❌ Ошибка при добавлении комментария: {e}")
        return None
    finally:
        conn.close()

def get_all_posts_with_authors():
    """Получение всех постов с именами авторов и категориями (используя JOIN)"""
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                p.id,
                p.title,
                p.content,
                p.created_at,
                u.username as author,
                c.name as category
            FROM posts p
            JOIN users u ON p.user_id = u.id
            JOIN categories c ON p.category_id = c.id
            ORDER BY p.created_at DESC
        """)
        
        posts = cursor.fetchall()
        
        print("\n" + "="*80)
        print("📝 ВСЕ ПОСТЫ В БЛОГЕ")
        print("="*80)
        
        if not posts:
            print("Пока нет ни одного поста")
            return []
        
        for post in posts:
            post_id, title, content, created_at, author, category = post
            print(f"\n🏷️  ID: {post_id}")
            print(f"📖 Заголовок: {title}")
            print(f"📝 Содержание: {content[:100]}..." if len(content) > 100 else f"📝 Содержание: {content}")
            print(f"👤 Автор: {author}")
            print(f"📂 Категория: {category}")
            print(f"📅 Дата: {created_at}")
            print("-" * 80)
        
        return posts
    except sqlite3.Error as e:
        print(f"❌ Ошибка при получении постов: {e}")
        return []
    finally:
        conn.close()

def get_posts_with_comments():
    """Получение постов с комментариями и авторами комментариев"""
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                p.id as post_id,
                p.title as post_title,
                u1.username as post_author,
                c.text as comment_text,
                u2.username as comment_author,
                c.created_at as comment_date
            FROM posts p
            JOIN users u1 ON p.user_id = u1.id
            LEFT JOIN comments c ON p.id = c.post_id
            LEFT JOIN users u2 ON c.user_id = u2.id
            ORDER BY p.created_at DESC, c.created_at ASC
        """)
        
        results = cursor.fetchall()
        
        print("\n" + "="*80)
        print("💬 ПОСТЫ С КОММЕНТАРИЯМИ")
        print("="*80)
        
        current_post = None
        for row in results:
            post_id, post_title, post_author, comment_text, comment_author, comment_date = row
            
            if current_post != post_id:
                current_post = post_id
                print(f"\n📖 Пост: '{post_title}' (автор: {post_author})")
                print("-" * 40)
            
            if comment_text:
                print(f"   💭 {comment_author}: {comment_text}")
                print(f"   📅 {comment_date}")
            else:
                print("   💭 Пока нет комментариев")
        
        return results
    except sqlite3.Error as e:
        print(f"❌ Ошибка при получении постов с комментариями: {e}")
        return []
    finally:
        conn.close()

def get_users_with_post_count():
    """Получение пользователей с количеством их постов"""
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                u.id,
                u.username,
                u.email,
                COUNT(p.id) as post_count
            FROM users u
            LEFT JOIN posts p ON u.id = p.user_id
            GROUP BY u.id, u.username, u.email
            ORDER BY post_count DESC
        """)
        
        users = cursor.fetchall()
        
        print("\n" + "="*50)
        print("👥 ПОЛЬЗОВАТЕЛИ И ИХ АКТИВНОСТЬ")
        print("="*50)
        
        for user in users:
            user_id, username, email, post_count = user
            print(f"👤 {username} ({email}) - постов: {post_count}")
        
        return users
    except sqlite3.Error as e:
        print(f"❌ Ошибка при получении пользователей: {e}")
        return []
    finally:
        conn.close()

# Демонстрация работы всех функций
def demo_blog_system():
    """Демонстрация работы системы блога"""
    print("🚀 ЗАПУСК ДЕМОНСТРАЦИИ СИСТЕМЫ БЛОГА")
    print("=" * 50)
    
    # Создаем базу данных
    create_blog_database()
    
    # Добавляем пользователей
    print("\n1. ДОБАВЛЕНИЕ ПОЛЬЗОВАТЕЛЕЙ:")
    user1_id = add_user("alex_dev", "alex@example.com")
    user2_id = add_user("maria_writer", "maria@example.com")
    user3_id = add_user("tech_guru", "tech@example.com")
    
    # Добавляем категории
    print("\n2. ДОБАВЛЕНИЕ КАТЕГОРИЙ:")
    cat1_id = add_category("Программирование", "Статьи о разработке ПО")
    cat2_id = add_category("Дизайн", "UI/UX дизайн и графика")
    cat3_id = add_category("Наука", "Научные статьи и исследования")
    
    # Создаем посты
    print("\n3. СОЗДАНИЕ ПОСТОВ:")
    post1_id = create_post(
        "Основы Python для начинающих", 
        "Python - это мощный и простой в изучении язык программирования...", 
        user1_id, cat1_id
    )
    
    post2_id = create_post(
        "Принципы хорошего UI дизайна", 
        "Хороший пользовательский интерфейс должен быть интуитивно понятным...", 
        user2_id, cat2_id
    )
    
    post3_id = create_post(
        "Искусственный интеллект в современном мире", 
        "AI технологии стремительно развиваются и меняют нашу жизнь...", 
        user3_id, cat3_id
    )
    
    # Добавляем комментарии
    print("\n4. ДОБАВЛЕНИЕ КОММЕНТАРИЕВ:")
    add_comment("Отличная статья для новичков!", post1_id, user2_id)
    add_comment("Спасибо, очень полезно!", post1_id, user3_id)
    add_comment("Интересные идеи по дизайну", post2_id, user1_id)
    add_comment("Жду продолжения темы про AI", post3_id, user2_id)
    
    # Показываем результаты
    print("\n5. РЕЗУЛЬТАТЫ:")
    get_all_posts_with_authors()
    get_posts_with_comments()
    get_users_with_post_count()

# Запускаем демонстрацию
if __name__ == "__main__":
    demo_blog_system()


def homework_functions():
    """Функции, требуемые в домашнем задании"""
    
    # 1. Функция добавления нового пользователя (уже реализована выше)
    print("1. Функция add_user - реализована ✓")
    
    # 2. Функция создания поста (уже реализована выше)
    print("2. Функция create_post - реализована ✓")
    
    # 3. Функция вывода всех постов с именами авторов (уже реализована выше)
    print("3. Функция get_all_posts_with_authors - реализована ✓")
    
    # Демонстрация работы основных функций
    print("\n" + "="*50)
    print("ДЕМОНСТРАЦИЯ ОСНОВНЫХ ФУНКЦИЙ")
    print("="*50)
    
    create_blog_database()
    
    # Добавляем тестовые данные
    user_id = add_user("test_user", "test@example.com")
    category_id = add_category("Тестовая категория")
    
    if user_id and category_id:
        post_id = create_post(
            "Тестовый пост", 
            "Это тестовый пост для демонстрации работы функций.", 
            user_id, category_id
        )
        
        if post_id:
            add_comment("Тестовый комментарий", post_id, user_id)
            
            # Показываем посты с JOIN
            get_all_posts_with_authors()

# Запуск только домашнего задания
if __name__ == "__main__":
    homework_functions()