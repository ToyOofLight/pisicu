import streamlit as st

import utils

css = '''<style>
    p {font-size: 25px!important;}
    label[data-baseweb="checkbox"] span {width:2rem;height:2rem;}
    .stMainBlockContainer {padding:0 20px}
    .stAppHeader, ._container_gzau3_1, ._viewerBadge_nim44_23 {display: none;}
    
#     [data-testid="StyledLinkIconContainer"] {left:0; width:100%;}
#     [data-testid="StyledLinkIconContainer"] span {margin-left:0;}
#     [data-testid="StyledLinkIconContainer"] a {display: none;}
#     h3 [data-testid="stHeaderActionElements"] {display :none;}
#     .stMainBlockContainer { padding-top:0; }
#
#     div.stButton > button:first-child { border: none; background-color: transparent; }
#     .stColumn button p { font-size: 20px; }
#     button:focus-visible { box-shadow:none!important; }
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

tasks = utils.get_tasks()
timp_prev = ''
tabs = st.tabs(['Azi + Zilnic', 'Săptămânal + Lunar', 'Anual'])

for t in range(len(tabs)):
    with tabs[t]:
        cols = st.columns(2 if t != 2 else 1)
        interval = slice(0, 2) if t == 0 else slice(2, 4) if t == 1 else slice(4, 5)
        for i, freq in enumerate(utils.FRECVENTE[interval]):
            colss = cols[i].columns([1, 6])
            freq_text = f'{freq} ({utils.WEEKDAYS[utils.TODAY.weekday()]} {utils.TODAY.strftime("%d%b")})' if freq == 'Azi' else freq
            colss[0].button('➕', key=f'{freq}+', on_click=utils.add_dialog, args=(freq,))
            procent = 0 if tasks[freq].empty else int(len(tasks[f'✓{freq}']) * 100 / (len(tasks[freq]) + len(tasks[f'✓{freq}'])))
            colss[1].subheader(f'{freq_text} [{procent}%]')
            cols[i].progress(procent)

            if freq not in tasks.keys():
                continue

            for j, task in tasks[freq].iterrows():
                if freq in ['Săptămânal', 'Anual']:
                    timp = ''.join([c for c in task['timp'] if not c.isnumeric()]) if freq == 'Anual' else task['timp']
                    titlu = utils.LUNI[timp] if freq == 'Anual' else timp
                    if not timp_prev:
                        timp_prev = timp
                        colss = cols[i].columns([1, 5])
                        cols[i].markdown(f"#### {titlu}")
                    elif timp != timp_prev:
                        colss = cols[i].columns([1, 5])
                        cols[i].markdown(f"#### {titlu}")
                        timp_prev = timp

                colss = cols[i].columns([5, 1, 1])
                text = ('' if freq in ['Azi', 'Săptămânal'] else f"({task['timp']}) ") + f"{task['nume']}"
                colss[0].checkbox(text, value=task['completed'], on_change=utils.check_task,
                                  args=(True, task['nume'], freq, task['timp']), help=task['info'])
                colss[1].button('✏️', key=f'edit_{freq}_{task["nume"]}_{task["timp"]}', on_click=utils.edit_dialog,
                                args=(task['nume'], freq, task['timp'], task['info']))
                colss[2].button('❌', key=f'del_{freq}_{task["nume"]}_{task["timp"]}', on_click=utils.delete_task,
                                args=(task['nume'], freq, task['timp']))

            cols[i].write('---')
            for j, task in tasks[f'✓{freq}'].iterrows():  # ✅ completate
                colss = cols[i].columns([5, 1, 1])
                text = ('' if freq == 'Azi' else f"({task['timp']}) ") + f"{task['nume']}"
                colss[0].checkbox(f'~~{text}~~', value=task['completed'], on_change=utils.check_task,
                                  args=(False, task['nume'], freq, task['timp']), help=task['info'])
                colss[1].button('✏️', key=f'edit_{freq}_{task["nume"]}_{task["timp"]}', on_click=utils.edit_dialog,
                                args=(task['nume'], freq, task['timp'], task['info']))
                colss[2].button('❌', key=f'del_{freq}_{task["nume"]}_{task["timp"]}', on_click=utils.delete_task,
                                args=(task['nume'], freq, task['timp']))

    # freq_text = f'{freq} ({utils.WEEKDAYS[utils.TODAY.weekday()]} {utils.TODAY.strftime("%d%b")})' if freq == 'Azi' else freq
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

utils.reset_tasks()

st.write(f'TODAY: {utils.dt.now(utils.ZoneInfo('Europe/Bucharest'))}')   # todo remove
st.write(f'TODAY: {utils.TODAY}')   # todo remove
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
