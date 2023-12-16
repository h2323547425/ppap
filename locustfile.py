from locust import HttpUser, task, between, SequentialTaskSet

class UserBehavior(SequentialTaskSet):
    count = 0

    def on_start(self):
        UserBehavior.count += 1
        self.user_id = UserBehavior.count
        self.client.post("/register", {"test-mode":"locust", "username": "test"+str(self.user_id), "password":"test-password"})

    @task
    def login(self):
        self.client.post("/login", {"test-mode":"locust", "username": "test"+str(self.user_id), "password":"test-password"})

    @task
    def get_dashboard(self):
        self.client.get("/dashboard/" + str(self.user_id) + "?test-mode=locust&username=" + "test"+str(self.user_id))

    @task
    def add_note(self):
        self.client.post("/dashboard/" + str(self.user_id), {"test-mode":"locust", "username": "test"+str(self.user_id), "note":"test note"})

class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(0.5, 5)