from django.db import models
from django.contrib.auth.models import User
from datetime import date, timedelta
from PIL import Image
from tinymce.models import HTMLField
from django.utils.translation import gettext_lazy as _



class CarModel(models.Model):
    make = models.CharField(_('marke'), max_length=200)
    model = models.CharField(_('modelis'), max_length=200)
    year = models.IntegerField(_('pagaminimo metai'), default=1997)
    engine = models.CharField(_('variklis'), max_length=200, default=_('super variklis'))
    
    def __str__(self):
        return _('{} {} {}').format(self.make, self.model, self.year)


    class Meta:
        verbose_name = _('Automobilio modelis')
        verbose_name_plural = _('Automobilių modeliai')

class Car(models.Model):
    plate_nr = models.CharField(_('Valstybinis numeris'), max_length=20, help_text=_('įrašykite automobilio valstybini numerį'))
    car_model = models.ForeignKey(CarModel, on_delete=models.SET_NULL, null=True, related_name='cars', verbose_name=_('automobilis'))
    vin_code = models.CharField(_('VIN kodas'), max_length=17, help_text=_('įrašykite automobilio 17 simbolių VIN kodą'))
    client = models.CharField(_('kliento vardas'), max_length=200)
    picture = models.ImageField(_('Automobilis'), upload_to='carservice/pictures', null=True)
    description = HTMLField(null=True, blank=True)


    def __str__(self):
        return self.plate_nr


    class Meta:
        verbose_name = _('Automobilis')
        verbose_name_plural = _('Automobiliai')


class Order(models.Model):
    date = models.CharField(_('Uzsakymo data'), max_length=10)
    due_back = models.DateField(_('Uzsakymo įvykdymo data'), max_length=10, null=True, blank=True)
    car = models.ForeignKey(Car, on_delete=models.SET_NULL, null=True, related_name='masinos', verbose_name=_('masina'))
    sum_total = models.DecimalField(_('kaina'), decimal_places=2, max_digits = 12)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders', verbose_name=_('savininkas'))

    ORDER_STATUS = (
        ('g', _('gautas')),
        ('p', _('pradetas vykdyti')),
        ('b', _('baigtas')),
        ('s', _('sustabdytas')),
    )
    status = models.CharField(_('statusas'), max_length=1, choices=ORDER_STATUS, blank=True, default='a', db_index=True)

    def __str__(self):
            return _('Uzsakymas gautas - {} {} uz {} eur is {} ir bus ivykdytas {}').format(self.date, self.car, self.sum_total, self.owner, self.due_back)

    def display_services(self):
        return ', '.join(str(order_line.service) for order_line in self.order_lines.all()[:3])
    display_services.short_description = _('Paslaugos')

    def display_order_lines(self):
        return 

    @property
    def is_overdue(self):
        if self.due_back and date.today() > self.due_back:
            return True
        return False

    class Meta:
        verbose_name = _('Užsakymas')
        verbose_name_plural = _('Užsakymai')


class Service(models.Model):
    name = models.CharField(_('pavadinimas'), max_length=200)
    price = models.DecimalField(_('kaina'), decimal_places=2, max_digits = 6)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = _('Paslauga')
        verbose_name_plural = _('Paslaugos')

class OrderLine(models.Model):
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, related_name='order_lines', verbose_name=_('uzsakymo eilute'))
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, related_name='order_lines', verbose_name=_('uzsakymas'))
    quantity = models.IntegerField(_('kiekis'))
    price = models.DecimalField(_('kaina'), decimal_places=2, max_digits = 8) 

    def __str__(self):
        return _('{} {}. kiekis - {}, kaina - {}').format(self.service, self.order, self.quantity, self.price)


    class Meta:
        verbose_name = _('užsakymo eilutė')
        verbose_name_plural = _('užsakymų eilutės')

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    picture = models.ImageField(default="default.png", upload_to="profile_pics")

    def __str__(self):
        return _("{} profilis").format(self.user.username)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = Image.open(self.picture.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.picture.path)

