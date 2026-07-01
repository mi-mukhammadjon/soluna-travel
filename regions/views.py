from django.views.generic import ListView, DetailView
from places.models import NearbyPlace
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
        # Yaqin atrofdagi joylar — shu regiondagi diqqatga sazovor joylar atrofida
        context['nearby_places'] = (
            NearbyPlace.objects
            .filter(attraction__region=self.object, is_active=True)
            .select_related('attraction')
            .order_by('category', '-rating', 'name')
        )
        return context