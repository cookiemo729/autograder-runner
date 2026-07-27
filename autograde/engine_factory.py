from autograde.engines.html_engine import HtmlEngine
from autograde.engines.playwright_engine import PlaywrightEngine


class EngineFactory:

    @staticmethod
    def create(engine_name):

        if engine_name == "html":
            return HtmlEngine()

        if engine_name == "playwright":
            return PlaywrightEngine()

        raise ValueError(f"Unknown engine: {engine_name}")