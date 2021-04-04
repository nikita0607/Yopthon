import json
import os
import importlib
import colorama

from colorama import Fore, Back, Style
from sys import argv, exit
from time import sleep


colorama.init(convert=True, autoreset=True)
a = argv   # Получаем доп. аргументы из ком. строки

cur_dir = os.getcwd()   # Получаем текущую рабочую папку
os.chdir(a.pop(0).replace("\\", "/").replace("/main.py", ""))   # Получаем папку, в которой лежит наш скрипт

# Если файл запущен через командную строку и имеет доп. аргументы
if len(a):
    run = "--стартани" in a   # Проверка на наличие флага запуска программы сразу после "компиляции"
    if run: a.remove("--стартани")

    name_file1 = a.pop(0)
    name_file2 = ""
    if "." in name_file1:
        name_file2 = name_file1[:name_file1.index(".")]+".py"
    if len(a): name_file2 = a[0]
#  Если "компилятор" запущен не через ком. строку или не было переданно доп. аргументов
else:
    print(Fore.CYAN, end="")
    name_file1 = input("Введите имя входного файла: ")
    name_file2 = input("Введите имя выходного файла (или оставте пустым): ")

    if not len(name_file2) and "." in name_file1:
        name_file2 = name_file1[:name_file1.index(".")]+".py"
    run = bool(len(input("Если не хотите запустить этот файл, оставте эту строку пустой: ")))

# print(name_file1, name_file2)

# Переменные для хранения синтакс. настроек
replace_str = []
aliases = {}
standart_classes = {}
preclasses_symbols = ["", " ", "+", "-", "*", "/", "%", "("]
alfabets = {}

# Загружаем синтаксические настройки
if os.path.isfile('syntax/alfabets.json'):
    with open("syntax/alfabets.json", encoding="utf-8") as alf:
        alfabets = json.load(alf)
if os.path.isfile('syntax/aliases.json'):
    with open('syntax/aliases.json', encoding="utf-8") as file:
        aliases = json.load(file)
if os.path.isfile('syntax/standart_classes.json'):
    with open('syntax/standart_classes.json', encoding="utf-8") as file:
        standart_classes = json.load(file)
        
os.chdir(cur_dir)
if not os.path.isfile(name_file1):   # Проверяем, существует ли файл указанный пользователем
    print(Fore.LIGHTRED_EX+f"Файл {name_file1} не найден!")
    exit(-1)
    
with open(name_file1, encoding='utf-8') as file1:   # Открываем и читаем этот файл
    code = file1.readlines().copy()
    for i in range(len(code)):
        code[i] = code[i].replace("{", " Жы ").replace("}", " жЫ ").replace("\n", "")

def tranform(string: str):   # Заменяем синтаксис в полученной строке
    while "\"" in string and string.count("\"") >= 2:   # Заменяем все строчные значение (в "" скобочках на знаки {} для послед. форматирования)
        ind = string.index("\"")
        ind2 = string[ind+1:].index("\"") + ind - 1

        replace_str.append(string[ind:ind2+3])
        string = string.replace(string[ind:ind2+3], "{}")

    for alias in aliases:   # Заменяем русские комманды на англ.
        string = string.replace(alias, aliases[alias])

    for st_class in standart_classes:  # Заменяем русские названия встроенных классов на англ.
        for sym in preclasses_symbols:
            string = string.replace(sym+st_class, sym+standart_classes[st_class])

    for alf in alfabets:   # Заменяем все буквы на англ.
        for repl in alfabets[alf]:
            string = string.replace(repl, alfabets[alf][repl])
            string = string.replace(repl.upper(), alfabets[alf][repl].upper())

    return string

count = 0
last = 0

print(Fore.CYAN+"Сборка файла")
print(Fore.CYAN+"-"*20)

for i in range(len(code)):   # Цикл, отвечающий за переделывание файла
    code[i] = " "+code[i].replace("\t", "    ").replace("ё", "е")+" "
    code[i] = tranform(code[i])
    count += 1
    # Отображение выполненной работы
    a = int(count // (len(code) / 100) // 5)
    if count // (len(code) / 100) > last:
        print(Fore.GREEN+Back.LIGHTCYAN_EX+"#"*(a-last), end="")
        last = a
    sleep(0.1*5/len(code))

print("\n", Fore.CYAN+"-"*20, sep="")
print(Fore.CYAN+"Сборка завршена")

for i in range(len(code)):
    code[i] = code[i][1:-1]

final_code = ""
for i in code:
    final_code += i + "\n"
final_code = final_code.format(*replace_str).replace("    ", "\t").replace(" Ji ", "{").replace(" jI ", "}")[:-1]

with open(name_file2, 'w', encoding='utf-8') as file2:   # Сохранение получ. кода
    file2.write(final_code)

if run:   # Если пользователь указал, что хочет запустить текущий файл
    name = ""
    dir = ""
    for i in range(len(name_file2)-1, -1, -1):
        if name_file2[i] == "\\":
            dir = name_file2[:i]
            break
        name = name_file2[i] + name

    os.chdir(dir)

    # Запуск файла и отработка возникающих ошибок
    try:
        print(Fore.LIGHTGREEN_EX+"-------Консоль файла---------")
        importlib.import_module(name)
    except ModuleNotFoundError:
        print(Fore.LIGHTGREEN_EX + "------------------------------")
        print(Fore.CYAN + "Работа файла завершена")
    except Exception as exception:
       print(Fore.LIGHTRED_EX+"------------------------------\nВозникла ошибка во время запуска файла:\n", "\t", Fore.RED+str(exception), sep="")