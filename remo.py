import pandas as pd
import streamlit as st
import datetime
import csv
import os


def data_check():
    with open('./data.csv', "r") as file:
        reader = csv.reader(file)
        datas = [data for data in reader]

    datas = pd.DataFrame(datas)
    datas = datas.rename({"0": "id", "1": "問題文", "2": "答え", "3": "復習日", "4": "復習回数"})
    st.table(datas)


def register_data():
    question: str = st.text_area(label='問題文を入力してください。', height=200)

    answer: str = st.text_area(label='答えを入力してください。', height=200)

    now: datetime = datetime.date.today() + datetime.timedelta(days=1)

    number: int = 0

    btn = st.button('登録')

    if btn:
        if question and answer:
            with open('./data.csv', 'a') as file:
                writer = csv.writer(file)
                with open('./data.csv') as file:
                    reader = csv.reader(file)
                    datas = [data for data in reader]
                data_id: int = len(datas)
                writer.writerow([data_id, question, answer, now, number])
            st.subheader("登録できました！！！")
        else:
            st.warning("登録情報を入力してください。")


def question_answer():
    # ファイル読み込み
    with open('./data.csv', "r") as file:
        reader = csv.reader(file)
        datas = [data for data in reader]

    # 復習日が今日のものを取り出す
    today: datetime = datetime.date.today()
    try:
        data: list = list(filter(lambda data: data[3] == str(today), datas))[0]
    except IndexError:
        st.write("復習する問題はありません。")
        return
    st.write("問題文")
    st.write(data[1])

    ans_btn = st.button('答えを見る')

    if ans_btn:
        st.write("答え")
        st.write(data[2])

        if datas[int(data[0])][4] == "0":
            datas[int(data[0])][3] = datetime.date.today() + datetime.timedelta(days=3)
        elif datas[int(data[0])][4] == "1":
            datas[int(data[0])][3] = datetime.date.today() + datetime.timedelta(days=7)
        elif datas[int(data[0])][4] == "2":
            datas[int(data[0])][3] = datetime.date.today() + datetime.timedelta(days=15)
        elif datas[int(data[0])][4] == "3":
            datas[int(data[0])][3] = datetime.date.today() + datetime.timedelta(days=25)
        else:
            datas[int(data[0])][3] = datetime.date.today() + datetime.timedelta(days=365)

        datas[int(data[0])][4] = int(datas[int(data[0])][4]) + 1

        with open('./data.csv', 'w') as file:
            writer = csv.writer(file)
            writer.writerows(datas)

        next_btn = st.button('次の問題へ')

        if next_btn:
            question_answer()


def main():
    # st.write(os.access('./data.csv', os.R_OK))
    # st.write(os.access('./data.csv', os.W_OK))
    # st.write(os.access('./data.csv', os.X_OK))
    os.chmod('./data.csv', 0o777)
    apps = {
        '-': None,
        "問題を登録": register_data,
        "復習する": question_answer,
        "データチェック": data_check
    }

    selected_app_name = st.sidebar.selectbox(label='選択してください。',
                                             options=list(apps.keys()))

    if selected_app_name == '-':
        st.info('選択してください。')
        st.stop()

        # 選択されたアプリケーションを処理する関数を呼び出す
    render_func = apps[selected_app_name]
    render_func()


if __name__ == '__main__':
    main()
