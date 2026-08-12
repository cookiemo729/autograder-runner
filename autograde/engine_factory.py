from autograde.engines.html_engine import HtmlEngine
from autograde.engines.playwright_engine import PlaywrightEngine
from autograde.engines.java_engine import JavaEngine


class EngineFactory:

    @staticmethod
    def create(engine_name):

        if engine_name == "html":
            return HtmlEngine()

        if engine_name == "playwright":
            return PlaywrightEngine()

        if engine_name == "java":
            return JavaEngine()

        raise ValueError(
            f"Unknown engine: {engine_name}"
        )