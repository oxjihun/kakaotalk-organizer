import customtkinter, json
from kakao_macro import KakaoRoom

# categories.json이라는 파일에서 따로 키워드 관리
# 모델 사용 여부에 따라 import 여부 결정
CATEGORIES = json.load(open("categories.json", "r", encoding="utf-8"))  # 더 이상 상수가 아님
USING_MODEL = None
def check_whether_using_model():
    global USING_MODEL
    USING_MODEL = any(category["condition"] == "model" for category in CATEGORIES) # 얘도 바뀔 수 있음
check_whether_using_model()

def sort_words(line):
    if USING_MODEL:
        from model_handler import predict
        prediction = predict(line)
        # print(prediction)
    for i in range(len(CATEGORIES)):
        category = CATEGORIES[i]
        if category["condition"] == "length" and len(line) >= category["min_length"]:
            return i
        if category["condition"] == "keyword":
            for keyword in category["keywords"]:
                if keyword in line:
                    return i
        if category["condition"] == "model":
            if prediction == category["name"]:
                return i
    return -1  # 매칭 X


class MessageFrame(customtkinter.CTkFrame):
    def __init__(
        self, master, name, time, message, height=50, fg_color=None, text_color=None
    ):
        super().__init__(master)
        self.grid_columnconfigure(1, weight=1)

        self.name = customtkinter.CTkLabel(self, text=name)
        self.name.grid(row=0, column=0, padx=20)

        self.time = customtkinter.CTkLabel(self, text=time)
        self.time.grid(row=1, column=0, padx=20)

        self.message = customtkinter.CTkTextbox(
            self, height=height, fg_color=fg_color, text_color=text_color
        )
        self.message.insert(index="0.0", text=message)
        self.message.grid(row=0, column=1, rowspan=2, sticky="ew")


class SystemTextFrame(customtkinter.CTkFrame):
    def __init__(self, master, text):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.label = customtkinter.CTkLabel(self, text=text)
        self.label.grid(row=0, column=0)


class LostFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, fg_color=None, colorize=False, textbox_height=50):
        super().__init__(master, fg_color=fg_color)
        self.grid_columnconfigure(0, weight=1)  # ?? ?? ?? ???п? ???? ???!

        self.elements = []
        self.colorize = colorize
        self.textbox_height = textbox_height
        # self.label = customtkinter.CTkLabel(self, text="djlsjdfkjlfjsdlkfs")
        # self.label.grid(row=0, column=0, padx=20)

    def show_kakao_list(self, kakao_list):
        for elem in self.elements:
            elem.destroy()
        row_counter = 0
        for kakao in reversed(kakao_list):
            if kakao['type'] == 'SystemText':
                elem = SystemTextFrame(self, text=kakao['matter'])
            else:
                name, time, message = kakao['matter']['name'], kakao['matter']['time'], kakao['matter']['message']
                category_id = sort_words(message)
                if self.colorize and category_id != -1:  # 뭔가 분류되었음
                    fg_color = CATEGORIES[category_id]["color"]
                else:
                    fg_color = None
                text_color = "white" if self.colorize and category_id != -1 else None
                elem = MessageFrame(
                    self,
                    name,
                    time,
                    message,
                    fg_color=fg_color,
                    text_color=text_color,
                    height=self.textbox_height,
                )
            elem.grid(row=row_counter, column=0, pady=5, sticky="ew")
            row_counter += 1
            self.elements.append(elem)


class ToplevelWindow(customtkinter.CTkToplevel):
    def __init__(self, master, name, fg_color, textbox_height=50):
        super().__init__(master)

        self.title(name)
        self.geometry("400x600")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.lost_frame = LostFrame(
            master=self, fg_color=fg_color, textbox_height=textbox_height
        )
        self.lost_frame.grid(padx=10, pady=10, sticky="news")


class ToplevelWindowButton(customtkinter.CTkButton):  # 새로 만듦
    def __init__(self, master, name, color, textbox_height=50):
        super().__init__(
            master, height=150, fg_color=color, text=name, command=self.open
        )
        self.name = name
        self.color = color
        self.textbox_height = textbox_height
        self.toplevel_window = None

    def exists(self):
        return self.toplevel_window is not None and self.toplevel_window.winfo_exists()

    def open(self):  # 여기로 옮김
        if not self.exists():
            self.toplevel_window = ToplevelWindow(
                self,
                name=self.name,
                fg_color=self.color,
                textbox_height=self.textbox_height,
            )  # create window if its None or destroyed
        self.toplevel_window.focus()  # if window exists focus it

    def show(self, kakao_list):
        if self.exists():
            self.toplevel_window.lost_frame.show_kakao_list(kakao_list)


class Frame1(customtkinter.CTkScrollableFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.buttons = []
        for i in range(len(CATEGORIES)):
            category = CATEGORIES[i]
            button = ToplevelWindowButton(
                self,
                category["name"],
                category["color"],
                textbox_height=category["textbox_height"],
            )
            button.grid(row=i // 2, column=i % 2, padx=10, pady=10, sticky="ew")
            self.buttons.append(button)


"================================================================================================================"
FAVORITES = json.load(open("favorites.json", "r", encoding="utf-8"))


class Favorite_Room(customtkinter.CTkButton):
    def __init__(self, master, name, func):
        super().__init__(master, text=name, command=lambda: func(name))
        self.name = name
        self.func = func


"""
def change_list(bef, aft):
    print(aft)
    print(bef)
    for i in range(len(FAVORITES)):
        if str(FAVORITES[i]) == bef:
            FAVORITES[i] = aft
            
            json.dump(FAVORITES, open("favorites.json", "w", encoding="utf-8"))
                
  """


class EditWindow(customtkinter.CTkToplevel):    
    def __init__(self, master):
        super().__init__(master)
        self.title("즐겨찾기 수정")
        self.geometry("300x200")

        self.grid_columnconfigure(0, weight=1)

        self.before = customtkinter.CTkEntry(
            self, placeholder_text="바꾸고 싶은 즐겨찾기 이름을 입력해 주세요"
        )
        self.before.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.after = customtkinter.CTkEntry(
            self, placeholder_text="새로 등록할 톡방의 이름을 입력해 주세요"
        )
        self.after.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.change = customtkinter.CTkButton(
            self, text="수정하기", command=self.change_list
        )
        self.change.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

    def change_list(self):
        before_room = self.before.get()
        after_room = self.after.get()

        if before_room in FAVORITES:
            n = FAVORITES.index(before_room)
            FAVORITES[n] = after_room
            json.dump(FAVORITES, open("favorites.json", "w", encoding="utf-8"), ensure_ascii=False )
            self.destroy()
            app.refresh()
        else:
            print("다시 입력해 주세요")


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("자료구조 대화 정리")
        self.geometry("500x800")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.mainframe = None
        self.refresh()

    def refresh(self):
        if self.mainframe is not None:
            self.mainframe.destroy()
        self.mainframe = MainFrame(self)
        self.mainframe.grid(row=0, column=0, sticky="news")


class MainFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        a = len(FAVORITES)
        for i in range(a):
            self.grid_columnconfigure(i, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(a, weight=3)

        self.entry = customtkinter.CTkEntry(self, placeholder_text="톡방 이름을 정확히 입력해주세요")
        self.entry.grid(
            row=0, column=0, columnspan=a + 1, padx=10, pady=10, sticky="news"
        )

        for i in range(a):
            favorite = FAVORITES[i]
            self.favor = Favorite_Room(self, FAVORITES[i], self.writeroom)
            self.favor.grid(row=1, column=i, padx=5, pady=5, sticky="ew")

        self.edit = customtkinter.CTkButton(self, text="···", command=self.edit_favor)
        self.edit.grid(row=1, column=a, padx=5, pady=5, sticky="ew")
        self.edit_window = None

        self.tabview = customtkinter.CTkTabview(self)
        self.tabview.grid(
            row=2, column=0, columnspan=a + 1, padx=10, pady=10, sticky="news"
        )

        self.tabview.add("전체 모드")
        mode_all = self.tabview.tab("전체 모드")
        mode_all.grid_rowconfigure(0, weight=1)
        mode_all.grid_columnconfigure(0, weight=1)
        self.mess = LostFrame(master=mode_all, colorize=True)
        self.mess.grid(row=0, column=0, sticky="news")

        self.tabview.add("분류별 모드")
        mode_category = self.tabview.tab("분류별 모드")
        mode_category.grid_rowconfigure(0, weight=1)
        mode_category.grid_columnconfigure(0, weight=1)
        self.frame = Frame1(master=mode_category)
        self.frame.grid(row=0, column=0, sticky="news")

        # 카테고리 시작

        self.tabview.add("카테고리 설정")
        mode_category_settings = self.tabview.tab("카테고리 설정")
        mode_category_settings.grid_rowconfigure(1, weight=1)
        mode_category_settings.grid_columnconfigure((0, 1), weight=1)

        self.category_settings = CategorySettingFrame(mode_category_settings)
        self.category_settings.grid(row=1, column=0, columnspan=2, sticky="news")

        self.category_add_button = customtkinter.CTkButton(  # 버튼 1
            mode_category_settings,
            text="카테고리 추가",
            command=lambda: self.category_settings.add_category(
                {
                    "name": "새로운 카테고리",
                    "color": "black",
                    "textbox_height": 50,
                    "condition": "keyword",
                    "keywords": ["줄마다", "키워드", "입력"],
                }
            ),
        )
        self.category_add_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.category_save_button = customtkinter.CTkButton(  # 버튼 2
            mode_category_settings,
            text="저장 및 새로고침",
            command=self.category_settings.save_category_settings,
        )
        self.category_save_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # 카테고리 끝

        self.button = customtkinter.CTkButton(
            self, text="메시지 불러오기", command=self.get_message
        )
        self.button.grid(
            row=3, column=0, columnspan=a + 1, padx=10, pady=10, sticky="news"
        )

        self.room = None

    def writeroom(self, text):
        self.entry.delete(0, "end")
        if len(self.entry.get()) == 0:
            self.entry.insert(0, text)

    def edit_favor(self):
        if self.edit_window is None or not self.edit_window.winfo_exists():
            self.edit_window = EditWindow(
                self
            )  # create window if its None or destroyed
            self.edit_window.focus()
        else:
            self.edit_window.focus()  # if window exists focus it

    def get_message(self):
        room_name = self.entry.get()
        if self.room is None:
            self.room = KakaoRoom(room_name)
        elif room_name != self.room.chatroom_name:
            self.room.exit_and_save()
            self.room = KakaoRoom(room_name)
        self.room.read_and_merge_data()

        current = self.tabview.get()
        if current == "전체 모드":
            self.mess.show_kakao_list(self.room.all_data)
        elif current == "분류별 모드":
            for i in range(len(self.frame.buttons)):
                self.frame.buttons[i].show(list(filter(lambda x: x['type'] == 'Message' and sort_words(x['matter']['message']) == i, self.room.all_data)))


class CategorySettingFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.removed_category = set()
        self.elem = []
        for category in CATEGORIES:
            self.add_category(category)

    def save_category_settings(self):
        global CATEGORIES
        CATEGORIES = []
        for i, e in enumerate(self.elem):
            if i not in self.removed_category:
                category = e.get_category()
                dummy_label = None
                try:
                    dummy_label = customtkinter.CTkFrame(
                        self, height=0, fg_color=category["color"]
                    )
                except:  # 색깔이 없음
                    category["color"] = "gray"
                if dummy_label is not None:
                    dummy_label.destroy()
                CATEGORIES.append(category)
        check_whether_using_model() 
        json.dump(
            CATEGORIES,
            open("categories.json", "w", encoding="utf-8"),
            ensure_ascii=False
        )
        app.refresh()

    def add_category(self, category):
        cid = len(self.elem)
        self.elem.append(CategorySetting(self, category, cid))
        self.elem[-1].grid(row=cid, column=0, padx=5, pady=5, sticky="ew")


class CategorySetting(customtkinter.CTkFrame):
    def __init__(self, master, category, cid):
        super().__init__(master, border_color='#888', border_width=2)
        self.cid = cid

        # 카테고리를 읽어서 변수 설정

        self.category = category
        self.name = category["name"]
        self.color = category["color"]
        self.textbox_height = category["textbox_height"]
        self.condition = category["condition"]
        if "keywords" not in self.category:
            self.category["keywords"] = []
        if "min_length" not in self.category:
            self.category["min_length"] = 50

        # 기본 설정

        self.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)
        self.grid_columnconfigure(1, weight=1)

        # 왼쪽 레이블

        customtkinter.CTkLabel(self, text="이름").grid(row=0, column=0, padx=5, pady=5)
        customtkinter.CTkLabel(self, text="색").grid(row=1, column=0, padx=5, pady=5)
        customtkinter.CTkLabel(self, text="글상자 높이").grid(
            row=2, column=0, padx=5, pady=5
        )
        customtkinter.CTkLabel(self, text="분류 조건").grid(row=3, column=0, padx=5, pady=5)

        # 오른쪽 내용

        self.ctk_name = customtkinter.CTkTextbox(self, height=30)
        self.ctk_name.insert(index="0.0", text=self.name)
        self.ctk_name.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.ctk_color = customtkinter.CTkTextbox(self, height=30)
        self.ctk_color.insert(index="0.0", text=self.color)
        self.ctk_color.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.ctk_textbox_height = customtkinter.CTkSlider(self, from_=30, to=120)
        self.ctk_textbox_height.set(self.textbox_height)
        self.ctk_textbox_height.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        # 마지막 옵션 관련

        self.DETAIL_OPTIONS = {
            "keyword": "키워드",
            "length": "텍스트 길이",
            "model": "모델",
        }  # 너와 나의 연결고리
        self.MIN_LENGTH_TEXT = "최소 길이"
        self.KEYWORDS_TEXT = "키워드\n\n(엔터로 구분)"

        self.ctk_condition = customtkinter.CTkOptionMenu(
            self, values=list(self.DETAIL_OPTIONS.values()), command=self.update_detail
        )
        self.ctk_condition.set(self.DETAIL_OPTIONS[self.condition])
        self.ctk_condition.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        self.ctk_detail_label, self.ctk_detail_content = None, None

        self.update_detail(self.DETAIL_OPTIONS[self.condition])

        # 삭제 버튼

        self.remove_button = customtkinter.CTkButton(
            self, text="이 카테고리 삭제", command=self.self_remove
        )
        self.remove_button.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

    def self_remove(self):
        self.master.removed_category.add(self.cid)
        self.destroy()

    def get_detail(self):
        if self.ctk_detail_label is not None:
            if self.ctk_detail_label.cget("text") == self.MIN_LENGTH_TEXT:
                self.category["min_length"] = int(
                    "".join(
                        filter(
                            lambda c: c in "0123456789",
                            self.ctk_detail_content.get("0.0", "end"),
                        )
                    )
                )
            elif self.ctk_detail_label.cget("text") == self.KEYWORDS_TEXT:
                self.category["keywords"] = list(
                    filter(
                        lambda kw: kw,
                        self.ctk_detail_content.get("0.0", "end").split("\n"),
                    )
                )
            self.ctk_detail_label.destroy()
            self.ctk_detail_content.destroy()

    def update_detail(self, choice):
        self.get_detail()  # 으아아아 스파게티 코딩

        if (
            choice == self.DETAIL_OPTIONS["length"]
            or choice == self.DETAIL_OPTIONS["keyword"]
        ):
            if choice == self.DETAIL_OPTIONS["length"]:
                self.ctk_detail_label = customtkinter.CTkLabel(
                    self, text=self.MIN_LENGTH_TEXT
                )
                self.ctk_detail_content = customtkinter.CTkTextbox(self, height=30)
                self.ctk_detail_content.insert(
                    index="0.0", text=self.category["min_length"]
                )

            elif choice == self.DETAIL_OPTIONS["keyword"]:
                self.ctk_detail_label = customtkinter.CTkLabel(
                    self, text=self.KEYWORDS_TEXT
                )
                self.ctk_detail_content = customtkinter.CTkTextbox(self, height=120)
                self.ctk_detail_content.insert(
                    index="0.0", text="\n".join(self.category["keywords"])
                )

            self.ctk_detail_label.grid(row=4, column=0, padx=5, pady=5)
            self.ctk_detail_content.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

        else:
            self.ctk_detail_label = None
            self.ctk_detail_content = None

    def get_category(self):
        self.category["name"] = self.ctk_name.get("0.0", "end").strip()
        self.category["color"] = self.ctk_color.get("0.0", "end").strip()
        self.category["textbox_height"] = self.ctk_textbox_height.get()
        self.category["condition"] = {
            "키워드": "keyword",
            "텍스트 길이": "length",
            "모델": "model",
        }[
            self.ctk_condition.get()
        ]  # 너와 나의 연결고리
        self.get_detail()
        return self.category


app = App()
app.mainloop()
if app.mainframe.room is not None:
    app.mainframe.room.exit_and_save()
