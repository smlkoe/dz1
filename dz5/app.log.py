import re

def main():
    # 1-2. Создание файла app.log
    log_content = """[INFO] User logged in
[ERROR] Connection timeout
[DEBUG] Starting calculation
[WARNING] Disk space low
[INFO] Database connection established
[ERROR] File not found
[DEBUG] Processing request ID 12345
[WARNING] Memory usage high
[INFO] Backup completed successfully
[ERROR] Authentication failed
[DEBUG] Cache cleared
[WARNING] High CPU usage
[INFO] User session started"""
    
    with open('app.log', 'w', encoding='utf-8') as file:
        file.write(log_content)
    print("✓ Файл app.log создан и заполнен\n")
    
    # 3. Все строки лога
    print("=== 3. Все строки лога ===")
    with open('app.log', 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for i, line in enumerate(lines, 1):
            print(f"{i:2d}. {line.strip()}")
    
    # 4. Строки с ERROR
    print("\n=== 4. Строки с ERROR ===")
    error_lines = [line.strip() for line in lines if 'ERROR' in line]
    for line in error_lines:
        print(line)
    
    # 5. Строки с timeout (регистронезависимо)
    print("\n=== 5. Строки с timeout ===")
    timeout_lines = [line.strip() for line in lines if re.search('timeout', line, re.IGNORECASE)]
    for line in timeout_lines:
        print(line)
    
    # 6. Общее количество строк
    print(f"\n=== 6. Общее количество строк: {len(lines)} ===")
    
    # 7. Количество WARNING
    warning_count = sum(1 for line in lines if 'WARNING' in line)
    print(f"=== 7. Количество строк с WARNING: {warning_count} ===")
    
    # 8. Добавление новой строки
    with open('app.log', 'a', encoding='utf-8') as file:
        file.write('\n[ERROR] New critical error detected')
    print("\n✓ 8. Новая строка с ERROR добавлена")
    
    # 9. Последние 3 строки
    print("\n=== 9. Последние 3 строки ===")
    with open('app.log', 'r', encoding='utf-8') as file:
        all_lines = file.readlines()
        for line in all_lines[-3:]:
            print(line.strip())
    
    # 10. Замена logged на connected
    print("\n=== 10. Замена 'logged' на 'connected' ===")
    with open('app.log', 'r', encoding='utf-8') as file:
        content = file.read()
    
    fixed_content = content.replace('logged', 'connected')
    
    with open('app_fixed.log', 'w', encoding='utf-8') as file:
        file.write(fixed_content)
    
    print("✓ Файл app_fixed.log создан")
    
    # Показать изменения
    print("\nИзменения:")
    with open('app.log', 'r', encoding='utf-8') as f1, open('app_fixed.log', 'r', encoding='utf-8') as f2:
        orig_lines = f1.readlines()
        fixed_lines = f2.readlines()
        
        for orig, fixed in zip(orig_lines, fixed_lines):
            if orig != fixed:
                print(f"Было: {orig.strip()}")
                print(f"Стало: {fixed.strip()}\n")

if __name__ == "__main__":
    main()