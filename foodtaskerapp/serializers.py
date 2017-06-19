from rest_framework import serializers
from foodtaskerapp.models import Restaurant , Meal


class RestaurantSerializer(serializers.ModelSerializer):
    # This do nothing

    # logo  = serializers.SerializerMethodFiled()

    # def get_logo(self, request):
    #     print("get_logo")
    #     request = self.context.get('request')
    #     logo_url = restaurant.logo.url
    #     return request.build_absolute_uri(logo_url)

    class Meta:
        model = Restaurant
        fields = ("id" , "name" , "phone" , "address" , "logo")


class MealSerializer(serializers.ModelSerializer):

    # def get_image(self, request):
    #     request = self.context.get('request')
    #     image_url = restaurant.meal.image
    #     return request.build_absolute_uri(iamge_url)

    class Meta:
        model = Meal
        fields =  ("id" , "name", "short_description", "image" , "price")
