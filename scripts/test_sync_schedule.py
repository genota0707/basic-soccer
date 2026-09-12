import unittest

from sync_schedule import build_schedule


EVENTS = "日付,内容,時間,会場,補足,表示\n2026-10-24,幼児向け単発スクール,,,詳細はLINEへ,公開\n2026-10-31,別の日程,,,,非公開\n"
BOOKINGS = "日付,時間,状態,表示\n2026-10-24,13:30〜15:00,空きあり,公開\n2026-10-31,16:30〜18:00,満席,非公開\n"


class ScheduleTest(unittest.TestCase):
    def test_public_rows_only_and_date_format(self):
        result = build_schedule(EVENTS, BOOKINGS)
        self.assertEqual([x["date"] for x in result["events"]], ["2026-10-24"])
        self.assertEqual(result["bookings"][0]["status"], "空きあり")
        self.assertEqual(len(result["bookings"]), 1)

    def test_invalid_status_stops_publication(self):
        with self.assertRaises(ValueError):
            build_schedule(EVENTS, BOOKINGS.replace("空きあり", "不明"))

    def test_invalid_date_stops_publication(self):
        with self.assertRaises(ValueError):
            build_schedule(EVENTS.replace("2026-10-24", "10月24日"), BOOKINGS)


if __name__ == "__main__":
    unittest.main()
