#!/usr/bin/env python3
"""
Упрощенная версия для быстрого анализа
"""

import subprocess
import platform

def simple_traceroute_analysis():
    """Простой анализ traceroute"""
    system = platform.system()
    
    print("🌐 ПРОСТОЙ АНАЛИЗ TRACEROUTE")
    print("=" * 40)
    
    # Получаем шлюз
    if system == "Windows":
        result = subprocess.run(["ipconfig"], capture_output=True, text=True, encoding='cp866')
        for line in result.stdout.split('\n'):
            if "Основной шлюз" in line or "Default Gateway" in line:
                gateway = line.split(":")[1].strip()
                if gateway:
                    print(f"📍 Шлюз: {gateway}")
                    break
    else:
        result = subprocess.run(["ip", "route"], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if "default" in line:
                gateway = line.split()[2]
                print(f"📍 Шлюз: {gateway}")
                break
    
    # Трассировка до шлюза
    print("\n1. Трассировка до шлюза (LAN):")
    if system == "Windows":
        subprocess.run(["tracert", "-d", gateway])
    else:
        subprocess.run(["traceroute", "-n", gateway])
    
    # Трассировка до локального сайта
    print("\n2. Трассировка до локального сайта (MAN):")
    local_site = "yandex.ru"  # Замените на сайт вашего города
    if system == "Windows":
        subprocess.run(["tracert", "-d", local_site])
    else:
        subprocess.run(["traceroute", "-n", local_site])
    
    # Трассировка до глобального сайта
    print("\n3. Трассировка до глобального сайта (WAN):")
    global_site = "stanford.edu"  # Замените на нужный сайт
    if system == "Windows":
        subprocess.run(["tracert", "-d", global_site])
    else:
        subprocess.run(["traceroute", "-n", global_site])

if __name__ == "__main__":
    simple_traceroute_analysis()