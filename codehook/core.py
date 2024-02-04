import os
import shutil
import tempfile
from pathlib import Path

from dotenv import load_dotenv
from rich import print
from rich.progress import Progress

from .aws import AWS
from .model import CloudName, Events, SourceName
from .sources.stripe import Stripe
from .openai import LLMProxy


class CodehookCore:
    """
    The main class for codehook's logic.
    """

    def __init__(self, cloud: CloudName):
        """
        Initializes a new instance of the CodehookCore class.

        Args:
            cloud (CloudName): The name of the cloud provider.
        """
        load_dotenv()
        self.stripe_api_key = os.getenv("STRIPE_API_KEY")
        self.stripe_wrapper = Stripe(self.stripe_api_key)

        self.cloud = AWS()
        self.llm_proxy = LLMProxy()

    
    def create(
        self,
        command: str,
        source: SourceName,
        enabled_events: list[Events],
    ):
        """
        Creates a python function that performs the logic described in COMMAND .

        Args:
            command (str): The logic to generate function code.
            source (SourceName): The name of the source.
            enabled_events (list[Events]): The list of enabled events.

        Returns:
            file: The file containing the function to be deployed.
        """
        print(f"Generating code with the command: {command}")
        code = self.llm_proxy.create_code(command)
        # Code comes back as ```python ... ``` so we need to remove the markdown
        print(f"Generated code: {code[9:-3]}")

        print("Creating hander")
        f = open("handler.py", "w")
        f.write(code[9:-3])
        f.close()
        print(f"File created: {f}")

        return f

    def deploy(
        self,
        file: Path,
        name: str,
        source: SourceName,
        enabled_events: list[Events],
    ):
        """
        Deploys a serverless lambda function, api endpoint, and webhook endpoint in the source saas platform.

        Args:
            file (Path): The path to the file to be deployed.
            name (str): The name of the serverless endpoint.
            source (SourceName): The name of the source.
            enabled_events (list[Events]): The list of enabled events.

        Returns:
            tuple: A tuple containing the name, API ID, API URL, and webhook ID.
        """
        events = [event.value for event in enabled_events]
        print(
            f"Creating a [blue]{source.value}[/blue] endpoint that listens to [blue]{events}[/blue] events..."
        )

        print(f"Deploying [blue]{file}[/blue] as [blue]{name}[/blue] :rocket:")
        with (
            Progress(transient=True) as progress,
            tempfile.TemporaryDirectory() as lambda_path,
        ):
            # Step 1: Move skeleton and supplied handler to temporary directory
            task = progress.add_task(
                "[blue]Creating codehook files[/blue] :writer:", total=300
            )
            print("Created temporary directory", lambda_path)
            progress.update(task, advance=100)

            shutil.copytree(
                "codehook/skeletons/stripe", lambda_path, dirs_exist_ok=True
            )
            print("Copied skeleton files to temporary directory", lambda_path)
            progress.update(task, advance=100)

            shutil.copy(file, lambda_path + "/handler.py")
            print("Copied custom handler to temporary directory", lambda_path)
            progress.update(task, advance=100)

            # Step 2: Deploy serverless function and API in the cloud
            task = progress.add_task(
                "[blue]Deploying serverless endpoint[/blue] :cloud:", total=500
            )
            function_id = self.cloud.create_function(name, lambda_path)
            progress.update(task, advance=300)

            api_id, api_url = self.cloud.create_api(name, function_id)
            progress.update(task, advance=200)

            # Step 3: Create webhook endpoint in the source
            # Link the webhook endpoint to the API URL
            task = progress.add_task(
                "[blue]Setting up endpoint in the source[/blue]", total=100
            )
            print("Configuring the webhook endpoint in the source")
            webhook_id = self.stripe_wrapper.create_webhook(events, api_url)
            progress.update(task, advance=100)
            print(f"Webhook endpoint {webhook_id} created")

        print("[bold green]Deployment complete[/bold green] :rocket:")
        print(f"Function name: [blue]{name}[/blue]")
        print(f"API ID: [blue]{api_id}[/blue]")
        print(f"Webhook URL: [blue]{api_url}[/blue]")
        print(f"Webhook ID: [blue]{webhook_id}[/blue]")

        return name, api_id, api_url, webhook_id

    def list(self):
        """
        Lists all codehook endpoints, lambda functions, and webhook endpoints.
        """
        print("Listing all codehook endpoints...")
        endpoint_ids = self.cloud.list_apis()

        print("Listing all lambda functions...")
        lambda_ids = self.cloud.list_functions()

        print("Listing all webhook endpoints...")
        webhook_ids = self.stripe_wrapper.list_webhooks()

        return endpoint_ids, lambda_ids, webhook_ids

    def delete(
        self,
        lambda_function_name: str = None,
        api_id: str = None,
        webhook_id: str = None,
        delete_all: bool = False,
    ):
        """
        Deletes a lambda function, API endpoint, and webhook endpoint.

        Args:
            lambda_function_name (str, optional): The name of the lambda function to delete.
            api_id (str, optional): The ID of the API endpoint to delete.
            webhook_id (str, optional): The ID of the webhook endpoint to delete.
            delete_all (bool, optional): Flag indicating whether to delete all functions and endpoints.
        """
        if delete_all:
            print("[bold red]Deleting all functions and endpoints[/bold red]")
            endpoint_ids, lambda_ids, webhook_ids = self.list()
            for endpoint_id in endpoint_ids:
                print(f"[bold red]Deleting [/bold red][blue]{api_id}[/blue]")
                self.cloud.delete_api(endpoint_id)
                print(f"[blue]{api_id}[/blue][bold green] deleted[/bold green]")
            for lambda_id in lambda_ids:
                print(f"[bold red]Deleting [/bold red][blue]{lambda_id}[/blue]")
                self.cloud.delete_function(lambda_id)
                print(f"[blue]{lambda_id}[/blue][bold green] deleted[/bold green]")
            for webhook_id in webhook_ids:
                print(f"[bold red]Deleting [/bold red][blue]{webhook_id}[/blue]")
                self.stripe_wrapper.delete_webhook(webhook_id)
                print(f"[blue]{webhook_id}[/blue][bold green] deleted[/bold green]")
        else:
            print(f"[bold red]Deleting [/bold red][blue]{api_id}[/blue]")
            self.cloud.delete_api(api_id)
            print(f"[blue]{api_id}[/blue][bold green] deleted[/bold green]")
            print(f"[bold red]Deleting [/bold red][blue]{lambda_id}[/blue]")
            self.cloud.delete_function(lambda_function_name)
            print(f"[blue]{lambda_id}[/blue][bold green] deleted[/bold green]")
            print(f"[bold red]Deleting [/bold red][blue]{webhook_id}[/blue]")
            self.stripe_wrapper.delete_webhook(webhook_id)
            print(f"[blue]{webhook_id}[/blue][bold green] deleted[/bold green]")

        print("[bold red]Deletion complete[/bold red]")
