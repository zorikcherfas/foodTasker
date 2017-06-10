from foodtaskerapp.models import Customer , Driver

def create_user_by_type(backend, user, request ,response, *args, **kwargs):
    if backend.name == 'facebook':
        avatar = 'https://graph.facebook.com/%s/picature?type=large' % response['id']
    else:
        avatar = ''

    # print("checking request")
    print(request["user_type"])
    if request['user_type'] == 'driver':
        print("good to go")
    else:
        print("not good")
    print(user.get_full_name())
    if request['user_type'] == "driver" and not Driver.objects.filter(user_id=user.id):
        print("create driver")
        Driver.objects.create(user_id=user.id , avatar = avatar)

    if request['user_type'] == 'customer' and not Customer.objects.filter(user_id=user.id):
        Customer.objects.create(user_id=user.id , avatar = avatar)
