# 코랩의 코드 복사함

# 로컬에서 모델을 사용할 때 필요한 코드 A
from tensorflow import keras
import numpy as np

model = keras.models.load_model("./model")
print("모델 로드 완료")

# 로컬에서 모델을 사용할 때 필요한 코드 B

keywords = ["위치", "구", "삽", "보신", "충전기", "찾았습니다", "있습니다","찾습니다", "갠톡", "어디", "라고", "연락처", "사람", "@", "깨워", "보라", "선생", "쌤", "봐달라", "보내주", "구합니다", "구함", "감사", "삽니다", "있", "있으신","혹시", "공감", "분", "아시는", "부탁","털렸", "죄송", "ㅎㄱ", "해결", "삭제", "ㅠ","ㅋ", "팔", "잃","?","연락", "톡", "빌려","계시","있는"
]

input_shape = (len(keywords),)  # 키워드 가짓수 == 메시지를 벡터로 바꿨을 때의 길이


def vectorize(sequences):
    results = np.zeros((len(sequences), *input_shape))
    for i, sequence in enumerate(sequences):
        for j in range(*input_shape):
            results[i, j] = int(keywords[j] in sequence)
    return results


id_to_label = ['분실물', '사람', '물건','정보','기타']

label_to_id = dict()
for i, label in enumerate(id_to_label):
    label_to_id[label] = i
output_num = len(id_to_label)  # 우리가 분류하고자 하는 메시지의 가짓수


def to_one_hot(sequences):
    results = np.zeros((len(sequences), output_num))
    for i, sequence in enumerate(sequences):
        results[i, label_to_id[sequence]] = 1
    return results


# 로컬에서 모델을 사용할 때 필요한 코드 C


def predict(message):
    predictions = model.predict(vectorize([message]))
    if np.max(predictions) > 0.35:
        return id_to_label[np.argmax(predictions[0])]
    return None
