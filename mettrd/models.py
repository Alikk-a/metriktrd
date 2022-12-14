from django.db import models

# Create your models here.

class Graph(models.Model):
    name = models.CharField(max_length=85, blank=True, verbose_name='Заголовок метрики')
    subname = models.CharField(max_length=83, blank=True, verbose_name='подзаголовок')
    file_name = models.CharField(max_length=50, blank=True, verbose_name='Файл данных')
    variable = models.CharField(max_length=50, blank=True, verbose_name='Переменная данных')
    ID_out = models.CharField(max_length=50, blank=True, verbose_name='ID_div для вывода')
    tagsmet = models.CharField(max_length=83, blank=True, verbose_name='Переключатели вида - набор - через ,')
    slider = models.IntegerField(blank=True, verbose_name='Слайдер вкл/выкл', null=True)
    barline = models.CharField(max_length=10, blank=True, verbose_name='тип Bar - bar, Line - scatter')
    laycolor = models.CharField(max_length=12, blank=True, verbose_name='Цвет фона графика')
    barmode = models.CharField(max_length=10, blank=True, verbose_name='Тип Bar - пусто  overlay  stack')
    rangestart = models.CharField(max_length=10, blank=True, verbose_name='Дата начала в формате строки 2021-05-01')

    class Meta:
        verbose_name = 'Метрики'
        verbose_name_plural = 'Метрики базовые'

    def __str__(self):
        return self.name

class Page(models.Model):
    metric = models.ForeignKey('Graph', on_delete=models.PROTECT, verbose_name='Метрика', null=True)
    id_page = models.IntegerField(blank=True, verbose_name='Страница - номер', null=True)
    sort = models.IntegerField(blank=True, verbose_name='сортировка', null=True)
    column = models.IntegerField(blank=True, verbose_name='колонка на странице (если одна - null', null=True)
    name_page = models.CharField(max_length=50, blank=True, verbose_name='Заголовок метрики', null=True)
    coment = models.CharField(max_length=300, blank=True, verbose_name='Коментарий к графику', null=True)

    class Meta:
        verbose_name ='Метрики на страницы'
        verbose_name_plural ='Вывод метрик на страницу'

    def __str__(self):
        return self.name_page

class Tranzact(models.Model):
    symbol = models.CharField(max_length=10, blank=False, verbose_name='Монета', null=True)
    id_trz = models.IntegerField(verbose_name='ID alert', null=True)
    time_trz = models.IntegerField(verbose_name='Время', null=True)
    amount = models.FloatField(verbose_name='Кол-во', null=True)
    amount_usd = models.FloatField(verbose_name='Кол-во', null=True)
    blockchain = models.CharField(max_length=20, verbose_name='blockchain', null=True)
    transaction_type = models.CharField(max_length=20, verbose_name='transaction_type', null=True)
    from_owner_type = models.CharField(max_length=20, verbose_name='From тип', null=True)
    to_owner_type = models.CharField(max_length=20, verbose_name='To тип', null=True)
    from_owner = models.CharField(max_length=20, verbose_name='From биржа', null=True)
    to_owner = models.CharField(max_length=20, verbose_name='To биржа', null=True)
    from_address = models.CharField(max_length=100, verbose_name='From адрес', null=True)
    to_address = models.CharField(max_length=100, verbose_name='To адрес', null=True)
    hash = models.CharField(max_length=100, verbose_name='hash', null=True)
    transaction_count = models.IntegerField(verbose_name='transaction_count', null=True)
    date_trz = models.DateTimeField(verbose_name='Время транз', blank=True)

    class Meta:
        verbose_name='Транзакции с Алерта'
        verbose_name_plural='Транзакции с Алерта'

    def amountRound(self):
        return round(self.amount)

    def amountusdRound(self):
        return round(self.amount_usd)

    def __str__(self):
        return self.hash

class Cursor(models.Model):
    cursorapi = models.CharField(max_length=35, blank=False, verbose_name='Курсор запроса')
    resultapi = models.CharField(max_length=12, verbose_name='результат', null=True)
    timeapi = models.DateTimeField(verbose_name='Время запроса', blank=True)
    countapi = models.IntegerField(verbose_name='кол-во полученных записей', blank=True, null=True)

    class Meta:
        verbose_name='Курсор с Алерт'
        verbose_name_plural='Курсор с Алерт'

    def __str__(self):
        return self.cursorapi


class City(models.Model):
    name = models.CharField(max_length=50, verbose_name='Наме городища')
    slug = models.CharField(max_length=50, blank=True, verbose_name='Slug он и ест slug')

    class Meta:
        verbose_name='Наме городища'
        verbose_name_plural='Наме городища'

    def __str__(self):
        return self.name

class Post(models.Model):
    image = models.ImageField(upload_to='event_images/')
    title = models.CharField(max_length=300, verbose_name='Наме поста')
    date = models.DateTimeField()
    text = models.TextField()

    class Meta:
        verbose_name='Наме статейки'
        verbose_name_plural='Наме стат'

    def get_summary(self):
        return self.text[:90]

    def __str__(self):
        return self.title


