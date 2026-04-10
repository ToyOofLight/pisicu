import streamlit as st
from streamlit_autorefresh import st_autorefresh

import utils

css = '''<style>
    button[kind="secondary"] { border: none!important; background-color: transparent; }
    p {font-size: 30px!important;}
    [data-baseweb="tab"] {margin-right: 30px}
    .stMainBlockContainer {padding:1!important}
    [data-baseweb="tab-list"] .st-bd, [data-baseweb="tab-list"] .st-bn:hover {color: blue}
    button[data-baseweb="tab"] p {font-size:55px!important;}
    # .st-c1 {background-color: green!important; border-color: green!important;}    # todo fix?
    div[data-baseweb="tab-highlight"] {background-color: blue!important;}
    label[data-baseweb="checkbox"] span {width:2rem;height:2rem;}
    .stMainBlockContainer {padding:0 20px}
    .stAppHeader, ._container_gzau3_1, ._viewerBadge_nim44_23 {display: none;}
'''

# region Specifications
st.set_page_config(page_title='Pisicu', page_icon='🛡️', layout='wide')
st.markdown(css, unsafe_allow_html=True)
cols = st.columns([1, 5, 3, 1])
# cols[-1].image('media\\morale.png')
# endregion

# if st.query_params.get('user') and st.query_params['user'] in utils.USERS:
#     if st.query_params['user'] == 'elvin':
#         with cols[0]:
#             utils.display_rank()

utils.reset_tasks()
tasks = utils.get_tasks() or {}
timp_prev = ''
tabs = st.tabs(['Azi+Zilnic', 'Săptămânal+Lunar', 'Anual'])
timpi = {'Zilnic': utils.dt.now(utils.ZoneInfo('Europe/Bucharest')),
         'Săptămânal': utils.dt.now(utils.ZoneInfo('Europe/Bucharest')).date().weekday(),
         'Lunar': utils.dt.now(utils.ZoneInfo('Europe/Bucharest')).date().day,
         'Anual': utils.dt.now(utils.ZoneInfo('Europe/Bucharest')).date()}

extra_azi_tasks = []
now = utils.dt.now(utils.ZoneInfo('Europe/Bucharest'))
for freq in ['Săptămânal', 'Lunar', 'Anual']:
    for i, task in tasks[freq].iterrows():
        if freq == 'Săptămânal':
            add = utils.WEEKDAYS[utils.dt.now(utils.ZoneInfo('Europe/Bucharest')).date().weekday()] == task['timp']
        elif freq == 'Lunar':
            add = utils.dt.now(utils.ZoneInfo('Europe/Bucharest')).day == task['timp']
        elif freq == 'Anual':
            add = f'{utils.dt.now(utils.ZoneInfo('Europe/Bucharest')).day}{utils.dt.now(utils.ZoneInfo('Europe/Bucharest')).strftime('%b')}' == task['timp']
        if add:
            extra_azi_tasks.append(task)

for t in range(len(tabs)):
    with tabs[t]:
        cols = st.columns(2 if t != 2 else 1)
        interval = slice(0, 2) if t == 0 else slice(2, 4) if t == 1 else slice(4, 5)
        for i, freq in enumerate(utils.FRECVENTE[interval]):
            st.session_state['delimitat_start'], st.session_state['delimitat_end'] = False, False

            colss = cols[i].columns([1, 6])
            freq_text = f'{freq} ({utils.WEEKDAYS[utils.dt.now(utils.ZoneInfo('Europe/Bucharest')).date().weekday()]} {utils.dt.now(utils.ZoneInfo('Europe/Bucharest')).day}{utils.dt.now(utils.ZoneInfo('Europe/Bucharest')).strftime('%b')})' if freq == 'Azi' else freq
            in_paranteza = ''
            if freq == 'Zilnic':
                in_paranteza = f' ({utils.dt.now(utils.ZoneInfo('Europe/Bucharest')).strftime('%H:%M')})'
            if freq == 'Săptămânal':
                in_paranteza = f' ({utils.WEEKDAYS[utils.dt.now(utils.ZoneInfo('Europe/Bucharest')).date().weekday()]})'
            if freq in ['Lunar', 'Anual']:
                in_paranteza = f' ({utils.dt.now(utils.ZoneInfo('Europe/Bucharest')).day}{utils.dt.now(utils.ZoneInfo('Europe/Bucharest')).strftime('%b')})'
            freq_text += in_paranteza
            colss[0].button('➕', key=f'{freq}+', on_click=utils.add_dialog, args=(freq,))

            procent = 100
            if tasks and not tasks[freq].empty:
                procent = 0 if all(tasks[f].empty for f in [freq, f'✓{freq}']) else int(len(tasks[f'✓{freq}']) * 100 / (len(tasks[freq]) + len(tasks[f'✓{freq}'])))
            if tasks and not (tasks[freq].empty and tasks[f'✓{freq}'].empty):
                colss[1].subheader(f'{freq_text} {procent}%')
                cols[i].progress(procent)
            else:
                colss[1].subheader(freq_text)
            if freq not in tasks.keys():
                continue

            for j, task in tasks[freq].iterrows():
                # region Delimitare Prezent
                if freq in ['Zilnic', 'Săptămânal', 'Lunar', 'Anual']:
                    task_timp = task['timp']
                    if freq == 'Zilnic':
                        task_timp = utils.dt.combine(utils.dt.now(utils.ZoneInfo('Europe/Bucharest')).date(), utils.dt.strptime(task_timp, '%H:%M').time())
                        task_timp = task_timp.replace(tzinfo=utils.ZoneInfo("Europe/Bucharest"))
                    elif freq == 'Săptămânal':
                        task_timp = utils.WEEKDAYS.index(task_timp)
                    elif freq == 'Anual':
                        task_timp = utils.dt.strptime(f"{task_timp}{utils.dt.now(utils.ZoneInfo('Europe/Bucharest')).year}", '%d%b%Y').date()
                    if not st.session_state['delimitat_start'] and task_timp == timpi[freq]:
                        cols[i].write('---')
                        st.session_state['delimitat_start'] = True
                    if not st.session_state['delimitat_end'] and task_timp > timpi[freq]:
                        if not (freq == 'Lunar' and not st.session_state['delimitat_start']):
                            cols[i].write(f'---')
                            st.session_state['delimitat_end'] = True
                # endregion

                if freq in ['Săptămânal', 'Lunar', 'Anual']:
                    timp = ''.join([c for c in task['timp'] if not c.isnumeric()]) if freq == 'Anual' else task['timp']
                    titlu = utils.LUNI[timp] if freq == 'Anual' else timp
                    if not timp_prev:
                        timp_prev = timp
                        colss = cols[i].columns([1, 5])
                        if freq != 'Lunar':
                            cols[i].markdown(f"#### {titlu}")
                    elif timp != timp_prev:
                        colss = cols[i].columns([1, 5])
                        if freq != 'Lunar':
                            cols[i].markdown(f"#### {titlu}")
                        timp_prev = timp

                colss = cols[i].columns([.5, .5, 4, 1, 1] if freq == 'Azi' else [5, 1, 1])
                if freq == 'Azi':   # Reorder
                    if task['idx'] > 0:
                        colss[0].button('⬆️️', help='move to top', key=f'top_{task["nume"]}',
                                        on_click=utils.move_task, args=(task['nume'], 'top'))
                    if task['idx'] < max(tasks[freq]['idx']):
                        colss[1].button('⬇️', help='move to bottom', key=f'bot_{task["nume"]}',
                                        on_click=utils.move_task, args=(task['nume'], 'bot'))

                text = ('' if freq in ['Azi', 'Săptămânal'] else f"({task['timp']}) ") + f"{task['nume']}"
                text = f'*{text}*' if task['one_time'] else text
                colss[2 if freq == 'Azi' else 0].checkbox(text, value=task['completed'], on_change=utils.check_task,
                                                          args=(True, task['nume'], freq, task['timp']), help=task['info'],
                                                          key=f'check_{freq}_{task["nume"]}_{task["timp"]}')
                colss[3 if freq == 'Azi' else 1].button('✏️', key=f'edit_{freq}_{task["nume"]}_{task["timp"]}',
                                                        on_click=utils.edit_dialog,
                                                        args=(task['nume'], freq, task['timp'], task['info'], task['one_time']))
                colss[4 if freq == 'Azi' else 2].button('❌', key=f'del_{freq}_{task["nume"]}_{task["timp"]}',
                                                        on_click=utils.delete_task, args=(task['nume'], freq, task['timp']))

            # region extra_azi_tasks:
            if freq == 'Azi' and extra_azi_tasks:
                cols[i].write('---')
                for task in extra_azi_tasks:
                    colsss = cols[i].columns([.5, .5, 4, 1, 1])
                    text = f'*{task['nume']}*' if task['one_time'] else task['nume']
                    colsss[2].checkbox(text, value=task['completed'], on_change=utils.check_task,
                                      args=(True, task['nume'], task['frecventa'], task['timp']), help=task['info'],
                                      key=f'check_{task['frecventa']}_{task["nume"]}_{task["timp"]}_azi')
                    colsss[3].button('✏️', key=f'edit_{task['frecventa']}_{task["nume"]}_{task["timp"]}_azi', on_click=utils.edit_dialog,
                                    args=(task['nume'], task['frecventa'], task['timp'], task['info'], task['one_time']))
                    colsss[4].button('❌', key=f'del_{task['frecventa']}_{task["nume"]}_{task["timp"]}_azi',
                                    on_click=utils.delete_task, args=(task['nume'], task['frecventa'], task['timp']))
            # endregion

            if not tasks[f'✓{freq}'].empty:
                with cols[i].expander('✅ Completate'):
                    for j, task in tasks[f'✓{freq}'].iterrows():  # ✅ completate
                        colss = st.columns([5, 1, 1])
                        text = ('' if freq == 'Azi' else f"({task['timp']}) ") + f"{task['nume']}"
                        text = f'*{text}*' if task['one_time'] else text
                        colss[0].checkbox(f'~~{text}~~', value=True, on_change=utils.check_task,
                                          args=(False, task['nume'], freq, task['timp']), help=task['info'],
                                          key=f'check_{freq}_{task["nume"]}_{task["timp"]}')
                        colss[1].button('✏️', key=f'edit_{freq}_{task["nume"]}_{task["timp"]}', on_click=utils.edit_dialog,
                                        args=(task['nume'], freq, task['timp'], task['info'], task['one_time']))
                        colss[2].button('❌', key=f'del_{freq}_{task["nume"]}_{task["timp"]}', on_click=utils.delete_task,
                                        args=(task['nume'], freq, task['timp']))

    # freq_text = f'{freq} ({utils.WEEKDAYS[utils.dt.now().date().weekday()]} {utils.dt.now().date().strftime("%d%b")})' if freq == 'Azi' else freq
    # cols[i].button(f'➕{" ‎ "*2}{freq_text}', key=f'{freq}+', on_click=utils.add_dialog, args=(freq,))
    #
    # if not freq in tasks.keys():
    #     continue
    #
    # for j, row in tasks[freq].iterrows():
    #     colss = cols[i].columns([5, 1, 1])
    #     text = f"{row['nume']}" + ('' if freq == 'Azi' else f" ({row['timp']})")
    #     colss[0].checkbox(text, value=row['completed'], on_change=utils.check_task,
    #                       args=(True, row['nume'], freq, row['timp']), help=row['info'])
    #     colss[1].button('✏️', key=f'edit_{freq}_{row["nume"]}', on_click=utils.edit_dialog,
    #                     args=(row['nume'], freq, row['timp'], row['info']))
    #     colss[2].button('❌', key=f'del_{freq}_{row["nume"]}', on_click=utils.delete_task,
    #                     args=(row['nume'], freq, row['timp']))
    # cols[i].write('---')
    # for j, row in tasks[f'✓{freq}'].iterrows():    # completate
    #     colss = cols[i].columns([5, 1, 1])
    #     text = f"{row['nume']}" + ('' if freq == 'Azi' else f" ({row['timp']})")
    #     colss[0].checkbox(f"~~{text}~~", value=row['completed'], on_change=utils.check_task,
    #                       args=(False, row['nume'], freq, row['timp']), help=row['info'])
    #     colss[1].button('✏️', key=f'edit_{freq}_{row["nume"]}', on_click=utils.edit_dialog,
    #                     args=(row['nume'], freq, row['timp'], row['info']))
    #     colss[2].button('❌', key=f'del_{freq}_{row["nume"]}', on_click=utils.delete_task,
    #                     args=(row['nume'], freq, row['timp']))

if st.query_params['user'] == 'Elvin':
    st.write(f'TODAY: {utils.dt.now(utils.ZoneInfo('Europe/Bucharest'))}')   # todo remove
    st.write(f'dt.now().date(): {utils.dt.now().date()}')   # todo remove
    st.write(f'dt.now(): {utils.dt.now()}')   # todo remove
    st.write(f'dt.now() + timedelta(hours=2): {utils.dt.now() + utils.timedelta(hours=2)}')   # todo remove

# with cols[-2].expander('🎂 Aniversări', expanded=True):
#     sarbatoriti, upcoming = utils.get_birthdays()
#     if len(sarbatoriti) > 0:
#         for pers in sarbatoriti:
#             st.subheader(f"{'🎁 ' if pers['cadou'] else ''}{pers['nume']}{pers['varsta']}")
#     if len(upcoming) > 0:
#         for pers in upcoming:
#             st.markdown(f"{pers['zi']}:⠀{pers['nume']}{pers['varsta']} 🎁")
#
# with st.expander(utils.AZI.upper(), expanded=True):
#     for quest, val in utils.get_today_quests():
#         if 'x5' in quest:   # Lever, Planche
#             colss = st.columns([4, 1, 1, 1, 1, 1, 30])
#             colss[0].checkbox(quest, value=val, on_change=utils.update_quest, args=(quest,))
#             for c in range(1, 5):
#                 colss[c].checkbox(' ' * c, value=val)
#             colss[5].checkbox('', value=val, on_change=utils.update_quest, args=(quest,))
#         elif quest in ['PIEPT + TRICEPS 🏋‍', 'ABS', 'LEGS 🦿', 'UMERI 🏋', 'SPATE-BICEPS 🦾']:
#             colss = st.columns([3, 3, 3, 3, 3, 3, 3, 3, 7])
#             colss[0].checkbox(quest, value=val, on_change=utils.update_quest, args=(quest,))
#             workout = utils.get_today_workout()    # override ca arg ziua din care se vrea workoutul
#             if not val:
#                 for c in range(1, len(workout) + 1):
#                     colss[c].checkbox(f'{workout[c - 1]}')
#         else:
#             st.checkbox(quest, value=val, on_change=utils.update_quest, args=(quest,))

# movement, food = st.tabs(['🏋 Movement', '🥙 Food'])
#
# with movement:
#     st.header("A cate")
#     st.image("https://static.streamlit.io/examples/cat.jpg", width=200)
#
# with food:
#     st.header("A doge")
#     st.image("https://static.streamlit.io/examples/dog.jpg", width=200)


st_autorefresh(interval=3600000, key='dataframerefresh')  # 🔃 Refresh the page every 1h
