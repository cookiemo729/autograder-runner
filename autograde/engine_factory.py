from autograde.engines.html_engine import HtmlEngine
from autograde.engines.playwright_engine import PlaywrightEngine
from autograde.engines.java_engine import JavaEngine
from autograde.engines.vue_engine import VueEngine


class EngineFactory:

    @staticmethod
    def create(engine_name):

        if engine_name == "html":
            return HtmlEngine()

        if engine_name == "playwright":
            return PlaywrightEngine()

        if engine_name == "java":
            return JavaEngine()

        if engine_name == "vue":
            return VueEngine()

        raise ValueError(
            f"Unknown engine: {engine_name}"
        )
