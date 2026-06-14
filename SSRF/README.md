# Some applications block input containing hostnames like 127.0.0.1 and localhost, or sensitive URLs like /admin
- Use an alternative IP representation of 127.0.0.1, such as 2130706433, 017700000001, or 127.1.
- Register your own domain name that resolves to 127.0.0.1. You can use spoofed.burpcollaborator.net for this purpose.
- Obfuscate blocked strings using URL encoding or case variation.
- Provide a URL that you control, which redirects to the target URL. Try using different redirect codes, as well as different protocols for the target URL. For example, switching from an http: to https: URL during the redirect has been shown to bypass some anti-SSRF filters. 

## What devs can do wrong and how to exploit:
- have a blacklist for certain ip addresses => (try the decimal or octal version of the ip address)
- have a blacklist for certain endpoints => (try encoding or even double encoding)

# Some applications only allow inputs that match, a whitelist of permitted values. 
- The filter may look for a match at the beginning of the input, or contained within in it. You may be able to bypass this filter by exploiting inconsistencies in URL parsing.

- The URL specification contains a number of features that are likely to be overlooked when URLs implement ad-hoc parsing and validation using this method:

    - You can embed credentials in a URL before the hostname, using the @ character. For example:
    https://expected-host:fakepassword@evil-host

    - You can use the # character to indicate a URL fragment. For example:
    https://evil-host#expected-host

    - You can leverage the DNS naming hierarchy to place required input into a fully-qualified DNS name that you control. For example:
    https://expected-host.evil-host
    - You can URL-encode characters to confuse the URL-parsing code. This is particularly useful if the code that implements the filter handles URL-encoded characters differently than the code that performs the back-end HTTP request. You can also try double-encoding characters; some servers recursively URL-decode the input they receive, which can lead to further discrepancies.
    - You can use combinations of these techniques together.