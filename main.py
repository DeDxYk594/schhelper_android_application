# -*-encoding:utf-8-*-
from datetime import datetime

import pytz
from kivy.app import App
from kivy.clock import Clock
from kivymd.theming import ThemeManager
from kivymd.uix.card import MDCardPost
from kivymd.uix.list import ThreeLineIconListItem
from kivymd.uix.navigationdrawer import NavigationDrawerIconButton
from kivymd.uix.navigationdrawer import NavigationLayout
from kivymd.uix.picker import MDThemePicker
from kivymd.uix.snackbar import Snackbar

SCHEDULE = {0: ["Русский язык", "История", "География", "Биология", "Алгебра", "Физика"],
            1: ["География", "Английский язык", "Информатика", "Геометрия", "Литература", "Физическая физкультура"],
            2: ["Биология", "История", "Химия", "Алгебра", "Физическая физкультура", "Физика"],
            3: ["Русский язык", "Алгебра", "Литература", "Физика", "ОБЖ", "Английский язык"],
            4: ["История", "Английский язык", "Физическая физкультура", "Литература", "Обществознание"],
            5: ["Химия", "Музыка", "Русский язык", "Литература", "Геометрия"]}

ALL_LESSON = ["Информатика", "Английский язык", "Физическая физкультура", "Алгебра", "Музыка", "Геометрия", "Физика",
              "История", "ОБЖ",
              "Обществознание", "Русский язык", "Литература", "Биология", "География", "Химия"]

DAYOFWEEK_DICT = {0: "Понедельник", 1: "Вторник", 2: "Среда", 3: "Четверг", 4: "Пятница", 5: "Суббота",
                  6: "Воскресенье"}
DEFAULT_SCHED = ["Нет уроков"]

THEME_FILE = "theme.ini"
DATA_FILE = "data.ini"
LASTPOST_FILE = "lastpost.ini"

try:
    o = open(THEME_FILE, "r", encoding="utf-8")
    theme = eval(o.read())
    o.close()
except:
    theme = None

try:
    o = open(DATA_FILE, "r", encoding="utf-8")
    data = eval(o.read())
    o.close()
except:
    data = {}


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
        self.swipe = True
        self.path_to_avatar = "assets\pencil.png"
        self.data_for_cancel = {}

    def callback(self, inst, value):
        if value:
            pass
        else:
            Snackbar(text="Удалено", button_text="Отмените!1", button_callback=self.btn_callback).show()
            self.data_for_cancel = self.data
            app.remove_from_data(self.header)

    def btn_callback(self, *_):
        app.cancel_delete(self.data_for_cancel)
        Snackbar(text="Отменено!").show()

    def set_data(self, data, header, nextday=False, addiction=None, from_tasks=False):
        data_visual = communise(data)[0]
        vis = ""
        for i in data_visual:
            vis += "   " * i[0]
            vis += i[1]
            vis += "\n"
        vis = vis[:-1]

        if not addiction:
            addiction = {False: "На потом", True: "На завтра"}[bool(nextday)]
        else:
            self.swipe=False

        self.data = data
        self.from_tasks = from_tasks
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

    def on_timeout(self, *_, **__):
        app.show_screen(self.val[4:])
        app.set_title_toolbar(self.val[4:])

    def on_release(self):
        app.wait_second(self)


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
    promoted = "Рекомендуемое"
    all_rasp = "Всё расписание"
    info_oproge = """Данное приложение было создано Жуковым Георгием. Если есть вопросы, пишите в ВК
    ВК: https://vk.com/warycow1
    Исходный код: https://github.com/DeDxYk594/schhelper_android_application"""
    info_mistake = """Если Вы нашли ошибку в домашнем задании, напишите в ВК Жукову Георгию
    https://vk.com/warycow1
    
Если приложение работает неправильно, напишите туда же или на github
    https://github.com/DeDxYk594/schhelper_android_application"""

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
        self.data = data

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
        self.refresh_data()

    def refresh_data(self):
        self.now = datetime.now()
        tz = pytz.timezone("Etc/GMT+4")
        tz.localize(self.now)

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

        self.main_widget.ids.rasp_list.clear_widgets()

        today_list_item = ThreeLineIconListItem()
        today_list_item.text = "Сегодня ({})".format(DAYOFWEEK_DICT[weekday])
        today_list_item.secondary_text = ", ".join(SCHEDULE.get(weekday, DEFAULT_SCHED))

        self.main_widget.ids.rasp_list.add_widget(today_list_item)
        self.algoritmus_nextday = False
        if weekday in (5, 6):
            weekday = -1
        weekday += 1
        if self.algoritmus_header in SCHEDULE[weekday]:
            self.algoritmus_nextday = True

        today_list_item = ThreeLineIconListItem()
        today_list_item.text = "Завтра ({})".format(DAYOFWEEK_DICT[weekday])
        today_list_item.secondary_text = ", ".join(SCHEDULE.get(weekday, DEFAULT_SCHED))

        self.main_widget.ids.rasp_list.add_widget(today_list_item)

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
            item.set_data(self.tasks_data[i], i, nextday, from_tasks=True)
            self.main_widget.ids.tasks_layout.add_widget(item)
        self.update_db()

    def get_last_post(self):
        try:
            o = open(LASTPOST_FILE, "r", encoding="utf-8")
            id = eval(o.read())
            o.close()
            return id
        except:
            return -100

    def set_last_post(self, id):
        o = open(LASTPOST_FILE, "w", encoding="utf-8")
        o.write(repr(id))
        o.close()

    def refresh_data_online(self, *_, **__):
        # todo add vk synchronisation
        print("refresh_data_online()")
        try:
            import vk
            # токен обрезан, перед продакшеном вставить
            api = vk.API(
                access_token="f9f6b7be7c38e3dcf882dec4de70cd40291241d6fca9818c25d46702c4fcdcafa111dbb37620577cab3ee")
            spisok = api.wall.get(owner_id=-181278776, count=15)
            last_post = self.get_last_post()
            spisok = spisok["items"]
            self.set_last_post(spisok[0]["id"])
            actions = []
            for i in spisok:
                if i["id"] == last_post:
                    break
                text = i["text"]
                if text.startswith("ADDHOMEWORK "):
                    text = text.split("ADDHOMEWORK ")[1]
                    data = eval(text)
                    actions.append(data)
                elif text.startswith("DESINFORMATION "):
                    text = text.split("DESINFORMATION ")[1]
                    data = eval(text)
                    actions.append([data])

            desinfs = 0

            actions.reverse()
            print(actions)
            for i in actions:
                changes = []
                if type(i) == dict:
                    for j in i:
                        key = ""
                        for k in ALL_LESSON:
                            if j.startswith(k):
                                key += k
                                break
                        if key not in changes:
                            for k in dict(self.data):
                                if k.startswith(key):
                                    del self.data[k]
                            changes.append(key)
                        self.data[j] = i[j]
                else:
                    desinfs += 1
                    for j in i[0]:
                        key = ""
                        for k in ALL_LESSON:
                            if j.startswith(k):
                                key += k
                                break
                        for k in dict(self.data):
                            if k.startswith(key):
                                del self.data[k]
                        changes.append(key)
                        self.data[j] = i[0][j]


        except Exception as e:
            Snackbar(text="Ошибка: {}".format(e)).show()
            return
        if not desinfs:
            Snackbar(text="Информация загружена успешно").show()
        else:
            Snackbar(text="Внимание! Была дезинформация!").show()
        self.refresh_data()

    def update_db(self):
        o = open(DATA_FILE, "w", encoding="utf-8")
        o.write(repr(self.data))
        o.close()

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

        o = open(THEME_FILE, "w", encoding="utf-8")
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
        for i in range(7):
            item = ThreeLineIconListItem()
            item.text = DAYOFWEEK_DICT[i]
            item.secondary_text = ", ".join(SCHEDULE.get(i, DEFAULT_SCHED))
            self.main_widget.ids.rasp_all_list.add_widget(item)
        self.refresh_data()

    def wait_second(self, obj):
        Clock.schedule_once(lambda x: self.show_screen("wait"), 0.1)
        Clock.schedule_once(obj.on_timeout, 0.6)


if __name__ == '__main__':
    app = MainApp()
    app.run()
