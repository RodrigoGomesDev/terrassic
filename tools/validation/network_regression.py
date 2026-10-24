"""Real socket regression of notebooks, two UUIDs, delta negotiation, reconnect and server restart."""
import argparse
import time
from pathlib import Path

from local_server import LocalServer
from minecraft_client import LocalClient


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def connect(server, name, supports_delta=True):
    client = LocalClient(server.port, name, server.loader, supports_delta)
    try:
        client.wait_for(lambda c: c.knowledge is not None)
        time.sleep(1)  # Let the channel-registration packet reach the server before creating a page.
        return client
    except BaseException:
        client.close()
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--loader", choices=["fabric", "forge"], required=True)
    parser.add_argument("--eula-file", type=Path, required=True)
    parser.add_argument("--startup-timeout", type=int, default=360)
    args = parser.parse_args()
    server = LocalServer(args.loader, args.eula_file)
    clients = []
    print(f"Reports and disposable world: {server.directory}", flush=True)
    try:
        server.start("network-create", timeout=args.startup_timeout)
        alice = connect(server, "TerraAlice")
        clients.append(alice)
        bob = connect(server, "TerraBob", supports_delta=False)
        clients.append(bob)
        require(alice.profile_uuid != bob.profile_uuid, "players must have different UUIDs")
        require(alice.knowledge.get("IntroSeen") == 1 and bob.knowledge.get("IntroSeen") == 1, "first join must initialize notebooks")
        require(not alice.knowledge.get("Pages") and not bob.knowledge.get("Pages"), "new notebooks must start independently empty")
        server.command('give TerraAlice terrassic:loose_page{Page:"c1_day_3"} 1')
        first_page = alice.wait_for(lambda c: len(c.knowledge.get("Pages", [])) == 1)
        require(first_page["Pages"] == ["c1_day_3"], "Alice must receive the explicitly selected page")
        require(alice.delta_packets > 0, "capable client must receive a delta over the real connection")
        require(not bob.knowledge.get("Pages"), "Alice's page must not leak to Bob")
        server.command('give TerraBob terrassic:loose_page{Page:"c1_day_9"} 1')
        bob_page = bob.wait_for(lambda c: len(c.knowledge.get("Pages", [])) == 1)
        require(bob_page["Pages"] == ["c1_day_9"], "Bob must have his own explicitly selected page")
        require(bob.delta_packets == 0 and bob.full_packets >= 2, "legacy-capability client must get full snapshots")
        alice_uuid, bob_uuid = alice.profile_uuid, bob.profile_uuid
        print(f"{args.loader}: real joins, distinct UUIDs, page delta and legacy full fallback passed", flush=True)
        alice.close()
        clients.remove(alice)
        server.wait(lambda: any("TerraAlice lost connection" in line for line in server.lines), 15)
        alice = connect(server, "TerraAlice")
        clients.append(alice)
        require(alice.profile_uuid == alice_uuid and alice.knowledge == first_page, "reconnect must restore the same notebook via a full snapshot")
        require(alice.full_packets >= 1 and alice.intro_packets == 0, "rejoin must force full state without replaying first-join intro")
        saved_alice, saved_bob = alice.knowledge, bob.knowledge
        for client in clients:
            client.close()
        clients.clear()
        server.stop()
        for player in (alice_uuid, bob_uuid):
            require((server.directory / "world/data" / f"terrassic_research_{player}.dat").is_file(), "real joined players need individual saved files")
        server.start("network-reload", timeout=args.startup_timeout)
        alice = connect(server, "TerraAlice")
        clients.append(alice)
        bob = connect(server, "TerraBob", supports_delta=False)
        clients.append(bob)
        require(alice.knowledge == saved_alice and bob.knowledge == saved_bob, "both notebooks must survive server restart independently")
        require(alice.intro_packets == bob.intro_packets == 0, "saved introduction flags must survive server restart")
        print(f"PASS: {args.loader} real sockets: UUID isolation, pages, delta, legacy fallback, reconnect and restart", flush=True)
    finally:
        for client in clients:
            client.close()
        server.stop()


if __name__ == "__main__":
    main()
