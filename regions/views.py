from django.views.generic import ListView, DetailView
from .models import Region


class RegionListView(ListView):
    model = Region
    template_name = 'regions/list.html'
    context_object_name = 'regions'
    queryset = Region.objects.filter(is_active=True).prefetch_related('attractions')


class RegionDetailView(DetailView):
    model = Region
    template_name = 'regions/detail.html'
    context_object_name = 'region'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['attractions'] = self.object.attractions.filter(is_active=True)
        context['tours'] = self.object.tours.filter(is_active=True)
        return context