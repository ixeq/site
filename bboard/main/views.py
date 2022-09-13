

# Create your views here.

from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import UpdateView
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.views.generic import CreateView
from django.views.generic.base import TemplateView


from .forms import RegisterUserForm
from .models import user_registrated
from .forms import ChangeUserInfoForm
from .models import AdvUser


def index(request):
    return render(request, 'main/index.html')
def other_page(request, page):
   try:
       template = get_template('main/' + page + '.html')
   except TemplateDoesNotExist:
       raise Http404
   return HttpResponse(template.render(request=request))
class BBLoginView(LoginView):
   template_name = 'main/login.html'

@login_required
def profile(request):
    return render(request, 'main/profile.html')

class BBLogoutView(LoginRequiredMixin, LogoutView):
   template_name = 'main/logout.html'


class ChangeUserInfoView(SuccessMessageMixin, LoginRequiredMixin,
                         UpdateView):
    model = AdvUser
    template_name = 'main/change_user_info.html'
    form_class = ChangeUserInfoForm
    success_url = reverse_lazy('main:profile')
    success_message = 'Личные данные пользователя изменены'

    def dispatch(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)

class BBPasswordChangeView(SuccessMessageMixin, LoginRequiredMixin,
                          PasswordChangeView):
   template_name = 'main/password_change.html'
   success_url = reverse_lazy('main:profile')
   success_message = 'Пароль пользователя изменен'

class RegisterUserForm(forms.ModelForm):
   email = forms.EmailField(required=True,
                            label='Адрес электронной почты')
   password1 = forms.CharField(label='Пароль',
                               widget=forms.PasswordInput,
                               help_text=password_validation.password_validators_help_text_html())
   password2 = forms.CharField(label='Пароль (повторно)',
                               widget=forms.PasswordInput,
                               help_text='Повторите тот же самый пароль еще раз')

def clean_password1(self):
    password1 = self.cleaned_data['password1']
    if password1:
           password_validation.validate_password(password1)
    return password1

def clean(self):
    super().clean()
    password1 = self.cleaned_data['password1']
    password2 = self.cleaned_data['password2']
    if password1 and password2 and password1 != password2:
        errors = {'password2': ValidationError(
            'Введенные пароли не совпадают', code='password_mismatch'
        )}
        raise ValidationError(errors)

def save(self, commit=True):
    user = super().save(commit=False)
    user.set_password(self.cleaned_data['password1'])
    user.is_active = False
    user.is_activated = False
    if commit:
        user.save()
    user_registrated.send(RegisterUserForm, instance=user)
    return user

class Meta:
    model = AdvUser
    fields = ('username', 'email', 'password1', 'password2',
                 'first_name', 'last_name', 'send_messages')

class RegisterUserView(CreateView):
   model = AdvUser
   template_name = 'main/register_user.html'
   form_class = RegisterUserForm
   success_url = reverse_lazy('main:register_done')

class RegisterDoneView(TemplateView):
   template_name = 'main/register_done.html'