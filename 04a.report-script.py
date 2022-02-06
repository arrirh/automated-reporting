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

q = \
"select toStartOfDay(toDateTime(time)) as day, \
        count(distinct user_id) as DAU, \
        countIf(action = 'view') as view, \
        countIf(action = 'like') as like, \
        like/view as CTR \
FROM simulator_20220120.feed_actions \
where time >= dateadd(day, -7, toDate(now())) and time < toDate(now()) \
group by day \
order by day"

df = pandahouse.read_clickhouse(q, connection=connection)

#Yesterday metrics
#_________________________________________________________________________

date = str(df.day.iloc[-1]).split()[0]
dau = df.DAU.iloc[-1]
view = df.view.iloc[-1]
like = df.like.iloc[-1]
ctr = round(df.CTR.iloc[-1]*100, 3)

text = f'Отчет за предыдущий день ({date}): \n DAU: {dau} пользователей \n Количество просмотров: {view} \n Количество лайков: {like} \n CTR = {ctr}%'

#Making report and sending
#_________________________________________________________________________
media_group = []
text = text = f'Отчет за предыдущий день ({date}): \n DAU: {dau} пользователей \n Количество просмотров: {view} \n Количество лайков: {like} \n CTR = {ctr}%'
add_plot_to_media_group(media_group, df, x = 'day', y = 'DAU', xlab = 'День', ylab = 'DAU', plot_title = 'DAU за последние 7 дней', plot_name = 'dau_plot.png', add_caption = True, caption = text)
add_plot_to_media_group(media_group, df, x = 'day', y = 'view', xlab = 'День', ylab = 'Кол-во просмотров', plot_title = 'Кол-во просмотров за последние 7 дней', plot_name = 'view_plot.png')
add_plot_to_media_group(media_group, df, x = 'day', y = 'like', xlab = 'День', ylab = 'Кол-во лайков', plot_title = 'Кол-во лайков за последние 7 дней', plot_name = 'like_plot.png')
add_plot_to_media_group(media_group, df, x = 'day', y = 'CTR', xlab = 'День', ylab = 'CTR', plot_title = 'CTR за последние 7 дней', plot_name = 'CTR_plot.png')
bot.send_media_group(chat_id = chat_id, media = media_group)
