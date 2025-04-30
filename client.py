import requests


class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def query(self, message, thread_id=None):
        """
        Sends a message to the /query API and returns the response.

        :param message: The message to send to the API.
        :param thread_id: Optional thread ID for the conversation.
        :return: The response from the API.
        """
        url = f"{self.base_url}/query"
        payload = {
            "message": message
        }
        if thread_id:
            payload["thread_id"] = str(thread_id)

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}