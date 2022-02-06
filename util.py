import telegram
import pandahouse
import matplotlib.pyplot as plt
import seaborn as sns
import io

def add_plot_to_media_group(media_group, data, x, y, xlab, ylab, plot_title,
                            plot_name = 'test_plot.png', add_caption = False, figsize = (7, 5.5), add_legend = False, 
                            hue = None, legend_title = None, legend_labels = None, caption = None):
    fig, ax = plt.subplots(figsize = figsize)
    sns.lineplot(ax = ax, data = data, x = x, y = y, hue = hue, ci = None, marker = 'o') #строим график
    plt.xticks(rotation=45)
    plt.xlabel(xlab)
    plt.ylabel(ylab)
    if add_legend:
        plt.legend(title = legend_title, labels = legend_labels)
    plt.title(plot_title)
    
    plot_object = io.BytesIO() #открываем буфер
    plt.savefig(plot_object, bbox_inches = 'tight') #сохраняем график в буфер
    plot_object.name = plot_name #называем файл
    plot_object.seek(0) #?
    plt.close() #закрываем график
    
    if add_caption:
        media_group.append(telegram.InputMediaPhoto(plot_object, caption = caption)) #caption только для первого
    else:
        media_group.append(telegram.InputMediaPhoto(plot_object))
        
    return(media_group)