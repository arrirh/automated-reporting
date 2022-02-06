import telegram
import pandahouse
import matplotlib.pyplot as plt
import seaborn as sns
import io
from datetime import datetime

from util import add_plot_to_media_group

#initiating bot
#_________________________________________________________________________

bot = telegram.Bot(token='5181637517:AAEMTMNyqIEjMlr7HKAgPA1OnnoFiw_wf58')
chat_id = -727662986

#connection to database
#_________________________________________________________________________

connection = {
    'host': 'https://clickhouse.lab.karpov.courses',
    'password': 'dpo_python_2020',
    'user': 'student',
    'database': 'simulator'
}


#Query for feed and message users
#_________________________________________________________________________

q = \
"SELECT toStartOfDay(toDateTime(time)) as day, count(distinct user_id) as users, f_m \
FROM\
(\
    select *, multiIf(\
            uses_feed == 1 and uses_message == 0, 'Feed',\
            uses_feed == 1 and uses_message == 1, 'Feed and message',\
            uses_feed == 0 and uses_message == 1, 'Message',\
            'none'\
        ) as f_m\
    from \
    (select f.*, if(f.user_id = 0, 0, 1) as uses_feed, if(m.user_id = 0, 0, 1) as uses_message\
    from\
    simulator_20220120.feed_actions f\
    FULL OUTER join\
    simulator_20220120.message_actions m\
    on f.user_id = m.user_id\
    where time >= dateadd(day, -7, toDate(now())) and time < toDate(now())\
    )\
)\
group by f_m, toStartOfDay(toDateTime(time))\
order by f_m, toStartOfDay(toDateTime(time))"

df = pandahouse.read_clickhouse(q, connection=connection)


#Yesterday metrics
#_________________________________________________________________________

date = str(df.day.iloc[-1]).split()[0]
date_for_indexing = df.day == df.day.iloc[-1]

only_feed_users = int(df.users[df.f_m == 'Feed'][date_for_indexing])
feed_message_users = int(df.users[df.f_m == 'Feed and message'][date_for_indexing])

if len(df.users[df.f_m == 'Message'][date_for_indexing]) == 0:
    only_message_users = 0
    legend_labels = ['Только ленты', 'И ленты, и мессенджера']
else:
    only_message_users = int(df.users[df.f_m == 'Message'][date_for_indexing])
    legend_labels = ['Только ленты', 'И ленты, и мессенджера', 'Только мессенджера']
    
#Creating draft for report
#_________________________________________________________________________
text = f'Отчет по работе всего приложения за предыдущий день ({date}):\nПользователи только ленты - {only_feed_users}, \nПользователи и ленты, и мессенджера - {feed_message_users}, \nПользователи только мессенджера - {only_message_users}'
media_group = []

#Adding first plot to list
#_________________________________________________________________________

add_plot_to_media_group(media_group, data = df, x = 'day', y = 'users', xlab = 'День', ylab = 'Количество пользователей', plot_title = 'Количество пользователей ленты и мессенджера',
                            plot_name = 'feed_message_users.png', add_caption = True, figsize = (9, 7), add_legend = True, 
                            hue = 'f_m', legend_title = 'Использование', legend_labels = legend_labels, caption = text)


#Query for all actions
#_________________________________________________________________________

q = \
"select toStartOfDay(toDateTime(time)) AS day, \
        count(*) as num, action \
from simulator_20220120.feed_actions  \
where time >= dateadd(day, -7, toDate(now())) and time < toDate(now())  \
group by day, action \
order by action, day \
\
union all \
\
select toStartOfDay(toDateTime(time)) AS day, count(user_id) AS num, 'message' as action \
from simulator_20220120.message_actions \
where time >= dateadd(day, -7, toDate(now())) and time < toDate(now()) \
group by day"

df = pandahouse.read_clickhouse(q, connection=connection)

#Adding second plot to list
#_________________________________________________________________________

add_plot_to_media_group(media_group, data = df, x = 'day', y = 'num', xlab = 'День', ylab = 'Количество', plot_title = 'Количество действий за день',
                            plot_name = 'all_actions.png', add_caption = True, figsize = (7, 8.5), add_legend = True, 
                            hue = 'action', legend_title = 'Действие', legend_labels = ['Лайк', 'Просмотр', 'Сообщение'])

#Sending plots
#_________________________________________________________________________

bot.send_media_group(chat_id = chat_id, media = media_group)


#Query for top 25 posts
#_________________________________________________________________________

q = "SELECT post_id AS post_id, \
       countIf(action = 'view') AS view, \
       countIf(action = 'like') AS like, \
       countIf(action = 'like')/countIf(action = 'view') AS CTR, \
       count(DISTINCT user_id) AS reach \
FROM simulator_20220120.feed_actions \
GROUP BY post_id \
ORDER BY view DESC \
LIMIT 25"

df = pandahouse.read_clickhouse(q, connection=connection)

file_object = io.StringIO()
df.to_csv(file_object)
file_object.seek(0)
file_object.name = 'top_25_posts.csv'

bot.sendDocument(chat_id = chat_id, document = file_object)