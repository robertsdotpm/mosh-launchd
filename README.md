# Mosh integration on Windows and other systems

So here's the problem. Mosh is cool. It's much more reliable than a regular shell
connection. But its integration is horrible on Windows (and maybe other OS.)
The way Mosh functions is:

1. A shell connection is made to the system you want to remote to.
2. A new Mosh server is started on that machine and it returns a unique port
and password for you to connect to.
3. THEN your client uses that information to connect back to that server.

You unfortunately have to do that manually on Windows though which is just... bad.
So I wrote a simple script to solve that. Here's how it works:

1. There's a custom REST daemon running on loopback - it will spawn a new Mosh
server and send back the connection details.
2 This can then be easily combined with standard shell scripts to automatically
login to the server with SSH, 'talk' to the REST server, and use its details
to connect back to it.

## Server machine

python3 -m pip install p2pd
git clone git@github.com:robertsdotpm/mosh-launchd.git
cd mosh-launchd
python3 main.py

(Server is now running)

## Client machine

bash -c "$(ssh YOUR_USER@SERVER_IP curl http://localhost:8088/ 2>/dev/null)"

(Client machine has id_rsa access to server machine already.)
(Client machine has curl installed.)

What this command does is:

1. Login to SERVER_IP over SSH.
2. Use curl to make a call to the special REST daemon on the server machine.
3. That daemon returns a bash command that happens to let you connect back to it
using mosh-client.
4. the client executes that command as a new bash command which happens to result in
a mosh shell back to the machine.

In other words its an implemention of what mosh normally does for windows
in a simple way that's more portable.
