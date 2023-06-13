# 다른 파일에서 사용하기 쉽도록 코드를 다듬어보자.

import time, win32con, win32api, win32gui, ctypes, pyperclip, json, os, re, hashlib, pathlib


# 엔터
def SendReturn(hwnd):
    win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
    time.sleep(0.01)
    win32api.PostMessage(hwnd, win32con.WM_KEYUP, win32con.VK_RETURN, 0)


# 채팅방에 메시지 전송
def kakao_sendtext(chatroom_name, text):
    # 핸들 _ 채팅방
    hwndMain = win32gui.FindWindow(None, chatroom_name)
    hwndEdit = win32gui.FindWindowEx(hwndMain, None, "RICHEDIT50W", None)
    # hwndListControl = win32gui.FindWindowEx( hwndMain, None, "EVA_VH_ListControl_Dblclk", None)
    win32api.SendMessage(hwndEdit, win32con.WM_SETTEXT, 0, text)
    SendReturn(hwndEdit)


# 채팅방 열기
def open_chatroom(chatroom_name):
    # 채팅방 목록 검색하는 Edit (채팅방이 열려있지 않아도 전송 가능하기 위하여)
    hwndkakao = win32gui.FindWindow(None, "카카오톡")
    hwndkakao_edit1 = win32gui.FindWindowEx(hwndkakao, None, "EVA_ChildWindow", None)
    hwndkakao_edit2_1 = win32gui.FindWindowEx(hwndkakao_edit1, None, "EVA_Window", None)
    hwndkakao_edit2_2 = win32gui.FindWindowEx(
        hwndkakao_edit1, hwndkakao_edit2_1, "EVA_Window", None
    )
    hwndkakao_edit3 = win32gui.FindWindowEx(hwndkakao_edit2_2, None, "Edit", None)

    # Edit에 검색 _ 입력되어있는 텍스트가 있어도 덮어쓰기됨
    win32api.SendMessage(hwndkakao_edit3, win32con.WM_SETTEXT, 0, chatroom_name)
    time.sleep(1)  # 안정성 위해 필요
    SendReturn(hwndkakao_edit3)
    time.sleep(1.5)


PBYTE256 = ctypes.c_ubyte * 256
_user32 = ctypes.WinDLL("user32")
GetKeyboardState = _user32.GetKeyboardState
SetKeyboardState = _user32.SetKeyboardState
PostMessage = win32api.PostMessage
SendMessage = win32gui.SendMessage
FindWindow = win32gui.FindWindow
IsWindow = win32gui.IsWindow
GetCurrentThreadId = win32api.GetCurrentThreadId
GetWindowThreadProcessId = _user32.GetWindowThreadProcessId
AttachThreadInput = _user32.AttachThreadInput

MapVirtualKeyA = _user32.MapVirtualKeyA
MapVirtualKeyW = _user32.MapVirtualKeyW

MakeLong = win32api.MAKELONG
w = win32con


# 조합키 쓰기 위해
def PostKeyEx(hwnd, key, shift, specialkey):
    if IsWindow(hwnd):
        ThreadId = GetWindowThreadProcessId(hwnd, None)

        lparam = MakeLong(0, MapVirtualKeyA(key, 0))
        msg_down = w.WM_KEYDOWN
        msg_up = w.WM_KEYUP

        if specialkey:
            lparam = lparam | 0x1000000

        if (
            len(shift) > 0
        ):  # Если есть модификаторы - используем PostMessage и AttachThreadInput
            pKeyBuffers = PBYTE256()
            pKeyBuffers_old = PBYTE256()

            SendMessage(hwnd, w.WM_ACTIVATE, w.WA_ACTIVE, 0)
            AttachThreadInput(GetCurrentThreadId(), ThreadId, True)
            GetKeyboardState(ctypes.byref(pKeyBuffers_old))

            for modkey in shift:
                if modkey == w.VK_MENU:
                    lparam = lparam | 0x20000000
                    msg_down = w.WM_SYSKEYDOWN
                    msg_up = w.WM_SYSKEYUP
                pKeyBuffers[modkey] |= 128

            SetKeyboardState(ctypes.byref(pKeyBuffers))
            time.sleep(0.01)
            PostMessage(hwnd, msg_down, key, lparam)
            time.sleep(0.01)
            PostMessage(hwnd, msg_up, key, lparam | 0xC0000000)
            time.sleep(0.01)
            SetKeyboardState(ctypes.byref(pKeyBuffers_old))
            time.sleep(0.01)
            AttachThreadInput(GetCurrentThreadId(), ThreadId, False)

        else:  # Если нету модификаторов - используем SendMessage
            SendMessage(hwnd, msg_down, key, lparam)
            SendMessage(hwnd, msg_up, key, lparam | 0xC0000000)


########################################################################################################################

# 더 편하게 쓰기 위해 클래스를 구현해봤음
# 다른 파일에서 이 클래스만 import하면 되도록 하는 게 목표

os.chdir(pathlib.Path(__file__).parent.resolve())


class KakaoRoom:
    def __init__(self, chatroom_name):
        folder = "cache"
        self.chatroom_name = chatroom_name
        self.file_path = (
            folder
            + "/%s.json"
            % hashlib.sha256(bytes(self.chatroom_name, encoding="u8")).hexdigest()
        )
        if not os.path.isdir(folder):
            os.system("mkdir " + folder)
        if os.path.isfile(self.file_path):
            self.all_data = json.load(open(self.file_path, "r", encoding="u8"))
        else:
            self.all_data = []

    def open(self):
        open_chatroom(self.chatroom_name)

    def send(self, text):
        self.open()
        kakao_sendtext(self.chatroom_name, text)

    def read_raw(self):
        self.open()
        # 핸들 _ 채팅방
        hwndMain = win32gui.FindWindow(None, self.chatroom_name)
        hwndListControl = win32gui.FindWindowEx(
            hwndMain, None, "EVA_VH_ListControl_Dblclk", None
        )
        # 조합키, 본문을 클립보드에 복사 ( ctl + A , C )
        PostKeyEx(hwndListControl, ord("A"), [w.VK_CONTROL], False)
        time.sleep(1)
        PostKeyEx(hwndListControl, ord("C"), [w.VK_CONTROL], False)
        ctext = pyperclip.paste()
        pyperclip.copy("")
        return ctext  # 내용 확인

    # 메시지끼리는 \r\n, 메시지 내에서는 \n으로 구분되어 있다는 관찰 덕분에 코드가 간단해짐
    # https://stackoverflow.com/questions/14689531/how-to-match-a-newline-character-in-a-raw-string
    # https://stackoverflow.com/questions/33312175/matching-any-character-including-newlines-in-a-python-regex-subexpression-not-g

    # 추가 관찰:
    # 톡이 많이 와 있어도 들어가면 가장 최신 걸 복사할 수 있다
    # 올라가도 최신 건 복사된다
    # 날짜가 맨 첫 줄에 항상 복사된다

    def process(self, raw_text):
        # https://airfox1.tistory.com/5 참고했으나 복붙은 아님
        so_msg_pattern = "\[(.*)\] \[(오[전후] [0-9]+:[0-9]+)\] (.*)"

        data = []
        popped_starting_date = False  # 복사 시 맨 처음에 강제로 날짜가 들어가 있기 때문에 제거해야 함

        for line in raw_text.split("\r\n"):
            if line == "":
                continue
            if re.match(so_msg_pattern, line, re.DOTALL):
                name, time, message = re.search(
                    so_msg_pattern, line, re.DOTALL
                ).groups()
                data.append(
                    {
                        "type": "Message",
                        "matter": {"name": name, "time": time, "message": message},
                    }
                )
            else:
                data.append({"type": "SystemText", "matter": line})
            if not popped_starting_date:
                data.pop()
                popped_starting_date = True
        return data

    def is_same_kakao(self, ka, kb):
        if ka["type"] == kb["type"] == "SystemText":
            if ka["matter"] == kb["matter"]:
                return True
        elif ka["type"] == kb["type"] == "Message":
            if (
                ka["matter"]["time"] == kb["matter"]["time"]
                and ka["matter"]["message"] == kb["matter"]["message"]
            ):
                return True
        return False

    def read_and_merge_data(self):  # 수정함
        new_data = self.process(self.read_raw())

        if len(new_data) == 0:  # 합칠 데이터 없음
            return None

        if len(self.all_data) == 0:  # 이번에 처음 읽어옴
            self.all_data = new_data
            return None
        
        # 긴 걸로 업데이트
        if self.is_same_kakao(self.all_data[-1], new_data[-1]) and len(self.all_data) < len(new_data): 
            self.all_data = new_data
            return None

        found_connection = False
        for i in range(len(new_data)):
            if self.is_same_kakao(self.all_data[-1], new_data[i]):
                found_connection = True
                break

        if not found_connection:  # 연결점을 못 찾음
            self.scroll_up(70)  # 좀 더 올려서 연결할 메시지를 찾아보자
            self.read_and_merge_data()  # 재귀

        else:  # 연결점 이후로 extend
            for j in range(i + 1, len(new_data)):
                self.all_data.append(new_data[j])

    # https://learn.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes

    def scroll_up(self, distance):  # read_raw 복붙 후 수정
        self.open()
        # 핸들 _ 채팅방
        hwndMain = win32gui.FindWindow(None, self.chatroom_name)
        hwndListControl = win32gui.FindWindowEx(
            hwndMain, None, "EVA_VH_ListControl_Dblclk", None
        )
        for _ in range(distance):
            PostKeyEx(hwndListControl, 0x26, [w.VK_CONTROL], False)

    def exit_and_save(self):  # 프로그램 종료 전에
        json.dump(
            self.all_data, open(self.file_path, "w", encoding="u8"), ensure_ascii=False
        )
