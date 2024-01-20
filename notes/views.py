from django.shortcuts import render
from django.contrib.auth.views import LoginView
from .forms import LoginForm, RegisterForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import RedirectView, View, CreateView
from django.db.models import Q
from .models import Note
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.http import HttpResponse
from django.urls import reverse_lazy

# Create your views here.

class SimpleLoginView(LoginView):
    form_class = LoginForm
    template_name = 'notes/login.html'
    
class SimpleRegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'notes/register.html'
    success_url = reverse_lazy('login')
    
class NoteDetailView(LoginRequiredMixin, View):
    template_name = 'notes/note_detail.html'
    no_note_template_name = 'notes/no_note.html'
    decryption_error_template_name = 'notes/decryption_error.html'
    def get(self, request, pk, *args, **kwargs):
        try:
            note = Note.objects.get(Q(pk=pk) & (Q(public=True) | Q(user=self.request.user)))
            context = {
                'note': note,
            }
            return render(request, self.template_name, context)
        except Exception as e:
            return render(request, self.no_note_template_name)
        
    def post(self, request, pk, *args, **kwargs):
        try:
            note = Note.objects.get(Q(pk=pk) & (Q(public=True) | Q(user=self.request.user)))
            password = request.POST.get('password', '')

            try:
                decrypted_text = note.get_decrypted_text(password)
                context = {
                    'note': note,
                    'decrypted_text': decrypted_text,
                }
                return render(request, self.template_name, context)
            except Exception as e:
                return render(request, self.decryption_error_template_name, {'error': str(e)})

        except Note.DoesNotExist:
            return render(request, self.no_note_template_name)
    
class NoteListView(LoginRequiredMixin, View):
    template_name = 'notes/note_list.html'
    
    def get(self, request, *args, **kwargs):
        public_notes = Note.objects.filter(public=True).exclude(user=self.request.user)
        my_notes = Note.objects.filter(user=self.request.user)
        
        context = {
            'public_notes': public_notes,
            'my_notes': my_notes,
        }
        
        return render(request, self.template_name, context)
    
class NoteCreateView(LoginRequiredMixin, CreateView):
    model = Note
    template_name = 'notes/add_note.html'
    fields = ['title', 'content', 'public', 'encrypted', 'password']
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('note_list')
    
class HomeRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False 
    
    def get_redirect_url(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            next_page = 'accounts/login/'
        else:
            next_page = '/my-notes/'
        return next_page
    
def simple_logout(request):
    logout(request)
    return redirect('home')