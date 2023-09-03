import typer


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
    typer.echo("Hello. You are codehooked.")
    