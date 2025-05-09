from flask import Flask, request, render_template
import pickle
import numpy as np
from datetime import datetime, timedelta

# Load mô hình ML
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

app = Flask(__name__)

# Danh sách các loại dầu từ file Excel (37 loại)
oil_names = [
    'BACH HO', 'BONNY LT', 'Heavy Bach Ho', 'YELLOW TUNA', 'KIMANIS', 'AMNA', 'QUA IBOE',
    'MURBAN', 'MIRI LT', 'BUNGA ORKID', 'KIKEH', 'CABINDA', 'RABI BLEND', 'RABI LIGHT',
    'BERTAM', 'CHAMPION', 'DAI HUNG', 'LABUAN', 'RUBY', 'TE GIAC TRANG', 'AZERI LT',
    "N'KOSSA", 'RANG DONG', 'CHIM SAO', 'THANG LONG', 'SOKOL', 'HAI THACH', 'SU TU DEN',
    'ESPO', 'WTI', 'SONG DOC', 'BU ATTIFEL', 'MINAS', 'PALANCA', 'FORCADOS',
    'SLOPS', 'CDU RESIDUE'
]

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/predict_single', methods=['GET', 'POST'])
def predict_single():
    if request.method == 'GET':
        return render_template('index.html', oil_names=oil_names)
    try:
        inputs = []
        for oil in oil_names:
            value = request.form.get(oil, '')
            if value.strip() == '':
                value = 0
            inputs.append(float(value))

        total = sum(inputs)
        if total > 100:
            return render_template('index.html', prediction="Tổng tỷ lệ dầu vượt quá 100%", oil_names=oil_names)

        X = np.array(inputs).reshape(1, -1)
        predicted_ph = model.predict(X)[0]
        return render_template('index.html', prediction=round(predicted_ph, 2), oil_names=oil_names)
    except Exception as e:
        return render_template('index.html', prediction=f"Lỗi: {e}", oil_names=oil_names)

@app.route('/trend', methods=['GET', 'POST'])
def trend():
    if request.method == 'GET':
        return render_template('trend_input.html')

    try:
        start_str = request.form.get('start_date')
        end_str = request.form.get('end_date')
        start_date = datetime.strptime(start_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_str, '%Y-%m-%d')

        # Tạo danh sách ngày theo từng ngày
        date_list = []
        current_date = start_date
        while current_date <= end_date:
            date_list.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)

        # Nếu là POST có dữ liệu dự đoán (submit lần 2)
        if 'predict_trend' in request.form:
            trend_data = []
            for date in date_list:
                inputs = []
                for oil in oil_names:
                    key = f"{oil}_{date}"
                    value = request.form.get(key, '')
                    if value.strip() == '':
                        value = 0
                    inputs.append(float(value))
                total = sum(inputs)
                if total > 100:
                    return render_template('trend_input.html', oil_names=oil_names, date_list=date_list,
                                           error=f"Tổng tỷ lệ dầu vượt quá 100%")
                X = np.array(inputs).reshape(1, -1)
                predicted_ph = model.predict(X)[0]
                trend_data.append({"date": date, "ph": round(predicted_ph, 2)})

            return render_template('trend.html', trend_data=trend_data)

        # Nếu mới nhập ngày → render form nhập dữ liệu theo từng ngày (mỗi ngày một nhóm input)
        return render_template('trend_input.html', oil_names=oil_names, date_list=date_list)

    except Exception as e:
        return render_template('trend_input.html', error=f"Lỗi: {e}")

if __name__ == '__main__':
    app.run(debug=True)
