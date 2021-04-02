# XML Digital Signature Verification - Java

This use case is based on a customer requirement to ensure that messages received as part of a processing flow are verified to have been untouched since they were created.  The original example uses XML Digital Signature in Java, and is implemented as an Oracle Service Bus callout.  As part of a move to Oracle Integration Cloud (OIC), the same type of flow is needed, but without a Java callout.   

In this example, the XML message has already been produced by the client and contains the XML Signature, as defined by the following spec:
[W3C](https://www.w3.org/TR/xmldsig-core/)

The XML file is Base64 encoded and passed in along with an OCID of a pre-shared secret which must be placed into an OIC Vault.  The function performs the following steps:
- Retrieves the plain-text pre-shared secret from the OCI Vault
- Decodes the XML into a DOM object
- Isolates the XMLSignature element and verifies it
- Returns true or false along with detailed messages if configured

### Diagram
![Diagram](../images/DigitalSignatureFlowJava.svg)

## Client Flow
The message is an existing XML document.  It must be paired with a working pre-shared secret key in order to verify.  This function has been tested in 2 ways:
1) Via a command line invocation using base64-encoded XML message and OCID of pre-shared secret
2) Via Oracle Integration, which reads the message from an SFTP adapter, and sends the base64-encoded contents of the message directly to the function

## Command Line
From the command line, the original message is first base64-encoded:
```bash
prompt> cat file.xml | base64 > file-base64.xml
```
Following this, the function is configured into an FN Context and invoked as such:
```bash
cat <<EOF | fn -v invoke FunctionsApp verify-signature-java
{"base64InputXML":"$(cat file-base64.xml)","secretOcid":"ocid1.vaultsecret.oc1.xxxxx"}
EOF
```
The reply will contain a JSON document with a boolean field (verified) and a string (messages).  These can be uses by upstream callers in order to continue or stop processing messages.
```
{"verified":true,"detail":"|Digital signature VALID!!!"}
```
-OR-
```
{"verified":false,"detail":"|Digital Signature found but failed.  Use DEBUG for more information."}
```
