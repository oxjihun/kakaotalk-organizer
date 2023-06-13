# KakaoTalk Organizer

20-046 박지훈, 21-065 오민준의 2023년 1학기 자료구조 프로젝트입니다.

## 개요

코로나19를 계기로 온라인 수업이 늘면서 카카오톡과 톡방 사용이 덩달아 증가했습니다. 친구들과의 소통 뿐만 아니라 수업 및 공지도 카카오톡을 통하다 보니, 이 메신저 앱 없이는 생활하기 힘들 정도가 되었습니다. 그런데 몇백명씩 있는 톡방이나 오픈채팅방의 경우 너무 많은 정보들이 한꺼번에 올라와 필요한 것을 놓치기 쉽다는 한계점이 있습니다. 저희는 이러한 불편함을 개선하고자 카카오톡 대화 정리 프로젝트를 진행하게 되었습니다.

## 설치 및 실행 방법

이 리포지토리의 코드를 다운로드하고, 아래의 라이브러리들을 설치한 다음 `interface.py`를 실행하면 됩니다.

### 코드 다운로드하기

상단의 초록색 'Code' 버튼을 누르고 'Download ZIP'을 누르면 됩니다.

만약 `git` 사용자라면 아래의 명령어로 비교적 간편하게 받을 수 있습니다.

```
git clone https://github.com/oxjihun/kakaotalk-organizer.git
```

### 라이브러리 설치 (필수)

[`CustomTkinter`](https://customtkinter.tomschimansky.com/)와 [`pyperclip`](https://pypi.org/project/pyperclip/)이 필요합니다.

```
pip install customtkinter
pip install pyperclip
```

### 라이브러리 설치 (선택)

모델을 이용하여 텍스트를 분류하고자 하는 사용자에게만 해당합니다. [`TensorFlow`](https://www.tensorflow.org/?hl=ko)와 [`NumPy`](https://numpy.org/)를 설치해야 합니다.

```
pip install tensorflow
pip install numpy
```

## 학습에 사용한 Colab

아래의 링크에 있는 Colab으로 텍스트 분류 모델을 만들었습니다. 결과는 이미 `model` 폴더에 저장되어 있으므로 사용자가 직접 Colab을 실행시킬 필요는 없습니다.

https://colab.research.google.com/drive/1-yIUTAcgxlxht2FEW7MSZ3HzJW5-rnLo?usp=sharing

## 참고한 자료

- https://airfox1.tistory.com/category/python/매크로

- https://customtkinter.tomschimansky.com

- https://docs.python.org/3/library/re.html

- https://docs.python.org/3/library/hashlib.html

- https://stackoverflow.com/questions/12595051/check-if-string-matches-pattern

- https://stackoverflow.com/a/11050652

- https://stackoverflow.com/q/13355233

- https://stackoverflow.com/a/30507349

- https://stackoverflow.com/a/65119935

- https://www.geeksforgeeks.org/python-os-path-isfile-method/

아래는 코딩에 사용하지는 않았지만 영감을 준 프로젝트입니다.

- https://github.com/uoneway/kakaotalk_msg_preprocessor
