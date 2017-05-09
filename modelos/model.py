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

class Modelo(models.Model):
    _name = 'enjoy.modelo'
    _description = 'Modelo de los Autos'

    name = fields.Char('Modelo', size=200, required=True)
    auto_ids = fields.One2many('enjoy.auto', 'modelo_id', 'Autos')


class Lugar(models.Model):
    _name = 'enjoy.lugar'
    _description = 'Zonas'

    name = fields.Char('Nombre', size=200, required=True)
    auto_ids = fields.One2many('enjoy.auto', 'radica', 'Autos')
    casa_ids = fields.One2many('enjoy.casa', 'lugar', 'Casas')
    provincia_id = fields.Many2one('enjoy.provincia', 'Provincia', required=True)


class Auto(models.Model):
    _name = 'enjoy.auto'
    _description = 'Autos'

    name = fields.Char('Nombre', compute='_getnombre')
    chofer = fields.Char('Chofer', size=200, required=True)
    propietario = fields.Char('Propietario', size=200, required=True)
    licencia = fields.Char('Licencia', size=11)
    modelo_id = fields.Many2one('enjoy.modelo', 'Modelo', required=True)
    aire = fields.Boolean('Tiene Aire Acondicionado?')
    capacidad = fields.Integer('Capacidad', required=True, default=4)
    radica = fields.Many2one('enjoy.lugar', 'Lugar donde Radica', required=True)
    phone = fields.Char('Telefono', size=50, required=True)
    tarjeta = fields.Char('Tarjeta', size=200)
    viaje_ids = fields.One2many('enjoy.viaje', 'auto_id', 'Viajes')

    @api.one
    @api.depends('chofer', 'modelo_id.name')
    def _getnombre(self):
        self.name = "%s - %s" % (self.chofer, self.modelo_id.name)


class Viaje(models.Model):
    _name = 'enjoy.viaje'
    _description = 'Viajes de los Autos'

    name = fields.Char('Nombre', compute='_getnombre')
    origen = fields.Many2one('enjoy.lugar', 'Origen', required=True)
    destino = fields.Many2one('enjoy.lugar', 'Destino', required=True)
    precio = fields.Integer('Precio', required=True)
    auto_id = fields.Many2one('enjoy.auto', 'Auto', required=True)
    capacidad = fields.Integer('Capacidad', related='auto_id.capacidad', store=True)
    phone = fields.Char('Teléfono', related='auto_id.phone', store=True)
    aire = fields.Boolean('A/C', related='auto_id.aire', store=True)
    transfer_ids = fields.One2many('enjoy.transfer', 'viaje_id', 'Transfer')

    @api.one
    @api.depends('origen', 'destino', 'auto_id')
    def _getnombre(self):
        self.name = "%s - %s: (%s)" % (self.origen.name, self.destino.name, self.auto_id.name)

    @api.constrains('origen', 'destino')
    def _check_duration(self):
        if self.origen == self.destino:
            raise ValueError("El origen y el destinos no deben cohincidir")

    _sql_constraints = [
        ('key_unique', 'UNIQUE(origen, destino, auto_id)', "Existen viajes repetidos"),
    ]


class Transfer(models.Model):
    _name = 'enjoy.transfer'
    _description = 'Transfers '

    viaje_id = fields.Many2one('enjoy.viaje', 'Viaje', required=True)
    precio = fields.Integer('Costo Final', required=True)
    utilidad = fields.Integer('Utilidades', compute='_calc_value')
    fecha = fields.Date('Fecha', required=True, default=date.today())
    auto_precio = fields.Integer('Precio del Viaje', related='viaje_id.precio', store=True)

    @api.one
    @api.depends('precio', 'viaje_id.precio')
    def _calc_value(self):
        if self.precio:
            self.utilidad = self.precio - self.viaje_id.precio


class Traslado(models.Model):
    _name = 'enjoy.traslado'
    _description = 'Traslado '

    name = fields.Selection([('t', 'Transfer'), ('l', 'Local')], 'Tipo de Viaje', required=True)
    origen = fields.Many2one('enjoy.lugar', 'Origen', required=True)
    destino = fields.Many2one('enjoy.lugar', 'Destino', required=True)
    van4 = fields.Integer('Van 4-7 plazas', required=True, default=0)
    van8 = fields.Integer('Van 8-10 plazas', required=True, default=0)
    van11 = fields.Integer('Van 11 o mas plazas', required=True, default=0)
    van3 = fields.Integer('Van hasta 3 plazas', required=True, default=0)
    tablilla_id = fields.Many2one('enjoy.tablilla', 'Tablilla', required=True)


class Diario(models.Model):
    _name = 'enjoy.diario'
    _description = 'Diario '

    name = fields.Char('Lugar', size=200, required=True)
    van4 = fields.Integer('Van 4-7 plazas', required=True, default=0)
    van8 = fields.Integer('Van 8-10 plazas', required=True, default=0)
    van11 = fields.Integer('Van 11 o mas plazas', required=True, default=0)
    van3 = fields.Integer('Van hasta 3 plazas', required=True, default=0)
    tablilla_id = fields.Many2one('enjoy.tablilla', 'Tablilla', required=True)
    condicion_id = fields.Many2one('enjoy.condicion', 'Condición')


class Condicion(models.Model):
    _name = 'enjoy.condicion'
    _description = 'Condicion '

    name = fields.Char('Identificador', size=200, required=True, default='* ')
    descrip = fields.Text('Descripción', required=True)
    tablilla_id = fields.Many2one('enjoy.tablilla', 'Tablilla', required=True)


class Tablilla(models.Model):
    _name = 'enjoy.tablilla'
    _description = 'Tablilla '

    name = fields.Char('Nombre', size=200, required=True, default='Tablilla de Renta')
    traslado_ids = fields.One2many('enjoy.traslado', 'tablilla_id', 'Traslados')
    diario_ids = fields.One2many('enjoy.diario', 'tablilla_id', 'Renta por Días')
    condicion_ids = fields.One2many('enjoy.condicion', 'tablilla_id', 'Condiciones')


# modulo de casa
class Cama(models.Model):
    _name = 'enjoy.cama'
    _description = 'Registro de cama '

    cantidad = fields.Integer('Cantidad', required=True, default=1)
    tipo = fields.Selection([('p', 'Personal'), ('m', 'Matrimonial'), ('em', 'Extra Matrimonial')], 'Tipo',
                            required=True)
    casa_id = fields.Many2one('enjoy.casa', 'Casa', required=True, ondelete='cascade')

    # @api.constrains('tipo', 'casa_id')
    # def _check_duration(self):
    #     if len(self.gastos_corrientes_ids) > 1:
    #         raise ValueError("Solo se admite un Gasto Corriente por año")

    _sql_constraints = [
        ('key_unique', 'UNIQUE(casa_id, tipo)', "Existen tipos de camas repetidos"),
    ]


class Banno(models.Model):
    _name = 'enjoy.banno'
    _description = 'Registro de Bannos'

    cantidad = fields.Integer('Cantidad', required=True, default=1)
    tipo = fields.Selection([('p', 'Privado'), ('c', 'Compartido')], 'Tipo', required=True)
    casa_id = fields.Many2one('enjoy.casa', 'Casa', required=True, ondelete='cascade')

    _sql_constraints = [
        ('key_unique', 'UNIQUE(casa_id, tipo)', "Existen tipos de baños repetidos"),
    ]


class Servicio(models.Model):
    _name = 'enjoy.servicio'
    _description = 'Registro de Servicios '

    name = fields.Char('Nombre', size=200, required=True)
    image = fields.Binary("Photo", attachment=True)
    casa_id = fields.Many2many('enjoy.casa', string='Casa')


class Zona(models.Model):
    _name = 'enjoy.zona'
    _description = 'Registro de Zona '

    name = fields.Char('Nombre', size=200, required=True)
    casa_id = fields.Many2many('enjoy.casa', string='Casa')


class Comision(models.Model):
    _name = 'enjoy.comision'
    _description = 'Precio de venta de casa por Vendedor'

    comision = fields.Integer('Comisión', required=True, default=0)
    casa_id = fields.Many2one('enjoy.casa', 'Nombre de la Casa', required=True, ondelete='cascade')
    user_id = fields.Many2one('res.users', 'Responsable', default=lambda self: self.env.user)
    precio = fields.Integer('Precio de la casa', compute='_getprecio')

    @api.one
    @api.depends('casa_id')
    def _getprecio(self):
        self.precio = self.casa_id.precio

    _sql_constraints = [
        ('comis_unique', 'UNIQUE(casa_id, user_id)', "Existen comisiones repetidas"),
    ]


class Provincia(models.Model):
    _name = 'enjoy.provincia'
    _description = 'Registro de provincia'

    name = fields.Char('Nombre', size=100, required=True)
    lugar_ids = fields.One2many('enjoy.lugar', 'provincia_id', 'Localizaciones')


class Catalogo(models.Model):
    _name = 'enjoy.catalogo'
    _description = 'Catalogo de casa'

    name = fields.Char('Nombre', compute='_getnombre')
    nombre = fields.Char('Nombre', size=200, required=True)
    lugar = fields.Many2one('enjoy.provincia', 'Provincia', required=True)
    desde = fields.Char('Desde', size=200, required=True)
    hasta = fields.Char('Hasta', size=200, required=True)
    casa_ids = fields.Many2many('enjoy.casa', 'enjoy_catalogo_casa', 'catalogo_id', 'casa_id', 'Casas y Apartamentos')

    @api.one
    @api.depends('nombre', 'lugar', 'desde', 'hasta')
    def _getnombre(self):
        self.name = "%s: %s (%s - %s)" % (self.nombre, self.lugar.name, self.desde, self.hasta)


class Casa(models.Model):
    _name = 'enjoy.casa'
    _description = 'Registro de casa '

    @api.model
    def _default_image(self):
        image_path = get_module_resource('enjoy', 'static/src/img', 'casa.jpg')
        return tools.image_resize_image_big(open(image_path, 'rb').read().encode('base64'))

    propiedad = fields.Char('Propiedad de ', size=200, required=True)
    name = fields.Char('Nombre de la Propiedad ', size=200, required=True)
    dir = fields.Text('Dirección', size=200)
    lugar = fields.Many2one('enjoy.lugar', 'Localización')
    # catalogo_id = Many2many('enjoy.catalogo', string='Catálogos')
    provincia = fields.Char('Provincia', related='lugar.provincia_id.name', store=True)
    phone = fields.Char('Teléfono', size=50, required=True)
    alojamiento = fields.Selection([('casa', 'Casa'), ('apto', 'Apartamento')], 'Tipo de Alojamiento',
                                   required=True)
    dispone = fields.Selection(
        [('entera', 'Propiedad Entera'), ('privada', 'Habitación Privada'), ('compartida', 'Habitación Compartida')],
        'Dispone de', required=True)
    capacidad = fields.Integer('Canti. Huespedes', required=True, default=4)
    dormitorios = fields.Integer('Cant. Dormitorios', required=True, default=4)
    cama_ids = fields.One2many('enjoy.cama', 'casa_id', 'Tipos de Cama')
    comision_ids = fields.One2many('enjoy.comision', 'casa_id', 'Comisiones')
    banno_ids = fields.One2many('enjoy.banno', 'casa_id', 'Cantidad de Baños')
    servicio_ids = fields.Many2many('enjoy.servicio', 'enjoy_servicio_casa', 'casa_id', 'servicio_id',
                                    'Servicios que ofrecen')
    zona_ids = fields.Many2many('enjoy.zona', 'enjoy_zona_casa', 'casa_id', 'zona_id', 'Zonas que pueden utilizar')
    para = fields.Selection([('f', 'Familia'), ('g', 'Grupos'), ('m', 'Mascotas')], 'Es Perfecto para',
                            required=True)
    precio = fields.Integer('Precio', required=True, default=0)
    # comision = fields.Integer('Comisión', required=True, default=0)
    fpago = fields.Selection([('e', 'Efectivo'), ('t', 'Tarjeta')], 'Forma de Pago', required=True)
    nivel = fields.Selection([('e', 'Económico'), ('c', 'Confort'), ('l', 'Lujo')], 'Nivel',
                             required=True)
    nivelx = fields.Char('Nivel', compute='_getnombre', store=True)

    image = fields.Binary("Photo", default=_default_image, attachment=True)
    image_lateral = fields.Binary("Imagen Lateral", default=_default_image, attachment=True)
    image_foot1 = fields.Binary("Imagen Abajo1", default=_default_image, attachment=True)
    image_foot2 = fields.Binary("Imagen Abajo2", default=_default_image, attachment=True)

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
            self.nivelx = 'Económico'
        if self.nivel == 'c':
            self.nivelx = 'Confort'
        if self.nivel == 'l':
            self.nivelx = 'Lujo'

    @api.model
    def create(self, vals):
        tools.image_resize_images(vals)
        return super(Casa, self).create(vals)

    @api.multi
    def write(self, vals):
        tools.image_resize_images(vals)
        return super(Casa, self).write(vals)

    _sql_constraints = [
        ('key_unique', 'UNIQUE(name)', "Existe una casa con ese nombre"),
    ]


class Reporte(models.Model):
    _name = 'enjoy.reporte'
    _description = 'Reporte de Reservacion de la Casa'

    name = fields.Many2one('enjoy.casa', 'Nombre de la Casa', required=True)
    user_id = fields.Many2one('res.users', 'Responsable', default=lambda self: self.env.user)
    fecha_inicio = fields.Date('Desde', required=True, default=date.today().strftime('%Y-%m-%d'))
    fecha_fin = fields.Date('Hasta', required=True)
    cliente = fields.Char('Cliente', required=True, size=200)
    descrip = fields.Text('Descripción', size=1000)
    state = fields.Selection(
        [('Borrador', 'Borrador'), ('Confirmado', 'Confirmado'), ('Cancelado', 'Cancelado'), ('Hecho', 'Hecho')],
        'Estado',
        required=True, default='Borrador')

    def state_borrador(self):
        self.write({'state': 'Borrador'})

    def state_confirmado(self):
        self.write({'state': 'Confirmado'})

    def state_cancelado(self):
        self.write({'state': 'Cancelado'})

    def state_done(self):
        self.write({'state': 'Hecho'})


class Restino(models.Model):
    _name = 'enjoy.destino'
    _description = 'Destinos para los Correos de los catalogo'

    name = fields.Char('Destinatario', size=100, required=True)
    report_id = fields.Many2one('enjoy.report.mail', 'Reporte', required=True)
