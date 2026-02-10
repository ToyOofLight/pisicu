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
# from contextlib import contextmanager
# from dotenv import load_dotenv
# from psycopg_pool import ConnectionPool

from supabase import create_client


# region Globale
supabase = create_client(st.secrets['SUPABASE_URL'], st.secrets['SUPABASE_KEY'])
BASE_PATH = 'E:\🛡️\coding\Vericu'
NOW = dt.now()
TODAY = dt.now(ZoneInfo('Europe/Bucharest')).date()
# TODAY = dt.today().date() # todo remove?
WEEKDAYS = ['Luni', 'Marți', 'Miercuri', 'Joi', 'Vineri', 'Sâmbătă', 'Duminică']
AZI = WEEKDAYS[TODAY.weekday()]
states_file = f"states_{str(TODAY)[4:].replace('-', '')}.csv"
FRECVENTE = ['Azi', 'Zilnic', 'Săptămânal', 'Lunar', 'Anual']
TIMPI = {'Zilnic': 'Ora', 'Săptămânal': 'Ziua', 'Lunar': 'Ziua', 'Anual': 'Data'}
USERS = ['elvin', 'ioana']
# endregion


def get_tasks():
    # with vericudb() as pool:  # todo remove
    #     with pool.connection() as conn:
    #         tasks = pd.read_sql('SELECT * FROM "tasks" WHERE "user" = %s', conn, params=(st.query_params['user'],))

    response = supabase.table('tasks').select('*').eq('user', st.query_params['user']).execute()
    tasks = pd.DataFrame(response.data)
    if tasks.empty:
        return tasks

    taskuri = {}
    for freq in FRECVENTE:
        freq_df = tasks[tasks['frecventa'] == freq]

        # Sort:
        if freq == 'Lunar':
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
        cols = st.columns(2)
        nume_col = 0 if freq == 'Azi' else 1
        timp = '.'
        if freq == 'Zilnic':
            timp = cols[0].time_input('Ora')
        elif freq == 'Săptămânal':
            timp = cols[0].selectbox('Ziua', WEEKDAYS)
        elif freq == 'Lunar':
            timp = cols[0].number_input(TIMPI[freq], min_value=1, max_value=31)
        elif freq == 'Anual':
            colss = cols[0].columns(2)
            ziua = colss[0].number_input('Ziua', min_value=1, max_value=31, step=1)
            luna = colss[1].selectbox('Luna', list(calendar.month_abbr)[1:])
            timp = f'{ziua}{luna}'

        nume = cols[nume_col].text_input('', placeholder='nume', autocomplete='off')
        info = st.text_area('', placeholder='ℹ info').replace('\n', '  \n')
        if nume and timp and st.columns([6, 1])[1].button('➕'):
            if ':' in str(timp):
                timp = ':'.join(str(timp).split(':')[:-1])

            (supabase.table('tasks').insert({'nume': nume, 'frecventa': freq, 'timp': timp, 'info': info,
                                             'completed': False, 'user': st.query_params['user']}).execute()
            )

            # query = 'INSERT INTO tasks (nume, frecventa, timp, info, completed, "user") VALUES (%s, %s, %s, %s, %s, %s)'  # todo remove
            # with vericudb() as pool, pool.connection() as conn:
            #     conn.execute(query, (nume, freq, timp, info, False, st.query_params['user']))
            st.rerun()

    add_task()


def edit_dialog(nume_i, freq, timp_i, info_i):
    @st.dialog(f'✏️ Edit task {freq}: {nume_i}' + ('' if freq == 'Azi' else f' ({timp_i})'))
    def edit_task():
        cols = st.columns(2)
        nume_col = 0 if freq == 'Azi' else 1
        timp = '.'
        if freq == 'Zilnic':
            timp = cols[0].time_input('Ora', value=timp_i)
        elif freq == 'Săptămânal':
            timp = cols[0].selectbox('Ziua', WEEKDAYS, index=WEEKDAYS.index(timp_i))
        elif freq == 'Lunar':
            timp = cols[0].number_input(TIMPI[freq], min_value=1, max_value=31, value=int(timp_i))
        elif freq == 'Anual':
            colss = cols[0].columns(2)
            day = ''.join(c for c in timp_i if c.isdigit())
            ziua = colss[0].number_input('Ziua', min_value=1, max_value=31, step=1, value=int(day))
            luna = colss[1].selectbox('Luna', list(calendar.month_abbr)[1:],
                                      index=list(calendar.month_abbr).index(timp_i[len(day):]) - 1)
            timp = f'{ziua}{luna}'

        nume = cols[nume_col].text_input('Nume', placeholder='nume', autocomplete='off', value=nume_i)
        info = st.text_area('', placeholder='ℹ info', value=info_i or '').replace('\n', '  \n')
        if nume and timp and st.columns([6, 1])[1].button('✅'):
            if ':' in str(timp):
                timp = ':'.join(str(timp).split(':')[:-1])
            # query = """   # todo remove
            #     UPDATE tasks SET nume = %s, timp = %s, info = %s
            #     WHERE "user" = %s AND nume = %s AND frecventa = %s AND timp = %s
            # """
            # with vericudb() as pool, pool.connection() as conn:
            #     conn.execute(query, (nume, timp, info, st.query_params['user'], nume_i, freq, timp_i))

            (supabase.table("tasks").update({"nume": nume, "timp": timp, "info": info})
             .eq("user", st.query_params["user"]).eq("nume", nume_i).eq("frecventa", freq).eq("timp", timp_i)
             .execute())

            st.rerun()
    edit_task()


# def delete_task(nume, frecventa, timp):
#     query = 'DELETE FROM tasks WHERE "user" = %s AND nume = %s AND frecventa = %s AND timp = %s'
#     with vericudb() as pool, pool.connection() as conn:
#         conn.execute(query, (st.query_params['user'], nume, frecventa, timp))
#         conn.commit()


def delete_task(nume, frecventa, timp):
    (supabase.table("tasks").delete().eq("user", st.query_params["user"]).eq("nume", nume).eq("frecventa", frecventa)
     .eq("timp", timp).execute())


# def check_task(completed, nume, frecventa, timp):
#     query = 'UPDATE tasks SET completed = %s, last_completed = %s WHERE "user" = %s AND nume = %s AND frecventa = %s AND timp = %s'
#     with vericudb() as pool:
#         with pool.connection() as conn:
#             with conn.cursor() as cursor:
#                 cursor.execute(query, (completed, NOW if completed else None, st.query_params['user'], nume, frecventa, timp))
#             conn.commit()


def check_task(completed, nume, frecventa, timp):
    data = {"completed": completed, "last_completed": dt.now(timezone.utc).isoformat() if completed else None}
    (supabase.table("tasks").update(data).eq("user", st.query_params["user"]).eq("nume", nume)
     .eq("frecventa", frecventa).eq("timp", timp).execute()
    )


def reset_tasks():
    response = supabase.table('tasks').select('nume, frecventa, timp, last_completed').execute()
    tasks = response.data

    for t in tasks:
        nume = t['nume']
        frecventa = t['frecventa']
        timp = t['timp']
        last_completed = pd.to_datetime(t['last_completed'])
        if not last_completed:
            continue
        reset = False

        if frecventa in ['Azi', 'Zilnic'] and NOW.day != last_completed.day:
            reset = True
        elif frecventa == 'Săptămânal' and NOW.isocalendar().week != last_completed.isocalendar().week:
            reset = True
        elif frecventa == 'Lunar' and NOW.month != last_completed.month:
            reset = True
        elif frecventa == 'Anual' and NOW.year != last_completed.year:
            reset = True

        if reset:
            if frecventa == 'Azi':
                supabase.table('tasks').delete().eq('frecventa', frecventa).execute()

            else:
                (supabase.table('tasks').update({'completed': False}).eq('nume', nume).eq('frecventa', frecventa)
                    .eq('timp', timp).execute()
                )
