from flask import Flask, render_template, request, send_file
import pandas as pd
import random
import calendar
import io

app = Flask(__name__)

def generate_weekly_roster():
    girls = ["Aarushi", "Ananya", "Diya", "Isha", "Meera"]
    boys = ["Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Krishna", "Ishaan"]

    girl_shifts = ['M', 'G1', 'G2', 'G3']
    boy_shifts = ['G3', 'S3']
    num_weeks = 4  # July 2024 has 4 full weeks (Mon-Fri)

    weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
    
    girls_data = {'Name': girls}
    boys_data = {'Name': boys}
    
    last_week_night_shift_boy = None

    for week_num in range(num_weeks):
        shift_girls = random.choices(girl_shifts, k=len(girls))
        shift_boys = boy_shifts * (len(boys) // 2)

        # Select a boy for the night shift who didn't have it last week
        night_shift_boy = random.choice([boy for boy in boys if boy != last_week_night_shift_boy])
        last_week_night_shift_boy = night_shift_boy

        for day in range(5):  # Only weekdays
            date_str = f'{(week_num * 7) + day + 1}{get_day_suffix((week_num * 7) + day + 1)} ({weekdays[day]})'

            for i, girl in enumerate(girls):
                girls_data.setdefault(date_str, []).append(shift_girls[i])

            for i, boy in enumerate(boys):
                if boy == night_shift_boy:
                    boys_data.setdefault(date_str, []).append('N')
                else:
                    boys_data.setdefault(date_str, []).append(random.choice(boy_shifts))

    girls_df = pd.DataFrame(girls_data)
    boys_df = pd.DataFrame(boys_data)

    return girls_df, boys_df

def get_day_suffix(day):
    if 11 <= day <= 13:
        return 'th'
    if day % 10 == 1:
        return 'st'
    if day % 10 == 2:
        return 'nd'
    if day % 10 == 3:
        return 'rd'
    return 'th'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    girls_df, boys_df = generate_weekly_roster()
    girls_html = girls_df.to_html(classes='table', index=False)
    boys_html = boys_df.to_html(classes='table', index=False)
    return render_template('index.html', girls_html=girls_html, boys_html=boys_html)

@app.route('/download/<string:roster_type>')
def download(roster_type):
    girls_df, boys_df = generate_weekly_roster()

    if roster_type == 'girls':
        csv_data = girls_df.to_csv(index=False)
        filename = 'girls_roster.csv'
    elif roster_type == 'boys':
        csv_data = boys_df.to_csv(index=False)
        filename = 'boys_roster.csv'

    # Create a bytes buffer
    buffer = io.BytesIO()
    buffer.write(csv_data.encode('utf-8'))
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name=filename, mimetype='text/csv')

if __name__ == '__main__':
    app.run(debug=True)
