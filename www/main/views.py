from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.template import Context, loader
from django.views.generic.base import View

from django.views.generic.edit import FormView
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, get_user, authenticate
from django.views.decorators.csrf import csrf_exempt

import jwt
from time import time


JWT_KEY = '@aslkdfnsadfkladjh0g^r4t5ri23nj45big09v1n243'
# загружаем шаблон и его состовляющие
template = loader.get_template('gora_template/gora_template.html')
head_title = 'GORA'

# main_menu = loader.get_template('menu.html').render()
# footer = loader.get_template('footer.html').render()

"""context = {
    'main_menu': main_menu,
    'footer': footer,
    'head_title': head_title,
}"""


class RegisterFormView(FormView):
    form_class = UserCreationForm

    template_name = 'gora_template/register_page.html'

    # Ссылка, на которую будет перенаправляться пользователь в случае успешной регистрации.
    # В данном случае указана ссылка на страницу входа для зарегистрированных пользователей.
    success_url = "/"

    # Шаблон, который будет использоваться при отображении представления.
    # template_name = "register.html"

    def form_valid(self, form):
        # Создаём пользователя, если данные в форму были введены корректно.
        form.save()

        # Вызываем метод базового класса
        return super(RegisterFormView, self).form_valid(form)


# Функция для установки сессионного ключа.
# По нему django будет определять, выполнил ли вход пользователь.


class LoginFormView(FormView):
    form_class = AuthenticationForm

    template_name = 'gora_template/login_page.html'

    success_url = "/"

    def form_valid(self, form):
        # Получаем объект пользователя на основе введённых в форму данных.
        self.user = form.get_user()

        # Выполняем аутентификацию пользователя.
        login(self.request, self.user)
        return super(LoginFormView, self).form_valid(form)


class LogoutView(View):
    def get(self, request):
        # Выполняем выход для пользователя, запросившего данное представление.
        logout(request)

        # После чего, перенаправляем пользователя на главную страницу.
        return HttpResponseRedirect("/?mes=0Вы вышли из аккаунта!")


@csrf_exempt
def auth_api(request):
    login = request.POST.get('login', None)
    password = request.POST.get('password', None)
    if not login or not password:
        return HttpResponse()

    user = authenticate(username=login, password=password)
    if user:
        return HttpResponse(jwt.encode({'username': user.username, 'expires': round(time() + 60)},
                                       JWT_KEY,
                                       algorithm='HS256'))
    else:
        return HttpResponseForbidden()


def main_page(request):
    """mes = request.GET.get('mes', False)
    m_type = 'ok'
    if mes:
        if mes[0] == '!':
            m_type = 'error'
        mes = mes[1:len(mes)]
    content_template = loader.get_template('main/index.html')
    content_context = {'mes': mes, 'type': m_type}
    content = content_template.render(content_context, request)
    context.update({'content': content})"""

    user = get_user(request)

    content_context = {'user': user}

    context = Context({
        'content': loader.get_template('gora_template/main_page.html').render(content_context),
    })
    # logout(request)
    return HttpResponse(template.render(context))