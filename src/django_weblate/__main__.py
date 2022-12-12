"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """Django Weblate."""


if __name__ == "__main__":
    main(prog_name="django-weblate")  # pragma: no cover
