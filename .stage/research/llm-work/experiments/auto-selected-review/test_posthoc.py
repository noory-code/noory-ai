"""코드 이름에 붙는 한국어 조사와 다른 식별자를 구별합니다."""

import unittest

from posthoc_probe import explicit_names


class NameTests(unittest.TestCase):
    def test_korean_particle_does_not_hide_code_name(self) -> None:
        self.assertEqual(explicit_names("write_driver_retrospective로 씁니다.",
                                        ["write_driver_retrospective"]),
                         ["write_driver_retrospective"])

    def test_part_of_another_identifier_is_not_a_match(self) -> None:
        self.assertEqual(explicit_names("old_entry와 entry_extra", ["entry"]), [])


if __name__ == "__main__":
    unittest.main()
