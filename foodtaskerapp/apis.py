import json
from django.http import JsonResponse
from foodtaskerapp.models import Restaurant , Meal , Order, OrderDetails
from foodtaskerapp.serializers import RestaurantSerializer ,MealSerializer
from oauth2_provider.models import AccessToken
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

def customer_get_restaurant(request):
    restaurants = RestaurantSerializer(
        Restaurant.objects.all().order_by("-id"),
        many=True,
        context =  {"request":request}
        ).data

    return JsonResponse({
    "restaurants": restaurants
    })


def customer_get_meals(request , restaurant_id):
    meals = MealSerializer(
        Meal.objects.filter(restaurant_id = restaurant_id).order_by("-id"),
        many=True,
        context = {"request": request}
        ).data

    return JsonResponse({
    "meals":meals

    })

@csrf_exempt
def customer_add_order(request):

    if request.method == "POST":
        # Get token
        access_token = AccessToken.objects.get(token = request.POST.get("access_token"),
            expires__gt = timezone.now())

        # Get profile
        customer = access_token.user.customer
        #Check wheater customer has any order that is not devliered

        if Order.objects.filter(customer = customer).exclude(status = Order.DELIVERED):
            return JsonResponse({"status":"fail" ,"error":"Your last order myst be completed."})
        #Check the address
        if not request.POST["address"]:
            return JsonResponse({"stastus": "failed" , "error":"Address is required."})

        #Get Order Details
        # print(request.POST["order_details"])
        # test = [{"meal_id":1 , "quantity":2} , {"meal_id":2 , "quantity":10}]
        # print(test)
        # order_details = json.loads(test)
        order_details = json.loads(request.POST["order_details"])

        order_total = 0

        for meal in order_details:
            order_total = Meal.objects.get(id = meal["meal_id"]).price * meal["quantity"]

        if len(order_details) > 0 :

            order = Order.objects.create(
            customer= customer,
            restaurant_id = request.POST["restaurant_id"],
            total = order_total,
            status = Order.COOKING,
            address = request.POST["address"]
            )

            for meal in order_details:
                OrderDetails.objects.create(
                    order =order,
                    meal_id = meal["meal_id"],
                    quantity = meal["quantity"],
                    sub_total = Meal.objects.get(id = meal["meal_id"]).price * meal["quantity"]
                )

            return JsonResponse({"status":"success"})




    return JsonResponse({

    })

def customer_get_lasts_order(request):

    return JsonResponse({

    })

def restaurant_order_notification(request , last_request_time):

    notification = Order.objects.filter(restaurant = request.user.restaurant,
    created_at__gt = last_request_time).count();

    return JsonResponse({"notification":notification})
