from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view()
def api_test(request):
    return Response({"status": True})

def room_detail(request):
    # write a room detail api after watching videos
    pass