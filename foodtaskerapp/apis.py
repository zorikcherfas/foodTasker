import json
from django.http import JsonResponse
from foodtaskerapp.models import Restaurant , Meal , Order, OrderDetails , Driver
from foodtaskerapp.serializers import RestaurantSerializer ,MealSerializer , OrderSerializer
from oauth2_provider.models import AccessToken
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt



###############
# Customer
###############
def customer_get_restaurants(request):

    try:
        restaurants = RestaurantSerializer(
            Restaurant.objects.all().order_by("-id"),
            many=True,
            context =  {"request":request}
            ).data

        return JsonResponse({
        "restaurants": restaurants
        })

    except AccessToken.DoesNotExist:
        return JsonResponse ({"status":"falied","error":"access_token is wrong"})


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

    print("add ordre was called")
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


def customer_get_latest_order(request):
    # access_token = AccessToken.objects.get(token = request.GET.get("access_token"),
        # expires__gt = timezone.now())
    access_token = AccessToken.objects.get(token = request.GET.get("access_token"),
    expires__gt = timezone.now())

    customer = access_token.user.customer
    order = OrderSerializer(Order.objects.filter(customer = customer).last()).data

    return JsonResponse({"order": order})

###############
# Restaurant
###############
def restaurant_order_notification(request, last_request_time):
    # try:
    #     notification = Order.objects.filter(restaurant = request.user.restaurant,created_at__gt = last_request_time).count()
    #
    #     return JsonResponse({"notification": notification})
    # except AccessToken.DoesNotExist:
    return JsonResponse ({"status":"falied","error":"access_token is wrong"})


def customer_driver_location(request):

    access_token = AccessToken.objects.get(token = request.GET.get("access_token"),
        expires__gt=timezone.now())

    customer = access_token.user.customer
    curret_order = Order.objects.filter(customer = customer , status = Order.ONTHEWAY).last()
    print(curret_order)
    location = curret_order.driver.location

    return JsonResponse({"location":location})


###############
# Restaurant
#############
def driver_get_ready_orders(request):
    orders = OrderSerializer(
        Order.objects.filter(status = Order.READY ,driver =None,).order_by("-id"), many=True
        ).data

    return JsonResponse({"orders":orders})

@csrf_exempt
def driver_pick_order(request):
    if request.method == "POST":
        # Get token
        access_token = AccessToken.objects.get(token = request.POST.get("access_token"),
            expires__gt = timezone.now())

    # Get Driver

        driver = access_token.user.driver

    #Check if driver an only pick one order in the same timezone
    if Order.objects.filter(driver = driver).exclude(status = Order.ONTHEWAY):
        return JsonResponse({"status":"failed" ,"Error": "You can only pick up one item at the same time"})

    try:
        order = Order.objects.get(
            id = request.POST["order_id"],
            driver = None,
            status = Order.READY
        )
        order.driver = driver
        order.status = Order.ONTHEWAY
        order.picked_at = timezone.now()
        order.save()

        return JsonResponse({"status":"success"})

    except Order.DoesNotExist:
        return JsonResponse({"status":"falied","error":"This order has been picked up by other driver"})

    return JsonResponse({})


def driver_get_latest_order(request):

    try:
        access_token = AccessToken.objects.get(token = request.GET.get("access_token"),
            expires__gt = timezone.now())

    except AccessToken.DoesNotExist:
        return JsonResponse ({"status":"falied","error":"access_token is wrong"})

    driver = access_token.user.driver
    order = OrderSerializer (
        Order.objects.filter(driver = driver).order_by("picked_at").last()
    ).data

    return JsonResponse({"order":order })

@csrf_exempt
def driver_complete_order(request):

    try:
        access_token = AccessToken.objects.get(token = request.POST.get("access_token"),
            expires__gt=timezone.now())
    except AccessToken.DoesNotExist:
        return JsonResponse ({"status":"falied","error":"access_token is wrong"})

    driver = access_token.user.driver

    order = Order.objects.get(id = request.POST['order_id'] , driver =driver)

    order.status  = order.DELIVERED
    order.save()

    return JsonResponse({"status":"success"})


#POST params: access_token , order_id
@csrf_exempt
def driver_get_revenue(request):

    try:
        # print(request.POST.get('access_token')
        access_token = AccessToken.objects.get(token = request.POST.get("access_token"),
            expires__gt=timezone.now())
    except AccessToken.DoesNotExist:
        return JsonResponse ({"status":"falied","error":"access_token is wrong"})

    driver = access_token.user.driver

    from datetime import timedelta

    reveneu = {}
    today = timezone.now()
    current_weekdays = [
        today + timedelta(days = i) for i in range(0-today.weekday(), 7 - today.weekday())
    ]


    for day in current_weekdays:
        print(day)
        orders = Order.objects.filter(
            driver = driver,
            status = Order.DELIVERED,
            created_at__year = day.year,
            created_at__month = day.month,
            created_at__day = day.day
        )

        reveneu[day.strftime("%a")] = sum(order.total for order in orders)

    return JsonResponse({"reveneu":reveneu})

#POST params: access_token , string "lat,lng"
@csrf_exempt
def driver_update_location(request):

    if request.method == "POST":

        access_token = AccessToken.objects.get(token = request.POST.get("access_token"),
            expires__gt=timezone.now())

        driver = access_token.user.driver
        driver.location = request.POST["location"]
        driver.save()

        return JsonResponse({})

    return JsonResponse({"status":"fail"})
