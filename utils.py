import calendar
# import os
# import shutil
# import tempfile
# import time
from datetime import timedelta, timezone, datetime as dt
from zoneinfo import ZoneInfo
import pandas as pd
# import psycopg2
# import requests
import streamlit as st
# from PIL import Image, ImageOps

from supabase import create_client


# region Globale
supabase = create_client(st.secrets['SUPABASE_URL'], st.secrets['SUPABASE_KEY'])
BASE_PATH = 'E:\🛡️\coding\Vericu'
NOW = dt.now()
TODAY = dt.now(ZoneInfo('Europe/Bucharest')).date()
WEEKDAYS = ['Luni', 'Marți', 'Miercuri', 'Joi', 'Vineri', 'Sâmbătă', 'Duminică']
LUNI = {
    'Jan': 'Ianuarie',
    'Feb': 'Februarie',
    'Mar': 'Martie',
    'Apr': 'Aprilie',
    'May': 'Mai',
    'Jun': 'Iunie',
    'Jul': 'Iulie',
    'Aug': 'August',
    'Sep': 'Septembrie',
    'Oct': 'Octombrie',
    'Nov': 'Noiembrie',
    'Dec': 'Decembrie'
}
AZI = WEEKDAYS[TODAY.weekday()]
states_file = f"states_{str(TODAY)[4:].replace('-', '')}.csv"
FRECVENTE = ['Azi', 'Zilnic', 'Săptămânal', 'Lunar', 'Anual']
USERS = ['elvin', 'ioana']
# endregion


def get_tasks():
    response = supabase.table('tasks').select('*').eq('user', st.query_params['user']).execute()
    tasks = pd.DataFrame(response.data)
    if tasks.empty:
        return tasks

    taskuri = {}
    for freq in FRECVENTE:
        freq_df = tasks[tasks['frecventa'] == freq]

        # Sort:
        if freq == 'Lunar':
            freq_df['timp'] = freq_df['timp'].astype(int)
            freq_df.sort_values(by=['timp'], inplace=True)
        elif freq != 'Azi':
            if freq == 'Zilnic':
                freq_df['temp'] = pd.to_datetime(freq_df['timp'], format='%H:%M').dt.time
            elif freq == 'Săptămânal':
                freq_df['temp'] = freq_df['timp'].apply(lambda x: WEEKDAYS.index(x))
            elif freq == 'Anual':
                freq_df['temp'] = pd.to_datetime(freq_df['timp'] + '2026', format='%d%b%Y')
            freq_df.sort_values(by=['temp'], inplace=True)
            freq_df.drop(columns=['temp'], inplace=True)

        taskuri[freq] = freq_df[tasks['completed'].isin([False, None])]
        taskuri[f'✓{freq}'] = freq_df[tasks['completed'] == True]

    return taskuri


def add_dialog(freq):
    @st.dialog(f'Adaugă task {freq}')
    def add_task():
        coloane = 1 if freq == 'Azi' else 2 if freq in ['Azi', 'Anual'] else [1, 2.4]
        cols = st.columns(coloane)
        nume_col = 0 if freq == 'Azi' else 1
        timp = '.'
        if freq == 'Zilnic':
            timp = cols[0].time_input('', value=(dt.now() + timedelta(hours=2)).time(), label_visibility='collapsed')
        elif freq == 'Săptămânal':
            timp = cols[0].selectbox('', WEEKDAYS, label_visibility='collapsed')
        elif freq == 'Lunar':
            timp = cols[0].number_input('', min_value=1, max_value=31, label_visibility='collapsed')
        elif freq == 'Anual':
            colss = cols[0].columns([1, 2])
            ziua = colss[0].number_input('', min_value=1, max_value=31, step=1, label_visibility='collapsed')
            luna = colss[1].selectbox('', list(calendar.month_abbr)[1:], label_visibility='collapsed')
            timp = f'{ziua}{luna}'

        nume = cols[nume_col].text_input('', placeholder='denumire', autocomplete='off', label_visibility='collapsed')
        info = st.text_area('', placeholder='ℹ info', label_visibility='collapsed').replace('\n', '  \n')
        if nume and timp and st.columns([6, 1])[1].button('➕'):
            if ':' in str(timp):
                timp = ':'.join(str(timp).split(':')[:-1])

            (supabase.table('tasks').insert({'nume': nume, 'frecventa': freq, 'timp': timp, 'info': info,
                                             'completed': False, 'user': st.query_params['user']}).execute()
            )
            st.rerun()

    add_task()


def edit_dialog(nume_i, freq, timp_i, info_i):
    @st.dialog(f'✏️ Edit task {freq}:\n\n{nume_i}' + ('' if freq == 'Azi' else f' ({timp_i})'))
    def edit_task():
        coloane = 1 if freq == 'Azi' else 2 if freq in ['Azi', 'Anual'] else [1, 2.4]
        cols = st.columns(coloane)
        nume_col = 0 if freq == 'Azi' else 1
        timp = '.'
        if freq == 'Zilnic':
            timp = cols[0].time_input('', value=timp_i, label_visibility='collapsed')
        elif freq == 'Săptămânal':
            timp = cols[0].selectbox('', WEEKDAYS, index=WEEKDAYS.index(timp_i), label_visibility='collapsed')
        elif freq == 'Lunar':
            timp = cols[0].number_input('', min_value=1, max_value=31, value=int(timp_i), label_visibility='collapsed')
        elif freq == 'Anual':
            colss = cols[0].columns(2)
            day = ''.join(c for c in timp_i if c.isdigit())
            ziua = colss[0].number_input('', min_value=1, max_value=31, step=1, value=int(day), label_visibility='collapsed')
            luna = colss[1].selectbox('', list(calendar.month_abbr)[1:], label_visibility='collapsed',
                                      index=list(calendar.month_abbr).index(timp_i[len(day):]) - 1)
            timp = f'{ziua}{luna}'

        nume = cols[nume_col].text_input('', placeholder='nume', autocomplete='off', value=nume_i,
                                         label_visibility='collapsed')
        info = st.text_area('', placeholder='ℹ info', value=info_i or '', label_visibility='collapsed').replace('\n', '  \n')
        if nume and timp and st.columns([6, 1])[1].button('✅'):
            if ':' in str(timp):
                timp = ':'.join(str(timp).split(':')[:-1])

            (supabase.table('tasks').update({'nume': nume, 'timp': timp, 'info': info})
             .eq('user', st.query_params['user']).eq('nume', nume_i).eq('frecventa', freq).eq('timp', timp_i)
             .execute())

            st.rerun()
    edit_task()


def delete_task(nume, frecventa, timp):
    (supabase.table("tasks").delete().eq("user", st.query_params["user"]).eq("nume", nume).eq("frecventa", frecventa)
     .eq("timp", timp).execute())


def check_task(completed, nume, frecventa, timp):
    data = {"completed": completed, "last_completed": dt.now(timezone.utc).isoformat() if completed else None}
    (supabase.table("tasks").update(data).eq("user", st.query_params["user"]).eq("nume", nume)
     .eq("frecventa", frecventa).eq("timp", timp).execute()
    )


def reset_tasks():
    response = supabase.table('tasks').select('nume, frecventa, timp, last_completed').execute()
    tasks = response.data

    st.write(f'NOW.day: {NOW.day}')  # todo remove

    for t in tasks:
        last_completed = pd.to_datetime(t['last_completed'])
        if not last_completed:
            continue
        nume = t['nume']
        frecventa = t['frecventa']
        timp = t['timp']
        reset = False

        if frecventa in ['Azi', 'Zilnic']:  # todo remove
            st.write(f'last_completed {nume} ({timp}): {last_completed.day}')  # todo remove

        if frecventa in ['Azi', 'Zilnic']:
            reset = NOW.day != last_completed.day
        elif frecventa == 'Săptămânal':
            reset = NOW.isocalendar().week != last_completed.isocalendar().week
        elif frecventa == 'Lunar':
            reset = NOW.month != last_completed.month
        elif frecventa == 'Anual':
            reset = NOW.year != last_completed.year

        if reset:
            if frecventa == 'Azi':
                supabase.table('tasks').delete().eq('frecventa', frecventa).execute()

            else:
                (supabase.table('tasks').update({'completed': False}).eq('nume', nume).eq('frecventa', frecventa)
                    .eq('timp', timp).execute()
                )
