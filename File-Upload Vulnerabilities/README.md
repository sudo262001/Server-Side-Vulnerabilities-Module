## For HTML forms the format/encoding of the body content is determined by the enctype attribute of the <form> element or the formenctype attribute of the <input> or <button> elements. The encoding may be one of the following:
1. application/x-www-form-urlencoded: the keys and values are encoded in key-value tuples separated by an ampersand (&), with an equals symbol (=) between the key and the value (e.g., first-name=Frida&last-name=Kahlo). Non-alphanumeric characters in both keys and values are percent-encoded: this is the reason why this type is not suitable to use with binary data and you should use multipart/form-data for this purpose instead.
2. multipart/form-data: each value is sent as a block of data ("body part"), with a user agent-defined delimiter (for example, boundary="delimiter12345") separating each part. The keys are described in the Content-Disposition header of each part or block of data.
3. text/plain

- The multipart/form-data encoding is used when a form includes files or a lot of data. This request body delineates each part of the form using a boundary string. An example of a request in this format:
```HTTP
POST /test HTTP/1.1
Host: example.com
Content-Type: multipart/form-data;boundary="delimiter12345"

--delimiter12345
Content-Disposition: form-data; name="field1"

value1
--delimiter12345
Content-Disposition: form-data; name="field2"; filename="example.txt"

value2
--delimiter12345--
```
* The Content-Disposition header indicates how the form data should be processed, specifying the field name and filename, if appropriate.
* One way that websites may attempt to validate file uploads is to check that this input-specific Content-Type header matches an expected MIME type. If the server is only expecting image files, for example, it may only allow types like image/jpeg and image/png. Problems can arise when the value of this header is implicitly trusted by the server.

## Preventing file execution in user-accessible directories
Scripts can still be uploaded without restrictions but they don't get executed
- Find another directory to upload the script on it and execute it (ex: path traversal)

## Insufficient blacklisting of dangerous file types
- before an Apache server will execute PHP files requested by a client, developers might have to add the following directives to their /etc/apache2/apache2.conf file:
```php
LoadModule php_module /usr/lib/apache2/modules/libphp.so
    AddType application/x-httpd-php .php
```
Many servers also allow developers to create special configuration files within individual directories in order to override or add to one or more of the global settings. Apache servers, for example, will load a directory-specific configuration from a file called .htaccess if one is present.

- Similarly, developers can make directory-specific configuration on IIS servers using a web.config file. This might include directives such as the following, which in this case allows JSON files to be served to users:
```xml
<staticContent>
    <mimeMap fileExtension=".json" mimeType="application/json" />
</staticContent>
```

## Obfuscating File Extensions
 Even the most exhaustive blacklists can potentially be bypassed using classic obfuscation techniques. 
 - Let's say the validation code is case sensitive and fails to recognize that exploit.pHp is in fact a .php file. 
You can also achieve similar results using the following techniques:
    - Provide multiple extensions. Depending on the algorithm used to parse the filename, the following file may be interpreted as either a PHP file or JPG image: exploit.php.jpg
    - Add trailing characters. Some components will strip or ignore trailing whitespaces, dots, and suchlike: exploit.php.
    - Try using the URL encoding (or double URL encoding) for dots, forward slashes, and backward slashes. If the value isn't decoded when validating the file extension, but is later decoded server-side, this can also allow you to upload malicious files that would otherwise be blocked: exploit%2Ephp
    - Add semicolons or URL-encoded null byte characters before the file extension. If validation is written in a high-level language like PHP or Java, but the server processes the file using lower-level functions in C/C++, for example, this can cause discrepancies in what is treated as the end of the filename: exploit.asp;.jpg or exploit.asp%00.jpg
    - Try using multibyte unicode characters, which may be converted to null bytes and dots after unicode conversion or normalization. Sequences like xC0 x2E, xC4 xAE or xC0 xAE may be translated to x2E if the filename parsed as a UTF-8 string, but then converted to ASCII characters before being used in a path.

## Note! To test if null byte worked the uploaded shell would be in exploit.php without the trailing null byte and the expected extension

- Other defenses involve stripping or replacing dangerous extensions to prevent the file from being executed. If this transformation isn't applied recursively, you can position the prohibited string in such a way that removing it still leaves behind a valid file extension. For example, consider what happens if you strip .php from the following filename:
exploit.p.phphp
* This is just a small selection of the many ways it's possible to obfuscate file extensions. 

## Flawed validation of the file's contents
- Instead of implicitly trusting the Content-Type specified in a request, more secure servers try to verify that the contents of the file actually match what is expected.

- In the case of an image upload function, the server might try to verify certain intrinsic properties of an image, such as its dimensions. If you try uploading a PHP script, for example, it won't have any dimensions at all. Therefore, the server can deduce that it can't possibly be an image, and reject the upload accordingly.

- Similarly, certain file types may always contain a specific sequence of bytes in their header or footer. These can be used like a fingerprint or signature to determine whether the contents match the expected type. For example, JPEG files always begin with the bytes FF D8 FF.

- Using special tools, such as ExifTool, it can be trivial to create a polyglot JPEG file containing malicious code within its metadata. 

## Exploiting file upload race conditions
Some websites upload the file directly to the main filesystem and then remove it again if it doesn't pass validation. This kind of behavior is typical in websites that rely on anti-virus software and the like to check for malware. This may only take a few milliseconds, but for the short time that the file exists on the server, the attacker can potentially still execute it.

These vulnerabilities are often extremely subtle, making them difficult to detect during blackbox testing unless you can find a way to leak the relevant source code. 
## Uploading files using PUT
It's worth noting that some web servers may be configured to support PUT requests. If appropriate defenses aren't in place, this can provide an alternative means of uploading malicious files, even when an upload function isn't available via the web interface. 