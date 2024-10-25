import streamlit as st
import pandas as pd
import time
import datetime
import subprocess
import altair as alt

st.set_page_config(page_title="Monitor de Processos", layout="wide")

chart_placeholder = st.empty()
table_placeholder = st.empty()

x = {'Time': [], 'Process Count': []}

process_data = []

N_POINTS = 20
MIN_PROCESS_COUNT = 420

def update_process_data():
    result = subprocess.run(['ps', 'aux'], stdout=subprocess.PIPE)
    lines = result.stdout.decode('utf-8').splitlines()

    process_count = len(lines) - 1 
    current_time = datetime.datetime.now().strftime("%H:%M:%S")

    x['Time'].append(current_time)
    x['Process Count'].append(process_count)

    current_process_data = []
    for line in lines[1:]:
        parts = line.split()
        if len(parts) >= 11: 
            user = parts[0]
            pid = parts[1]
            cpu = parts[2]
            mem = parts[3]
            current_process_data.append({
                'User': user,
                'PID': pid,
                'CPU (%)': cpu,
                'Memory (%)': mem,
            })
    
    return current_process_data, process_count

while True:
    process_data, process_count = update_process_data()

    chart_data = pd.DataFrame(x)
    chart_data['Time'] = pd.to_datetime(chart_data['Time'], format='%H:%M:%S')

    if len(chart_data) > N_POINTS:
        chart_data = chart_data.tail(N_POINTS)

    chart_data = chart_data[chart_data['Process Count'] > MIN_PROCESS_COUNT]

    if not chart_data.empty:
        line_chart = alt.Chart(chart_data).mark_line().encode(
            x=alt.X('Time:T', axis=alt.Axis(format='%H:%M:%S')),
            y=alt.Y('Process Count:Q', scale=alt.Scale(domain=[MIN_PROCESS_COUNT, chart_data['Process Count'].max() + 50]))  
        ).properties(
            width=800, 
            height=400
        )
        chart_placeholder.altair_chart(line_chart, use_container_width=True)
    else:
        chart_placeholder.empty() 

    process_df = pd.DataFrame(process_data)
    table_placeholder.dataframe(process_df, use_container_width=True) 
    time.sleep(1)
