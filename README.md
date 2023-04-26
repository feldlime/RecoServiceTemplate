## Py-Spy
Запустил цикл в 1000 итераций, который отправлял запросы на каждую "ручку", скрины [тут](https://github.com/robertzaraev/RecoServiceTemplate/tree/HW_1/py-spy).
1. Health
2. Popular
3. kNN+bm25 

Вывод: Так как популярные лейблы сразу написаны в классе, то неудивительно, что нагрузка с health примерно одинаковая. С моделью все немного интереснее, мы заранее сохраняли предикты для пользователей в csv файл, поэтому нагрузка идет на какие-то системные файлы, а также на файлы uvicorn'a.
## Sentry
Создал 3 ошибки, чтобы их трекал sentry
1. Юзер у которого id делится на 666
2. Модель не найдена
3. Слишком большой userId

Скрины [тут](https://github.com/robertzaraev/RecoServiceTemplate/tree/HW_1/sentry_pic).

## MLFlow
У меня на компьютере не ставился rectools вообще, понижал версию питона - все равно ему что-то не нравится. Док-ва [тут](https://github.com/robertzaraev/RecoServiceTemplate/blob/HW_1/mlflow/rectools1.png) и [тут](https://github.com/robertzaraev/RecoServiceTemplate/blob/HW_1/mlflow/rectools2.png). Поэтому я использовал ресурсы [GoogleColab](https://github.com/robertzaraev/RecoServiceTemplate/blob/HW_1/mlflow/knnfinal.ipynb) и [DataBricks](https://github.com/robertzaraev/RecoServiceTemplate/blob/HW_1/mlflow/metrics/Вся%20информация%20о%20эксперименте.png) для того, чтобы трекать эксперименты.
1. Три метрики лучшей модели - [map@10](https://github.com/robertzaraev/RecoServiceTemplate/blob/HW_1/mlflow/metrics/map%4010.png), [precision@10](https://github.com/robertzaraev/RecoServiceTemplate/blob/HW_1/mlflow/metrics/precision.png), [recall@10](https://github.com/robertzaraev/RecoServiceTemplate/blob/HW_1/mlflow/metrics/recall.png).
2. Продолжительная метрика: я использовал kNN, поэтому изменение метрик считал по мере увеличения соседей.
3. Техническая метрика: 
- считал [вес](https://github.com/robertzaraev/RecoServiceTemplate/blob/HW_1/mlflow/metrics/weight_mb.png) каждой модели, по мере увеличения кол-ва соседей
- считал [время обучения](https://github.com/robertzaraev/RecoServiceTemplate/blob/HW_1/mlflow/metrics/learning_time.png)
- считал [время затрачиваемое на рекомендации](https://github.com/robertzaraev/RecoServiceTemplate/blob/HW_1/mlflow/metrics/recos_time.png)
4. В конце ноутбука представлены примеры экспериментов + скачал лучшую модель, ноутбук [тут](https://github.com/robertzaraev/RecoServiceTemplate/blob/HW_1/mlflow/knnfinal.ipynb).
5. Я развернул локально MLFlow, но локально затрекать эксперименты не смог из-за выше указанной причины. Прикладываю docker-compose и [скрин](https://github.com/robertzaraev/RecoServiceTemplate/blob/HW_1/mlflow/docker-localhost.png).
