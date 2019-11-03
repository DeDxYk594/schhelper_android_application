# -*-encoding:utf-8-*-
from datetime import datetime

import pytz
from kivy.app import App
from kivymd.theming import ThemeManager
from kivymd.uix.card import MDCardPost
from kivymd.uix.navigationdrawer import NavigationDrawerIconButton
from kivymd.uix.navigationdrawer import NavigationLayout
from kivymd.uix.picker import MDThemePicker
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.menu import MDMenuItem,MDDropdownMenu



SCHEDULE = {0: ["Русский язык", "История", "География", "Биология", "Алгебра", "Физика"],
            1: ["География", "Английский язык", "Информатика", "Геометрия", "Литература", "Физическая физкультура"],
            2: ["Биология", "История", "Химия", "Алгебра", "Физическая физкультура", "Физика"],
            3: ["Русский язык", "Алгебра", "Литература", "Физика", "ОБЖ", "Английский язык"],
            4: ["История", "Английский язык", "Физическая физкультура", "Литература", "Обществознание"],
            5: ["Химия", "Музыка", "Русский язык", "Литература", "Геометрия"]}

THEME_FILE = "theme.ini"

try:
    o = open(THEME_FILE, "r")
    theme = eval(o.read())
    o.close()
except:
    theme = None


# Vspomogatelnaiye function
def _categorize(res):
    ret = {}
    for i in res:
        ret[tuple(_district_cats(i))] = res[i]

    ret0 = {}
    keys = {}
    for i in ret:
        key = []
        cat = [ret0]
        for j in i:
            key.append(j)
            try:
                cat.append(cat[-1][j])
            except:
                cat[-1][j] = {}
                cat.append(cat[-1][j])
        cat[-1]["__value__"] = ret[tuple(key)]

    return ret0


def _district_cats(res):
    ret = [""]
    mode = 0
    for i in res:
        if i in "()":
            if i == "(" and not mode:
                ret.append("")
                mode += 1
            elif i == ")" and mode:
                mode -= 1
        else:
            ret[-1] += i
    ret0 = [i.strip() for i in ret]

    return ret0


# Lets build a communistic PROject! (c)Gosha
def communise(r):
    tmp = repr(_categorize(r))
    level = -1
    maxlevel = -1
    ret = []
    tmp0 = []
    now = []
    for i in tmp:
        if i == "{":
            level += 1
            if level > maxlevel:
                maxlevel += 1
            now.clear()
        elif i in "\"'":
            if "'" in tmp0:
                tmp0.remove("'")
                if now:
                    if now[0] != "__value__:":
                        ret[-1][1] += ":"
                else:
                    ret[-1][1] += ":"


            else:
                tmp0.append("'")
                try:
                    if ret[-1][1] == "__value__:":
                        ret.remove(ret[-1])
                except:
                    pass
                ret.append([level + 0, ""])
        elif i == "}":
            level -= 1
            now.clear()
        elif i == "," and not "'" in tmp0:
            now.clear()
        elif i == ":":
            try:
                now.append(ret[-1][1])
            except:
                pass

        else:
            if "'" in tmp0:
                ret[-1][1] += i

    for i in range(20):
        try:

            ret.remove([i, "__value__:"])
        except:
            pass
    return ret, maxlevel


# Карточка с предметом, используется для отображения списка текущих заданий
class ItemCard(MDCardPost):
    def __init__(self, **_):
        super().__init__(**_)
        menu_item = [{"viewclass": "MDMenuItem", "text": "Сделано", "callback": lambda: self.callback(None, 0)}]
        self.right_menu = [menu_item, menu_item]
        print("setted menu")
        self.swipe=True
        self.path_to_avatar = "assets\pencil.png"
        self.data_for_cancel = {}



    def callback(self, inst, value):
        if value:
            print(value)
        else:
            Snackbar(text="Удалено", button_text="Отмените!1", button_callback=self.btn_callback).show()
            self.data_for_cancel = self.data
            app.remove_from_data(self.header)

    def btn_callback(self, *_):
        app.cancel_delete(self.data_for_cancel)
        Snackbar(text="Отменено!").show()

    def set_data(self, data, header, nextday=False, addiction=None,from_tasks=False):
        data_visual = communise(data)[0]
        vis = ""
        for i in data_visual:
            vis += "   " * i[0]
            vis += i[1]
            vis += "\n"
        vis = vis[:-1]

        if not addiction:
            addiction = {False: "На потом", True: "На завтра"}[bool(nextday)]

        self.data = data
        self.from_tasks=from_tasks
        self.header = header
        self.nextday = nextday
        self.addiction = addiction

        self.text_post = vis
        self.name_data = "{}\n{}".format(self.header, self.addiction)


# Кнопка в NavigationDrawerе, для удобства была переименована
class NavButton(NavigationDrawerIconButton):
    def __init__(self, *_, **__):
        super().__init__(*_, **__)
        app.nav_buttons.append(self)


# Базовый класс, отвечает за расположение всего
class MainLayout(NavigationLayout):
    def __init__(self, *_, **__):
        super().__init__(*_, **__)
        app.main_widget = self


class MainApp(App):
    # Переменные - переводы
    # Объявлены, чтобы можно было получить к ним доступ из kv файла

    # Метки в NavigationDrawerе
    customization = "Кастомизация"
    algoritmus = "Алгоритмус"
    tasks = "Список домашки"
    raspisanie = "Умное расписание"
    netochnost = "Что-то не так?"
    oproge = "О приложении"
    settings = "Настройки"

    # Метки интерфейса
    algoritmus_promotes = "Алгоритмус предлагает сделать:"
    change_theme = "Настроить внешний вид"
    save = "Сохранить"
    render_theme = "Фон: {}\nБазовый цвет: {}\nВторичный цвет: {}"

    # Подзаголовки NavigationDrawerа
    main_subheader = "Основное"
    settings_subheader = "Опции"

    def __init__(self):
        # Объявление переменных, отвечающих за работу КЛАССА
        self.algoritmus_data = {}
        self.algoritmus_header = ""

        # Маин виджет потом будет задан из тела MainLayout
        self.main_widget = None

        # Theme Manager, куда же без него!
        self.theme_cls = ThemeManager()

        # Loading theme from file
        try:
            self.theme_cls.accent_palette = theme["accent"]
            self.theme_cls.primary_palette = theme["primary"]
            self.theme_cls.theme_style = theme["style"]
        except:
            self.theme_cls.theme_style = "Light"

        # Список всех кнопок
        self.nav_buttons = []

        # today`s weekday
        self.now = datetime.now()
        tz = pytz.timezone("Etc/GMT+4")
        tz.localize(self.now)

        self.title = "9В - ДЗ"

        # Данные домашки
        # todo сделать импорт из ВК
        # Дата временная
        self.data = {'Информатика(обе группы)': 'Не задано; делали проверочную',
                     'Английский язык (с Гошей)': 'WB p21 wordlist columns 2,3; WB p21-22 ex 16,17 ',
                     'Английский язык (без Гоши)': 'Неизвестно', "Русский язык(письменно)": "Задание 1"}

        # Инит в суперклассе, иначе кинет ошибку
        super().__init__()

        # ThemePicker - то самое окошко, где выбирают цвета темы
        self.md_theme_picker = MDThemePicker()

    def remove_from_data(self, name):
        data = dict(self.data)
        for i in self.data:
            if i.startswith(name):
                del data[i]

        self.data = data
        print(self.data)
        self.refresh_data()

    def refresh_data(self):
        self.now = datetime.now()
        tz = pytz.timezone("Etc/GMT+4")
        tz.localize(self.now)
        print(self.now.weekday())

        hierarchy = []
        weekday = self.now.weekday()
        for i in range(6):
            i += 0
            i += weekday
            if i == 6:
                i = 0
            elif i > 6:
                i -= 6

            for j in SCHEDULE[i]:
                if j not in hierarchy:
                    hierarchy.append(j)

        self.algoritmus_data = {}
        self.algoritmus_header = ""
        for i in hierarchy:
            for j in self.data:
                if j.startswith(i):
                    self.algoritmus_data[j] = self.data[j]
                    self.algoritmus_header = i
            if self.algoritmus_data:
                break

        self.algoritmus_nextday = False
        if weekday in (5, 6):
            weekday = -1
        weekday += 1
        if self.algoritmus_header in SCHEDULE[weekday]:
            self.nextday = True

        print(self.algoritmus_data)
        if self.data:
            self.main_widget.ids.algoritmuscard.set_data(self.algoritmus_data, self.algoritmus_header,
                                                         self.algoritmus_nextday)
        else:
            self.main_widget.ids.algoritmuscard.set_data(
                {"Действия": "Попробуй обновить данные. Если ничего не поменялось, отдыхай))"},
                "Наверное, ты всё сделал", False, "База данных пуста :(")

        self.tasks_data = {}

        for i in hierarchy:
            self.tasks_data[i] = {}
            for j in self.data:
                if j.startswith(i):
                    self.tasks_data[i][j] = self.data[j]
            if self.tasks_data[i] == {}:
                self.tasks_data[i] = {
                    "Не найдено записей в базе данных": "Обновите базу данных. Если так и остаётся, значит, всё сделано!"}

        self.main_widget.ids.tasks_layout.clear_widgets()
        for i in self.tasks_data:
            item = ItemCard()
            nextday = False
            if i in SCHEDULE[weekday]:
                nextday = True
            print("tasks_data = ", self.tasks_data[i])
            item.set_data(self.tasks_data[i], i, nextday,from_tasks=True)
            self.main_widget.ids.tasks_layout.add_widget(item)

    def refresh_data_online(self):
        # todo add vk synchronisation
        print("refresh_data_online()")
        self.refresh_data()

    def update_db(self):
        pass

    def show_screen(self, name):
        # Ставит другой экран по вызову
        self.main_widget.ids.scr_mngr.current = name

    def build(self):
        return

    def set_title_toolbar(self, title):
        self.main_widget.ids.toolbar.title = eval("self." + title)

    def theme_picker_open(self):
        self.md_theme_picker.open()

    def _get_theme_string(self):
        return self.render_theme.format(self.theme_cls.theme_style,
                                        self.theme_cls.primary_palette,
                                        self.theme_cls.accent_palette)

    def update_theme(self):
        self.main_widget.ids.theme_label.text = self._get_theme_string()
        rend = {}
        rend["primary"] = self.theme_cls.primary_palette
        rend["accent"] = self.theme_cls.accent_palette
        rend["style"] = self.theme_cls.theme_style

        o = open(THEME_FILE, "w")
        o.write(repr(rend))
        o.close()

    def cancel_delete(self, data):
        for i in data:
            self.data[i] = data[i]
        self.refresh_data()

    def refresh_names_navdrawer(self):
        for i in self.nav_buttons:
            val = i.val
            i.text = eval(val)
        # Заодно обновим дату
        self.refresh_data()


if __name__ == '__main__':
    app = MainApp()
    app.run()
