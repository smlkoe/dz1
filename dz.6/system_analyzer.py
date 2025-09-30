#!/usr/bin/env python3
"""
System Analyzer - Скрипт для анализа конфигурации системы
Требует запуска от имени администратора для получения полной информации
"""

import subprocess
import json
import platform
import os
from datetime import datetime

class SystemAnalyzer:
    def __init__(self):
        self.report_data = {}
        self.is_admin = self.check_admin_privileges()
    
    def check_admin_privileges(self):
        """Проверка прав администратора"""
        try:
            # Для Windows
            if platform.system() == "Windows":
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin()
            # Для Linux/Mac
            else:
                return os.geteuid() == 0
        except:
            return False
    
    def get_desktop_path(self):
        """Получение правильного пути к рабочему столу"""
        try:
            # Пробуем стандартный путь
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            if os.path.exists(desktop):
                return desktop
            
            # Пробуем путь OneDrive
            onedrive_desktop = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop")
            if os.path.exists(onedrive_desktop):
                return onedrive_desktop
            
            # Пробуем получить через системные переменные
            if "ONEDRIVE" in os.environ:
                onedrive_desktop2 = os.path.join(os.environ["ONEDRIVE"], "Desktop")
                if os.path.exists(onedrive_desktop2):
                    return onedrive_desktop2
            
            # Если ничего не найдено, используем домашнюю директорию
            return os.path.expanduser("~")
            
        except Exception as e:
            print(f"⚠️ Ошибка при определении пути к рабочему столу: {e}")
            return os.path.expanduser("~")
    
    def run_powershell_command(self, command):
        """Выполнение PowerShell команды и возврат результата"""
        try:
            result = subprocess.run(
                ["powershell", "-Command", command],
                capture_output=True,
                text=True,
                check=True,
                encoding='utf-8'
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            return f"Ошибка: {e}"
    
    def get_general_info(self):
        """Получение общей информации о системе"""
        print("🔍 Получение общей информации о системе...")
        
        # Используем systeminfo для получения общей информации
        try:
            system_info = subprocess.run(
                ["systeminfo"], 
                capture_output=True, 
                text=True, 
                check=True,
                encoding='utf-8'
            )
            info_lines = system_info.stdout.split('\n')
            
            # Извлекаем ключевую информацию
            os_name = next((line.split(":")[1].strip() for line in info_lines if "OS Name" in line), "N/A")
            os_version = next((line.split(":")[1].strip() for line in info_lines if "OS Version" in line), "N/A")
            processor = next((line.split(":")[1].strip() for line in info_lines if "Processor(s)" in line), "N/A")
            total_ram = next((line.split(":")[1].strip() for line in info_lines if "Total Physical Memory" in line), "N/A")
            
            self.report_data['general_info'] = {
                'OS Name': os_name,
                'OS Version': os_version,
                'Processor': processor,
                'Total RAM': total_ram,
                'Architecture': platform.architecture()[0],
                'Python Version': platform.python_version(),
                'System': platform.system(),
                'Release': platform.release()
            }
        except Exception as e:
            print(f"⚠️ Ошибка при получении общей информации: {e}")
            # Альтернативный способ получения информации
            self.report_data['general_info'] = {
                'OS Name': platform.system(),
                'OS Version': platform.release(),
                'Processor': 'N/A',
                'Total RAM': 'N/A',
                'Architecture': platform.architecture()[0],
                'Python Version': platform.python_version()
            }
    
    def get_cpu_info(self):
        """Получение информации о процессоре"""
        print("🔍 Анализ процессора...")
        
        command = """
        Get-CimInstance -ClassName Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors, MaxClockSpeed, Manufacturer | ConvertTo-Json
        """
        
        result = self.run_powershell_command(command)
        if result and not result.startswith("Ошибка"):
            try:
                cpu_info = json.loads(result) if result.startswith('[') else [json.loads(result)]
                self.report_data['cpu_info'] = cpu_info
            except json.JSONDecodeError as e:
                print(f"⚠️ Ошибка парсинга данных процессора: {e}")
                # Альтернативная информация о процессоре
                self.report_data['cpu_info'] = [{
                    'Name': platform.processor(),
                    'NumberOfCores': 'N/A',
                    'NumberOfLogicalProcessors': 'N/A',
                    'MaxClockSpeed': 'N/A',
                    'Manufacturer': 'N/A'
                }]
    
    def get_ram_info(self):
        """Получение информации об оперативной памяти"""
        print("🔍 Анализ оперативной памяти...")
        
        command = """
        Get-CimInstance -ClassName Win32_PhysicalMemory | Select-Object Manufacturer, Capacity, Speed, MemoryType, PartNumber | ConvertTo-Json
        """
        
        result = self.run_powershell_command(command)
        if result and not result.startswith("Ошибка"):
            try:
                ram_info = json.loads(result) if result.startswith('[') else [json.loads(result)]
                
                # Конвертируем Capacity в GB
                for module in ram_info:
                    if 'Capacity' in module and module['Capacity']:
                        module['Capacity_GB'] = round(module['Capacity'] / (1024**3), 2)
                
                self.report_data['ram_info'] = ram_info
            except json.JSONDecodeError as e:
                print(f"⚠️ Ошибка парсинга данных памяти: {e}")
                self.report_data['ram_info'] = []
        else:
            self.report_data['ram_info'] = []
    
    def get_disk_info(self):
        """Получение информации о накопителях"""
        print("🔍 Анализ накопителей...")
        
        command = """
        Get-CimInstance -ClassName Win32_DiskDrive | Select-Object Model, Size, InterfaceType, MediaType, SerialNumber | ConvertTo-Json
        """
        
        result = self.run_powershell_command(command)
        if result and not result.startswith("Ошибка"):
            try:
                disk_info = json.loads(result) if result.startswith('[') else [json.loads(result)]
                
                # Конвертируем Size в GB
                for disk in disk_info:
                    if 'Size' in disk and disk['Size']:
                        disk['Size_GB'] = round(disk['Size'] / (1024**3), 2)
                
                self.report_data['disk_info'] = disk_info
            except json.JSONDecodeError as e:
                print(f"⚠️ Ошибка парсинга данных дисков: {e}")
                self.report_data['disk_info'] = []
        else:
            self.report_data['disk_info'] = []
    
    def get_gpu_info(self):
        """Получение информации о видеокартах"""
        print("🔍 Анализ видеокарт...")
        
        command = """
        Get-CimInstance -ClassName Win32_VideoController | Where-Object {$_.Name -notlike "*Remote*" -and $_.Name -notlike "*Microsoft*"} | Select-Object Name, DriverVersion, AdapterRAM, VideoProcessor | ConvertTo-Json
        """
        
        result = self.run_powershell_command(command)
        if result and not result.startswith("Ошибка"):
            try:
                gpu_info = json.loads(result) if result.startswith('[') else [json.loads(result)]
                self.report_data['gpu_info'] = gpu_info
            except json.JSONDecodeError as e:
                print(f"⚠️ Ошибка парсинга данных видеокарт: {e}")
                self.report_data['gpu_info'] = []
        else:
            self.report_data['gpu_info'] = []
    
    def generate_report(self):
        """Генерация итогового отчета"""
        print("📊 Генерация отчета...")
        
        # Получаем правильный путь к рабочему столу
        desktop_path = self.get_desktop_path()
        report_path = os.path.join(desktop_path, "MyPC_Report.txt")
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write("=== ОТЧЕТ О КОНФИГУРАЦИИ СИСТЕМЫ ===\n")
                f.write(f"Сформирован: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Права администратора: {'Да' if self.is_admin else 'Нет'}\n")
                f.write(f"Отчет сохранен: {report_path}\n\n")
                
                # Общая информация
                if 'general_info' in self.report_data:
                    f.write("--- ОБЩАЯ ИНФОРМАЦИЯ О СИСТЕМЕ ---\n")
                    for key, value in self.report_data['general_info'].items():
                        f.write(f"{key}: {value}\n")
                    f.write("\n")
                
                # Процессор
                if 'cpu_info' in self.report_data and self.report_data['cpu_info']:
                    f.write("--- ПРОЦЕССОР (CPU) ---\n")
                    for cpu in self.report_data['cpu_info']:
                        f.write(f"Модель: {cpu.get('Name', 'N/A')}\n")
                        f.write(f"Производитель: {cpu.get('Manufacturer', 'N/A')}\n")
                        f.write(f"Физические ядра: {cpu.get('NumberOfCores', 'N/A')}\n")
                        f.write(f"Логические процессоры: {cpu.get('NumberOfLogicalProcessors', 'N/A')}\n")
                        f.write(f"Макс. частота: {cpu.get('MaxClockSpeed', 'N/A')} МГц\n\n")
                
                # Оперативная память
                if 'ram_info' in self.report_data and self.report_data['ram_info']:
                    f.write("--- ОПЕРАТИВНАЯ ПАМЯТЬ (RAM) ---\n")
                    total_ram_gb = 0
                    for i, ram in enumerate(self.report_data['ram_info'], 1):
                        f.write(f"Модуль {i}:\n")
                        f.write(f"  Производитель: {ram.get('Manufacturer', 'N/A')}\n")
                        f.write(f"  Объем: {ram.get('Capacity_GB', 'N/A')} GB\n")
                        f.write(f"  Скорость: {ram.get('Speed', 'N/A')} МГц\n")
                        f.write(f"  Тип памяти: {ram.get('MemoryType', 'N/A')}\n")
                        f.write(f"  Part Number: {ram.get('PartNumber', 'N/A')}\n")
                        if 'Capacity_GB' in ram and ram['Capacity_GB']:
                            total_ram_gb += ram['Capacity_GB']
                    
                    if total_ram_gb > 0:
                        f.write(f"\nОбщий объем RAM: {total_ram_gb} GB\n")
                    f.write("\n")
                else:
                    f.write("--- ОПЕРАТИВНАЯ ПАМЯТЬ (RAM) ---\n")
                    f.write("Информация о памяти недоступна\n\n")
                
                # Накопители
                if 'disk_info' in self.report_data and self.report_data['disk_info']:
                    f.write("--- НАКОПИТЕЛИ (HDD/SSD) ---\n")
                    for disk in self.report_data['disk_info']:
                        f.write(f"Модель: {disk.get('Model', 'N/A')}\n")
                        f.write(f"Объем: {disk.get('Size_GB', 'N/A')} GB\n")
                        f.write(f"Интерфейс: {disk.get('InterfaceType', 'N/A')}\n")
                        f.write(f"Тип носителя: {disk.get('MediaType', 'N/A')}\n")
                        f.write(f"Серийный номер: {disk.get('SerialNumber', 'N/A')}\n\n")
                else:
                    f.write("--- НАКОПИТЕЛИ (HDD/SSD) ---\n")
                    f.write("Информация о дисках недоступна\n\n")
                
                # Видеокарты
                if 'gpu_info' in self.report_data and self.report_data['gpu_info']:
                    f.write("--- ВИДЕОКАРТЫ (GPU) ---\n")
                    for gpu in self.report_data['gpu_info']:
                        f.write(f"Модель: {gpu.get('Name', 'N/A')}\n")
                        f.write(f"Версия драйвера: {gpu.get('DriverVersion', 'N/A')}\n")
                        ram_gb = round(gpu.get('AdapterRAM', 0) / (1024**3), 2) if gpu.get('AdapterRAM') else "N/A"
                        f.write(f"Видеопамять: {ram_gb} GB\n")
                        f.write(f"Видеопроцессор: {gpu.get('VideoProcessor', 'N/A')}\n\n")
                else:
                    f.write("--- ВИДЕОКАРТЫ (GPU) ---\n")
                    f.write("Информация о видеокартах недоступна\n\n")
            
            return report_path
            
        except Exception as e:
            print(f"❌ Ошибка при сохранении отчета: {e}")
            # Сохраняем в текущую директорию как запасной вариант
            backup_path = "MyPC_Report.txt"
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(f"Ошибка при сохранении отчета: {e}\n")
            return backup_path
    
    def display_summary(self):
        """Вывод краткой сводки в консоль"""
        print("\n" + "="*50)
        print("📋 КРАТКАЯ СВОДКА СИСТЕМЫ")
        print("="*50)
        
        if 'cpu_info' in self.report_data and self.report_data['cpu_info']:
            cpu = self.report_data['cpu_info'][0]
            print(f"💻 Процессор: {cpu.get('Name', 'N/A')}")
            print(f"   Ядра: {cpu.get('NumberOfCores', 'N/A')} физических, {cpu.get('NumberOfLogicalProcessors', 'N/A')} логических")
        else:
            print(f"💻 Процессор: {platform.processor()}")
        
        if 'ram_info' in self.report_data and self.report_data['ram_info']:
            total_ram = sum(ram.get('Capacity_GB', 0) for ram in self.report_data['ram_info'])
            print(f"🧠 Оперативная память: {total_ram} GB ({len(self.report_data['ram_info'])} модуля)")
        else:
            print("🧠 Оперативная память: информация недоступна")
        
        if 'disk_info' in self.report_data and self.report_data['disk_info']:
            total_disk = sum(disk.get('Size_GB', 0) for disk in self.report_data['disk_info'])
            print(f"💾 Накопители: {len(self.report_data['disk_info'])} устройств, {total_disk} GB всего")
        else:
            print("💾 Накопители: информация недоступна")
        
        if 'gpu_info' in self.report_data and self.report_data['gpu_info']:
            gpu_names = [gpu.get('Name', 'N/A') for gpu in self.report_data['gpu_info']]
            print(f"🎮 Видеокарты: {', '.join(gpu_names)}")
        else:
            print("🎮 Видеокарты: информация недоступна")
        
        print(f"🛡️  Права администратора: {'✅ Да' if self.is_admin else '⚠️ Нет'}")
    
    def analyze_system(self):
        """Основной метод анализа системы"""
        print("🚀 Запуск анализа системы...")
        print(f"📁 Текущая директория: {os.getcwd()}")
        
        if not self.is_admin:
            print("⚠️  ВНИМАНИЕ: Скрипт запущен без прав администратора.")
            print("   Некоторые данные могут быть недоступны.\n")
        
        self.get_general_info()
        self.get_cpu_info()
        self.get_ram_info()
        self.get_disk_info()
        self.get_gpu_info()
        
        report_path = self.generate_report()
        self.display_summary()
        
        print(f"\n✅ Отчет сохранен: {report_path}")
        print("🎯 Анализ завершен!")

def main():
    """Основная функция"""
    print("System Analyzer - Анализатор системы")
    print("=" * 40)
    
    try:
        analyzer = SystemAnalyzer()
        analyzer.analyze_system()
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        print("Попробуйте запустить скрипт от имени администратора")

if __name__ == "__main__":
    main()