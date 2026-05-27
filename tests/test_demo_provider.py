from mexico_traffic_monitor.providers import DemoTrafficProvider


def test_demo_provider_returns_incidents():
    provider = DemoTrafficProvider()

    incidents = provider.fetch_incidents()

    assert incidents
    assert all(incident.city for incident in incidents)
    assert all(incident.latitude for incident in incidents)
    assert all(incident.longitude for incident in incidents)


def test_demo_provider_changes_congestion_over_time():
    provider = DemoTrafficProvider()

    first = provider.fetch_incidents()
    second = provider.fetch_incidents()

    assert [item.congestion_level for item in first] != [item.congestion_level for item in second]
