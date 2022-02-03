import telegram
import pandahouse
import matplotlib.pyplot as plt
import seaborn as sns
import io
from datetime import datetime


#util
#_________________________________________________________________________
def add_plot_to_media_group(media_group, data, x, y, plot_name = 'test_plot.png', add_caption = False, caption = None):
    sns.lineplot(data = data, x = x, y = y) #строим график
    plot_object = io.BytesIO() #открываем буфер
    plt.savefig(plot_object) #сохраняем график в буфер
    plot_object.name = plot_name #называем файл
    plot_object.seek(0) #?
    plt.close() #закрываем график
    
    if add_caption:
        media_group.append(telegram.InputMediaPhoto(plot_object, caption = caption)) 
    else:
        media_group.append(telegram.InputMediaPhoto(plot_object)) #caption только для первого
        
    return(media_group)



#initiating bot
#_________________________________________________________________________

bot = telegram.Bot(token='5252171555:AAGaUq6yiM5XCJ8t2GFPdrEPvtjZwZQVleg')
chat_id = 329018735

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
add_plot_to_media_group(media_group, df, 'day', 'DAU', plot_name = 'dau_plot.png', add_caption = True, caption = text)
add_plot_to_media_group(media_group, df, 'day', 'view', plot_name = 'view_plot.png')
add_plot_to_media_group(media_group, df, 'day', 'like', plot_name = 'like_plot.png')
add_plot_to_media_group(media_group, df, 'day', 'CTR', plot_name = 'CTR_plot.png')
bot.send_media_group(chat_id = chat_id, media = media_group)
