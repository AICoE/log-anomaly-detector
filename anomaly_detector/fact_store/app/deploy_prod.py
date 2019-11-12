"""Deploy a production ready Factstore via Gunicorn."""
from gunicorn.six import iteritems
import gunicorn.app.base


class GunicornFactstore(gunicorn.app.base.BaseApplication):
    """Gunicorn bootstrapper for Factsore."""

    def __init__(self, app, options=None):
        """Initialize app and options."""
        self.options = options or {}
        self.application = app
        super(GunicornFactstore, self).__init__()

    def load_config(self):
        """Load configurations for Gunicorn."""
        config = dict([(key, value) for key, value in iteritems(self.options)
                       if key in self.cfg.settings and value is not None])
        for key, value in iteritems(config):
            self.cfg.set(key.lower(), value)

    def load(self):
        """Get the wsgi application."""
        return self.application
