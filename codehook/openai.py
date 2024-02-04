from openai import OpenAI


class LLMProxy:
    LLM_SYSTEM_PROMPT="""
    You are a helpful code assistant that can teach a junior developer how to code. 
    Your language of choice is Python. Don't explain the code, just generate the code block itself. 
    Comment the code block generously.
    """
    def __init__(self):
        self.client = OpenAI()
        pass

    def create_code(self, command: str):
        """
        Creates a Python function that performs the logic described in COMMAND.

        :param command: The logic to generate function code.
        :return: The code of the function to be deployed.
        """
        response = self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {
                "role": "system",
                "content": """
                    You are a helpful code assistant that can teach a junior developer how to code. 
                    Your language of choice is Python. 
                    Don't explain the code, just generate the code block itself. 
                    Comment the code block generously.
                """
                },
                {
                "role": "user",
                "content": """
                    You will write a function with the following signature:\n
                    ```python\n
                    def handler_logic(body):\n    
                    \"\"\"\n    
                    Handles the logic around a Stripe webhook event\n    
                    :param body: The event in JSON format. Example available on example_payload.json\n    
                    :return: A tuple containing the HTTP status code and the body of the response.\n    
                    The response body is a str and is used for logging purposes only, as webhooks are asynchronous.\n        
                    (response_code, response_body)\n    
                    \"\"\"\n```\n 
                    Write the function with the signature of handler_logic that {command}
                """.format(command=command)
                }
            ],
            temperature=0.2,
            max_tokens=1024,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        print(f"Usage: {response.usage}")

        return response.choices[0].message.content
