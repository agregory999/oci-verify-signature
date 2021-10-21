# Generate XML

Test program to generate signed XML to use with the signature verification function located here:
[verify-signature-java](../verify-signature-java)

Given a basic XML file (example: report.xml), we can generate a signed XML file, to be sent and verified.  The signing process uses a "pre-shared secret key", a string that is known by both parties.  On the signing side, that key is used to generate the necessary signature which is inserted into the xml.    

Key is located in AGVault:
ocid1.vaultsecret.oc1.iad.amaaaaaaytsgwaya3xably7gcwtu3ir4hf4btzlfqeszcj5vtbqlbwwnjwga

Hard-coded text in the class
OCID needed for Verification

## Compile and Run

1) Compile the program using vscode or command line

```bash
prompt> javac -d . GenerateSignedXML.java
```

2) Obtain or create a valid XML file
3) Run the program with

```bash
prompt> java -cp . com.oracle.digitalsignature.GenerateSignedXML report.xml  
<?xml version="1.0" encoding="UTF-8" standalone="no"?><purchaseReport xmlns="http://www.example.com/Report" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" period="P3M" periodEnding="1999-12-31" xsi:schemaLocation="http://www.example.com/Report  report.xsd">
...
<Signature xmlns="http://www.w3.org/2000/09/xmldsig#"><SignedInfo><CanonicalizationMethod Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"/><SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#hmac-sha1"/><Reference URI=""><Transforms><Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"/></Transforms><DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/><DigestValue>nk+ObQEgnPPtnefSk6FvvMyfVa4=</DigestValue></Reference></SignedInfo><SignatureValue>wOSG0wCFOEAvsB7e+X/HjlJtIx8=</SignatureValue></Signature></purchaseReport>       
```

4) Save the resulting XML to a file as such:

```bash
prompt> java -cp . com.oracle.digitalsignature.GenerateSignedXML report.xml > report-signed.xml 
```
## Test Verification

Follow the instructions in the [Verify Signature Java](../verify-signature-java) directory to deploy the function to an OCI tenancy with Oracle Functions installed and configured.

Invoke with the signed XML file and refer to an OCID for a Secret in an OCI Vault that you need to create.  In this case the same "Pre-shared secret" that is in the code is also located in the Vault, and the OCID in the following command simply refers to the matching key:

```bash
prompt>  cat <<EOF|fn -v invoke FunctionsApp verify-signature-java
{"base64InputXML":"$(report-signed.xml|base64)","secretOcid":"ocid1.vaultsecret.oc1.iad.amaaaaaaytsgwaya3xably7gcwtu3ir4hf4btzlfqeszcj5vtbqlbwwnjwga"}
EOF
```
The output should be as follows:
```
{"verified":true,"detail":"|Digital signature VALID!!!"}
```

To get a negative result, simply copy the signed XML file, make a change, and then re-execute with the changed file.

```
prompt> cp report-signed.xml report-signed-tampered.xml
prompt> vi report-signed-tampered.xml
prompt> cat <<EOF|fn -v invoke FunctionsApp verify-signature-java
{"base64InputXML":"$(report-signed-tampered.xml|base64)","secretOcid":"ocid1.vaultsecret.oc1.iad.amaaaaaaytsgwaya3xably7gcwtu3ir4hf4btzlfqeszcj5vtbqlbwwnjwga"}
EOF
```
The result should look similar to:
```
{"verified":false,"detail":"|Digital Signature found but failed.  Use DEBUG for more information."}
```

## Add Debug

Add a debug flag to the call in order to see more information.  Append it to the JSON input:

```bash
prompt> at <<EOF|fn -v invoke FunctionsApp verify-signature-java 
{"base64InputXML":"$(cat report-signed.xml|base64)","secretOcid":"ocid1.vaultsecret.oc1.iad.amaaaaaaytsgwaya3xably7gcwtu3ir4hf4btzlfqeszcj5vtbqlbwwnjwga","debug":true}
EOF
{"verified":true,"detail":"|Secret Found:abcXML from Base64:<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?><purchaseReport xmlns=\"http://www.example.com/Report\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" period=\"P3M\" periodEnding=\"1999-12-31\" xsi:schemaLocation=\"http://www.example.com/Report  report.xsd\">\n\n <regions>\n  <zip code=\"95819\">\n   <part number=\"872-AA\" quantity=\"1\"/>\n   <part number=\"926-AA\" quantity=\"1\"/>\n   <part number=\"833-AA\" quantity=\"1\"/>\n   <part number=\"455-BX\" quantity=\"1\"/>\n  </zip>\n  <zip code=\"63143\">\n   <part number=\"455-BX\" quantity=\"4\"/>\n  </zip>\n </regions>\n\n <parts>\n  <part number=\"872-AA\">Lawnmower</part>\n  <part number=\"926-AA\">Baby Monitor</part>\n  <part number=\"833-AA\">Lapis Necklace</part>\n  <part number=\"455-BX\">Sturdy Shelves</part>\n </parts>\n\n<Signature xmlns=\"http://www.w3.org/2000/09/xmldsig#\"><SignedInfo><CanonicalizationMethod Algorithm=\"http://www.w3.org/TR/2001/REC-xml-c14n-20010315\"/><SignatureMethod Algorithm=\"http://www.w3.org/2000/09/xmldsig#hmac-sha1\"/><Reference URI=\"\"><Transforms><Transform Algorithm=\"http://www.w3.org/2000/09/xmldsig#enveloped-signature\"/></Transforms><DigestMethod Algorithm=\"http://www.w3.org/2000/09/xmldsig#sha1\"/><DigestValue>nk+ObQEgnPPtnefSk6FvvMyfVa4=</DigestValue></Reference></SignedInfo><SignatureValue>wOSG0wCFOEAvsB7e+X/HjlJtIx8=</SignatureValue></Signature></purchaseReport>|XMLSig: org.jcp.xml.dsig.internal.dom.DOMXMLSignature@451d3bee|SigVal: [B@320494b6|Sig Method: http://www.w3.org/2000/09/xmldsig#hmac-sha1|Digital signature VALID!!!"}
```

