def test_dashboard_shows_events(page):
    page.goto("http://localhost:8000/dashboard/")
    assert page.locator("h2").inner_text() == "Dashboard"
