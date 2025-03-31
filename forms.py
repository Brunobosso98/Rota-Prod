
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FloatField, FileField, TextAreaField, SelectField, SelectMultipleField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, NumberRange, Optional
from flask_wtf.file import FileRequired, FileAllowed
from models import Location, db

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])
    remember_me = BooleanField('Lembrar-me')
    submit = SubmitField('Entrar')

class AdminRegistrationForm(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    company_name = StringField('Nome da Empresa', validators=[DataRequired()])
    cnpj = StringField('CNPJ', validators=[DataRequired(), Length(min=14, max=18)])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirmar Senha', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrar')

class UserCreateForm(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField('Função', choices=[('manager', 'Gerente de Vendas'), ('seller', 'Vendedor')], validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirmar Senha', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Cadastrar Usuário')

class UserAssignForm(FlaskForm):
    users = SelectMultipleField('Selecionar Usuários', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Atribuir')

class RouteForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired()])
    description = TextAreaField('Descrição')
    start_location = HiddenField('Ponto de Partida', validators=[Optional()])
    state_filter = SelectField('Estado', validators=[Optional()], choices=[('', 'Todos')])
    city_filter = SelectMultipleField('Cidade', validators=[Optional()], choices=[('', 'Todas')])  # Mudado para SelectMultipleField
    locations = SelectMultipleField('Locais', coerce=int)
    sellers = SelectMultipleField('Vendedores', coerce=int)
    managers = SelectMultipleField('Gerentes', coerce=int)
    
    def __init__(self, *args, **kwargs):
        super(RouteForm, self).__init__(*args, **kwargs)
        # Preencher estados e cidades dinamicamente
        locations = Location.query.all()
        states = sorted(set(loc.state for loc in locations if loc.state))
        self.state_filter.choices.extend([(s, s) for s in states])

class EditRouteForm(FlaskForm):
    name = StringField('Nome da Rota', validators=[DataRequired()])
    description = TextAreaField('Descrição')
    managers = SelectMultipleField('Gerentes', coerce=int, validators=[Optional()])
    sellers = SelectMultipleField('Vendedores', coerce=int, validators=[Optional()], render_kw={"multiple": True})
    submit = SubmitField('Atualizar Rota')

    def process_formdata(self, valuelist):
        # Garantir que todos os valores são processados corretamente
        if valuelist:
            try:
                self.data = [int(x) for x in valuelist]
            except ValueError:
                raise ValueError('Invalid choice(s): one or more data inputs could not be coerced to integers.')

class CloneRouteForm(FlaskForm):
    name = StringField('Nome da Nova Rota', validators=[DataRequired()])
    submit = SubmitField('Clonar Rota')

class CompleteRouteForm(FlaskForm):
    confirm = BooleanField('Confirmar Finalização da Rota', validators=[DataRequired()])
    submit = SubmitField('Finalizar Rota')

class LocationForm(FlaskForm):
    name = StringField('Nome do Local', validators=[DataRequired()])
    city = StringField('Cidade', validators=[DataRequired()])
    state = SelectField('Estado', validators=[DataRequired()], choices=[
        ('AC', 'Acre'),
        ('AL', 'Alagoas'),
        ('AP', 'Amapá'),
        ('AM', 'Amazonas'),
        ('BA', 'Bahia'),
        ('CE', 'Ceará'),
        ('DF', 'Distrito Federal'),
        ('ES', 'Espírito Santo'),
        ('GO', 'Goiás'),
        ('MA', 'Maranhão'),
        ('MT', 'Mato Grosso'),
        ('MS', 'Mato Grosso do Sul'),
        ('MG', 'Minas Gerais'),
        ('PA', 'Pará'),
        ('PB', 'Paraíba'),
        ('PR', 'Paraná'),
        ('PE', 'Pernambuco'),
        ('PI', 'Piauí'),
        ('RJ', 'Rio de Janeiro'),
        ('RN', 'Rio Grande do Norte'),
        ('RS', 'Rio Grande do Sul'),
        ('RO', 'Rondônia'),
        ('RR', 'Roraima'),
        ('SC', 'Santa Catarina'),
        ('SP', 'São Paulo'),
        ('SE', 'Sergipe'),
        ('TO', 'Tocantins')
    ])
    latitude = FloatField('Latitude', validators=[
        DataRequired(),
        NumberRange(min=-90, max=90, message='Latitude deve estar entre -90 e 90')
    ])
    longitude = FloatField('Longitude', validators=[
        DataRequired(),
        NumberRange(min=-180, max=180, message='Longitude deve estar entre -180 e 180')
    ])
    street = StringField('Rua', validators=[Optional(), Length(max=200)])
    number = StringField('Número', validators=[Optional(), Length(max=20)])
    telephone = StringField('Telefone', validators=[Optional(), Length(max=20)])
    submit = SubmitField('Salvar Local')

class ProfileForm(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    company_cnpj = StringField('CNPJ da Empresa (somente leitura)', render_kw={'readonly': True})
    current_password = PasswordField('Senha Atual')
    new_password = PasswordField('Nova Senha')
    confirm_password = PasswordField('Confirmar Nova Senha', validators=[EqualTo('new_password')])
    submit = SubmitField('Atualizar Perfil')

class AssignSellerForm(FlaskForm):
    """Formulário para atribuir vendedores a uma rota"""
    sellers = SelectMultipleField('Vendedores', coerce=int, validators=[Optional()])
    submit = SubmitField('Atribuir Vendedores')

class ChangePlanForm(FlaskForm):
    plan = SelectField('Plano', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Atualizar Plano')
