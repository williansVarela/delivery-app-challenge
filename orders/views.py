from urllib.parse import quote

import requests
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View

from .forms import DistanceForm
from .models import DistanceQuery


class DistanceCalculatorView(View):
    def get(self, request):
        form = DistanceForm()

        return render(
            request,
            "orders/delivery_distance.html",
            {"form": form, "result": None, "error": None},
        )

    def post(self, request):
        form = DistanceForm(request.POST)

        if form.is_valid():
            source = form.cleaned_data["source"]
            destination = form.cleaned_data["destination"]

            source_coords = self.get_geolocation(source)
            destination_coords = self.get_geolocation(destination)

            if source_coords and destination_coords:
                distance = self.get_distance(source_coords, destination_coords)
                if distance:
                    DistanceQuery.objects.create(
                        source_address=source,
                        destination_address=destination,
                        distance=distance,
                    )
                    return render(
                        request,
                        "orders/delivery_distance.html",
                        {
                            "form": form,
                            "result": f"Distance: {distance} km",
                        },
                    )
                else:
                    return JsonResponse(
                        {
                            "error": "Could not fetch geolocation data for one or both addresses."
                        }
                    )
            else:
                return JsonResponse(
                    {"error": "Invalid data. Please check the addresses and try again."}
                )

        else:
            return JsonResponse(
                {"error": "Invalid data. Please check the addresses and try again."}
            )

    def get_geolocation(self, address: str) -> tuple[float, float] | None:
        """
        Get the latitude and longitude of an address using openstreetmap API.

        :param address: The address to get the geolocation from.
        """

        url = f"https://nominatim.openstreetmap.org/search?q={quote(address)}&format=json&limit=1"
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate, br",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
            "Referer": "https://map.project-osrm.org/",
        }
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return None

        data = response.json()
        if data:
            return (float(data[0].get("lon")), float(data[0].get("lat")))

        return None

    def get_distance(
        self,
        source_coords: tuple[float, float],
        destination_coords: tuple[float, float],
    ) -> float | None:
        """
        Calculate the distance between two address points using openstreetmap API.

        :param source_coords: tuple containing the  longitude and latitude of the source
        address. Example: (-46.85542307242641,-23.51617475)
        :param destination_coords: tuple containing the longitude and latitude of the
        destination address. Example: (-46.85058547252888,-23.50928835)
        """
        destination = "{0},{1};{2},{3}".format(
            source_coords[0],
            source_coords[1],
            destination_coords[0],
            destination_coords[1],
        )

        url = f"https://routing.openstreetmap.de/routed-car/route/v1/driving/{destination}?overview=false&alternatives=true&steps=true"
        response = requests.get(url)

        data = response.json()

        if data["code"] == "Ok":
            distance_meters = data["routes"][0]["distance"]
            return round(distance_meters / 1000, 1)
        return None


class HistoryView(View):
    def get(self, request):
        queries = DistanceQuery.objects.all().order_by("-created_at")
        return render(
            request, "orders/distance_query_history.html", {"queries": queries}
        )
