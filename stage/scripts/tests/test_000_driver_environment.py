from __future__ import annotations

import unittest

from driver_test_environment import (
    DRIVER_REVIEW_ENVIRONMENT_VARIABLES,
    sanitized_driver_test_environment,
)


class DriverTestEnvironmentTest(unittest.TestCase):
    def test_sanitizer_removes_only_driver_review_variables(self):
        source = {
            "KEEP_ME": "ordinary",
            **{
                name: f"inherited-{index}"
                for index, name in enumerate(
                    DRIVER_REVIEW_ENVIRONMENT_VARIABLES
                )
            },
        }

        self.assertEqual(
            {"KEEP_ME": "ordinary"},
            sanitized_driver_test_environment(source),
        )


if __name__ == "__main__":
    unittest.main()
