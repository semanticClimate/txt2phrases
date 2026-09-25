# Unit tests for logging configuration.
import logging

from txt2phrases.logging_config import configure_logging, LOGGER_NAME


class TestConfigureLogging:
    def test_default_level_is_info(self):
        logger = configure_logging()
        assert logger.level == logging.INFO

    def test_verbose_sets_debug(self):
        logger = configure_logging(verbosity=1)
        assert logger.level == logging.DEBUG

    def test_quiet_sets_warning(self):
        logger = configure_logging(quiet=True)
        assert logger.level == logging.WARNING

    def test_quiet_overrides_verbose(self):
        logger = configure_logging(verbosity=1, quiet=True)
        assert logger.level == logging.WARNING

    def test_returns_the_txt2phrases_logger(self):
        logger = configure_logging()
        assert logger.name == LOGGER_NAME == "txt2phrases"

    def test_reconfiguring_does_not_stack_handlers(self):
        configure_logging()
        configure_logging()
        configure_logging(verbosity=1)
        logger = logging.getLogger(LOGGER_NAME)
        assert len(logger.handlers) == 1, "each call should replace, not accumulate, handlers"

    def test_messages_are_captured_by_caplog(self, caplog):
        configure_logging()
        logger = logging.getLogger("txt2phrases.some_module")

        with caplog.at_level(logging.INFO, logger="txt2phrases"):
            logger.info("hello from a submodule")

        assert "hello from a submodule" in caplog.text

    def test_quiet_suppresses_info_messages(self, capfd):
        configure_logging(quiet=True)
        logger = logging.getLogger("txt2phrases.some_module")

        logger.info("should not appear")
        logger.warning("should appear")

        out, _ = capfd.readouterr()
        assert "should not appear" not in out
        assert "should appear" in out
