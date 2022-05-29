from django.db import models
from django.contrib.auth.models import User
from datetime import date, timedelta
from PIL import Image
from tinymce.models import HTMLField



class CarModel(models.Model):
    make = models.CharField('marke', max_length=200)
    model = models.CharField('modelis', max_length=200)
    year = models.IntegerField('pagaminimo metai', default=1997)
    engine = models.CharField('variklis', max_length=200, default='super variklis')
    
    def __str__(self):
        return f'{self.make} {self.model} {self.year}'


    class Meta:
        verbose_name = 'Automobilio modelis'
        verbose_name_plural = 'Automobilių modeliai'

class Car(models.Model):
    plate_nr = models.CharField('Valstybinis numeris', max_length=20, help_text='įrašykite automobilio valstybini numerį')
    car_model = models.ForeignKey(CarModel, on_delete=models.SET_NULL, null=True, related_name='cars', verbose_name='automobilis')
    vin_code = models.CharField('VIN kodas', max_length=17, help_text='įrašykite automobilio 17 simbolių VIN kodą')
    client = models.CharField('kliento vardas', max_length=200)
    picture = models.ImageField('Automobilis', upload_to='carservice/pictures', null=True)
    description = HTMLField(null=True, blank=True)


    def __str__(self):
        return self.plate_nr


    class Meta:
        verbose_name = 'Automobilis'
        verbose_name_plural = 'Automobiliai'


class Order(models.Model):
    date = models.CharField('Uzsakymo data', max_length=10)
    due_back = models.DateField('Uzsakymo įvykdymo data', max_length=10, null=True, blank=True)
    car = models.ForeignKey(Car, on_delete=models.SET_NULL, null=True, related_name='masinos', verbose_name='masina')
    sum_total = models.DecimalField('kaina', decimal_places=2, max_digits = 12)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders', verbose_name='savininkas')

    ORDER_STATUS = (
        ('g', 'gautas'),
        ('p', 'pradetas vykdyti'),
        ('b', 'baigtas'),
        ('s', 'sustabdytas'),
    )
    status = models.CharField('statusas', max_length=1, choices=ORDER_STATUS, blank=True, default='a', db_index=True)

    def __str__(self):
            return f'Uzsakymas gautas - {self.date} {self.car} uz {self.sum_total} eur is {self.owner} ir bus ivykdytas {self.due_back}'

    def display_services(self):
        return ', '.join(str(order_line.service) for order_line in self.order_lines.all()[:3])
    display_services.short_description = 'Paslaugos'

    def display_order_lines(self):
        return 

    @property
    def is_overdue(self):
        if self.due_back and date.today() > self.due_back:
            return True
        return False

    class Meta:
        verbose_name = 'Užsakymas'
        verbose_name_plural = 'Užsakymai'


class Service(models.Model):
    name = models.CharField('pavadinimas', max_length=200)
    price = models.DecimalField('kaina', decimal_places=2, max_digits = 6)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Paslauga'
        verbose_name_plural = 'Paslaugos'

class OrderLine(models.Model):
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, related_name='order_lines', verbose_name='uzsakymo eilute')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, related_name='order_lines', verbose_name='uzsakymas')
    quantity = models.IntegerField('kiekis')
    price = models.DecimalField('kaina', decimal_places=2, max_digits = 8) 

    def __str__(self):
        return f'{self.service} {self.order}. kiekis - {self.quantity}, kaina - {self.price}'


    class Meta:
        verbose_name = 'užsakymo eilutė'
        verbose_name_plural = 'užsakymų eilutės'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    picture = models.ImageField(default="default.png", upload_to="profile_pics")

    def __str__(self):
        return f"{self.user.username} profilis"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = Image.open(self.picture.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.picture.path)

