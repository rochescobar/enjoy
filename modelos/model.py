# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo import tools, _
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError, Warning
from odoo.modules.module import get_module_resource

from datetime import date, datetime
import time
import logging

_logger = logging.getLogger(__name__)


# ------------------------------------------------Modelos Locales-------------------------------------------------------
# class Users(models.Model):
#     _name = "res.users"
#     _inherit = "res.users"
#     _description = 'Users'
#
#     comision = fields.Integer('Commission')


class Modelo(models.Model):
    _name = 'enjoy.modelo'
    _description = 'Modelo de los Autos'

    name = fields.Char('Model', size=200, required=True)
    auto_ids = fields.One2many('enjoy.auto', 'modelo_id', 'Cars')


class Place(models.Model):
    _name = 'enjoy.lugar'
    _description = 'Zonas'

    name = fields.Char('Name', size=200, required=True)
    auto_ids = fields.One2many('enjoy.auto', 'radica', 'Cars')
    casa_ids = fields.One2many('enjoy.casa', 'lugar', 'Houses')
    provincia_id = fields.Many2one('enjoy.provincia', 'Province', required=True)


class Auto(models.Model):
    _name = 'enjoy.auto'
    _description = 'Autos'

    name = fields.Char('Name', compute='_getnombre')
    chofer = fields.Char('Driver', size=200, required=True)
    propietario = fields.Char('Owner', size=200, required=True)
    licencia = fields.Char('License', size=11)
    modelo_id = fields.Many2one('enjoy.modelo', 'Model', required=True)
    aire = fields.Boolean('Air conditioner?')
    capacidad = fields.Integer('Capacity', required=True, default=4)
    radica = fields.Many2one('enjoy.lugar', 'Where you work', required=True)
    phone = fields.Char('Phone', size=50, required=True)
    tarjeta = fields.Char('Card', size=200)
    viaje_ids = fields.One2many('enjoy.viaje', 'auto_id', 'Travels')

    @api.one
    @api.depends('chofer', 'modelo_id.name')
    def _getnombre(self):
        self.name = "%s - %s" % (self.chofer, self.modelo_id.name)


class Travel(models.Model):
    _name = 'enjoy.viaje'
    _description = 'Travels de los Autos'

    name = fields.Char('Name', compute='_getnombre')
    origen = fields.Many2one('enjoy.lugar', 'From', required=True)
    destino = fields.Many2one('enjoy.lugar', 'To', required=True)
    precio = fields.Integer('Price', required=True)
    auto_id = fields.Many2one('enjoy.auto', 'Car', required=True)
    capacidad = fields.Integer('Capacity', related='auto_id.capacidad', store=True)
    phone = fields.Char('Phone', related='auto_id.phone', store=True)
    aire = fields.Boolean('A/C', related='auto_id.aire', store=True)
    transfer_ids = fields.One2many('enjoy.transfer', 'viaje_id', 'Transfer')

    @api.one
    @api.depends('origen', 'destino', 'auto_id')
    def _getnombre(self):
        self.name = "%s - %s: (%s)" % (self.origen.name, self.destino.name, self.auto_id.name)

    @api.constrains('origen', 'destino')
    def _check_duration(self):
        if self.origen == self.destino:
            raise ValueError("Origin and destination must not coincide")

    _sql_constraints = [
        ('key_unique', 'UNIQUE(origen, destino, auto_id)', "There are repeated trips"),
    ]


class Transfer(models.Model):
    _name = 'enjoy.transfer'
    _description = 'Transfers '

    viaje_id = fields.Many2one('enjoy.viaje', 'Travel', required=True)
    precio = fields.Integer('Final Cost', required=True)
    utilidad = fields.Integer('Utilities', compute='_calc_value')
    fecha = fields.Date('Date', required=True, default=date.today())
    auto_precio = fields.Integer('Travel cost', related='viaje_id.precio', store=True)

    @api.one
    @api.depends('precio', 'viaje_id.precio')
    def _calc_value(self):
        if self.precio:
            self.utilidad = self.precio - self.viaje_id.precio


class Traslado(models.Model):
    _name = 'enjoy.traslado'
    _description = 'Traslado '

    name = fields.Selection([('t', 'Transfer'), ('l', 'Local')], 'Tipo de Travel', required=True)
    origen = fields.Many2one('enjoy.lugar', 'From', required=True)
    destino = fields.Many2one('enjoy.lugar', 'To', required=True)
    van4 = fields.Integer('Van 4-7 places', required=True, default=0)
    van8 = fields.Integer('Van 8-10 places', required=True, default=0)
    van11 = fields.Integer('Van 11 places or more', required=True, default=0)
    van3 = fields.Integer('They go to 3 places', required=True, default=0)
    tablilla_id = fields.Many2one('enjoy.tablilla', 'Clapboard', required=True)


class Diario(models.Model):
    _name = 'enjoy.diario'
    _description = 'Diario '

    name = fields.Char('Place', size=200, required=True)
    van4 = fields.Integer('Van 4-7 places', required=True, default=0)
    van8 = fields.Integer('Van 8-10 places', required=True, default=0)
    van11 = fields.Integer('Van 11 places or more', required=True, default=0)
    van3 = fields.Integer('They go to 3 places', required=True, default=0)
    tablilla_id = fields.Many2one('enjoy.tablilla', 'Clapboard', required=True)
    condicion_id = fields.Many2one('enjoy.condicion', 'Condition')


class Condicion(models.Model):
    _name = 'enjoy.condicion'
    _description = 'Condicion '

    name = fields.Char('Identifier', size=200, required=True, default='* ')
    descrip = fields.Text('Description', required=True)
    tablilla_id = fields.Many2one('enjoy.tablilla', 'Clapboard', required=True)


class Clapboard(models.Model):
    _name = 'enjoy.tablilla'
    _description = 'Clapboard '

    name = fields.Char('Name', size=200, required=True, default='Clapboard de Renta')
    traslado_ids = fields.One2many('enjoy.traslado', 'tablilla_id', 'Transfers')
    diario_ids = fields.One2many('enjoy.diario', 'tablilla_id', 'Rent per day')
    condicion_ids = fields.One2many('enjoy.condicion', 'tablilla_id', 'Conditions')


# modulo de casa
class Cama(models.Model):
    _name = 'enjoy.cama'
    _description = 'Registro de cama '

    cantidad = fields.Integer('Quantity', required=True, default=1)
    tipo = fields.Selection([('p', 'Personal'), ('m', 'Matrimonial'), ('em', 'Extra Matrimonial')], 'Tipo',
                            required=True)
    casa_id = fields.Many2one('enjoy.casa', 'House', required=True, ondelete='cascade')

    # @api.constrains('tipo', 'casa_id')
    # def _check_duration(self):
    #     if len(self.gastos_corrientes_ids) > 1:
    #         raise ValueError("Solo se admite un Gasto Corriente por año")

    _sql_constraints = [
        ('key_unique', 'UNIQUE(casa_id, tipo)', "There are repeated bed types"),
    ]


class Banno(models.Model):
    _name = 'enjoy.banno'
    _description = 'Registro de Bannos'

    cantidad = fields.Integer('Quantity', required=True, default=1)
    tipo = fields.Selection([('p', 'Private'), ('c', 'Shared')], 'Tipo', required=True)
    casa_id = fields.Many2one('enjoy.casa', 'House', required=True, ondelete='cascade')

    _sql_constraints = [
        ('key_unique', 'UNIQUE(casa_id, tipo)', "There are repeated types of baths"),
    ]


class Servicio(models.Model):
    _name = 'enjoy.servicio'
    _description = 'Registro de Servicios '

    name = fields.Char('Name', size=200, required=True)
    image = fields.Binary("Photo", attachment=True)
    casa_id = fields.Many2many('enjoy.casa', string='House')


class Zona(models.Model):
    _name = 'enjoy.zona'
    _description = 'Registro de Zona '

    name = fields.Char('Name', size=200, required=True)
    casa_id = fields.Many2many('enjoy.casa', string='House')


class Comision(models.Model):
    _name = 'enjoy.comision'
    _description = 'Precio de venta de casa por Vendedor'

    comision = fields.Integer('Commission', required=True, default=0)
    casa_id = fields.Many2one('enjoy.casa', 'House name', required=True, ondelete='cascade')
    user_id = fields.Many2one('res.users', 'Responsable', default=lambda self: self.env.user)
    precio = fields.Integer('House price', compute='_getprecio')

    @api.one
    @api.depends('casa_id')
    def _getprecio(self):
        self.precio = self.casa_id.precio

    _sql_constraints = [
        ('comis_unique', 'UNIQUE(casa_id, user_id)', "Existen comisiones repetidas"),
    ]


class Province(models.Model):
    _name = 'enjoy.provincia'
    _description = 'Registro de provincia'

    name = fields.Char('Name', size=100, required=True)
    lugar_ids = fields.One2many('enjoy.lugar', 'provincia_id', 'Locations')


class Catalogo(models.Model):
    _name = 'enjoy.catalogo'
    _description = 'Catalogo de casa'

    name = fields.Char('Name', compute='_getnombre')
    nombre = fields.Char('Name', size=200, required=True)
    lugar = fields.Many2one('enjoy.provincia', 'Province', required=True)
    desde = fields.Char('From', size=200, required=True)
    hasta = fields.Char('To', size=200, required=True)
    casa_ids = fields.Many2many('enjoy.casa', 'enjoy_catalogo_casa', 'catalogo_id', 'casa_id', 'Houses and apartments')

    @api.one
    @api.depends('nombre', 'lugar', 'desde', 'hasta')
    def _getnombre(self):
        self.name = "%s: %s (%s - %s)" % (self.nombre, self.lugar.name, self.desde, self.hasta)


class House(models.Model):
    _name = 'enjoy.casa'
    _description = 'Registro de casa '

    @api.model
    def _default_image(self):
        image_path = get_module_resource('enjoy', 'static/src/img', 'casa.jpg')
        return tools.image_resize_image_big(open(image_path, 'rb').read().encode('base64'))

    propiedad = fields.Char('Property of', size=200, required=True)
    name = fields.Char('Property Name ', size=200, required=True)
    dir = fields.Text('Address', size=200)
    lugar = fields.Many2one('enjoy.lugar', 'Location')
    # catalogo_id = Many2many('enjoy.catalogo', string='Catálogos')
    provincia = fields.Char('Province', related='lugar.provincia_id.name', store=True)
    phone = fields.Char('Phone', size=50, required=True)
    alojamiento = fields.Selection([('casa', 'House'), ('apto', 'Apartment')], 'Type of accommodation',
                                   required=True)
    dispone = fields.Selection(
            [('entera', 'Entire Property'), ('privada', 'Private room'), ('compartida', 'Shared room')],
        'Dispone de', required=True)
    capacidad = fields.Integer('Number of Guests', required=True, default=4)
    dormitorios = fields.Integer('Number of Bedrooms', required=True, default=4)
    cama_ids = fields.One2many('enjoy.cama', 'casa_id', 'Types of Bed')
    comision_ids = fields.One2many('enjoy.comision', 'casa_id', 'Commissions')
    banno_ids = fields.One2many('enjoy.banno', 'casa_id', 'Number of bathrooms')
    servicio_ids = fields.Many2many('enjoy.servicio', 'enjoy_servicio_casa', 'casa_id', 'servicio_id',
                                    'Services offered')
    zona_ids = fields.Many2many('enjoy.zona', 'enjoy_zona_casa', 'casa_id', 'zona_id', 'Areas you can use')
    para = fields.Selection([('f', 'Family'), ('g', 'Groups'), ('m', 'Pets')], 'Is perfect for',
                            required=True)
    precio = fields.Integer('Precio', required=True, default=0)
    # comision = fields.Integer('Commission', required=True, default=0)
    fpago = fields.Selection([('e', 'Cash'), ('t', 'Card')], 'Way to pay', required=True)
    nivel = fields.Selection([('e', 'Economic'), ('c', 'Confort'), ('l', 'luxurious')], 'Level',
                             required=True)
    nivelx = fields.Char('Level', compute='_getnombre', store=True)

    image = fields.Binary("Photo", default=_default_image, attachment=True)
    image_lateral = fields.Binary("Side Image", default=_default_image, attachment=True)
    image_foot1 = fields.Binary("Image Below1", default=_default_image, attachment=True)
    image_foot2 = fields.Binary("Image Below2", default=_default_image, attachment=True)

    image_medium = fields.Binary("Medium-sized photo", attachment=True,
                                 help="Medium-sized photo of the employee. It is automatically "
                                      "resized as a 128x128px image, with aspect ratio preserved. "
                                      "Use this field in form views or some kanban views.")
    image_small = fields.Binary("Small-sized photo", attachment=True,
                                help="Small-sized photo of the employee. It is automatically "
                                     "resized as a 64x64px image, with aspect ratio preserved. "
                                     "Use this field anywhere a small image is required.")

    @api.one
    @api.depends('nivel')
    def _getnombre(self):
        if self.nivel == 'e':
            self.nivelx = 'Economic'
        if self.nivel == 'c':
            self.nivelx = 'Confort'
        if self.nivel == 'l':
            self.nivelx = 'luxurious'

    @api.model
    def create(self, vals):
        tools.image_resize_images(vals)
        return super(House, self).create(vals)

    @api.multi
    def write(self, vals):
        tools.image_resize_images(vals)
        return super(House, self).write(vals)

    _sql_constraints = [
        ('key_unique', 'UNIQUE(name)', "There is a house with that name"),
    ]


class Reporte(models.Model):
    _name = 'enjoy.reporte'
    _description = 'Reporte de Reservacion de la House'

    name = fields.Many2one('enjoy.casa', 'House name', required=True)
    user_id = fields.Many2one('res.users', 'Responsable', default=lambda self: self.env.user)
    fecha_inicio = fields.Date('From', required=True, default=date.today().strftime('%Y-%m-%d'))
    fecha_fin = fields.Date('To', required=True)
    cliente = fields.Char('Client', required=True, size=200)
    descrip = fields.Text('Description', size=1000)
    state = fields.Selection(
        [('Draft', 'Draft'), ('Confirmed', 'Confirmed'), ('Cancelled', 'Cancelled'), ('Done', 'Done')],
        'Estado',
        required=True, default='Draft')

    def state_borrador(self):
        self.write({'state': 'Draft'})

    def state_confirmado(self):
        self.write({'state': 'Confirmed'})

    def state_cancelado(self):
        self.write({'state': 'Cancelled'})

    def state_done(self):
        self.write({'state': 'Done'})


class Restino(models.Model):
    _name = 'enjoy.destino'
    _description = 'Tos para los Correos de los catalogo'

    name = fields.Char('Addressee', size=100, required=True)
    report_id = fields.Many2one('enjoy.report.mail', 'Reporte', required=True)
