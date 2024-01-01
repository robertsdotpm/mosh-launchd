"""
This module provides a simple REST server that will
spawn a new mosh server and return its connect details
when calling its root URL path e.g. http://localhost:8080/
-> mosh-client ... 

You can then easily construct shell commands that will
automatically spawn a mosh server and connect to it on
systems like Windows where the integration with mosh
is currently poorly supported.

Requires: p2pd
Use: python3 -m pip install p2pd
"""

import asyncio, re
from p2pd import *

LISTEN_PORT = 8088
MOSH_SERVER = "c:\\cygwin64\\bin\\mosh-server.exe"

async def create_mosh_server():
    proc = await asyncio.create_subprocess_exec(
        MOSH_SERVER,
        "new",
        "-i",
        "0.0.0.0",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT
    )

    stdout = proc.stdout
    out = await stdout.read()
    return proc, out

class Launchd(RESTD):
    proc_list = []

    def __init__(self, interface):
        self.interface = interface
        super().__init__()

    @RESTD.GET()
    async def fork_mosh_server(self, v, pipe):
        # Spawn a new mosh server process.
        p = b'MOSH CONNECT ([0-9]+) ([^\s]+)'
        proc, buf = await create_mosh_server()
        port, key = re.findall(p, buf)[0]
        port = to_s(port); key = to_s(key)

        """
        This is very important: the reference to the sub process
        has to be saved or the Python garbage collector will kill
        it and the mosh server will be closed. It's enough
        to just saved references to the proc in a list.
        """
        self.proc_list.append(proc)

        # Return the mosh server details to the REST client.
        ip = self.interface.nic(IP4)
        return f"export MOSH_KEY='{key}'; mosh-client {ip} {port}"
        

async def main():
    # Lookup table to get the right loopback address.
    localhost = {
        IP4: "127.0.0.1",
        IP6: "::1"
    }

    # Get ip stack details for default interface.
    i = await Interface()

    # Bind to loopback for all supported AFs.
    targets = []
    for af in i.supported():
        ips = localhost[af]
        r = await i.route(af=af).bind(ips=ips, port=LISTEN_PORT)
        targets.append([r, TCP])

    # Start the launch daemon and listen on loopback targets.
    d = await Launchd(i).listen_specific([*targets])
    while 1:
        await asyncio.sleep(1)

async_test(main)