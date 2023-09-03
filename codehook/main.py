import typer
import boto3
from dotenv import load_dotenv

load_dotenv()
app = typer.Typer()


@app.callback()
def callback():
    """
    Callback function
    """


@app.command()
def deploy():
    """
    Deploy function
    """
    s3 = boto3.resource("s3")
    for bucket in s3.buckets.all(): # type: ignore
        typer.echo(bucket.name)
