from locust import HttpUser, task, between


class QuickstartUser(HttpUser):
    
    @task
    def room_get(self):
        self.client.post("/accounts/api/v1/jwt/create/", data={ "phone": '9123456789', "password": 'reza1385'})
        